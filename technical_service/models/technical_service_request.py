# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning
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
    ], string='Urgency', default='low', required=True)

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

    # Material Request Fields
    x_requires_material = fields.Boolean(string='Requires Material', default=False)
    x_material_list = fields.Text(string='Required Materials')

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

    # Computed field to check if user can assign technician
    x_can_assign_technician = fields.Boolean(
        string='Can Assign Technician',
        compute='_compute_can_assign_technician',
        compute_sudo=False,
        default=lambda self: self._default_can_assign_technician()
    )

    # Override parent's maintenance_team_id to use our custom default
    maintenance_team_id = fields.Many2one(
        'maintenance.team',
        string='Team',
        required=True,
        default=lambda self: self._get_default_team_custom(),
        tracking=True
    )

    # Created By User (custom field - independent from parent model)
    x_owner_user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.uid,
        readonly=True,
        tracking=True
    )

    # Department field for organizational structure
    x_department_id = fields.Many2one('hr.department', string='Department',
                                     compute='_compute_department', store=True)

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

    # Validation warning fields removed - now handled by wizard

    # User Satisfaction & Feedback
    x_user_satisfaction = fields.Selection([
        ('1', 'Very Dissatisfied'),
        ('2', 'Dissatisfied'),
        ('3', 'Neutral'),
        ('4', 'Satisfied'),
        ('5', 'Very Satisfied'),
    ], string='User Satisfaction')
    x_user_feedback = fields.Text(string='User Feedback')

    # Customer Feedback fields (using priority widget - values must be '1' to '5')
    x_feedback_score = fields.Selection([
        ('1', 'Very Dissatisfied'),
        ('2', 'Dissatisfied'),
        ('3', 'Neutral'),
        ('4', 'Satisfied'),
        ('5', 'Very Satisfied'),
    ], string='Feedback Score', help='Customer satisfaction rating (1-5 stars)')
    x_feedback_date = fields.Datetime(string='Feedback Date')
    x_feedback_comment = fields.Text(string='Feedback Comment')

    # Escalation
    x_escalation_level = fields.Integer(string='Escalation Level', default=0)
    x_escalated_to = fields.Many2one('res.users', string='Escalated To')
    x_escalation_date = fields.Datetime(string='Escalation Date')

    # _compute_validation_warning removed - now handled by wizard

    def _default_can_assign_technician(self):
        """Default value for can assign technician permission"""
        user = self.env.user
        return user._is_superuser() or \
               user.has_group('technical_service_presentation.group_technical_cto') or \
               user.has_group('technical_service_presentation.group_technical_department_manager') or \
               user.has_group('technical_service_presentation.group_technical_team_leader')

    @api.depends_context('uid')
    def _compute_can_assign_technician(self):
        """Check if current user can assign technician"""
        for record in self:
            user = self.env.user
            # Allow superusers (admin) and specific roles
            record.x_can_assign_technician = user._is_superuser() or \
                                              user.has_group('technical_service_presentation.group_technical_cto') or \
                                              user.has_group('technical_service_presentation.group_technical_department_manager') or \
                                              user.has_group('technical_service_presentation.group_technical_team_leader')

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

    def _get_default_team_custom(self):
        """Get default team based on x_is_default_assignment field"""
        default_team = self.env['maintenance.team'].search([
            ('x_is_default_assignment', '=', True)
        ], limit=1)
        if default_team:
            return default_team.id
        # Fallback to standard Odoo behavior if no default team is set
        team = self.env['maintenance.team'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        if not team:
            team = self.env['maintenance.team'].search([], limit=1)
        return team.id if team else False

    @api.model
    def default_get(self, fields_list):
        """Override default_get to set default values when form is opened"""
        defaults = super().default_get(fields_list)

        # Auto-set employee_id to logged-in user's employee
        if 'employee_id' in fields_list and not defaults.get('employee_id'):
            employee = self.env['hr.employee'].search([
                ('user_id', '=', self.env.uid)
            ], limit=1)
            if employee:
                defaults['employee_id'] = employee.id


        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate request number and set default values"""
        for vals in vals_list:
            # Generate request number
            if vals.get('x_request_number', 'New') == 'New':
                vals['x_request_number'] = self.env['ir.sequence'].next_by_code('technical.service.request') or 'REQ-001'

            # Auto-set employee_id to logged-in user's employee if not specified
            if not vals.get('employee_id'):
                employee = self.env['hr.employee'].search([
                    ('user_id', '=', self.env.uid)
                ], limit=1)
                if employee:
                    vals['employee_id'] = employee.id

            # Auto-set maintenance_team_id to default team if not specified
            if not vals.get('maintenance_team_id'):
                default_team = self.env['maintenance.team'].search([
                    ('x_is_default_assignment', '=', True)
                ], limit=1)
                if default_team:
                    vals['maintenance_team_id'] = default_team.id

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

    # Warning system - only informative, doesn't block save

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

    @api.depends('create_uid', 'employee_id')
    def _compute_department(self):
        """Compute department from request creator or assigned employee"""
        for record in self:
            if record.employee_id and record.employee_id.department_id:
                record.x_department_id = record.employee_id.department_id
            elif record.create_uid and record.create_uid.employee_id:
                record.x_department_id = record.create_uid.employee_id.department_id
            else:
                record.x_department_id = False

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override search_read to filter by department when context flag is set"""
        if self.env.context.get('search_default_department'):
            current_employee = self.env.user.employee_id
            if current_employee:
                dept_employee_ids = []

                # 1. Current user's employee
                dept_employee_ids.append(current_employee.id)

                # 2. Subordinates
                subordinates = self.env['hr.employee'].search([
                    ('parent_id', '=', current_employee.id)
                ])
                dept_employee_ids.extend(subordinates.ids)

                # 3. Department colleagues
                if current_employee.department_id:
                    dept_colleagues = self.env['hr.employee'].search([
                        ('department_id', '=', current_employee.department_id.id)
                    ])
                    dept_employee_ids.extend(dept_colleagues.ids)

                # Add to domain
                dept_employee_ids = list(set(dept_employee_ids))
                dept_domain = [('employee_id', 'in', dept_employee_ids)]

                if domain:
                    domain = ['&'] + dept_domain + domain
                else:
                    domain = dept_domain

        return super(TechnicalServiceRequest, self).search_read(domain, fields, offset, limit, order)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Override search to filter by department when context flag is set"""
        if self.env.context.get('search_default_department'):
            current_employee = self.env.user.employee_id
            if current_employee:
                dept_employee_ids = []

                # 1. Current user's employee
                dept_employee_ids.append(current_employee.id)

                # 2. Subordinates
                subordinates = self.env['hr.employee'].search([
                    ('parent_id', '=', current_employee.id)
                ])
                dept_employee_ids.extend(subordinates.ids)

                # 3. Department colleagues
                if current_employee.department_id:
                    dept_colleagues = self.env['hr.employee'].search([
                        ('department_id', '=', current_employee.department_id.id)
                    ])
                    dept_employee_ids.extend(dept_colleagues.ids)

                # Add to domain
                dept_employee_ids = list(set(dept_employee_ids))
                dept_domain = [('employee_id', 'in', dept_employee_ids)]

                if args:
                    args = ['&'] + dept_domain + list(args)
                else:
                    args = dept_domain

        if count:
            return super(TechnicalServiceRequest, self).search_count(args)
        return super(TechnicalServiceRequest, self).search(args, offset=offset, limit=limit, order=order)
