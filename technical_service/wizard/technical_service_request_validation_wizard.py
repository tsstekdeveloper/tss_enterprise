# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TechnicalServiceRequestValidationWizard(models.TransientModel):
    """
    Wizard to warn users about missing information when creating service requests
    Shows a popup with option to continue editing or save anyway
    """
    _name = 'technical_service.request.validation.wizard'
    _description = 'Service Request Validation Warning'

    # Warning message to display
    warning_message = fields.Html(string='Warning Message', readonly=True)

    # Store the request data temporarily
    request_data = fields.Text(string='Request Data', readonly=True)

    def action_stay_editing(self):
        """Close wizard and return to form editing"""
        return {'type': 'ir.actions.act_window_close'}

    def action_continue_save(self):
        """Save the request despite warnings"""
        self.ensure_one()

        # Get the stored request data
        if not self.request_data:
            raise UserError(_('No request data found to save.'))

        # Parse the stored data and create the request
        import json
        vals = json.loads(self.request_data)

        # Create the maintenance request with skip validation context
        request = self.env['maintenance.request'].with_context(skip_validation_wizard=True).create(vals)

        # Return action to open the created request
        return {
            'type': 'ir.actions.act_window',
            'name': _('Service Request'),
            'res_model': 'maintenance.request',
            'res_id': request.id,
            'view_mode': 'form',
            'target': 'current',
        }
