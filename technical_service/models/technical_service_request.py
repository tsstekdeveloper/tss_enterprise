# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class TechnicalServiceRequest(models.Model):
    """
    Main Service Request Model
    Inherited from: maintenance.request (/opt/odoo/odoo18/addons/maintenance/models/maintenance.py)
    Purpose: Extend maintenance request for comprehensive technical service management

    Added Fields:
        - Request categorization (IT vs Technical)
        - Priority matrix (impact × urgency)
        - Location hierarchy
        - SLA tracking fields
        - Multiple work orders support
    """
    _inherit = 'maintenance.request'
    _description = 'Technical Service Request'

    # Request Type and Categorization
    x_request_type = fields.Selection([
        ('incident', 'Incident'),
        ('service_request', 'Service Request'),
        ('preventive', 'Preventive Maintenance'),
        ('installation', 'Installation/Setup'),
    ], string='Request Type', default='incident', required=True, tracking=True)

    x_service_category = fields.Selection([
        ('it', 'IT/Bilgi İşlem'),
        ('technical', 'Technical Service/Teknik Servis'),
        ('facility', 'Facility/Tesis'),
    ], string='Service Category', default='technical', required=True, tracking=True)

    # IT-specific categories
    x_it_category = fields.Selection([
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('network', 'Network'),
        ('user_support', 'User Support'),
        ('server', 'Server/Infrastructure'),
        ('security', 'Security'),
    ], string='IT Category')

    # Technical Service categories
    x_technical_category = fields.Selection([
        ('electrical', 'Electrical'),
        ('mechanical', 'Mechanical'),
        ('hvac', 'HVAC'),
        ('plumbing', 'Plumbing'),
        ('equipment', 'Equipment/Device'),
        ('furniture', 'Furniture/Fixture'),
    ], string='Technical Category')

    # Priority Matrix Fields
    x_impact = fields.Selection([
        ('low', 'Low - Single User'),
        ('medium', 'Medium - Department'),
        ('high', 'High - Floor/Building'),
        ('critical', 'Critical - Entire System'),
    ], string='Impact', default='low', required=True)

    x_urgency = fields.Selection([
        ('low', 'Low - Can Wait'),
        ('medium', 'Medium - Normal'),
        ('high', 'High - Urgent'),
        ('critical', 'Critical - Immediate'),
    ], string='Urgency', default='medium', required=True)

    x_priority_level = fields.Selection([
        ('p4', 'P4 - Low'),
        ('p3', 'P3 - Medium'),
        ('p2', 'P2 - High'),
        ('p1', 'P1 - Critical'),
    ], string='Priority Level', compute='_compute_priority_level', store=True)

    # Location Hierarchy
    x_campus_id = fields.Many2one('technical_service.campus', string='Campus')
    x_building_id = fields.Many2one('technical_service.building', string='Building')
    x_floor = fields.Char(string='Floor')
    x_room = fields.Char(string='Room/Location')
    x_location_details = fields.Text(string='Location Details')

    # SLA Management
    x_sla_policy_id = fields.Many2one('technical_service.sla', string='SLA Policy')
    x_response_deadline = fields.Datetime(string='Response Deadline', compute='_compute_sla_deadlines', store=True)
    x_resolution_deadline = fields.Datetime(string='Resolution Deadline', compute='_compute_sla_deadlines', store=True)
    x_response_time = fields.Float(string='Response Time (Hours)', compute='_compute_response_time', store=True)
    x_resolution_time = fields.Float(string='Resolution Time (Hours)', compute='_compute_resolution_time', store=True)
    x_sla_status = fields.Selection([
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('breached', 'Breached'),
    ], string='SLA Status', compute='_compute_sla_status', store=True)

    # Request Number (auto-generated)
    x_request_number = fields.Char(string='Request Number', readonly=True, copy=False, default='New')

    # Technician assignment field (for compatibility with maintenance module)
    technician_user_id = fields.Many2one('res.users', string='Technician', tracking=True)

    # Extended Status Management
    x_status_detail = fields.Selection([
        ('waiting_parts', 'Waiting for Parts'),
        ('waiting_vendor', 'Waiting for Vendor'),
        ('waiting_user', 'Waiting for User'),
        ('waiting_approval', 'Waiting for Approval'),
    ], string='Status Detail')

    # Work Orders
    x_work_order_ids = fields.One2many('technical_service.work_order', 'x_request_id', string='Work Orders')
    x_work_order_count = fields.Integer(string='Work Order Count', compute='_compute_work_order_count')

    # Additional tracking fields
    x_assigned_date = fields.Datetime(string='Assigned Date', readonly=True)
    x_detailed_location = fields.Text(string='Detailed Location')
    x_downtime = fields.Float(string='Downtime (Hours)', default=0.0)

    # Category fields
    x_category = fields.Selection([
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('network', 'Network'),
        ('electrical', 'Electrical'),
        ('mechanical', 'Mechanical'),
        ('hvac', 'HVAC'),
        ('other', 'Other'),
    ], string='Category')

    x_subcategory = fields.Char(string='Subcategory')

    # SLA deadline field (alias for resolution deadline)
    x_sla_deadline = fields.Datetime(string='SLA Deadline', related='x_resolution_deadline', readonly=True)

    # Resolution Details
    x_resolution_description = fields.Html(string='Resolution Description')
    x_root_cause = fields.Text(string='Root Cause')
    x_resolution_code = fields.Char(string='Resolution Code')

    # User Satisfaction & Feedback
    x_user_satisfaction = fields.Selection([
        ('1', 'Very Dissatisfied'),
        ('2', 'Dissatisfied'),
        ('3', 'Neutral'),
        ('4', 'Satisfied'),
        ('5', 'Very Satisfied'),
    ], string='User Satisfaction')
    x_user_feedback = fields.Text(string='User Feedback')

    # Customer Feedback fields
    x_feedback_score = fields.Integer(string='Feedback Score')
    x_feedback_date = fields.Datetime(string='Feedback Date')
    x_feedback_comment = fields.Text(string='Feedback Comment')

    # Escalation
    x_escalation_level = fields.Integer(string='Escalation Level', default=0)
    x_escalated_to = fields.Many2one('res.users', string='Escalated To')
    x_escalation_date = fields.Datetime(string='Escalation Date')

    @api.depends('x_impact', 'x_urgency')
    def _compute_priority_level(self):
        """
        Compute priority based on impact × urgency matrix
        Reference: customer_req.md section 7 - Priority Matrix
        """
        priority_matrix = {
            ('low', 'low'): 'p4',
            ('low', 'medium'): 'p3',
            ('low', 'high'): 'p2',
            ('low', 'critical'): 'p2',
            ('medium', 'low'): 'p3',
            ('medium', 'medium'): 'p2',
            ('medium', 'high'): 'p1',
            ('medium', 'critical'): 'p1',
            ('high', 'low'): 'p2',
            ('high', 'medium'): 'p1',
            ('high', 'high'): 'p1',
            ('high', 'critical'): 'p1',
            ('critical', 'low'): 'p1',
            ('critical', 'medium'): 'p1',
            ('critical', 'high'): 'p1',
            ('critical', 'critical'): 'p1',
        }

        for record in self:
            if record.x_impact and record.x_urgency:
                record.x_priority_level = priority_matrix.get(
                    (record.x_impact, record.x_urgency), 'p3'
                )
            else:
                record.x_priority_level = 'p3'

    @api.depends('x_priority_level', 'x_sla_policy_id', 'create_date')
    def _compute_sla_deadlines(self):
        """Calculate SLA response and resolution deadlines"""
        for record in self:
            if record.create_date and record.x_sla_policy_id:
                # Get SLA times based on priority
                sla_line = record.x_sla_policy_id.x_line_ids.filtered(
                    lambda l: l.x_priority == record.x_priority_level
                )
                if sla_line:
                    # Calculate deadlines from creation date
                    create_dt = fields.Datetime.to_datetime(record.create_date)
                    record.x_response_deadline = create_dt + timedelta(hours=sla_line[0].x_response_time)
                    record.x_resolution_deadline = create_dt + timedelta(hours=sla_line[0].x_resolution_time)
                else:
                    record.x_response_deadline = False
                    record.x_resolution_deadline = False
            else:
                record.x_response_deadline = False
                record.x_resolution_deadline = False

    @api.depends('x_work_order_ids')
    def _compute_work_order_count(self):
        for record in self:
            record.x_work_order_count = len(record.x_work_order_ids)

    @api.depends('create_date', 'stage_id')
    def _compute_response_time(self):
        """Calculate actual response time"""
        for record in self:
            if record.create_date and record.stage_id and record.stage_id.done:
                delta = fields.Datetime.now() - record.create_date
                record.x_response_time = delta.total_seconds() / 3600.0
            else:
                record.x_response_time = 0.0

    @api.depends('create_date', 'close_date')
    def _compute_resolution_time(self):
        """Calculate actual resolution time"""
        for record in self:
            if record.create_date and record.close_date:
                # Convert both to datetime if needed
                create_dt = fields.Datetime.to_datetime(record.create_date)

                # Handle close_date as Date field (it's a Date field in maintenance.request)
                if isinstance(record.close_date, datetime):
                    close_dt = record.close_date
                else:
                    # Convert date to datetime at end of day
                    from datetime import time
                    close_dt = datetime.combine(record.close_date, time(23, 59, 59))

                delta = close_dt - create_dt
                record.x_resolution_time = delta.total_seconds() / 3600.0
            else:
                record.x_resolution_time = 0.0

    @api.depends('x_response_deadline', 'x_resolution_deadline', 'stage_id')
    def _compute_sla_status(self):
        """Compute current SLA status"""
        now = fields.Datetime.now()
        for record in self:
            if not record.stage_id or record.stage_id.done:
                record.x_sla_status = 'on_track'
            elif record.x_resolution_deadline:
                if now > record.x_resolution_deadline:
                    record.x_sla_status = 'breached'
                elif now > (record.x_resolution_deadline - timedelta(hours=1)):
                    record.x_sla_status = 'at_risk'
                else:
                    record.x_sla_status = 'on_track'
            else:
                record.x_sla_status = 'on_track'

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate request number"""
        for vals in vals_list:
            if vals.get('x_request_number', 'New') == 'New':
                vals['x_request_number'] = self.env['ir.sequence'].next_by_code('technical.service.request') or 'REQ-001'
        return super().create(vals_list)

    @api.onchange('x_service_category')
    def _onchange_service_category(self):
        """Clear subcategory when main category changes"""
        if self.x_service_category == 'it':
            self.x_technical_category = False
        elif self.x_service_category == 'technical':
            self.x_it_category = False

    def write(self, vals):
        """Override write to track assignment date"""
        if 'technician_user_id' in vals and vals['technician_user_id']:
            vals['x_assigned_date'] = fields.Datetime.now()
        return super().write(vals)

    def action_create_work_order(self):
        """Create work order from request"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Work Order'),
            'res_model': 'technical_service.work_order',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_x_request_id': self.id,
                'default_name': f"WO - {self.name}",
                'default_x_technician_id': self.technician_user_id.id,
            }
        }

    def action_assign_technician(self):
        """Open wizard to assign technician"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assign Technician'),
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit'},
        }

    def action_start_work(self):
        """Start working on the request"""
        self.ensure_one()
        # Find in-progress stage
        in_progress_stage = self.env['maintenance.stage'].search([('name', 'ilike', 'progress')], limit=1)
        if not in_progress_stage:
            in_progress_stage = self.env['maintenance.stage'].search([], limit=1, offset=1)
        if in_progress_stage:
            self.stage_id = in_progress_stage
        return True

    def action_resolve(self):
        """Mark request as resolved"""
        self.ensure_one()
        # Find done stage
        done_stage = self.env['maintenance.stage'].search([('done', '=', True)], limit=1)
        if done_stage:
            self.stage_id = done_stage
            self.close_date = fields.Date.today()
        return True

    def action_escalate(self):
        """Escalate request to next level"""
        self.ensure_one()
        self.x_escalation_level += 1
        self.x_escalation_date = fields.Datetime.now()

        # Send notification to manager
        if self.maintenance_team_id and self.maintenance_team_id.manager_id:
            self.x_escalated_to = self.maintenance_team_id.manager_id
            self.message_post(
                body=_(f"Request escalated to level {self.x_escalation_level}"),
                partner_ids=[self.maintenance_team_id.manager_id.partner_id.id]
            )
