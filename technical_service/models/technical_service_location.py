# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TechnicalServiceCampus(models.Model):
    """Campus/Site definition for multi-location management"""
    _name = 'technical_service.campus'
    _description = 'Campus/Site'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Campus Name', required=True, tracking=True)
    code = fields.Char(string='Campus Code', tracking=True)

    # Location details
    address = fields.Char(string='Address')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    zip = fields.Char(string='ZIP')

    # Contact information
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    manager_id = fields.Many2one('hr.employee', string='Campus Manager')

    # Related records
    building_ids = fields.One2many('technical_service.building', 'campus_id', string='Buildings')
    building_count = fields.Integer(string='Building Count', compute='_compute_building_count')

    # Additional information
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    @api.depends('building_ids')
    def _compute_building_count(self):
        for record in self:
            record.building_count = len(record.building_ids)


class TechnicalServiceBuilding(models.Model):
    """Building definition within a campus"""
    _name = 'technical_service.building'
    _description = 'Building'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Building Name', required=True, tracking=True)
    code = fields.Char(string='Building Code', tracking=True)
    campus_id = fields.Many2one('technical_service.campus', string='Campus', required=True)

    # Building details
    building_type = fields.Selection([
        ('office', 'Office Building'),
        ('warehouse', 'Warehouse'),
        ('production', 'Production Facility'),
        ('residential', 'Residential'),
        ('mixed', 'Mixed Use'),
        ('other', 'Other'),
    ], string='Building Type', default='office')

    floor_count = fields.Integer(string='Number of Floors')
    floor_list = fields.Html(string='Floor List')
    total_area = fields.Float(string='Total Area (m²)')

    # Management
    manager_id = fields.Many2one('hr.employee', string='Building Manager')
    maintenance_team_id = fields.Many2one('maintenance.team', string='Maintenance Team')

    # Additional information
    notes = fields.Html(string='Notes')
    active = fields.Boolean(default=True)

    @api.constrains('floor_count')
    def _check_floor_count(self):
        for record in self:
            if record.floor_count and record.floor_count < 0:
                raise ValidationError(_('Floor count must be positive'))