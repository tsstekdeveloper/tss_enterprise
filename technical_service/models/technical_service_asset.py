# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class TechnicalServiceAsset(models.Model):
    """
    Asset/Equipment Management Model
    Inherited from: maintenance.equipment (/opt/odoo/odoo18/addons/maintenance/models/maintenance.py)
    Purpose: Extended asset management with warranty, contracts, and maintenance history

    Added Fields:
        - Detailed asset information
        - Warranty and contract tracking
        - Location and assignment
        - Maintenance history
    """
    _inherit = 'maintenance.equipment'
    _description = 'Technical Service Asset'

    # Asset Identification
    x_asset_code = fields.Char(string='Asset Code', copy=False)
    x_barcode = fields.Char(string='Barcode', copy=False)
    x_qr_code = fields.Char(string='QR Code', copy=False)

    # Asset Details
    x_asset_type = fields.Selection([
        ('it_equipment', 'IT Equipment'),
        ('facility_equipment', 'Facility Equipment'),
        ('vehicle', 'Vehicle'),
        ('furniture', 'Furniture'),
        ('tool', 'Tool/Instrument'),
        ('other', 'Other'),
    ], string='Asset Type', required=True, default='it_equipment')

    x_manufacturer = fields.Char(string='Manufacturer')
    x_purchase_date = fields.Date(string='Purchase Date')
    x_purchase_value = fields.Float(string='Purchase Value')
    x_current_value = fields.Float(string='Current Value')
    x_depreciation_rate = fields.Float(string='Depreciation Rate (%)')

    # Location
    x_campus_id = fields.Many2one('technical_service.campus', string='Campus')
    x_building_id = fields.Many2one('technical_service.building', string='Building')
    x_floor = fields.Char(string='Floor')
    x_room = fields.Char(string='Room/Location')

    # Assignment
    x_assigned_employee_id = fields.Many2one('hr.employee', string='Assigned Employee')

    # Maintenance Team (fix for widget error)
    maintenance_team_id = fields.Many2one('maintenance.team', string='Maintenance Team')
    x_department_id = fields.Many2one('hr.department', string='Department')
    x_assignment_date = fields.Date(string='Assignment Date')

    # Warranty Information
    x_warranty_start_date = fields.Date(string='Warranty Start Date')
    x_warranty_end_date = fields.Date(string='Warranty End Date')
    x_warranty_status = fields.Selection([
        ('in_warranty', 'In Warranty'),
        ('expired', 'Expired'),
        ('no_warranty', 'No Warranty'),
    ], string='Warranty Status', compute='_compute_warranty_status', store=True)
    x_warranty_vendor_id = fields.Many2one('res.partner', string='Warranty Vendor')

    # Contract Information
    x_contract_id = fields.Many2one('technical_service.contract', string='Maintenance Contract')
    x_contract_start_date = fields.Date(string='Contract Start Date')
    x_contract_end_date = fields.Date(string='Contract End Date')
    x_contract_status = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('none', 'No Contract'),
    ], string='Contract Status', compute='_compute_contract_status', store=True)

    # Maintenance Information
    x_last_maintenance_date = fields.Date(string='Last Maintenance Date')
    x_next_maintenance_date = fields.Date(string='Next Maintenance Date')
    x_maintenance_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('as_needed', 'As Needed'),
    ], string='Maintenance Frequency')

    # Calibration (for instruments)
    x_requires_calibration = fields.Boolean(string='Requires Calibration')
    x_last_calibration_date = fields.Date(string='Last Calibration Date')
    x_next_calibration_date = fields.Date(string='Next Calibration Date')
    x_calibration_certificate = fields.Binary(string='Calibration Certificate')

    # Statistics
    x_total_maintenance_cost = fields.Float(string='Total Maintenance Cost', compute='_compute_maintenance_stats')
    x_failure_count = fields.Integer(string='Failure Count', compute='_compute_maintenance_stats')
    x_downtime_hours = fields.Float(string='Total Downtime (Hours)', compute='_compute_maintenance_stats')

    @api.depends('x_warranty_end_date')
    def _compute_warranty_status(self):
        """Compute warranty status based on end date"""
        today = fields.Date.today()
        for record in self:
            if not record.x_warranty_end_date:
                record.x_warranty_status = 'no_warranty'
            elif record.x_warranty_end_date >= today:
                record.x_warranty_status = 'in_warranty'
            else:
                record.x_warranty_status = 'expired'

    @api.depends('x_contract_end_date')
    def _compute_contract_status(self):
        """Compute contract status based on end date"""
        today = fields.Date.today()
        for record in self:
            if not record.x_contract_id:
                record.x_contract_status = 'none'
            elif record.x_contract_end_date and record.x_contract_end_date >= today:
                record.x_contract_status = 'active'
            else:
                record.x_contract_status = 'expired'

    def _compute_maintenance_stats(self):
        """Compute maintenance statistics"""
        for record in self:
            # Get all maintenance requests for this equipment
            requests = self.env['maintenance.request'].search([
                ('equipment_id', '=', record.id)
            ])

            # Calculate statistics
            record.x_failure_count = len(requests.filtered(
                lambda r: r.x_request_type == 'incident'
            ))

            record.x_total_maintenance_cost = sum(
                wo.x_total_parts_cost
                for req in requests
                for wo in req.x_work_order_ids
            )

            record.x_downtime_hours = sum(
                req.x_resolution_time
                for req in requests
                if req.x_resolution_time
            )

    def action_create_maintenance_request(self):
        """Create maintenance request for this asset"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Maintenance Request'),
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_equipment_id': self.id,
                'default_x_campus_id': self.x_campus_id.id,
                'default_x_building_id': self.x_building_id.id,
                'default_x_floor': self.x_floor,
                'default_x_room': self.x_room,
            }
        }

    @api.model
    def create_maintenance_reminders(self):
        """Cron job to create maintenance reminders"""
        today = fields.Date.today()
        reminder_days = 7  # Create reminder 7 days before

        # Find assets needing maintenance soon
        assets = self.search([
            ('x_next_maintenance_date', '<=', today + timedelta(days=reminder_days)),
            ('x_next_maintenance_date', '>=', today),
        ])

        for asset in assets:
            # Check if reminder already exists
            existing = self.env['maintenance.request'].search([
                ('equipment_id', '=', asset.id),
                ('x_request_type', '=', 'preventive'),
                ('stage_id.done', '=', False),
            ])

            if not existing:
                # Create preventive maintenance request
                self.env['maintenance.request'].create({
                    'name': f"Scheduled Maintenance - {asset.name}",
                    'equipment_id': asset.id,
                    'x_request_type': 'preventive',
                    'schedule_date': asset.x_next_maintenance_date,
                    'description': f"Scheduled maintenance for {asset.name}",
                })


class TechnicalServiceContract(models.Model):
    """Maintenance contracts management"""
    _name = 'technical_service.contract'
    _description = 'Maintenance Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Contract Number', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    contract_type = fields.Selection([
        ('amc', 'Annual Maintenance Contract'),
        ('warranty', 'Extended Warranty'),
        ('service', 'Service Agreement'),
        ('sla', 'SLA Agreement'),
    ], string='Contract Type', required=True)

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    value = fields.Float(string='Contract Value')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Coverage
    x_coverage_type = fields.Selection([
        ('full', 'Full Coverage'),
        ('parts', 'Parts Only'),
        ('labor', 'Labor Only'),
        ('limited', 'Limited Coverage'),
    ], string='Coverage Type')

    x_response_time = fields.Float(string='Response Time (Hours)')
    x_resolution_time = fields.Float(string='Resolution Time (Hours)')

    equipment_ids = fields.One2many('maintenance.equipment', 'x_contract_id', string='Covered Equipment')
    equipment_count = fields.Integer(string='Equipment Count', compute='_compute_equipment_count')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for record in self:
            record.equipment_count = len(record.equipment_ids)

    def action_activate(self):
        """Activate contract"""
        self.ensure_one()
        self.state = 'active'

    def action_expire(self):
        """Expire contract"""
        self.ensure_one()
        self.state = 'expired'

    @api.model
    def check_contract_expiry(self):
        """Cron job to check and update expired contracts"""
        today = fields.Date.today()

        # Find expired contracts
        expired_contracts = self.search([
            ('state', '=', 'active'),
            ('end_date', '<', today),
        ])

        for contract in expired_contracts:
            contract.state = 'expired'

        # Send notifications for contracts expiring soon (30 days)
        expiring_soon = self.search([
            ('state', '=', 'active'),
            ('end_date', '<=', today + timedelta(days=30)),
            ('end_date', '>=', today),
        ])

        for contract in expiring_soon:
            contract.message_post(
                body=_(f"Contract {contract.name} is expiring on {contract.end_date}"),
                subject=_("Contract Expiry Reminder"),
            )