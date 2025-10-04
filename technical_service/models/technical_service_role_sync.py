# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResUsersRoleSync(models.Model):
    """
    Automatic Role and Security Group Synchronization
    =================================================
    This model extends res.users to automatically sync technical roles
    with security groups when roles are computed or changed.
    """
    _inherit = 'res.users'

    # Auto-sync flag
    auto_sync_groups = fields.Boolean(
        string='Auto-sync Security Groups',
        default=True,
        help='Automatically sync security groups based on technical role'
    )

    @api.model
    def create(self, vals):
        """Override create to sync groups after user creation"""
        user = super().create(vals)
        if user.auto_sync_groups:
            user._sync_technical_groups()
        return user

    def write(self, vals):
        """Override write to sync groups when role changes"""
        res = super().write(vals)
        if 'technical_role' in vals or 'auto_sync_groups' in vals:
            for user in self:
                if user.auto_sync_groups:
                    user._sync_technical_groups()
        return res

    def _sync_technical_groups(self):
        """Sync user's security groups based on technical role"""
        for user in self:
            if not user.technical_role:
                continue

            # Get the groups this user should have based on role
            role_groups = user._get_role_security_groups()

            # Get all technical service groups
            all_tech_groups = self._get_all_technical_groups()

            # Remove user from all technical groups first
            user.groups_id = [(3, g.id, 0) for g in all_tech_groups]

            # Add user to appropriate groups based on role
            if role_groups:
                user.groups_id = [(4, g.id, 0) for g in role_groups]
                _logger.info(f"Synced groups for user {user.name} with role {user.technical_role}")

    def _get_role_security_groups(self):
        """Get security groups based on user's technical role"""
        self.ensure_one()

        # Role to group mapping
        role_group_mapping = {
            'USR': ['base.group_user'],  # Standard user - base only
            'HRM': ['hr.group_hr_manager'],  # HR Manager
            'CTO': ['technical_service_presentation.group_technical_cto'],
            'DPM': ['technical_service_presentation.group_technical_department_manager'],
            'TML': ['technical_service_presentation.group_technical_team_leader'],
            'SRT': ['technical_service_presentation.group_technical_senior_technician'],
            'TCH': ['technical_service_presentation.group_technical_technician'],
            'DSP': ['technical_service_presentation.group_technical_dispatcher'],
            'LCM': ['technical_service_presentation.group_technical_location_manager'],
            'INV': ['technical_service_presentation.group_technical_inventory_manager'],
            'RPT': ['technical_service_presentation.group_technical_reporting'],
        }

        groups = self.env['res.groups']
        group_refs = role_group_mapping.get(self.technical_role, [])

        for ref in group_refs:
            try:
                group = self.env.ref(ref)
                groups |= group
            except ValueError:
                _logger.warning(f"Security group {ref} not found")

        # Add implied groups based on hierarchy
        if self.technical_role in ['CTO', 'DPM', 'TML']:
            # Managers should have user access too
            try:
                groups |= self.env.ref('base.group_user')
            except:
                pass

        return groups

    def _get_all_technical_groups(self):
        """Get all technical service related security groups"""
        group_refs = [
            'technical_service_presentation.group_technical_cto',
            'technical_service_presentation.group_technical_department_manager',
            'technical_service_presentation.group_technical_team_leader',
            'technical_service_presentation.group_technical_senior_technician',
            'technical_service_presentation.group_technical_technician',
            'technical_service_presentation.group_technical_dispatcher',
            'technical_service_presentation.group_technical_location_manager',
            'technical_service_presentation.group_technical_inventory_manager',
            'technical_service_presentation.group_technical_reporting',
        ]

        groups = self.env['res.groups']
        for ref in group_refs:
            try:
                groups |= self.env.ref(ref)
            except:
                pass

        return groups

    def action_sync_all_users(self):
        """Action to sync all users' groups based on their roles"""
        users = self.search([('technical_role', '!=', False)])
        users._sync_technical_groups()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%d users synchronized') % len(users),
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def sync_all_user_roles(self):
        """Cron job to sync all user roles periodically"""
        users = self.search([])
        # First compute all roles
        users._compute_technical_role()
        # Then sync groups
        users.filtered('auto_sync_groups')._sync_technical_groups()
        _logger.info(f"Synced roles and groups for {len(users)} users")