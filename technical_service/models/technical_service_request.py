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

    # TASK 07 - PHASE 6: Effective Team for Default Routing
    # Date: 18 October 2025
    x_effective_team_id = fields.Many2one(
        'maintenance.team',
        compute='_compute_effective_team',
        store=True,
        string='Efektif Takım',
        help='Yeni stage\'de ise default assignment team, değilse atanan team'
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

    # History Tracking (Task 07)
    x_history_ids = fields.One2many(
        'technical_service.request.history',
        'request_id',
        string='History',
        help='Complete audit trail of all events and changes'
    )

    # Cancel Approval Tracking (Task 07 - Phase 4B)
    x_pending_cancel = fields.Boolean(
        string='Pending Cancellation',
        default=False,
        help='True if request is in Onayda stage waiting for cancel approval'
    )
    x_cancel_reason = fields.Text(
        string='Cancellation Reason',
        help='Reason provided when cancellation was requested'
    )
    x_previous_stage_id = fields.Many2one(
        'maintenance.stage',
        string='Previous Stage',
        help='Stage to return to if cancel request is rejected'
    )

    # ============================================
    # PERMISSION COMPUTED FIELDS (Task 07 - Phase 1D)
    # ============================================

    x_can_put_on_hold = fields.Boolean(
        string='Can Put On Hold',
        compute='_compute_workflow_permissions',
        compute_sudo=False,
        help='Current user can put this request on hold'
    )

    x_can_send_for_approval = fields.Boolean(
        string='Can Send For Approval',
        compute='_compute_workflow_permissions',
        compute_sudo=False,
        help='Current user can send this request for approval'
    )

    x_can_approve = fields.Boolean(
        string='Can Approve',
        compute='_compute_workflow_permissions',
        compute_sudo=False,
        help='Current user can approve this request'
    )

    x_can_reject = fields.Boolean(
        string='Can Reject',
        compute='_compute_workflow_permissions',
        compute_sudo=False,
        help='Current user can reject this request'
    )

    x_can_cancel = fields.Boolean(
        string='Can Cancel',
        compute='_compute_workflow_permissions',
        compute_sudo=False,
        help='Current user can cancel this request'
    )

    x_can_create_work_order = fields.Boolean(
        string='Can Create Work Order',
        compute='_compute_workflow_permissions',
        compute_sudo=False,
        help='Current user can create work orders'
    )

    # Standard User Check - For limiting field editability
    # Based on stage and user role/ownership
    x_is_standard_user = fields.Boolean(
        string='Is Standard User',
        compute='_compute_is_standard_user',
        compute_sudo=False,
        store=False,  # Don't store - always compute fresh based on current user
        help='True if current user cannot edit this request based on stage and permissions'
    )

    # Work Orders editability - For Team Leaders, Senior Technicians, Technicians
    x_can_edit_work_orders = fields.Boolean(
        string='Can Edit Work Orders',
        compute='_compute_can_edit_work_orders',
        compute_sudo=False,
        store=False,
        help='True if current user can edit Work Orders and Resolution tabs'
    )

    # Final Stage Check - For preventing all edits in final stages
    x_is_final_stage = fields.Boolean(
        string='Is Final Stage',
        compute='_compute_is_final_stage',
        compute_sudo=False,
        store=False,
        help='True if request is in Onayda, Tamamlandı, Reddedildi, or İptal Edildi stage'
    )

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

    @api.depends('stage_id', 'maintenance_team_id')
    def _compute_effective_team(self):
        """
        TASK 07 - PHASE 6: Compute effective team for default routing
        If stage is 'Yeni', use default assignment team; otherwise use assigned team
        """
        for record in self:
            if record.stage_id and record.stage_id.name == 'Yeni':
                # Find default assignment team
                default_team = self.env['maintenance.team'].search([
                    ('x_is_default_assignment_team', '=', True)
                ], limit=1)
                record.x_effective_team_id = default_team.id if default_team else record.maintenance_team_id.id
            else:
                # Use assigned team for other stages
                record.x_effective_team_id = record.maintenance_team_id.id

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
        """Get default team based on x_is_default_assignment_team field"""
        default_team = self.env['maintenance.team'].search([
            ('x_is_default_assignment_team', '=', True)
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

    # ============================================
    # HELPER METHODS FOR STAGE MANAGEMENT (Task 07 - Phase 2)
    # ============================================

    def _get_stage_by_name(self, stage_name):
        """
        Get stage by name (helper for automatic transitions)
        Returns: maintenance.stage record or False
        """
        return self.env['maintenance.stage'].search([('name', '=', stage_name)], limit=1)

    def _transition_to_stage(self, new_stage_name, reason=None, is_auto=True):
        """
        Transition request to new stage and log history
        Args:
            new_stage_name: Name of target stage (e.g., 'Yeni', 'Ekip Atandı')
            reason: Optional reason for transition
            is_auto: Whether this is automatic (True) or manual (False)
        """
        self.ensure_one()
        new_stage = self._get_stage_by_name(new_stage_name)
        if not new_stage:
            return False

        old_stage = self.stage_id

        # Update stage with context flag to skip duplicate history logging
        self.with_context(skip_stage_history=True).write({'stage_id': new_stage.id})

        # Log history
        self.env['technical_service.request.history'].log_stage_change(
            request=self,
            old_stage=old_stage,
            new_stage=new_stage,
            reason=reason,
            is_auto=is_auto
        )

        return True

    # ============================================
    # CREATE/WRITE HOOKS (Task 07 - Phase 2)
    # ============================================

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to:
        1. Generate request number
        2. Set default values
        3. Auto-transition to 'Yeni' stage (Task 07 - Phase 2A)
        4. Log creation in history
        """
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

            # Task 07 - Phase 2A: Force initial stage to 'Yeni' if not specified
            if not vals.get('stage_id'):
                stage_new = self.env['maintenance.stage'].search([('name', '=', 'Yeni')], limit=1)
                if stage_new:
                    vals['stage_id'] = stage_new.id

        # Create records
        records = super().create(vals_list)

        # Task 07 - Phase 2A: Log creation in history for each record
        for record in records:
            self.env['technical_service.request.history'].create({
                'request_id': record.id,
                'event_type': 'stage_change',
                'new_stage_id': record.stage_id.id,
                'note': _('Request created'),
                'is_automatic': True,
            })

            # Task 07 - Business Logic Fix: Do NOT auto-transition on create()
            # Team assignment during creation should NOT trigger stage change
            # Only Dispatcher can move request from 'Yeni' to 'Ekip Atandı'
            # (This logic remains in write() for when team is changed AFTER creation)

        return records

    @api.onchange('x_service_category')
    def _onchange_service_category(self):
        """Clear subcategory when main category changes"""
        if self.x_service_category == 'it':
            self.x_technical_category = False
        elif self.x_service_category == 'technical':
            self.x_it_category = False

    def write(self, vals):
        """
        Override write to:
        1. Track assignment date
        2. Auto-transition stages based on field changes (Task 07 - Phase 2B)
        3. Log changes in history
        """
        result = True

        for record in self:
            # Store old values for history tracking
            old_team = record.maintenance_team_id
            old_technician = record.technician_user_id
            old_stage = record.stage_id

            # Perform the write
            result = super(TechnicalServiceRequest, record).write(vals) and result

            # Task 07 - Phase 2B: Automatic stage transitions after write

            # 1. Team Assignment → 'Ekip Atandı'
            new_team = record.maintenance_team_id
            if new_team and new_team != old_team and record.stage_id.name == 'Yeni':
                # Set assigned date when transitioning to 'Ekip Atandı'
                record.write({'x_assigned_date': fields.Datetime.now()})
                record._transition_to_stage('Ekip Atandı', reason=_('Team assigned'))

                # Log assignment change
                self.env['technical_service.request.history'].log_assignment(
                    request=record,
                    old_team=old_team,
                    new_team=new_team,
                    old_tech=old_technician,
                    new_tech=record.technician_user_id,
                    note=_('Team assignment changed')
                )

            # 2. Technician Assignment (log only, no stage change)
            new_technician = record.technician_user_id
            if new_technician != old_technician:
                self.env['technical_service.request.history'].log_assignment(
                    request=record,
                    old_team=old_team if old_team != new_team else False,
                    new_team=new_team if old_team != new_team else False,
                    old_tech=old_technician,
                    new_tech=new_technician,
                    note=_('Technician assignment changed')
                )

            # 3. Manual stage change (log if stage changed manually)
            if 'stage_id' in vals and record.stage_id != old_stage:
                # Check if this is a manual change (not from _transition_to_stage)
                # If it's manual, it won't have been logged yet
                if not self.env.context.get('skip_stage_history'):
                    self.env['technical_service.request.history'].log_stage_change(
                        request=record,
                        old_stage=old_stage,
                        new_stage=record.stage_id,
                        reason=_('Manual stage change'),
                        is_auto=False
                    )

        return result

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

    # ============================================
    # MANUAL WORKFLOW ACTIONS (Task 07 - Phase 3)
    # ============================================

    def action_put_on_hold(self):
        """
        Open wizard to put request on hold
        Task 07 - Phase 3A
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Put Request On Hold'),
            'res_model': 'technical_service.request.put.on.hold.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }

    def action_send_for_approval(self):
        """
        Send request for approval (manual button)
        Task 07 - Phase 3B
        Transitions from 'Devam Ediyor' to 'Onayda'
        """
        self.ensure_one()

        # Check permission
        if not self.x_can_send_for_approval:
            raise UserError(_('You do not have permission to send this request for approval'))

        # Check if in correct stage
        if self.stage_id.name != 'Devam Ediyor':
            raise UserError(_('Request must be in "Devam Ediyor" stage to send for approval'))

        # Check if all work orders are completed
        if self.x_work_order_ids:
            incomplete_wos = self.x_work_order_ids.filtered(
                lambda wo: wo.x_work_status != 'completed'
            )
            if incomplete_wos:
                raise UserError(_('All work orders must be completed before sending for approval. '
                                 'Incomplete work orders: %s', ', '.join(incomplete_wos.mapped('name'))))

        # Transition to 'Onayda'
        self._transition_to_stage(
            'Onayda',
            reason=_('Sent for approval by %s', self.env.user.name),
            is_auto=False
        )

        # Notify department manager
        if self.x_department_id and self.x_department_id.manager_id:
            self.activity_schedule(
                activity_type_xmlid='mail.mail_activity_data_todo',
                summary=_('Approve Service Request'),
                note=_('Please review and approve/reject this service request.'),
                user_id=self.x_department_id.manager_id.user_id.id
            )

            self.message_post(
                body=_('Request sent for approval to %s', self.x_department_id.manager_id.name),
                message_type='notification',
                subtype_xmlid='mail.mt_note',
                partner_ids=[self.x_department_id.manager_id.user_id.partner_id.id]
            )

        return True

    def action_approve(self):
        """
        Approve request (manual button)
        Task 07 - Phase 3C & Phase 4B
        - If x_pending_cancel=True: Approve cancellation → 'İptal Edildi'
        - Otherwise: Approve completion → 'Tamamlandı'
        """
        self.ensure_one()

        # Check permission
        if not self.x_can_approve:
            raise UserError(_('You do not have permission to approve this request'))

        # Check if in correct stage
        if self.stage_id.name != 'Onayda':
            raise UserError(_('Request must be in "Pending Approval" stage to approve'))

        # Phase 4B: Check if this is a cancel approval or completion approval
        if self.x_pending_cancel:
            # CANCEL APPROVAL: Transition to 'İptal Edildi'
            self._transition_to_stage(
                'İptal Edildi',
                reason=self.x_cancel_reason or _('Cancelled (approved by %s)', self.env.user.name),
                is_auto=False
            )

            # Cancel all pending work orders
            pending_wos = self.x_work_order_ids.filtered(
                lambda wo: wo.x_work_status in ['pending', 'in_progress', 'paused']
            )
            for wo in pending_wos:
                wo.write({'x_work_status': 'cancelled'})

            # Log cancellation approval
            self.env['technical_service.request.history'].log_approval(
                request=self,
                status='cancelled',
                reason=self.x_cancel_reason
            )

            # Notify requester
            if self.create_uid:
                self.message_post(
                    body=_('✓ Your cancellation request has been approved by %s.<br/>Request cancelled.',
                           self.env.user.name),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                    partner_ids=[self.create_uid.partner_id.id]
                )

            # Clear cancel tracking fields
            self.write({
                'x_pending_cancel': False,
                'x_cancel_reason': False,
                'x_previous_stage_id': False,
            })

        else:
            # COMPLETION APPROVAL: Transition to 'Tamamlandı'
            self._transition_to_stage(
                'Tamamlandı',
                reason=_('Approved by %s', self.env.user.name),
                is_auto=False
            )

            # Log approval
            self.env['technical_service.request.history'].log_approval(
                request=self,
                status='approved',
                reason=None
            )

            # Notify requester
            if self.create_uid:
                self.message_post(
                    body=_('✓ Your service request has been approved and completed.'),
                    message_type='notification',
                    subtype_xmlid='mail.mt_note',
                    partner_ids=[self.create_uid.partner_id.id]
                )

        # Close any pending activities
        self.activity_ids.action_done()

        return True

    def action_reject(self):
        """
        Open wizard to reject request
        Task 07 - Phase 3D
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Request'),
            'res_model': 'technical_service.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }

    def action_cancel(self):
        """
        Open wizard to cancel request
        Task 07 - Phase 3E
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cancel Request'),
            'res_model': 'technical_service.request.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }

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

    @api.depends_context('uid')
    @api.depends('stage_id', 'create_uid', 'maintenance_team_id', 'technician_user_id')
    def _compute_workflow_permissions(self):
        """
        Compute workflow permissions for current user
        Task 07 - Phase 1D: Permission-based workflow buttons

        Roles:
        - CTO: Full access
        - Department Manager: Can approve/reject their department requests
        - Team Leader: Can create work orders, put on hold for their team
        - Dispatcher: Can assign and manage workflow
        - Technician: Can update work orders they're assigned to
        - Standard User: Can only cancel their own requests (if not started)
        """
        for record in self:
            user = self.env.user

            # Admin has all permissions
            if user._is_superuser():
                record.x_can_put_on_hold = True
                record.x_can_send_for_approval = True
                record.x_can_approve = True
                record.x_can_reject = True
                record.x_can_cancel = True
                record.x_can_create_work_order = True
                continue

            # Get user roles
            is_cto = user.has_group('technical_service_presentation.group_technical_cto')
            is_dept_manager = user.has_group('technical_service_presentation.group_technical_department_manager')
            is_team_leader = user.has_group('technical_service_presentation.group_technical_team_leader')
            is_dispatcher = user.has_group('technical_service_presentation.group_technical_dispatcher')
            is_senior_technician = user.has_group('technical_service_presentation.group_technical_senior_technician')
            is_technician = user.has_group('technical_service_presentation.group_technical_technician')
            is_owner = record.create_uid == user

            # Get user's team membership (for team leaders)
            user_team_ids = []
            if user.employee_id:
                team_members = self.env['technical_service.team.member'].search([
                    ('employee_id', '=', user.employee_id.id)
                ])
                user_team_ids = team_members.mapped('team_id').ids

            # Get stage info
            stage_name = record.stage_id.name if record.stage_id else ''
            is_new = stage_name == 'Yeni'
            is_team_assigned = stage_name == 'Ekip Atandı'
            is_on_hold = stage_name == 'Beklemede'
            is_wo_created = stage_name == 'İş Emri Oluşturuldu'
            is_in_progress = stage_name == 'Devam Ediyor'
            is_pending_approval = stage_name == 'Onayda'
            is_completed = stage_name == 'Tamamlandı'
            is_rejected = stage_name == 'Reddedildi'
            is_cancelled = stage_name == 'İptal Edildi'

            # Initialize all to False
            record.x_can_put_on_hold = False
            record.x_can_send_for_approval = False
            record.x_can_approve = False
            record.x_can_reject = False
            record.x_can_cancel = False
            record.x_can_create_work_order = False

            # Put On Hold - Team Leader, Senior Technician, Technician ONLY
            # Dispatcher alone does NOT have this permission
            # Can put on hold if not already completed/rejected/cancelled
            if not (is_completed or is_rejected or is_cancelled):
                # Team Leader can put on hold for their team
                if is_team_leader and record.maintenance_team_id.id in user_team_ids:
                    record.x_can_put_on_hold = True
                # Senior Technician can put on hold
                elif is_senior_technician:
                    record.x_can_put_on_hold = True
                # Technician can put on hold if assigned to them
                elif is_technician and record.technician_user_id == user:
                    record.x_can_put_on_hold = True

            # Send for Approval - Technician (assigned), Team Leader, Dispatcher
            # Can send for approval when in "Devam Ediyor" stage
            if is_in_progress:
                if is_cto or is_dept_manager or is_dispatcher:
                    record.x_can_send_for_approval = True
                elif is_team_leader and record.maintenance_team_id.id in user_team_ids:
                    record.x_can_send_for_approval = True
                elif is_technician and record.technician_user_id == user:
                    record.x_can_send_for_approval = True

            # Approve - Department Manager, CTO, OR Owner (for cancel approval)
            # Can approve when in "Onayda" stage
            # PHASE 4B: Owner can approve if x_pending_cancel=True (cancel approval)
            if is_pending_approval:
                if is_cto:
                    record.x_can_approve = True
                elif is_dept_manager:
                    # Check if this is their department
                    if record.x_department_id and user.employee_id and \
                       record.x_department_id == user.employee_id.department_id:
                        record.x_can_approve = True
                elif is_owner and record.x_pending_cancel:
                    # Owner can approve cancellation requests
                    record.x_can_approve = True

            # Reject - Department Manager, CTO, OR Owner (for cancel rejection)
            # Can reject when in "Onayda" stage
            # PHASE 4B: Owner can reject if x_pending_cancel=True (cancel rejection)
            if is_pending_approval:
                if is_cto:
                    record.x_can_reject = True
                elif is_dept_manager:
                    # Check if this is their department
                    if record.x_department_id and user.employee_id and \
                       record.x_department_id == user.employee_id.department_id:
                        record.x_can_reject = True
                elif is_owner and record.x_pending_cancel:
                    # Owner can reject cancellation requests
                    record.x_can_reject = True

            # Cancel - Different rules for owner vs other roles
            # Standard User (owner): Can ONLY cancel in "Yeni" stage (before team assignment)
            # Other roles (Team Leader, Dispatcher, Dept Manager, CTO): Can cancel in "Yeni" or "Ekip Atandı"
            if is_new or is_team_assigned:
                if is_cto or is_dept_manager or is_dispatcher:
                    record.x_can_cancel = True
                elif is_team_leader and record.maintenance_team_id.id in user_team_ids:
                    record.x_can_cancel = True
                elif is_owner and is_new:
                    # Owner can ONLY cancel in "Yeni" stage (not after team assigned)
                    record.x_can_cancel = True

            # Create Work Order - Team Leader, Dispatcher, Dept Manager, CTO
            # Can create work order when in "Ekip Atandı" or "Devam Ediyor" stages
            if is_team_assigned or is_in_progress or is_wo_created:
                if is_cto or is_dept_manager or is_dispatcher:
                    record.x_can_create_work_order = True
                elif is_team_leader and record.maintenance_team_id.id in user_team_ids:
                    record.x_can_create_work_order = True

    @api.depends_context('uid')
    @api.depends('stage_id', 'create_uid')
    def _compute_is_standard_user(self):
        """
        Compute if current user can edit this request based on stage and permissions.

        RULES:
        1. If stage is in FINAL STAGES (Onayda, Tamamlandı, Reddedildi, İptal Edildi):
           - NO ONE can edit (including CTO and Department Manager)
           - Returns True (readonly) for ALL users

        2. If stage = "Yeni" (New):
           - Creator can edit
           - CTO can edit
           - Department Manager can edit
           - Dispatcher can edit
           - All others are readonly

        3. If stage != "Yeni" (beyond New, but not final):
           - CTO can edit
           - Department Manager can edit
           - All others (including creator) are readonly

        Returns True (readonly) if user CANNOT edit, False if user CAN edit
        """
        for record in self:
            # FIRST CHECK: Final stage lockdown - NO ONE can edit
            if record.x_is_final_stage:
                record.x_is_standard_user = True
                continue

            user = self.env.user

            # Superuser always has access (except in final stages, already checked above)
            if user._is_superuser():
                record.x_is_standard_user = False
                continue

            # Check user roles
            is_cto = user.has_group('technical_service_presentation.group_technical_cto')
            is_dept_manager = user.has_group('technical_service_presentation.group_technical_department_manager')
            is_dispatcher = user.has_group('technical_service_presentation.group_technical_dispatcher')

            # CTO and Department Manager always have edit access (except final stages)
            if is_cto or is_dept_manager:
                record.x_is_standard_user = False
                continue

            # Get stage name
            stage_name = record.stage_id.name if record.stage_id else ''

            # If stage is "Yeni" (New)
            if stage_name == 'Yeni':
                # Creator can edit in "Yeni" stage
                is_creator = (record.create_uid.id == user.id if record.create_uid else False)

                # Dispatcher can edit in "Yeni" stage
                if is_creator or is_dispatcher:
                    record.x_is_standard_user = False
                else:
                    record.x_is_standard_user = True
            else:
                # Beyond "Yeni" stage: only CTO and Dept Manager can edit (already handled above)
                # Everyone else is readonly
                record.x_is_standard_user = True

    @api.depends('stage_id')
    def _compute_is_final_stage(self):
        """
        Check if request is in a final stage where NO ONE can edit.

        Final stages:
        - "Onayda" (Approval pending)
        - "Tamamlandı" (Completed)
        - "Reddedildi" (Rejected)
        - "İptal Edildi" (Cancelled)

        Returns True if in final stage, False otherwise
        """
        final_stage_names = ['Onayda', 'Tamamlandı', 'Reddedildi', 'İptal Edildi']

        for record in self:
            stage_name = record.stage_id.name if record.stage_id else ''
            record.x_is_final_stage = stage_name in final_stage_names

    @api.depends_context('uid')
    @api.depends('stage_id')
    def _compute_can_edit_work_orders(self):
        """
        Check if current user can edit Work Orders and Resolution tabs.

        RULES:
        1. User must be Team Leader, Senior Technician, or Technician
        2. Stage must NOT be in final stages (Onayda, Tamamlandı, Reddedildi, İptal Edildi)

        Returns True if user CAN edit Work Orders/Resolution, False otherwise
        """
        for record in self:
            user = self.env.user

            # Superuser always has access
            if user._is_superuser():
                record.x_can_edit_work_orders = not record.x_is_final_stage
                continue

            # Check if in final stage - NO ONE can edit
            if record.x_is_final_stage:
                record.x_can_edit_work_orders = False
                continue

            # Check user roles
            is_team_leader = user.has_group('technical_service_presentation.group_technical_team_leader')
            is_senior_tech = user.has_group('technical_service_presentation.group_technical_senior_technician')
            is_technician = user.has_group('technical_service_presentation.group_technical_technician')

            # Grant access if user has any of these roles
            if is_team_leader or is_senior_tech or is_technician:
                record.x_can_edit_work_orders = True
            else:
                record.x_can_edit_work_orders = False

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
