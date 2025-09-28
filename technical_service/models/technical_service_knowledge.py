# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TechnicalServiceKnowledgeBase(models.Model):
    _name = 'technical.service.knowledge.base'
    _description = 'Technical Service Knowledge Base'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(string='Title', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    category_id = fields.Many2one('technical.service.knowledge.category', string='Category')
    tags = fields.Char(string='Tags', help='Comma-separated tags for searching')

    problem_description = fields.Text(string='Problem Description', required=True)
    solution = fields.Html(string='Solution', required=True)

    # Related fields
    related_assets = fields.Many2many(
        'maintenance.equipment',
        'knowledge_asset_rel',
        'knowledge_id',
        'asset_id',
        string='Related Assets'
    )
    related_requests = fields.Many2many(
        'maintenance.request',
        'knowledge_request_rel',
        'knowledge_id',
        'request_id',
        string='Related Requests'
    )

    # Additional information
    symptoms = fields.Text(string='Symptoms')
    root_cause = fields.Text(string='Root Cause')
    prevention = fields.Text(string='Prevention Tips')

    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    # Statistics
    views_count = fields.Integer(string='Views', default=0)
    helpful_count = fields.Integer(string='Marked as Helpful', default=0)

    # Publishing
    is_published = fields.Boolean(string='Published', default=False)
    author_id = fields.Many2one('res.users', string='Author', default=lambda self: self.env.user)
    publish_date = fields.Date(string='Publish Date')

    active = fields.Boolean(string='Active', default=True)

    def action_publish(self):
        self.write({
            'is_published': True,
            'publish_date': fields.Date.today()
        })

    def action_unpublish(self):
        self.is_published = False

    def action_increment_views(self):
        self.views_count += 1

    def action_mark_helpful(self):
        self.helpful_count += 1


class TechnicalServiceKnowledgeCategory(models.Model):
    _name = 'technical.service.knowledge.category'
    _description = 'Knowledge Base Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    parent_id = fields.Many2one('technical.service.knowledge.category', string='Parent Category')
    child_ids = fields.One2many('technical.service.knowledge.category', 'parent_id', string='Child Categories')

    description = fields.Text(string='Description')
    icon = fields.Char(string='Icon', help='Font Awesome icon class')
    color = fields.Integer(string='Color Index')

    article_count = fields.Integer(string='Articles', compute='_compute_article_count')

    @api.depends()
    def _compute_article_count(self):
        for category in self:
            category.article_count = self.env['technical.service.knowledge.base'].search_count([
                ('category_id', '=', category.id)
            ])