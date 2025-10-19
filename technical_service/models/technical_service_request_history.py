# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

class TechnicalServiceRequestHistory(models.Model):
    """
    Service Request History Tracking
    Purpose: Track all events and changes in service request lifecycle

    This model provides a complete audit trail for service requests including:
    - Stage transitions
    - Assignment changes
    - Work order events
    - Approval/rejection decisions
    - Comments and notes

    Reference: Task 07 - Business Logic Implementation
    """
    _name = 'technical_service.request.history'
    _description = 'Service Request History'
    _order = 'timestamp desc'
    _rec_name = 'event_type'

    # ============================================
    # CORE FIELDS
    # ============================================

    request_id = fields.Many2one(
        'maintenance.request',
        string='Service Request',
        required=True,
        ondelete='cascade',
        index=True,
        help='Related service request'
    )

    timestamp = fields.Datetime(
        string='Timestamp',
        default=fields.Datetime.now,
        required=True,
        index=True,
        help='When this event occurred'
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True,
        help='User who triggered this event'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        related='user_id.employee_id',
        store=True,
        readonly=True,
        help='Employee record of the user'
    )

    # ============================================
    # EVENT CATEGORIZATION
    # ============================================

    event_type = fields.Selection([
        ('stage_change', 'Stage Değişikliği'),
        ('assignment', 'Atama'),
        ('work_order', 'İş Emri'),
        ('comment', 'Yorum'),
        ('approval', 'Onay/Red'),
        ('cancellation', 'İptal'),
        ('hold', 'Bekletme'),
        ('field_change', 'Alan Değişikliği'),
    ], string='Event Type', required=True, index=True)

    # ============================================
    # STAGE CHANGE TRACKING
    # ============================================

    old_stage_id = fields.Many2one(
        'maintenance.stage',
        string='Old Stage',
        help='Previous stage (null if this is creation)'
    )

    new_stage_id = fields.Many2one(
        'maintenance.stage',
        string='New Stage',
        help='New stage after transition'
    )

    stage_change_duration = fields.Float(
        string='Duration in Previous Stage (Hours)',
        compute='_compute_stage_duration',
        store=True,
        help='How long the request was in the previous stage'
    )

    # ============================================
    # ASSIGNMENT TRACKING
    # ============================================

    old_team_id = fields.Many2one(
        'maintenance.team',
        string='Old Team',
        help='Previous assigned team'
    )

    new_team_id = fields.Many2one(
        'maintenance.team',
        string='New Team',
        help='Newly assigned team'
    )

    old_technician_id = fields.Many2one(
        'res.users',
        string='Old Technician',
        help='Previous assigned technician'
    )

    new_technician_id = fields.Many2one(
        'res.users',
        string='New Technician',
        help='Newly assigned technician'
    )

    # ============================================
    # WORK ORDER EVENTS
    # ============================================

    work_order_id = fields.Many2one(
        'technical_service.work_order',
        string='Work Order',
        help='Related work order (if applicable)'
    )

    work_order_status = fields.Char(
        string='Work Order Status',
        help='Status of work order at time of event'
    )

    # ============================================
    # APPROVAL/REJECTION
    # ============================================

    approval_status = fields.Selection([
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
        ('cancelled', 'İptal Edildi'),
    ], string='Approval Status')

    # ============================================
    # NOTES AND REASONS
    # ============================================

    note = fields.Text(
        string='Not/Açıklama',
        help='Additional notes or description of the event'
    )

    reason = fields.Text(
        string='Sebep',
        help='Reason for hold/cancel/reject actions'
    )

    # ============================================
    # METADATA
    # ============================================

    is_automatic = fields.Boolean(
        string='Automatic',
        default=False,
        help='True if this event was triggered automatically by the system'
    )

    # Computed display field for better readability
    description = fields.Html(
        string='Description',
        compute='_compute_description',
        store=True,
        help='Human-readable description of this history entry'
    )

    # ============================================
    # COMPUTED METHODS
    # ============================================

    @api.depends('old_stage_id', 'new_stage_id', 'timestamp')
    def _compute_stage_duration(self):
        """Calculate how long the request was in the previous stage"""
        for record in self:
            if record.event_type == 'stage_change' and record.old_stage_id:
                # Find previous stage change to this stage
                previous_entry = self.search([
                    ('request_id', '=', record.request_id.id),
                    ('event_type', '=', 'stage_change'),
                    ('new_stage_id', '=', record.old_stage_id.id),
                    ('timestamp', '<', record.timestamp),
                ], order='timestamp desc', limit=1)

                if previous_entry:
                    delta = record.timestamp - previous_entry.timestamp
                    record.stage_change_duration = delta.total_seconds() / 3600.0
                else:
                    record.stage_change_duration = 0.0
            else:
                record.stage_change_duration = 0.0

    @api.depends('event_type', 'old_stage_id', 'new_stage_id', 'old_team_id',
                 'new_team_id', 'approval_status', 'work_order_id', 'user_id')
    def _compute_description(self):
        """Generate human-readable description of the history event"""
        for record in self:
            desc = []

            if record.event_type == 'stage_change':
                old = record.old_stage_id.name if record.old_stage_id else 'Yok'
                new = record.new_stage_id.name if record.new_stage_id else 'Yok'
                desc.append(f"<b>Stage:</b> {old} → {new}")
                if record.stage_change_duration > 0:
                    desc.append(f"<br/><b>Önceki stage'de geçen süre:</b> {record.stage_change_duration:.2f} saat")

            elif record.event_type == 'assignment':
                if record.new_team_id:
                    old_team = record.old_team_id.name if record.old_team_id else 'Yok'
                    desc.append(f"<b>Ekip:</b> {old_team} → {record.new_team_id.name}")
                if record.new_technician_id:
                    old_tech = record.old_technician_id.name if record.old_technician_id else 'Yok'
                    desc.append(f"<b>Teknisyen:</b> {old_tech} → {record.new_technician_id.name}")

            elif record.event_type == 'work_order':
                if record.work_order_id:
                    desc.append(f"<b>İş Emri:</b> {record.work_order_id.name}")
                    if record.work_order_status:
                        desc.append(f" - {record.work_order_status}")

            elif record.event_type == 'approval':
                if record.approval_status == 'approved':
                    desc.append("<b>Durum:</b> Talep onaylandı ✓")
                elif record.approval_status == 'rejected':
                    desc.append("<b>Durum:</b> Talep reddedildi ✗")
                elif record.approval_status == 'cancelled':
                    desc.append("<b>Durum:</b> Talep iptal edildi")

            elif record.event_type == 'cancellation':
                desc.append("<b>İptal işlemi</b>")
                if record.reason:
                    desc.append(f"<br/><b>Sebep:</b> {record.reason}")

            elif record.event_type == 'hold':
                desc.append("<b>Talep bekletmeye alındı</b>")
                if record.reason:
                    desc.append(f"<br/><b>Sebep:</b> {record.reason}")

            elif record.event_type == 'comment':
                desc.append("<b>Yorum eklendi</b>")

            elif record.event_type == 'field_change':
                desc.append("<b>Alan değişikliği</b>")

            # Add user info
            if record.user_id:
                desc.append(f"<br/><b>Kullanıcı:</b> {record.user_id.name}")

            # Add notes if available
            if record.note:
                desc.append(f"<br/><i>{record.note}</i>")

            # Add automatic flag
            if record.is_automatic:
                desc.append("<br/><span style='color: gray;'>(Otomatik)</span>")

            record.description = "<br/>".join(desc) if desc else "Bilgi yok"

    # ============================================
    # HELPER METHODS (to be called from request model)
    # ============================================

    @api.model
    def log_stage_change(self, request, old_stage, new_stage, reason=None, is_auto=False):
        """
        Helper method to log stage changes

        Args:
            request: maintenance.request record
            old_stage: Previous maintenance.stage record (can be False)
            new_stage: New maintenance.stage record
            reason: Optional reason for the change
            is_auto: Boolean indicating if this was automatic

        Returns:
            Created history record
        """
        return self.create({
            'request_id': request.id,
            'event_type': 'stage_change',
            'old_stage_id': old_stage.id if old_stage else False,
            'new_stage_id': new_stage.id,
            'note': reason,
            'is_automatic': is_auto,
        })

    @api.model
    def log_assignment(self, request, old_team, new_team, old_tech, new_tech, note=None):
        """
        Helper method to log assignment changes

        Args:
            request: maintenance.request record
            old_team: Previous team (can be False)
            new_team: New team (can be False)
            old_tech: Previous technician (can be False)
            new_tech: New technician (can be False)
            note: Optional note

        Returns:
            Created history record(s)
        """
        vals = {
            'request_id': request.id,
            'event_type': 'assignment',
            'note': note,
            'is_automatic': False,
        }

        if old_team != new_team:
            vals['old_team_id'] = old_team.id if old_team else False
            vals['new_team_id'] = new_team.id if new_team else False

        if old_tech != new_tech:
            vals['old_technician_id'] = old_tech.id if old_tech else False
            vals['new_technician_id'] = new_tech.id if new_tech else False

        return self.create(vals)

    @api.model
    def log_work_order_event(self, request, work_order, status_text, note=None):
        """
        Helper method to log work order events

        Args:
            request: maintenance.request record
            work_order: technical_service.work_order record
            status_text: Text description of status (e.g., 'created', 'started', 'completed')
            note: Optional note

        Returns:
            Created history record
        """
        return self.create({
            'request_id': request.id,
            'event_type': 'work_order',
            'work_order_id': work_order.id,
            'work_order_status': status_text,
            'note': note,
            'is_automatic': False,
        })

    @api.model
    def log_approval(self, request, status, reason=None):
        """
        Helper method to log approval/rejection/cancellation

        Args:
            request: maintenance.request record
            status: 'approved', 'rejected', or 'cancelled'
            reason: Reason for rejection/cancellation

        Returns:
            Created history record
        """
        return self.create({
            'request_id': request.id,
            'event_type': 'approval',
            'approval_status': status,
            'reason': reason,
            'is_automatic': False,
        })

    @api.model
    def log_hold(self, request, reason):
        """
        Helper method to log hold events

        Args:
            request: maintenance.request record
            reason: Reason for putting on hold

        Returns:
            Created history record
        """
        return self.create({
            'request_id': request.id,
            'event_type': 'hold',
            'reason': reason,
            'is_automatic': False,
        })
