# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # SLA Configuration
    module_technical_service_sla = fields.Boolean(
        string="Enable SLA Management",
        help="Enable Service Level Agreement management for service requests"
    )

    technical_service_default_sla_warning_hours = fields.Integer(
        string="Default SLA Warning Hours",
        default=2,
        config_parameter='technical_service.default_sla_warning_hours',
        help="Number of hours before SLA deadline to show warning"
    )

    # Work Order Configuration
    technical_service_auto_assign_work_order = fields.Boolean(
        string="Auto-assign Work Orders",
        config_parameter='technical_service.auto_assign_work_order',
        help="Automatically assign work orders based on technician workload"
    )

    technical_service_default_work_duration = fields.Float(
        string="Default Work Duration (hours)",
        default=2.0,
        config_parameter='technical_service.default_work_duration',
        help="Default duration for new work orders"
    )

    # Request Configuration
    technical_service_auto_create_work_order = fields.Boolean(
        string="Auto-create Work Orders",
        config_parameter='technical_service.auto_create_work_order',
        help="Automatically create work orders when service request is confirmed"
    )

    technical_service_request_email_template_id = fields.Many2one(
        'mail.template',
        string="Service Request Email Template",
        domain="[('model', '=', 'maintenance.request')]",
        config_parameter='technical_service.request_email_template_id',
        help="Email template to use for new service requests"
    )

    # Asset Configuration
    technical_service_track_asset_history = fields.Boolean(
        string="Track Asset History",
        default=True,
        config_parameter='technical_service.track_asset_history',
        help="Keep history of all changes to assets"
    )

    technical_service_preventive_maintenance_days = fields.Integer(
        string="Preventive Maintenance Reminder (days)",
        default=30,
        config_parameter='technical_service.preventive_maintenance_days',
        help="Days before next maintenance to send reminder"
    )

    # Team Configuration
    technical_service_team_assignment_method = fields.Selection([
        ('manual', 'Manual Assignment'),
        ('round_robin', 'Round Robin'),
        ('workload', 'Based on Workload'),
        ('expertise', 'Based on Expertise')
    ], string="Team Assignment Method",
       default='manual',
       config_parameter='technical_service.team_assignment_method',
       help="Method for assigning service requests to teams"
    )

    # Notification Configuration
    technical_service_notify_customer = fields.Boolean(
        string="Notify Customers",
        default=True,
        config_parameter='technical_service.notify_customer',
        help="Send email notifications to customers on status changes"
    )

    technical_service_notify_technician = fields.Boolean(
        string="Notify Technicians",
        default=True,
        config_parameter='technical_service.notify_technician',
        help="Send email notifications to technicians on new assignments"
    )

    # Report Configuration
    technical_service_include_internal_notes = fields.Boolean(
        string="Include Internal Notes in Reports",
        config_parameter='technical_service.include_internal_notes',
        help="Include internal notes when generating service reports"
    )

    # Stock SMS fields (to fix missing field errors)
    stock_move_sms_validation = fields.Boolean(
        string="SMS Validation for Stock Moves",
        config_parameter='stock.move_sms_validation',
        help="Enable SMS validation for stock moves"
    )

    stock_sms_confirmation_template_id = fields.Many2one(
        'sms.template',
        string="SMS Confirmation Template",
        config_parameter='stock.stock_sms_confirmation_template_id',
        help="SMS template for stock move confirmations"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()

        res.update(
            technical_service_default_sla_warning_hours=int(params.get_param('technical_service.default_sla_warning_hours', 2)),
            technical_service_auto_assign_work_order=params.get_param('technical_service.auto_assign_work_order', False),
            technical_service_default_work_duration=float(params.get_param('technical_service.default_work_duration', 2.0)),
            technical_service_auto_create_work_order=params.get_param('technical_service.auto_create_work_order', False),
            technical_service_track_asset_history=params.get_param('technical_service.track_asset_history', True),
            technical_service_preventive_maintenance_days=int(params.get_param('technical_service.preventive_maintenance_days', 30)),
            technical_service_team_assignment_method=params.get_param('technical_service.team_assignment_method', 'manual'),
            technical_service_notify_customer=params.get_param('technical_service.notify_customer', True),
            technical_service_notify_technician=params.get_param('technical_service.notify_technician', True),
            technical_service_include_internal_notes=params.get_param('technical_service.include_internal_notes', False),
            stock_move_sms_validation=params.get_param('stock.move_sms_validation', False),
            stock_sms_confirmation_template_id=int(params.get_param('stock.stock_sms_confirmation_template_id', 0)) or False,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()

        params.set_param('technical_service.default_sla_warning_hours', self.technical_service_default_sla_warning_hours)
        params.set_param('technical_service.auto_assign_work_order', self.technical_service_auto_assign_work_order)
        params.set_param('technical_service.default_work_duration', self.technical_service_default_work_duration)
        params.set_param('technical_service.auto_create_work_order', self.technical_service_auto_create_work_order)
        params.set_param('technical_service.track_asset_history', self.technical_service_track_asset_history)
        params.set_param('technical_service.preventive_maintenance_days', self.technical_service_preventive_maintenance_days)
        params.set_param('technical_service.team_assignment_method', self.technical_service_team_assignment_method)
        params.set_param('technical_service.notify_customer', self.technical_service_notify_customer)
        params.set_param('technical_service.notify_technician', self.technical_service_notify_technician)
        params.set_param('technical_service.include_internal_notes', self.technical_service_include_internal_notes)
        params.set_param('stock.move_sms_validation', self.stock_move_sms_validation)
        params.set_param('stock.stock_sms_confirmation_template_id', self.stock_sms_confirmation_template_id.id if self.stock_sms_confirmation_template_id else False)