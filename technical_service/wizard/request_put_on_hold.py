# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RequestPutOnHoldWizard(models.TransientModel):
    """
    Wizard for putting service request on hold
    Task 07 - Phase 3A: Manual workflow action
    """
    _name = 'technical_service.request.put.on.hold.wizard'
    _description = 'Put Request On Hold'

    request_id = fields.Many2one(
        'maintenance.request',
        string='Service Request',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('active_id')
    )

    reason = fields.Text(
        string='Reason for Hold',
        required=True,
        help='Explain why this request is being put on hold'
    )

    expected_resume_date = fields.Date(
        string='Expected Resume Date',
        help='When do you expect to resume work on this request?'
    )

    def action_confirm_hold(self):
        """
        Confirm putting the request on hold
        Transitions to 'Beklemede' stage
        TASK 07 - PHASE 4C: Added permission check
        """
        self.ensure_one()

        if not self.request_id:
            raise UserError(_('No request specified'))

        request = self.request_id

        # PHASE 4C: Permission check
        if not request.x_can_put_on_hold:
            raise UserError(_(
                'You do not have permission to put this request on hold.\n'
                'Only Team Leaders, Senior Technicians, and Technicians can perform this action.'
            ))

        # Transition to 'Beklemede'
        request._transition_to_stage(
            'Beklemede',
            reason=self.reason,
            is_auto=False
        )

        # Log hold event
        self.env['technical_service.request.history'].log_hold(
            request=request,
            reason=self.reason
        )

        # Post to chatter
        message = _('Request put on hold.<br/>Reason: %s', self.reason)
        if self.expected_resume_date:
            message += _('<br/>Expected resume date: %s', self.expected_resume_date)
        
        request.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        return {'type': 'ir.actions.act_window_close'}
