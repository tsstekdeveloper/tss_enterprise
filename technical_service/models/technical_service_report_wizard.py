# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class TechnicalServiceReportWizard(models.TransientModel):
    _name = 'technical.service.report.wizard'
    _description = 'Technical Service Report Wizard'

    report_type = fields.Selection([
        ('service_summary', 'Service Summary Report'),
        ('team_performance', 'Team Performance Report'),
        ('sla_compliance', 'SLA Compliance Report'),
        ('asset_history', 'Asset Service History'),
        ('customer_satisfaction', 'Customer Satisfaction Report'),
        ('inventory_status', 'Inventory Status Report'),
        ('preventive_maintenance', 'Preventive Maintenance Report')
    ], string='Report Type', required=True, default='service_summary')

    # Date filters
    date_from = fields.Date(string='From Date', required=True,
                           default=lambda self: fields.Date.today() - timedelta(days=30))
    date_to = fields.Date(string='To Date', required=True,
                         default=fields.Date.today)

    # Filter options
    team_id = fields.Many2one('maintenance.team', string='Team')
    customer_id = fields.Many2one('res.partner', string='Customer')
    asset_id = fields.Many2one('maintenance.equipment', string='Asset')
    request_state = fields.Selection([
        ('all', 'All'),
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Request Status', default='all')

    # Output options
    include_charts = fields.Boolean(string='Include Charts', default=True)
    include_details = fields.Boolean(string='Include Detailed Records', default=False)
    group_by = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('team', 'Team'),
        ('customer', 'Customer'),
        ('priority', 'Priority')
    ], string='Group By', default='month')

    def generate_report(self):
        """Generate the selected report"""
        self.ensure_one()

        # Build domain based on filters
        domain = []
        if self.date_from:
            domain.append(('create_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('create_date', '<=', self.date_to))
        if self.team_id:
            domain.append(('team_id', '=', self.team_id.id))
        if self.customer_id:
            domain.append(('customer_id', '=', self.customer_id.id))
        if self.request_state != 'all':
            domain.append(('state', '=', self.request_state))

        # Generate report based on type
        if self.report_type == 'service_summary':
            return self._generate_service_summary(domain)
        elif self.report_type == 'team_performance':
            return self._generate_team_performance(domain)
        elif self.report_type == 'sla_compliance':
            return self._generate_sla_compliance(domain)
        elif self.report_type == 'asset_history':
            return self._generate_asset_history()
        elif self.report_type == 'customer_satisfaction':
            return self._generate_satisfaction_report()
        elif self.report_type == 'inventory_status':
            return self._generate_inventory_report()
        elif self.report_type == 'preventive_maintenance':
            return self._generate_preventive_report()

    def _generate_service_summary(self, domain):
        """Generate service summary report"""
        requests = self.env['maintenance.request'].search(domain)

        # Calculate statistics
        total_requests = len(requests)
        completed_requests = len(requests.filtered(lambda r: r.state == 'completed'))
        avg_resolution_time = sum(requests.mapped('resolution_time')) / total_requests if total_requests else 0

        # You would typically return an action to open a report view
        # For now, we'll return a simple notification
        message = f"""
        Service Summary Report
        Period: {self.date_from} to {self.date_to}
        Total Requests: {total_requests}
        Completed: {completed_requests}
        Average Resolution Time: {avg_resolution_time:.2f} hours
        """

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Service Summary Report',
                'message': message,
                'sticky': True,
            }
        }

    def _generate_team_performance(self, domain):
        """Generate team performance report"""
        # Implementation for team performance report
        pass

    def _generate_sla_compliance(self, domain):
        """Generate SLA compliance report"""
        # Implementation for SLA compliance report
        pass

    def _generate_asset_history(self):
        """Generate asset service history report"""
        # Implementation for asset history report
        pass

    def _generate_satisfaction_report(self):
        """Generate customer satisfaction report"""
        # Implementation for satisfaction report
        pass

    def _generate_inventory_report(self):
        """Generate inventory status report"""
        # Implementation for inventory report
        pass

    def _generate_preventive_report(self):
        """Generate preventive maintenance report"""
        # Implementation for preventive maintenance report
        pass