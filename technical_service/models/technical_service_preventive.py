# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class TechnicalServicePreventiveMaintenance(models.Model):
    _name = 'technical.service.preventive.maintenance'
    _description = 'Preventive Maintenance Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'next_maintenance_date'

    name = fields.Char(string='Maintenance Plan Name', required=True)
    asset_id = fields.Many2one('maintenance.equipment', string='Asset', required=True)
    team_id = fields.Many2one('maintenance.team', string='Assigned Team')

    # Schedule Configuration
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
        ('custom', 'Custom')
    ], string='Frequency', required=True, default='monthly')

    custom_frequency_days = fields.Integer(string='Custom Frequency (days)',
                                          help='Only used when frequency is Custom')

    # Dates
    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.today)
    last_maintenance_date = fields.Date(string='Last Maintenance Date')
    next_maintenance_date = fields.Date(string='Next Maintenance Date',
                                       compute='_compute_next_maintenance', store=True)

    # Task Details
    maintenance_type = fields.Selection([
        ('inspection', 'Inspection'),
        ('cleaning', 'Cleaning'),
        ('calibration', 'Calibration'),
        ('replacement', 'Parts Replacement'),
        ('testing', 'Testing'),
        ('comprehensive', 'Comprehensive Service')
    ], string='Maintenance Type', required=True, default='inspection')

    task_description = fields.Text(string='Task Description', required=True)
    checklist = fields.Text(string='Maintenance Checklist')
    estimated_duration = fields.Float(string='Estimated Duration (hours)', default=1.0)

    # Parts and Resources
    required_parts = fields.Text(string='Required Parts/Materials')
    special_tools = fields.Text(string='Special Tools Required')
    safety_precautions = fields.Text(string='Safety Precautions')

    # Status
    state = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired')
    ], string='Status', default='active', tracking=True)

    is_overdue = fields.Boolean(string='Overdue', compute='_compute_overdue')

    # History
    maintenance_count = fields.Integer(string='Maintenances Performed', default=0)
    work_order_ids = fields.One2many('technical_service.work_order',
                                    'preventive_maintenance_id',
                                    string='Generated Work Orders')

    # Notifications
    notify_days_before = fields.Integer(string='Notify Days Before', default=7,
                                       help='Send notification X days before maintenance')
    notify_team = fields.Boolean(string='Notify Team', default=True)
    notify_customer = fields.Boolean(string='Notify Customer', default=False)

    @api.depends('frequency', 'custom_frequency_days', 'last_maintenance_date', 'start_date')
    def _compute_next_maintenance(self):
        for record in self:
            base_date = record.last_maintenance_date or record.start_date

            if not base_date:
                record.next_maintenance_date = False
                continue

            if record.frequency == 'daily':
                next_date = base_date + timedelta(days=1)
            elif record.frequency == 'weekly':
                next_date = base_date + timedelta(weeks=1)
            elif record.frequency == 'monthly':
                next_date = base_date + relativedelta(months=1)
            elif record.frequency == 'quarterly':
                next_date = base_date + relativedelta(months=3)
            elif record.frequency == 'semi_annual':
                next_date = base_date + relativedelta(months=6)
            elif record.frequency == 'annual':
                next_date = base_date + relativedelta(years=1)
            elif record.frequency == 'custom' and record.custom_frequency_days:
                next_date = base_date + timedelta(days=record.custom_frequency_days)
            else:
                next_date = base_date

            record.next_maintenance_date = next_date

    @api.depends('next_maintenance_date', 'state')
    def _compute_overdue(self):
        today = fields.Date.today()
        for record in self:
            record.is_overdue = (
                record.state == 'active' and
                record.next_maintenance_date and
                record.next_maintenance_date < today
            )

    def action_create_work_order(self):
        """Create a work order for this maintenance"""
        work_order = self.env['technical.service.work.order'].create({
            'title': f"Preventive Maintenance: {self.name}",
            'description': self.task_description,
            'asset_id': self.asset_id.id,
            'team_id': self.team_id.id if self.team_id else False,
            'preventive_maintenance_id': self.id,
            'work_type': 'preventive',
            'priority': 'medium',
            'estimated_hours': self.estimated_duration,
        })

        # Update maintenance record
        self.write({
            'last_maintenance_date': fields.Date.today(),
            'maintenance_count': self.maintenance_count + 1
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'technical.service.work.order',
            'view_mode': 'form',
            'res_id': work_order.id,
        }

    def action_suspend(self):
        self.state = 'suspended'

    def action_reactivate(self):
        self.state = 'active'

    @api.model
    def check_upcoming_maintenances(self):
        """Cron job to check and notify upcoming maintenances"""
        today = fields.Date.today()

        for maintenance in self.search([('state', '=', 'active')]):
            if maintenance.next_maintenance_date:
                days_until = (maintenance.next_maintenance_date - today).days

                if days_until == maintenance.notify_days_before:
                    # Send notifications
                    maintenance.message_post(
                        body=f"Upcoming maintenance scheduled in {days_until} days for {maintenance.asset_id.name}"
                    )

                elif days_until < 0:
                    # Overdue notification
                    maintenance.message_post(
                        body=f"OVERDUE: Maintenance for {maintenance.asset_id.name} was due {abs(days_until)} days ago"
                    )