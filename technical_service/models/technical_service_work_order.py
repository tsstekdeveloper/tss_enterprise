# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class TechnicalServiceWorkOrder(models.Model):
    """
    Work Order Model for Field Service Operations
    New model (not inheriting) to avoid conflicts with project.task
    Purpose: Manage field service work orders with checklist, time tracking, and parts usage

    Added Fields:
        - Link to service request
        - Checklist items
        - Time logs
        - Parts consumption
        - Signature fields
    """
    _name = 'technical_service.work_order'
    _description = 'Technical Service Work Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Basic fields from task-like functionality
    name = fields.Char(string='Title', required=True, tracking=True)
    title = fields.Char(string='Work Order Title', related='name')  # Alias for compatibility
    description = fields.Text(string='Description')

    # Priority and Team
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium')

    team_id = fields.Many2one('maintenance.team', string='Assigned Team')
    asset_id = fields.Many2one('maintenance.equipment', string='Asset')

    # Time estimates
    estimated_hours = fields.Float(string='Estimated Hours', default=1.0)
    work_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive'),
        ('emergency', 'Emergency')
    ], string='Work Type', default='corrective')

    # Link to Request
    x_request_id = fields.Many2one(
        'maintenance.request',
        string='Service Request',
        required=True,
        ondelete='cascade'
    )

    # Technician Assignment
    x_technician_id = fields.Many2one(
        'hr.employee',
        string='Assigned Technician',
        tracking=True
    )
    x_technician_user_id = fields.Many2one(
        related='x_technician_id.user_id',
        string='Technician User',
        store=True
    )

    # Preventive Maintenance Link
    preventive_maintenance_id = fields.Many2one(
        'technical.service.preventive.maintenance',
        string='Preventive Maintenance',
        help='Link to preventive maintenance schedule if this work order was generated from it'
    )

    # Work Order Details
    x_work_type = fields.Selection([
        ('inspection', 'Inspection'),
        ('repair', 'Repair'),
        ('installation', 'Installation'),
        ('maintenance', 'Maintenance'),
        ('diagnosis', 'Diagnosis'),
    ], string='Work Type', required=True, default='repair')

    x_estimated_duration = fields.Float(string='Estimated Duration (Hours)', default=1.0)
    x_actual_duration = fields.Float(string='Actual Duration (Hours)', compute='_compute_actual_duration', store=True)

    # Schedule
    x_scheduled_date = fields.Datetime(string='Scheduled Date', tracking=True)
    x_start_datetime = fields.Datetime(string='Start Date/Time', tracking=True)
    x_end_datetime = fields.Datetime(string='End Date/Time', tracking=True)

    # Checklist
    x_checklist_line_ids = fields.One2many(
        'technical_service.work_order.checklist',
        'work_order_id',
        string='Checklist Items'
    )
    x_checklist_progress = fields.Float(
        string='Checklist Progress (%)',
        compute='_compute_checklist_progress',
        store=True
    )

    # Parts Usage
    x_parts_line_ids = fields.One2many(
        'technical_service.work_order.parts',
        'work_order_id',
        string='Used Parts'
    )
    x_total_parts_cost = fields.Float(
        string='Total Parts Cost',
        compute='_compute_total_parts_cost',
        store=True
    )

    # Time Logs
    x_time_log_ids = fields.One2many(
        'technical_service.work_order.timelog',
        'work_order_id',
        string='Time Logs'
    )

    # Work Status
    x_work_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Work Status', default='pending', tracking=True)

    # Results
    x_work_performed = fields.Text(string='Work Performed Description')
    x_root_cause = fields.Text(string='Root Cause Analysis')
    x_recommendations = fields.Text(string='Recommendations')

    # Safety
    x_safety_checklist_completed = fields.Boolean(string='Safety Checklist Completed')
    x_risk_assessment = fields.Text(string='Risk Assessment')

    # Signatures
    x_technician_signature = fields.Binary(string='Technician Signature')
    x_customer_signature = fields.Binary(string='Customer Signature')
    x_signature_date = fields.Datetime(string='Signature Date')

    # Photos
    x_before_photo = fields.Binary(string='Before Photo')
    x_after_photo = fields.Binary(string='After Photo')

    @api.depends('x_checklist_line_ids.is_done')
    def _compute_checklist_progress(self):
        """Calculate checklist completion percentage"""
        for record in self:
            if record.x_checklist_line_ids:
                done_count = len(record.x_checklist_line_ids.filtered('is_done'))
                total_count = len(record.x_checklist_line_ids)
                record.x_checklist_progress = (done_count / total_count) * 100
            else:
                record.x_checklist_progress = 0.0

    @api.depends('x_parts_line_ids.subtotal')
    def _compute_total_parts_cost(self):
        """Calculate total cost of used parts"""
        for record in self:
            record.x_total_parts_cost = sum(record.x_parts_line_ids.mapped('subtotal'))

    @api.depends('x_time_log_ids.duration')
    def _compute_actual_duration(self):
        """Calculate total actual duration from time logs"""
        for record in self:
            record.x_actual_duration = sum(record.x_time_log_ids.mapped('duration'))

    def action_start_work(self):
        """Start work order and create time log"""
        self.ensure_one()
        if self.x_work_status != 'pending':
            raise UserError(_('Work order must be in pending status to start.'))

        self.write({
            'x_work_status': 'in_progress',
            'x_start_datetime': fields.Datetime.now(),
        })

        # Create time log entry
        self.env['technical_service.work_order.timelog'].create({
            'work_order_id': self.id,
            'start_time': fields.Datetime.now(),
            'technician_id': self.x_technician_id.id,
        })

        return True

    def action_pause_work(self):
        """Pause work order and stop time log"""
        self.ensure_one()
        if self.x_work_status != 'in_progress':
            raise UserError(_('Can only pause work that is in progress.'))

        self.x_work_status = 'paused'

        # Stop current time log
        current_log = self.x_time_log_ids.filtered(lambda l: not l.end_time)
        if current_log:
            current_log[0].end_time = fields.Datetime.now()

        return True

    def action_resume_work(self):
        """Resume paused work order"""
        self.ensure_one()
        if self.x_work_status != 'paused':
            raise UserError(_('Can only resume paused work.'))

        self.x_work_status = 'in_progress'

        # Create new time log entry
        self.env['technical_service.work_order.timelog'].create({
            'work_order_id': self.id,
            'start_time': fields.Datetime.now(),
            'technician_id': self.x_technician_id.id,
        })

        return True

    def action_complete_work(self):
        """Complete work order"""
        self.ensure_one()
        if self.x_work_status not in ['in_progress', 'paused']:
            raise UserError(_('Work must be in progress or paused to complete.'))

        # Stop any open time logs
        open_logs = self.x_time_log_ids.filtered(lambda l: not l.end_time)
        for log in open_logs:
            log.end_time = fields.Datetime.now()

        self.write({
            'x_work_status': 'completed',
            'x_end_datetime': fields.Datetime.now(),
        })

        # Update request status if all work orders are completed
        if self.x_request_id:
            all_completed = all(
                wo.x_work_status == 'completed'
                for wo in self.x_request_id.x_work_order_ids
            )
            if all_completed:
                # Find done stage
                done_stage = self.env['maintenance.stage'].search([('done', '=', True)], limit=1)
                if done_stage:
                    self.x_request_id.stage_id = done_stage

        return True


class WorkOrderChecklist(models.Model):
    """Checklist items for work orders"""
    _name = 'technical_service.work_order.checklist'
    _description = 'Work Order Checklist'
    _order = 'sequence, id'

    work_order_id = fields.Many2one('technical_service.work_order', string='Work Order', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Checklist Item', required=True)
    description = fields.Text(string='Description')
    is_done = fields.Boolean(string='Done', default=False)
    done_date = fields.Datetime(string='Completion Date')
    notes = fields.Text(string='Notes')

    @api.onchange('is_done')
    def _onchange_is_done(self):
        """Set completion date when marked as done"""
        if self.is_done:
            self.done_date = fields.Datetime.now()
        else:
            self.done_date = False


class WorkOrderParts(models.Model):
    """Parts used in work orders"""
    _name = 'technical_service.work_order.parts'
    _description = 'Work Order Parts'

    work_order_id = fields.Many2one('technical_service.work_order', string='Work Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Part/Product', required=True, domain=[('type', 'in', ['product', 'consu'])])
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    unit_price = fields.Float(string='Unit Price', related='product_id.standard_price', readonly=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    stock_move_id = fields.Many2one('stock.move', string='Stock Move')
    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price


class WorkOrderTimeLog(models.Model):
    """Time tracking for work orders"""
    _name = 'technical_service.work_order.timelog'
    _description = 'Work Order Time Log'
    _order = 'start_time desc'

    work_order_id = fields.Many2one('technical_service.work_order', string='Work Order', required=True, ondelete='cascade')
    technician_id = fields.Many2one('hr.employee', string='Technician', required=True)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time')
    duration = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)
    work_description = fields.Text(string='Work Description')

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration = delta.total_seconds() / 3600.0
            else:
                record.duration = 0.0