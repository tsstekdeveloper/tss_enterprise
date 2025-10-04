# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TechnicalServiceOrganization(models.Model):
    """
    Technical Service Organization Structure
    ========================================
    HR'dan bağımsız teknik ekip hiyerarşisi yönetimi

    Bu model technical_service module'üne ekleniyor çünkü:
    - Business entity ve veri modeli
    - İş mantığı ve hesaplamalar içeriyor
    - Presentation layer sadece görünüm yapacak
    """
    _name = 'technical_service.organization'
    _description = 'Technical Service Organization Structure'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'parent_left'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Temel Alanlar
    name = fields.Char(
        string='Pozisyon Adı',
        required=True,
        tracking=True,
        help='Bu pozisyonun adı (örn: IT Müdürü, Network Takım Lideri)'
    )

    complete_name = fields.Char(
        string='Tam Pozisyon',
        compute='_compute_complete_name',
        recursive=True,
        store=True,
        help='Hiyerarşik tam pozisyon adı'
    )

    active = fields.Boolean(
        string='Aktif',
        default=True,
        tracking=True
    )

    # Kullanıcı İlişkisi
    user_id = fields.Many2one(
        'res.users',
        string='Kullanıcı',
        tracking=True,
        help='Bu pozisyona atanan kullanıcı'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Çalışan',
        compute='_compute_employee_id',
        store=True,
        help='İlişkili HR çalışan kaydı'
    )

    # Hiyerarşi
    parent_id = fields.Many2one(
        'technical_service.organization',
        string='Üst Pozisyon',
        index=True,
        tracking=True,
        ondelete='cascade',
        help='Hiyerarşide üst pozisyon'
    )

    parent_path = fields.Char(index=True)
    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)

    child_ids = fields.One2many(
        'technical_service.organization',
        'parent_id',
        string='Alt Pozisyonlar',
        help='Bu pozisyona bağlı alt pozisyonlar'
    )

    child_count = fields.Integer(
        string='Alt Pozisyon Sayısı',
        compute='_compute_child_count'
    )

    # Organizasyon Tipleri
    organization_type = fields.Selection([
        ('cto', 'CTO/Teknik Direktör'),
        ('department_manager', 'Birim Yöneticisi'),
        ('team_leader', 'Takım Lideri'),
        ('senior_technician', 'Kıdemli Teknisyen'),
        ('technician', 'Teknisyen'),
        ('dispatcher', 'Dispatcher'),
        ('location_manager', 'Lokasyon Yöneticisi'),
        ('inventory_manager', 'Envanter Yöneticisi'),
    ], string='Organizasyon Tipi',
       required=True,
       tracking=True,
       help='Bu pozisyonun organizasyondaki rolü')

    department_type = fields.Selection([
        ('it', 'Bilgi İşlem'),
        ('facility', 'Tesis Yönetimi'),
        ('maintenance', 'Bakım Onarım'),
        ('support', 'Destek Hizmetleri'),
        ('housekeeping', 'Temizlik Hizmetleri')
    ], string='Birim',
       tracking=True,
       help='Bu pozisyonun bağlı olduğu birim')

    # İlişkiler
    location_ids = fields.Many2many(
        'technical_service.campus',
        string='Sorumlu Lokasyonlar',
        help='Bu pozisyonun sorumlu olduğu lokasyonlar'
    )

    team_ids = fields.One2many(
        'maintenance.team',
        'technical_org_id',
        string='Yönetilen Takımlar',
        help='Bu pozisyon tarafından yönetilen takımlar'
    )

    # İstatistikler
    subordinate_count = fields.Integer(
        string='Ast Sayısı',
        compute='_compute_subordinate_count',
        help='Bu pozisyonun altındaki toplam kişi sayısı'
    )

    # ========== Compute Methods ==========

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = '%s / %s' % (record.parent_id.complete_name, record.name)
            else:
                record.complete_name = record.name

    @api.depends('user_id')
    def _compute_employee_id(self):
        for record in self:
            if record.user_id:
                record.employee_id = self.env['hr.employee'].search([
                    ('user_id', '=', record.user_id.id)
                ], limit=1)
            else:
                record.employee_id = False

    @api.depends('child_ids')
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_ids)

    def _compute_subordinate_count(self):
        """Alt pozisyonlardaki toplam kullanıcı sayısı"""
        for record in self:
            subordinates = self.search([
                ('parent_left', '>', record.parent_left),
                ('parent_right', '<', record.parent_right)
            ])
            record.subordinate_count = len(subordinates.filtered('user_id'))

    # ========== Business Logic Methods ==========

    def get_subordinate_users(self):
        """Alt pozisyonlardaki tüm kullanıcıları getir"""
        self.ensure_one()
        subordinates = self.search([
            ('parent_left', '>', self.parent_left),
            ('parent_right', '<', self.parent_right),
            ('user_id', '!=', False)
        ])
        return subordinates.mapped('user_id')

    def get_subordinate_user_ids(self):
        """Alt pozisyonlardaki tüm kullanıcı ID'lerini getir (domain için)"""
        self.ensure_one()
        return self.get_subordinate_users().ids

    def get_managed_teams(self):
        """Bu pozisyon ve altındaki pozisyonlar tarafından yönetilen takımları getir"""
        self.ensure_one()
        subordinates = self.search([
            ('parent_left', '>=', self.parent_left),
            ('parent_right', '<=', self.parent_right)
        ])
        return subordinates.mapped('team_ids')

    def get_managed_team_ids(self):
        """Yönetilen takım ID'lerini getir (domain için)"""
        self.ensure_one()
        return self.get_managed_teams().ids

    def get_department_positions(self):
        """Aynı birimdeki tüm pozisyonları getir"""
        self.ensure_one()
        if not self.department_type:
            return self.browse()

        return self.search([
            ('department_type', '=', self.department_type)
        ])

    def get_parent_chain(self):
        """Üst pozisyon zincirini getir (root'a kadar)"""
        self.ensure_one()
        chain = self.browse()
        current = self
        while current:
            chain += current
            current = current.parent_id
        return chain

    # ========== Constraints ==========

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Döngüsel hiyerarşi oluşturamazsınız!'))

    @api.constrains('user_id')
    def _check_user_unique(self):
        for record in self:
            if record.user_id:
                duplicate = self.search([
                    ('user_id', '=', record.user_id.id),
                    ('id', '!=', record.id),
                    ('active', '=', True)
                ])
                if duplicate:
                    raise ValidationError(_(
                        'Bu kullanıcı zaten %s pozisyonuna atanmış!'
                    ) % duplicate.complete_name)

    @api.constrains('organization_type', 'parent_id')
    def _check_organization_hierarchy(self):
        """Organizasyon tipi hiyerarşi kurallarını kontrol et"""
        for record in self:
            if not record.parent_id:
                # Root pozisyon sadece CTO olabilir
                if record.organization_type != 'cto':
                    raise ValidationError(_('En üst pozisyon sadece CTO/Teknik Direktör olabilir!'))
            else:
                # Hiyerarşi kuralları
                parent_type = record.parent_id.organization_type
                child_type = record.organization_type

                # CTO altında sadece department_manager olabilir
                if parent_type == 'cto' and child_type not in ['department_manager', 'dispatcher', 'inventory_manager']:
                    raise ValidationError(_('CTO altında sadece Birim Yöneticisi, Dispatcher veya Envanter Yöneticisi olabilir!'))

                # Department Manager altında team_leader olmalı
                if parent_type == 'department_manager' and child_type not in ['team_leader', 'location_manager']:
                    raise ValidationError(_('Birim Yöneticisi altında sadece Takım Lideri veya Lokasyon Yöneticisi olabilir!'))

                # Team Leader altında teknisyenler olmalı
                if parent_type == 'team_leader' and child_type not in ['senior_technician', 'technician']:
                    raise ValidationError(_('Takım Lideri altında sadece teknisyenler olabilir!'))

    # ========== Actions ==========

    def action_view_subordinates(self):
        """Alt pozisyonları görüntüle"""
        self.ensure_one()
        action = self.env.ref('technical_service.action_technical_service_organization').read()[0]
        action['domain'] = [('parent_id', '=', self.id)]
        action['context'] = {'default_parent_id': self.id}
        return action

    def action_view_teams(self):
        """Yönetilen takımları görüntüle"""
        self.ensure_one()
        action = self.env.ref('maintenance.maintenance_team_action').read()[0]
        action['domain'] = [('technical_org_id', '=', self.id)]
        action['context'] = {'default_technical_org_id': self.id}
        return action

    # ========== Name Methods ==========

    @api.model
    def name_create(self, name):
        """Override to set default organization_type"""
        if self._context.get('default_organization_type'):
            return super().name_create(name)
        else:
            # Default olarak technician oluştur
            return self.create({'name': name, 'organization_type': 'technician'}).name_get()[0]

    def name_get(self):
        """Pozisyon adını kullanıcı bilgisi ile birlikte göster"""
        result = []
        for record in self:
            if record.user_id:
                name = '%s (%s)' % (record.name, record.user_id.name)
            else:
                name = record.name
            result.append((record.id, name))
        return result


class MaintenanceTeam(models.Model):
    """Maintenance Team'e technical organization ilişkisi ekleme"""
    _inherit = 'maintenance.team'

    technical_org_id = fields.Many2one(
        'technical_service.organization',
        string='Teknik Organizasyon',
        domain="[('organization_type', 'in', ['team_leader', 'department_manager'])]",
        help='Bu takımı yöneten teknik organizasyon pozisyonu'
    )


class MaintenanceRequest(models.Model):
    """Maintenance Request'e technical organization ilişkisi ekleme"""
    _inherit = 'maintenance.request'

    technical_org_id = fields.Many2one(
        'technical_service.organization',
        string='Atanan Organizasyon',
        compute='_compute_technical_org_id',
        store=True,
        help='Bu talebin atandığı teknik organizasyon pozisyonu'
    )

    @api.depends('technician_user_id', 'maintenance_team_id')
    def _compute_technical_org_id(self):
        """Teknisyen veya takıma göre organizasyon pozisyonunu bul"""
        for record in self:
            org_id = False

            # Önce teknisyenden bul
            if record.technician_user_id:
                org = self.env['technical_service.organization'].search([
                    ('user_id', '=', record.technician_user_id.id),
                    ('active', '=', True)
                ], limit=1)
                if org:
                    org_id = org.id

            # Teknisyen yoksa takımdan bul
            if not org_id and record.maintenance_team_id:
                if record.maintenance_team_id.technical_org_id:
                    org_id = record.maintenance_team_id.technical_org_id.id

            record.technical_org_id = org_id


class ResUsers(models.Model):
    """Res Users'a technical organization ve rol yönetimi ekleme"""
    _inherit = 'res.users'

    technical_org_id = fields.Many2one(
        'technical_service.organization',
        string='Teknik Pozisyon',
        compute='_compute_technical_org_id',
        store=True,
        help='Kullanıcının teknik organizasyondaki pozisyonu'
    )

    technical_org_type = fields.Selection(
        related='technical_org_id.organization_type',
        string='Teknik Rol',
        readonly=True,
        help='Kullanıcının teknik organizasyondaki rolü'
    )

    # Ana technical role field - 11 rolden biri
    technical_role = fields.Selection([
        ('USR', 'Standard User'),
        ('HRM', 'HR Manager'),
        ('CTO', 'CTO/Teknik Direktör'),
        ('DPM', 'Department Manager'),
        ('TML', 'Team Leader'),
        ('SRT', 'Senior Technician'),
        ('TCH', 'Technician'),
        ('DSP', 'Dispatcher'),
        ('LCM', 'Location Manager'),
        ('INV', 'Inventory Manager'),
        ('RPT', 'Reporting Officer'),
    ], string='Sistem Rolü',
       compute='_compute_technical_role',
       store=True,
       help='Kullanıcının sistemdeki ana rolü (otomatik belirlenir)')

    @api.depends('partner_id')  # Trigger compute when user is created/updated
    def _compute_technical_org_id(self):
        """Kullanıcının teknik organizasyon pozisyonunu bul"""
        TechOrg = self.env['technical_service.organization']
        for user in self:
            org = TechOrg.search([
                ('user_id', '=', user.id),
                ('active', '=', True)
            ], limit=1)
            user.technical_org_id = org.id if org else False

    @api.depends('employee_ids', 'technical_org_id', 'groups_id')
    def _compute_technical_role(self):
        """Kullanıcının sistem rolünü otomatik belirle"""
        for user in self:
            role = 'USR'  # Default role

            # 1. CTO kontrolü - organization_type'dan
            if user.technical_org_id and user.technical_org_id.organization_type == 'cto':
                role = 'CTO'

            # 2. Department Manager kontrolü
            elif user.technical_org_id and user.technical_org_id.organization_type == 'department_manager':
                role = 'DPM'

            # 3. Ekip bazlı roller - technical_service.team.member üzerinden kontrol
            else:
                # Kullanıcının üye olduğu takımları ve rollerini bul
                team_members = self.env['technical_service.team.member'].search([
                    ('user_id', '=', user.id)
                ])

                for member in team_members:
                    team = member.team_id

                    # Takım lideri kontrolü
                    if member.member_role == 'team_leader':
                        role = 'TML'
                        break

                    # Ekip tipine göre özel roller
                    if team.team_type == 'dispatching':
                        role = 'DSP'
                    elif team.team_type == 'inventory':
                        role = 'INV'
                    elif team.team_type == 'location':
                        role = 'LCM'
                    # Normal ekiplerdeki roller
                    elif member.member_role == 'senior_technician':
                        role = 'SRT'
                    elif member.member_role == 'technician':
                        role = 'TCH'

            # 4. HR Manager kontrolü - employee'den
            if not role or role == 'USR':
                if user.employee_ids:
                    # HR Manager mı kontrolü
                    employee = user.employee_ids[0]
                    if employee.parent_id and employee.child_ids:
                        # Altında çalışanı varsa HR Manager
                        role = 'HRM'

            # 5. Reporting Officer kontrolü - özel grup üyeliği
            if user.has_group('technical_service_presentation.group_technical_reporting'):
                role = 'RPT'

            user.technical_role = role

    def get_technical_security_groups(self):
        """Kullanıcının rolüne göre security gruplarını getir"""
        self.ensure_one()

        group_mapping = {
            'USR': [],  # Base user, no extra groups
            'HRM': ['hr.group_hr_manager'],
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

        if self.technical_role:
            group_refs = group_mapping.get(self.technical_role, [])
            groups = self.env['res.groups']
            for ref in group_refs:
                try:
                    group = self.env.ref(ref)
                    groups |= group
                except:
                    pass
            return groups
        return self.env['res.groups']