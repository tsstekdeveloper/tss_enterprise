# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RequestCancelWizard(models.TransientModel):
    """
    Wizard for cancelling service request
    Task 07 - Phase 3E: Manual workflow action
    User requirement: Owner can cancel their own pending requests
    """
    _name = 'technical_service.request.cancel.wizard'
    _description = 'Cancel Service Request'

    request_id = fields.Many2one(
        'maintenance.request',
        string='Service Request',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('active_id')
    )

    cancel_reason = fields.Text(
        string='Cancellation Reason',
        required=True,
        help='Explain why this request is being cancelled'
    )

    requires_approval = fields.Boolean(
        string='Requires Approval',
        compute='_compute_requires_approval',
        help='If work has started, cancellation requires approval from owner'
    )

    def _compute_requires_approval(self):
        """
        Check if cancellation requires approval from request owner
        Business Rule: When Dispatcher or Team Leader cancels a request,
        the request owner must approve the cancellation.
        Only the owner can cancel directly without approval.
        """
        for wizard in self:
            request = wizard.request_id
            current_user = self.env.user
            is_owner = request.create_uid == current_user

            # Requires approval if current user is NOT the owner
            # (i.e., Dispatcher or Team Leader is cancelling)
            wizard.requires_approval = not is_owner

    def action_confirm_cancel(self):
        """
        Confirm cancellation
        Task 07 - Phase 4B: Stage-based cancel approval
        - Owner can cancel directly → 'İptal Edildi'
        - Non-owner (Dispatcher/Team Leader) must request approval → 'Onayda' stage
        """
        self.ensure_one()

        if not self.request_id:
            raise UserError(_('No request specified'))

        request = self.request_id

        # Check permission
        if not request.x_can_cancel:
            raise UserError(_(
                'You do not have permission to cancel this request.\n'
                'Requests can only be cancelled when in "Yeni" (New) or "Ekip Atandı" (Team Assigned) stages.'
            ))

        current_user = self.env.user
        is_owner = request.create_uid == current_user

        # If requires approval and user is not owner
        if self.requires_approval and not is_owner:
            # PHASE 4B: Send to "Onayda" stage for owner approval
            self._request_cancel_approval()

            # Show notification to user
            message = _('Cancellation request sent. Request moved to "Onayda" stage for owner approval.')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Cancellation Request Sent'),
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        else:
            # Owner cancelling - cancel immediately
            self._execute_cancel()
            return {'type': 'ir.actions.act_window_close'}

    def _request_cancel_approval(self):
        """
        Send cancellation approval request to owner
        Task 07 - Phase 4B: Move request to "Onayda" stage
        """
        request = self.request_id

        # Store current stage to return to if rejected
        request.write({'x_previous_stage_id': request.stage_id.id})

        # Mark as pending cancellation
        request.write({
            'x_pending_cancel': True,
            'x_cancel_reason': self.cancel_reason,
        })

        # Transition to 'Onayda' stage
        request._transition_to_stage(
            'Onayda',
            reason=_('Cancellation requested by %s', self.env.user.name),
            is_auto=False
        )

        # Post to chatter
        request.message_post(
            body=_('⚠️ Cancellation requested by %s<br/>'
                   'Reason: %s<br/>'
                   'Request moved to "Onayda" stage. Owner must approve or reject.',
                   self.env.user.name, self.cancel_reason),
            message_type='notification',
            subtype_xmlid='mail.mt_note',
            partner_ids=[request.create_uid.partner_id.id]
        )

        # Log in history
        self.env['technical_service.request.history'].create({
            'request_id': request.id,
            'event_type': 'comment',
            'note': _('Cancellation requested by %s. Waiting for owner approval in "Onayda" stage.',
                      self.env.user.name),
            'is_automatic': False,
        })

    def _execute_cancel(self):
        """Execute the cancellation"""
        request = self.request_id

        # Transition to 'İptal Edildi'
        request._transition_to_stage(
            'İptal Edildi',
            reason=self.cancel_reason,
            is_auto=False
        )

        # Cancel all pending work orders
        pending_wos = request.x_work_order_ids.filtered(
            lambda wo: wo.x_work_status in ['pending', 'in_progress', 'paused']
        )
        for wo in pending_wos:
            wo.write({'x_work_status': 'cancelled'})

        # Log cancellation
        self.env['technical_service.request.history'].log_approval(
            request=request,
            status='cancelled',
            reason=self.cancel_reason
        )

        # Post to chatter
        request.message_post(
            body=_('Request cancelled by %s<br/>Reason: %s', self.env.user.name, self.cancel_reason),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
