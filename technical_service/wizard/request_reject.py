# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RequestRejectWizard(models.TransientModel):
    """
    Wizard for rejecting service request
    Task 07 - Phase 3D: Manual workflow action
    User requirement: Must create new request when rejecting
    """
    _name = 'technical_service.request.reject.wizard'
    _description = 'Reject Service Request'

    request_id = fields.Many2one(
        'maintenance.request',
        string='Service Request',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('active_id')
    )

    rejection_reason = fields.Text(
        string='Rejection Reason',
        required=True,
        help='Explain why this request is being rejected'
    )

    # Check if this is a cancel rejection (conditional required fields)
    is_cancel_rejection = fields.Boolean(
        string='Is Cancel Rejection',
        compute='_compute_is_cancel_rejection',
        help='True if rejecting a cancel request'
    )

    # New request fields (mandatory only for completion rejection)
    new_request_name = fields.Char(
        string='New Request Title',
        help='Title for the new corrected request'
    )

    new_request_description = fields.Html(
        string='New Request Description',
        help='Detailed description of what needs to be done correctly'
    )

    copy_attachments = fields.Boolean(
        string='Copy Attachments',
        default=True,
        help='Copy attachments from rejected request to new request'
    )

    @api.depends('request_id', 'request_id.x_pending_cancel')
    def _compute_is_cancel_rejection(self):
        """Check if this is a cancel rejection"""
        for wizard in self:
            wizard.is_cancel_rejection = wizard.request_id.x_pending_cancel if wizard.request_id else False

    @api.onchange('is_cancel_rejection')
    def _onchange_is_cancel_rejection(self):
        """Make new request fields required only for completion rejection"""
        if not self.is_cancel_rejection:
            # Completion rejection - new request fields required
            self._fields['new_request_name'].required = True
            self._fields['new_request_description'].required = True
        else:
            # Cancel rejection - new request fields not required
            self._fields['new_request_name'].required = False
            self._fields['new_request_description'].required = False

    def action_confirm_reject(self):
        """
        Confirm rejection
        Task 07 - Phase 3D & Phase 4B
        - If x_pending_cancel=True: Reject cancel request → return to previous stage
        - Otherwise: Reject completion → create new request and mark as 'Reddedildi'
        """
        self.ensure_one()

        if not self.request_id:
            raise UserError(_('No request specified'))

        request = self.request_id

        # Check permission (should be department manager or CTO)
        if not request.x_can_reject:
            raise UserError(_('You do not have permission to reject this request'))

        # Phase 4B: Check if this is a cancel rejection
        if request.x_pending_cancel:
            # CANCEL REJECTION: Return to previous stage
            return self._reject_cancel_request()

        # 1. Create new request with corrected information
        new_request_vals = {
            'name': self.new_request_name,
            'description': self.new_request_description,
            'maintenance_team_id': request.maintenance_team_id.id,
            'x_service_category': request.x_service_category,
            'x_it_category': request.x_it_category,
            'x_technical_category': request.x_technical_category,
            'x_campus_id': request.x_campus_id.id if request.x_campus_id else False,
            'x_building_id': request.x_building_id.id if request.x_building_id else False,
            'x_floor': request.x_floor,
            'x_room': request.x_room,
            'x_impact': request.x_impact,
            'x_urgency': request.x_urgency,
            'employee_id': request.create_uid.employee_id.id if request.create_uid.employee_id else False,
        }

        new_request = self.env['maintenance.request'].create(new_request_vals)

        # 2. Copy attachments if requested
        if self.copy_attachments:
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'maintenance.request'),
                ('res_id', '=', request.id)
            ])
            for attachment in attachments:
                attachment.copy({'res_id': new_request.id})

        # 3. Transition original request to 'Reddedildi'
        request._transition_to_stage(
            'Reddedildi',
            reason=self.rejection_reason,
            is_auto=False
        )

        # 4. Log rejection
        self.env['technical_service.request.history'].log_approval(
            request=request,
            status='rejected',
            reason=self.rejection_reason
        )

        # 5. Post to both requests' chatter
        request.message_post(
            body=_('Request rejected.<br/>Reason: %s<br/>New request created: %s (#%s)',
                   self.rejection_reason, new_request.name, new_request.x_request_number),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        new_request.message_post(
            body=_('This request was created to replace rejected request: %s (#%s)<br/>Original rejection reason: %s',
                   request.name, request.x_request_number, self.rejection_reason),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        # 6. Return action to open new request
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Request Created'),
            'res_model': 'maintenance.request',
            'res_id': new_request.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _reject_cancel_request(self):
        """
        Reject a cancel request
        Task 07 - Phase 4B
        Return the request to its previous stage before cancellation was requested
        """
        request = self.request_id

        # Get the previous stage (stored when cancel was requested)
        if not request.x_previous_stage_id:
            raise UserError(_('Cannot reject: Previous stage information is missing'))

        # Transition back to previous stage
        request.write({'stage_id': request.x_previous_stage_id.id})

        # Log the rejection
        self.env['technical_service.request.history'].create({
            'request_id': request.id,
            'event_type': 'comment',
            'note': _('Cancel request rejected by %s. Returned to "%s" stage.<br/>Reason: %s',
                      self.env.user.name,
                      request.x_previous_stage_id.name,
                      self.rejection_reason),
            'is_automatic': False,
        })

        # Post to chatter
        request.message_post(
            body=_('❌ Cancel request rejected by %s<br/>'
                   'Request returned to "%s" stage.<br/>'
                   'Rejection reason: %s',
                   self.env.user.name,
                   request.x_previous_stage_id.name,
                   self.rejection_reason),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        # Notify the person who requested cancellation
        if request.create_uid:
            request.message_post(
                body=_('Your cancellation request has been rejected.<br/>'
                       'The service request will continue. Rejection reason: %s',
                       self.rejection_reason),
                message_type='notification',
                subtype_xmlid='mail.mt_note',
                partner_ids=[request.create_uid.partner_id.id]
            )

        # Clear cancel tracking fields
        request.write({
            'x_pending_cancel': False,
            'x_cancel_reason': False,
            'x_previous_stage_id': False,
        })

        # Close wizard
        return {'type': 'ir.actions.act_window_close'}
