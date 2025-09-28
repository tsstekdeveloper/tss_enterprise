# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TechnicalServicePriority(models.Model):
    _name = 'technical.service.priority'
    _description = 'Technical Service Priority'
    _order = 'level'
    _rec_name = 'name'

    name = fields.Char(string='Priority Name', required=True)
    level = fields.Integer(string='Priority Level', required=True, default=1)
    color = fields.Integer(string='Color Index', default=0)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    # SLA Configuration
    response_hours = fields.Float(string='Response Time (hours)', default=4.0)
    resolution_hours = fields.Float(string='Resolution Time (hours)', default=24.0)

    _sql_constraints = [
        ('level_unique', 'UNIQUE(level)', 'Priority level must be unique!'),
        ('name_unique', 'UNIQUE(name)', 'Priority name must be unique!'),
    ]