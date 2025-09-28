# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TechnicalServiceInventory(models.Model):
    _name = 'technical.service.inventory'
    _description = 'Technical Service Inventory Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Part Name', required=True)
    code = fields.Char(string='Part Code', required=True)
    category = fields.Selection([
        ('hardware', 'Hardware'),
        ('cable', 'Cables & Connectors'),
        ('consumable', 'Consumables'),
        ('tool', 'Tools'),
        ('spare', 'Spare Parts'),
        ('other', 'Other')
    ], string='Category', required=True, default='spare')

    description = fields.Text(string='Description')
    manufacturer = fields.Char(string='Manufacturer')
    model_number = fields.Char(string='Model Number')

    # Stock Information
    quantity_on_hand = fields.Float(string='Quantity on Hand', default=0.0)
    minimum_quantity = fields.Float(string='Minimum Quantity', default=1.0)
    reorder_quantity = fields.Float(string='Reorder Quantity', default=10.0)
    unit_of_measure = fields.Char(string='Unit of Measure', default='Unit(s)')

    # Location
    warehouse_location = fields.Char(string='Warehouse Location')
    storage_bin = fields.Char(string='Storage Bin/Shelf')

    # Pricing
    unit_cost = fields.Float(string='Unit Cost', digits=(10, 2))
    selling_price = fields.Float(string='Selling Price', digits=(10, 2))
    total_value = fields.Float(string='Total Value', compute='_compute_total_value', store=True)

    # Vendor Information
    vendor_id = fields.Many2one('res.partner', string='Primary Vendor')
    vendor_part_number = fields.Char(string='Vendor Part Number')
    lead_time_days = fields.Integer(string='Lead Time (days)', default=7)

    # Usage tracking
    last_used_date = fields.Date(string='Last Used Date')
    usage_count = fields.Integer(string='Times Used', default=0)

    # Status
    is_active = fields.Boolean(string='Active', default=True)
    is_critical = fields.Boolean(string='Critical Part', default=False)
    needs_reorder = fields.Boolean(string='Needs Reorder', compute='_compute_needs_reorder', store=True)

    # Related work orders
    work_order_ids = fields.Many2many('technical_service.work_order', string='Related Work Orders')

    @api.depends('quantity_on_hand', 'unit_cost')
    def _compute_total_value(self):
        for record in self:
            record.total_value = record.quantity_on_hand * record.unit_cost

    @api.depends('quantity_on_hand', 'minimum_quantity')
    def _compute_needs_reorder(self):
        for record in self:
            record.needs_reorder = record.quantity_on_hand <= record.minimum_quantity

    @api.constrains('minimum_quantity', 'reorder_quantity')
    def _check_quantities(self):
        for record in self:
            if record.minimum_quantity < 0:
                raise ValidationError("Minimum quantity cannot be negative!")
            if record.reorder_quantity < 0:
                raise ValidationError("Reorder quantity cannot be negative!")

    def action_use_part(self, quantity=1):
        """Mark part as used and decrease quantity"""
        if self.quantity_on_hand >= quantity:
            self.quantity_on_hand -= quantity
            self.usage_count += 1
            self.last_used_date = fields.Date.today()
        else:
            raise ValidationError(f"Insufficient quantity! Only {self.quantity_on_hand} available.")

    def action_receive_stock(self, quantity):
        """Receive stock and increase quantity"""
        self.quantity_on_hand += quantity

    def action_reorder(self):
        """Create purchase order or notification for reordering"""
        # This would integrate with purchase module if available
        self.message_post(
            body=f"Reorder requested for {self.name}. Current quantity: {self.quantity_on_hand}, "
                 f"Reorder quantity: {self.reorder_quantity}"
        )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Part code must be unique!'),
    ]