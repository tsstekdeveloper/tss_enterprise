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

    # Team Type for Role Assignment
    team_type = fields.Selection([
        ('operational', 'Operasyonel Ekip'),      # Normal technical teams
        ('dispatching', 'Dispatching Ekibi'),     # DSP role assignment
        ('inventory', 'Envanter Ekibi'),          # INV role assignment
        ('location', 'Lokasyon Ekibi'),           # LCM role assignment
    ], string='Ekip Tipi', default='operational',
       help='Ekip tipi, üyelerin otomatik rol atamasını belirler')

    # Team Leader - Computed from team members
    team_leader_user_id = fields.Many2one(
        'res.users',
        string='Takım Lideri',
        compute='_compute_team_leader',
        store=True,
        help='Bu ekibin takım lideri (team members içinden otomatik belirlenir)'
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
    x_is_default_assignment = fields.Boolean(
        string='Use for Default Assignment',
        help='If checked, this team will be automatically assigned to new service requests. Only one team can be marked as default.'
    )

    @api.depends('x_member_ids')
    def _compute_member_count(self):
        for team in self:
            team.x_member_count = len(team.x_member_ids)

    @api.depends('x_member_ids.member_role', 'x_member_ids.user_id', 'x_member_ids.employee_id.user_id')
    def _compute_team_leader(self):
        """Compute team leader from team members with team_leader role"""
        for team in self:
            leader_members = team.x_member_ids.filtered(
                lambda m: m.member_role == 'team_leader' and m.user_id
            )
            if leader_members:
                # Use the first team leader found
                team.team_leader_user_id = leader_members[0].user_id
            else:
                team.team_leader_user_id = False

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

    @api.constrains('x_is_default_assignment')
    def _check_default_assignment(self):
        """Ensure only one team is marked as default for assignment"""
        for team in self:
            if team.x_is_default_assignment:
                other_default = self.env['maintenance.team'].search([
                    ('x_is_default_assignment', '=', True),
                    ('id', '!=', team.id)
                ], limit=1)
                if other_default:
                    raise ValidationError(
                        _('Only one team can be marked as default for assignment. Team "%s" is already set as default.') % other_default.name
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
        required=True
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