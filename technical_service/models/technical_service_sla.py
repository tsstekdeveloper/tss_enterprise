# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TechnicalServiceSLA(models.Model):
    """
    SLA (Service Level Agreement) Policy Management
    Purpose: Define response and resolution time targets based on priority

    Reference: customer_req.md section 8 - SLA Targets
    """
    _name = 'technical_service.sla'
    _description = 'SLA Policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='SLA Policy Name', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Applicability
    x_apply_to = fields.Selection([
        ('all', 'All Requests'),
        ('category', 'By Category'),
        ('location', 'By Location'),
        ('customer', 'By Customer'),
    ], string='Apply To', default='all')

    x_service_category_ids = fields.Many2many(
        'maintenance.equipment.category',
        string='Equipment Categories'
    )
    x_campus_ids = fields.Many2many(
        'technical_service.campus',
        string='Campuses'
    )
    x_partner_ids = fields.Many2many(
        'res.partner',
        string='Customers'
    )

    # Business Hours
    x_business_hours_start = fields.Float(string='Business Hours Start', default=8.0)
    x_business_hours_end = fields.Float(string='Business Hours End', default=18.0)
    x_include_weekends = fields.Boolean(string='Include Weekends', default=False)
    x_timezone = fields.Selection([
        ('UTC', 'UTC'),
        ('Europe/Istanbul', 'Istanbul'),
        ('America/New_York', 'New York'),
    ], string='Timezone', default='Europe/Istanbul')

    # SLA Lines by Priority
    x_line_ids = fields.One2many(
        'technical_service.sla.line',
        'sla_id',
        string='SLA Lines'
    )

    # Escalation Rules
    x_enable_escalation = fields.Boolean(string='Enable Escalation', default=True)
    x_escalation_rules_ids = fields.One2many(
        'technical_service.sla.escalation',
        'sla_id',
        string='Escalation Rules'
    )

    @api.model
    def get_applicable_sla(self, request):
        """Find applicable SLA policy for a request"""
        domain = [('active', '=', True)]

        # Search for matching SLA policies
        sla_policies = self.search(domain)

        for sla in sla_policies:
            if sla.x_apply_to == 'all':
                return sla
            elif sla.x_apply_to == 'category' and request.category_id in sla.x_service_category_ids:
                return sla
            elif sla.x_apply_to == 'location' and request.x_campus_id in sla.x_campus_ids:
                return sla
            elif sla.x_apply_to == 'customer' and request.partner_id in sla.x_partner_ids:
                return sla

        # Return default SLA if exists
        default_sla = self.search([('x_apply_to', '=', 'all')], limit=1)
        return default_sla


class TechnicalServiceSLALine(models.Model):
    """SLA time targets by priority"""
    _name = 'technical_service.sla.line'
    _description = 'SLA Line'
    _order = 'x_priority'

    sla_id = fields.Many2one('technical_service.sla', string='SLA Policy', required=True, ondelete='cascade')

    x_priority = fields.Selection([
        ('p1', 'P1 - Critical'),
        ('p2', 'P2 - High'),
        ('p3', 'P3 - Medium'),
        ('p4', 'P4 - Low'),
    ], string='Priority', required=True)

    x_response_time = fields.Float(string='Response Time (Hours)', required=True)
    x_resolution_time = fields.Float(string='Resolution Time (Hours)', required=True)

    x_after_hours_response = fields.Float(string='After Hours Response (Hours)')
    x_after_hours_resolution = fields.Float(string='After Hours Resolution (Hours)')

    _sql_constraints = [
        ('unique_priority_per_sla', 'UNIQUE(sla_id, x_priority)', 'Priority must be unique per SLA policy!'),
    ]

    @api.constrains('x_response_time', 'x_resolution_time')
    def _check_times(self):
        for record in self:
            if record.x_response_time <= 0 or record.x_resolution_time <= 0:
                raise ValidationError(_('Response and resolution times must be positive!'))
            if record.x_response_time > record.x_resolution_time:
                raise ValidationError(_('Response time cannot be greater than resolution time!'))


class TechnicalServiceSLAEscalation(models.Model):
    """SLA escalation rules"""
    _name = 'technical_service.sla.escalation'
    _description = 'SLA Escalation Rule'
    _order = 'x_level'

    sla_id = fields.Many2one('technical_service.sla', string='SLA Policy', required=True, ondelete='cascade')

    x_level = fields.Integer(string='Escalation Level', required=True)
    x_trigger_after = fields.Float(string='Trigger After (% of SLA)', required=True, help="Percentage of SLA time elapsed")
    x_notify_users = fields.Many2many('res.users', string='Notify Users')
    x_notify_groups = fields.Many2many('res.groups', string='Notify Groups')
    x_email_template_id = fields.Many2one('mail.template', string='Email Template')
    x_auto_reassign = fields.Boolean(string='Auto Reassign', default=False)
    x_reassign_to = fields.Many2one('res.users', string='Reassign To')

    _sql_constraints = [
        ('unique_level_per_sla', 'UNIQUE(sla_id, x_level)', 'Escalation level must be unique per SLA policy!'),
    ]

    @api.constrains('x_trigger_after')
    def _check_trigger(self):
        for record in self:
            if not 0 < record.x_trigger_after <= 100:
                raise ValidationError(_('Trigger percentage must be between 0 and 100!'))

    def execute_escalation(self, request):
        """Execute escalation actions for a request"""
        # Send notifications
        if self.x_notify_users:
            request.message_post(
                body=_(f"SLA Escalation Level {self.x_level}: Request {request.name} needs attention"),
                partner_ids=self.x_notify_users.mapped('partner_id').ids
            )

        # Auto reassign if configured
        if self.x_auto_reassign and self.x_reassign_to:
            request.technician_user_id = self.x_reassign_to

        # Mark escalation in request
        request.x_escalation_level = self.x_level
        request.x_escalation_date = fields.Datetime.now()
        request.x_escalated_to = self.x_reassign_to