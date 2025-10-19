# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TechnicalServiceTeam(models.Model):
    """
    Technical Service Team Management
    Inherited from: maintenance.team (/opt/odoo/odoo18/addons/maintenance/models/maintenance.py)
    Purpose: Extended team management with skills, shifts, and workload

    Added Fields:
        - Team specialization
        - Shift management
        - Skill matrix
        - Workload tracking
    """
    _inherit = 'maintenance.team'
    _description = 'Technical Service Team'

    # Team Specialization
    x_specialization = fields.Selection([
        ('it', 'IT/Bilgi İşlem'),
        ('electrical', 'Electrical'),
        ('mechanical', 'Mechanical'),
        ('hvac', 'HVAC'),
        ('plumbing', 'Plumbing'),
        ('general', 'General Maintenance'),
        ('mixed', 'Mixed/All'),
    ], string='Team Specialization', default='mixed')

    # ============================================
    # TASK 06: ORGANIZATIONAL HIERARCHY
    # Date: 17 October 2024
    # ============================================

    # Hierarchy Fields
    parent_id = fields.Many2one(
        'maintenance.team',
        string='Üst Ekip',
        ondelete='restrict',
        help='Bu ekibin bağlı olduğu üst seviye ekip'
    )

    child_ids = fields.One2many(
        'maintenance.team',
        'parent_id',
        string='Alt Ekipler'
    )

    hierarchy_path = fields.Char(
        string='Hierarchy Path',
        compute='_compute_hierarchy_path',
        store=True,
        index=True,
        help='Full path: /1/5/23/'
    )

    hierarchy_level = fields.Integer(
        string='Seviye',
        compute='_compute_hierarchy_level',
        store=True,
        help='0=Root, 1=Üst Ekip, 2=Alt Ekip'
    )

    # Team hierarchy permissions
    can_have_children = fields.Boolean(
        string='Alt Ekip Eklenebilir',
        default=True,
        help='Bu ekibin altına başka ekipler bağlanabilir mi?'
    )

    # Team active status (for service assignment)
    is_active = fields.Boolean(
        string='Aktif',
        default=True,
        help='Pasif ekiplere servis talebi atanamaz'
    )

    # Management
    department_manager_id = fields.Many2one(
        'hr.employee',
        string='Departman Yöneticisi',
        domain=lambda self: [('user_id.groups_id', 'in', [
            self.env.ref('technical_service_presentation.group_technical_cto').id,
            self.env.ref('technical_service_presentation.group_technical_department_manager').id
        ])],
        help='Bu ekibin departman yöneticisi (Department Manager veya CTO rolü olan çalışan)'
    )

    # Team Leader - Employee with Team Leader role
    team_leader_user_id = fields.Many2one(
        'hr.employee',
        string='Takım Lideri',
        domain=lambda self: [('user_id.groups_id', 'in', [
            self.env.ref('technical_service_presentation.group_technical_team_leader').id
        ])],
        help='Bu ekibin takım lideri (Team Leader rolüne sahip çalışan)'
    )

    # Team Members with Skills
    x_member_ids = fields.One2many(
        'technical_service.team.member',
        'team_id',
        string='Team Members'
    )
    x_member_count = fields.Integer(
        string='Member Count',
        compute='_compute_member_count'
    )

    # Shift Information
    x_shift_type = fields.Selection([
        ('regular', 'Regular Hours'),
        ('shift', 'Shift Based'),
        ('24x7', '24x7 Coverage'),
        ('on_call', 'On Call'),
    ], string='Shift Type', default='regular')

    x_current_shift = fields.Selection([
        ('day', 'Day Shift'),
        ('evening', 'Evening Shift'),
        ('night', 'Night Shift'),
        ('weekend', 'Weekend'),
    ], string='Current Shift')

    # Coverage Areas
    x_campus_ids = fields.Many2many(
        'technical_service.campus',
        string='Coverage Areas'
    )

    # Workload
    x_active_requests = fields.Integer(
        string='Active Requests',
        compute='_compute_workload'
    )
    x_pending_requests = fields.Integer(
        string='Pending Requests',
        compute='_compute_workload'
    )
    x_avg_resolution_time = fields.Float(
        string='Avg Resolution Time (Hours)',
        compute='_compute_workload'
    )

    # Auto Assignment
    x_auto_assign = fields.Boolean(string='Auto Assignment', default=True)
    x_assignment_method = fields.Selection([
        ('round_robin', 'Round Robin'),
        ('least_loaded', 'Least Loaded'),
        ('skill_based', 'Skill Based'),
        ('location_based', 'Location Based'),
    ], string='Assignment Method', default='round_robin')
    # TASK 07 - PHASE 6: Default Assignment Team Routing
    # Date: 18 October 2025
    x_is_default_assignment_team = fields.Boolean(
        string='Varsayılan Atama Takımı',
        default=False,
        help='Yeni servis talepleri otomatik olarak bu takımın listesinde görünecektir, atanan takımdan bağımsız olarak.'
    )

    @api.depends('x_member_ids')
    def _compute_member_count(self):
        for team in self:
            team.x_member_count = len(team.x_member_ids)


    @api.depends('parent_id', 'parent_id.hierarchy_path')
    def _compute_hierarchy_path(self):
        """Compute hierarchy path for efficient queries"""
        for team in self:
            if team.parent_id:
                team.hierarchy_path = f"{team.parent_id.hierarchy_path}{team.id}/"
            else:
                team.hierarchy_path = f"/{team.id}/"

    @api.depends('parent_id')
    def _compute_hierarchy_level(self):
        """Compute hierarchy level (depth in tree)"""
        for team in self:
            if not team.parent_id:
                team.hierarchy_level = 0
            else:
                level = 1
                parent = team.parent_id
                while parent and level < 10:  # Max 10 levels
                    level += 1
                    parent = parent.parent_id
                team.hierarchy_level = level

    def _compute_workload(self):
        for team in self:
            # Active requests
            active_requests = self.env['maintenance.request'].search([
                ('maintenance_team_id', '=', team.id),
                ('stage_id.done', '=', False)
            ])
            team.x_active_requests = len(active_requests)

            # Pending requests
            pending_requests = active_requests.filtered(
                lambda r: not r.user_id
            )
            team.x_pending_requests = len(pending_requests)

            # Average resolution time
            completed_requests = self.env['maintenance.request'].search([
                ('maintenance_team_id', '=', team.id),
                ('stage_id.done', '=', True),
                ('x_resolution_time', '>', 0)
            ], limit=100)  # Last 100 for performance

            if completed_requests:
                team.x_avg_resolution_time = sum(
                    completed_requests.mapped('x_resolution_time')
                ) / len(completed_requests)
            else:
                team.x_avg_resolution_time = 0.0

    @api.constrains('x_is_default_assignment_team')
    def _check_default_assignment_team(self):
        """Ensure only one team is marked as default for assignment - Task 07 Phase 6"""
        for team in self:
            if team.x_is_default_assignment_team:
                other_default = self.env['maintenance.team'].search([
                    ('x_is_default_assignment_team', '=', True),
                    ('id', '!=', team.id)
                ], limit=1)
                if other_default:
                    raise ValidationError(
                        _('Sadece bir takım varsayılan atama takımı olarak işaretlenebilir. "%s" takımı zaten varsayılan olarak ayarlanmış.') % other_default.name
                    )

    def assign_technician(self, request):
        """Assign best available technician to request"""
        self.ensure_one()

        if not self.x_auto_assign:
            return False

        # Get available members
        available_members = self.x_member_ids.filtered(
            lambda m: m.x_is_available
        )

        if not available_members:
            return False

        # Assignment based on method
        if self.x_assignment_method == 'round_robin':
            # Get least recently assigned member
            member = available_members.sorted('x_last_assigned_date')[0]

        elif self.x_assignment_method == 'least_loaded':
            # Get member with least active requests
            member = min(available_members, key=lambda m: m.x_active_request_count)

        elif self.x_assignment_method == 'skill_based':
            # Match skills with request category
            skilled_members = available_members.filtered(
                lambda m: request.category_id.id in m.x_skill_category_ids.ids
            )
            if skilled_members:
                member = skilled_members[0]
            else:
                member = available_members[0]

        elif self.x_assignment_method == 'location_based':
            # Assign based on location proximity
            location_members = available_members.filtered(
                lambda m: request.x_campus_id.id in m.x_coverage_campus_ids.ids
            )
            if location_members:
                member = location_members[0]
            else:
                member = available_members[0]

        else:
            member = available_members[0]

        # Assign technician
        if member:
            request.technician_user_id = member.user_id
            member.x_last_assigned_date = fields.Datetime.now()
            return True

        return False


class TechnicalServiceTeamMember(models.Model):
    """Team member with skills and availability"""
    _name = 'technical_service.team.member'
    _description = 'Team Member'
    _rec_name = 'employee_id'

    team_id = fields.Many2one(
        'maintenance.team',
        string='Team',
        required=True,
        ondelete='cascade'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        domain=lambda self: [('user_id.groups_id', 'in', [
            self.env.ref('technical_service_presentation.group_technical_dispatcher').id,
            self.env.ref('technical_service_presentation.group_technical_technician').id,
            self.env.ref('technical_service_presentation.group_technical_senior_technician').id
        ])]
    )
    user_id = fields.Many2one(
        related='employee_id.user_id',
        string='User',
        store=True,
        readonly=False  # Allow manual override if needed
    )

    # Member Role in Team
    member_role = fields.Selection([
        ('team_leader', 'Takım Lideri'),
        ('senior_technician', 'Kıdemli Teknisyen'),
        ('technician', 'Teknisyen'),
    ], string='Ekip İçi Rol', default='technician',
       help='Bu üyenin ekip içindeki rolü')

    # TASK 06: TSS Security Roles
    tss_role_ids = fields.Many2many(
        'res.groups',
        'tech_member_tss_role_rel',
        'member_id',
        'group_id',
        string='TSS Rolleri',
        compute='_compute_tss_roles',
        help='Bu üyenin TSS security rolleri (user_id\'den)'
    )

    # Skills
    x_skill_category_ids = fields.Many2many(
        'maintenance.equipment.category',
        'tech_service_member_skill_rel',
        'member_id',
        'category_id',
        string='Skill Categories'
    )
    x_skill_level = fields.Selection([
        ('junior', 'Junior'),
        ('mid', 'Mid-Level'),
        ('senior', 'Senior'),
        ('expert', 'Expert'),
    ], string='Skill Level', default='mid')

    x_certifications = fields.Text(string='Certifications')

    # Availability
    x_is_available = fields.Boolean(string='Is Available', default=True)
    x_availability_status = fields.Selection([
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('on_leave', 'On Leave'),
        ('off_duty', 'Off Duty'),
    ], string='Status', default='available')

    # Shift
    x_shift = fields.Selection([
        ('day', 'Day Shift'),
        ('evening', 'Evening Shift'),
        ('night', 'Night Shift'),
        ('flexible', 'Flexible'),
    ], string='Shift', default='day')

    # Coverage
    x_coverage_campus_ids = fields.Many2many(
        'technical_service.campus',
        'tech_service_member_campus_rel',
        'member_id',
        'campus_id',
        string='Coverage Areas'
    )

    # Workload
    x_active_request_count = fields.Integer(
        string='Active Requests',
        compute='_compute_workload'
    )
    x_completed_today = fields.Integer(
        string='Completed Today',
        compute='_compute_workload'
    )

    # Assignment tracking
    x_last_assigned_date = fields.Datetime(string='Last Assigned')

    # ============================================
    # PHASE 1: ORGANIZATIONAL ARCHITECTURE FIELDS
    # Added: 16 October 2024
    # ============================================

    # Department Linkage
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        compute='_compute_department_from_team',
        store=True,
        help='Department derived from team or employee'
    )

    # HR Job Position
    job_position_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        related='employee_id.job_id',
        store=True,
        readonly=True,
        help='Job position from HR employee record'
    )

    # Hierarchy Level (1-5)
    hierarchy_level = fields.Integer(
        string='Hierarchy Level',
        compute='_compute_hierarchy_level',
        store=True,
        help='1=CTO, 2=Dept Mgr, 3=Team Lead, 4=Senior Tech, 5=Technician'
    )

    # Equipment Manager Flag
    is_equipment_manager = fields.Boolean(
        string='Equipment Manager Role',
        default=False,
        help='Has equipment manager responsibilities (dual role support)'
    )

    # Matrix Management
    dotted_line_manager_id = fields.Many2one(
        'technical_service.team.member',
        string='Secondary Manager',
        help='Matrix organization - secondary reporting line'
    )

    # Delegation System
    delegation_active = fields.Boolean(
        string='Delegation Active',
        compute='_compute_delegation_active',
        store=True,
        help='Currently delegating responsibilities'
    )

    delegation_to_id = fields.Many2one(
        'technical_service.team.member',
        string='Delegated To',
        domain="[('team_id', '=', team_id)]",
        help='Temporarily delegating work to this member'
    )

    delegation_start_date = fields.Date(
        string='Delegation Start'
    )

    delegation_end_date = fields.Date(
        string='Delegation End'
    )

    @api.depends('member_role')
    def _compute_hierarchy_level(self):
        """Compute hierarchy level based on role"""
        for member in self:
            if member.member_role == 'team_leader':
                member.hierarchy_level = 3
            elif member.member_role == 'senior_technician':
                member.hierarchy_level = 4
            else:
                member.hierarchy_level = 5

    @api.depends('team_id', 'employee_id.department_id')
    def _compute_department_from_team(self):
        """Compute department from team or employee"""
        for member in self:
            if member.employee_id and member.employee_id.department_id:
                member.department_id = member.employee_id.department_id
            else:
                member.department_id = False

    @api.depends('delegation_to_id', 'delegation_start_date', 'delegation_end_date')
    def _compute_delegation_active(self):
        """Check if delegation is currently active"""
        today = fields.Date.today()
        for member in self:
            if member.delegation_to_id and member.delegation_start_date:
                if not member.delegation_end_date or member.delegation_end_date >= today:
                    if member.delegation_start_date <= today:
                        member.delegation_active = True
                        continue
            member.delegation_active = False

    # End of Phase 1 fields
    # ============================================

    def _compute_workload(self):
        for member in self:
            # Active requests
            active_requests = self.env['maintenance.request'].search([
                ('technician_user_id', '=', member.user_id.id),
                ('stage_id.done', '=', False)
            ])
            member.x_active_request_count = len(active_requests)

            # Completed today
            today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0)
            completed_today = self.env['maintenance.request'].search([
                ('technician_user_id', '=', member.user_id.id),
                ('close_date', '>=', today_start),
                ('stage_id.done', '=', True)
            ])
            member.x_completed_today = len(completed_today)

    @api.onchange('x_availability_status')
    def _onchange_availability_status(self):
        """Update availability based on status"""
        if self.x_availability_status in ['available']:
            self.x_is_available = True
        else:
            self.x_is_available = False

    @api.depends('user_id.groups_id')
    def _compute_tss_roles(self):
        """Compute TSS roles from user's security groups"""
        for member in self:
            if member.user_id:
                tss_groups = member.user_id.groups_id.filtered(
                    lambda g: g.category_id and g.category_id.name == 'Technical Service Roles'
                )
                member.tss_role_ids = tss_groups
            else:
                member.tss_role_ids = False

    @api.constrains('member_role', 'team_id')
    def _check_single_team_leader(self):
        """Ensure only one team leader per team"""
        for member in self:
            if member.member_role == 'team_leader':
                other_leaders = self.search([
                    ('team_id', '=', member.team_id.id),
                    ('member_role', '=', 'team_leader'),
                    ('id', '!=', member.id)
                ])
                if other_leaders:
                    raise ValidationError(_('Bir ekipte sadece bir takım lideri olabilir!'))