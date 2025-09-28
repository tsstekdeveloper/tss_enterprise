# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TechnicalServiceSatisfactionSurvey(models.Model):
    _name = 'technical.service.satisfaction.survey'
    _description = 'Technical Service Customer Satisfaction Survey'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Survey Title', required=True)
    service_request_id = fields.Many2one('maintenance.request', string='Service Request')
    work_order_id = fields.Many2one('technical_service.work_order', string='Work Order')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    survey_date = fields.Date(string='Survey Date', default=fields.Date.today)

    # Rating Questions (1-5 scale)
    overall_rating = fields.Selection([
        ('1', 'Very Dissatisfied'),
        ('2', 'Dissatisfied'),
        ('3', 'Neutral'),
        ('4', 'Satisfied'),
        ('5', 'Very Satisfied')
    ], string='Overall Satisfaction', required=True)

    response_time_rating = fields.Selection([
        ('1', '1 - Very Poor'),
        ('2', '2 - Poor'),
        ('3', '3 - Average'),
        ('4', '4 - Good'),
        ('5', '5 - Excellent')
    ], string='Response Time')

    technician_professionalism = fields.Selection([
        ('1', '1 - Very Poor'),
        ('2', '2 - Poor'),
        ('3', '3 - Average'),
        ('4', '4 - Good'),
        ('5', '5 - Excellent')
    ], string='Technician Professionalism')

    quality_of_work = fields.Selection([
        ('1', '1 - Very Poor'),
        ('2', '2 - Poor'),
        ('3', '3 - Average'),
        ('4', '4 - Good'),
        ('5', '5 - Excellent')
    ], string='Quality of Work')

    communication_rating = fields.Selection([
        ('1', '1 - Very Poor'),
        ('2', '2 - Poor'),
        ('3', '3 - Average'),
        ('4', '4 - Good'),
        ('5', '5 - Excellent')
    ], string='Communication')

    # Yes/No Questions
    would_recommend = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('maybe', 'Maybe')
    ], string='Would you recommend our service?')

    issue_resolved = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('partially', 'Partially')
    ], string='Was your issue resolved?')

    # Open-ended feedback
    positive_feedback = fields.Text(string='What did you like about our service?')
    improvement_suggestions = fields.Text(string='How can we improve our service?')
    additional_comments = fields.Text(string='Additional Comments')

    # Computed fields
    average_rating = fields.Float(string='Average Rating', compute='_compute_average_rating', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)

    @api.depends('overall_rating', 'response_time_rating', 'technician_professionalism',
                 'quality_of_work', 'communication_rating')
    def _compute_average_rating(self):
        for record in self:
            ratings = []
            for field in ['overall_rating', 'response_time_rating', 'technician_professionalism',
                         'quality_of_work', 'communication_rating']:
                value = getattr(record, field)
                if value:
                    ratings.append(int(value))

            if ratings:
                record.average_rating = sum(ratings) / len(ratings)
            else:
                record.average_rating = 0.0

    def action_send_survey(self):
        self.state = 'sent'
        # Here you would implement email sending logic

    def action_complete_survey(self):
        self.state = 'completed'