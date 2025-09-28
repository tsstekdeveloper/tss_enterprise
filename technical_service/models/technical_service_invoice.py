# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class TechnicalServiceInvoice(models.Model):
    _name = 'technical.service.invoice'
    _description = 'Technical Service Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'invoice_date desc'

    name = fields.Char(string='Invoice Number', required=True, copy=False, readonly=True, default=lambda self: 'New')
    service_request_id = fields.Many2one('maintenance.request', string='Service Request')
    work_order_id = fields.Many2one('technical_service.work_order', string='Work Order')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.today, required=True)
    due_date = fields.Date(string='Due Date', required=True)

    # Invoice Lines
    labor_hours = fields.Float(string='Labor Hours')
    labor_rate = fields.Float(string='Labor Rate (per hour)', default=50.0)
    labor_amount = fields.Float(string='Labor Amount', compute='_compute_labor_amount', store=True)

    parts_amount = fields.Float(string='Parts Amount')
    other_charges = fields.Float(string='Other Charges')

    subtotal = fields.Float(string='Subtotal', compute='_compute_totals', store=True)
    tax_rate = fields.Float(string='Tax Rate (%)', default=10.0)
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_totals', store=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_totals', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('technical.service.invoice') or 'New'
            if not vals.get('due_date') and vals.get('invoice_date'):
                invoice_date = fields.Date.from_string(vals['invoice_date'])
                vals['due_date'] = invoice_date + timedelta(days=30)
        return super().create(vals_list)

    @api.depends('labor_hours', 'labor_rate')
    def _compute_labor_amount(self):
        for record in self:
            record.labor_amount = record.labor_hours * record.labor_rate

    @api.depends('labor_amount', 'parts_amount', 'other_charges', 'tax_rate')
    def _compute_totals(self):
        for record in self:
            record.subtotal = record.labor_amount + record.parts_amount + record.other_charges
            record.tax_amount = record.subtotal * (record.tax_rate / 100)
            record.total_amount = record.subtotal + record.tax_amount

    def action_send(self):
        self.state = 'sent'

    def action_mark_paid(self):
        self.state = 'paid'

    def action_cancel(self):
        self.state = 'cancelled'