# Teknik Talep Yönetimi - Menü Yapısı ve Yetkilendirme Planı

## 📋 Özet
Bu doküman, tüm teknik servis fonksiyonlarını tek çatı altında toplayacak "Teknik Talep Yönetimi" modülünün menü yapısını ve yetkilendirme sistemini planlamak için oluşturulmuştur.

## 🏗️ Modül Mimarisi - Security Layer Pattern (ÖNERİLEN)

### ✅ Seçilen Yaklaşım: İki Katmanlı Modül Yapısı

#### 1️⃣ **technical_service** (Core Business Logic Module)
**Sorumlulukları:**
- ✓ Tüm model tanımlamaları (fields, methods, computations)
- ✓ **technical_service.organization model** (YENİ EKLENECEK)
- ✓ Business logic ve iş kuralları
- ✓ Temel CRUD view'ları
- ✓ Workflow ve state yönetimi
- ✓ Raporlama altyapısı
- ✓ API ve integrations
- ✓ Data migrations
- ✓ Computed methods (get_subordinate_users, get_managed_teams, etc.)

**Bu modülde OLMAYACAK:**
- ✗ Karmaşık menü yapıları
- ✗ Rol bazlı erişim kuralları
- ✗ Özelleştirilmiş dashboard'lar
- ✗ Security groups tanımları

#### 2️⃣ **technical_service_presentation** (Security & Access Layer Module)
**Sorumlulukları:**
- ✓ Tüm security groups tanımlamaları (11 rol)
- ✓ Record rules (domain filtreleri)
- ✓ Menü yapısı ve hiyerarşi
- ✓ Rol bazlı dashboard'lar
- ✓ Özelleştirilmiş list/form view'lar (inherit only)
- ✓ Field-level access control (computed fields)
- ✓ Teknik organizasyon VIEW'ları (inherit)

**Bu modülde OLMAYACAK:**
- ✗ Yeni model tanımlamaları (sadece _inherit)
- ✗ Yeni stored field'lar (bunlar core module'e eklenir)
- ✗ Business logic değişiklikleri
- ✗ Model method'ları (compute hariç)

### 🎯 Bu Yaklaşımın Avantajları

1. **Separation of Concerns**: Business logic ile access control ayrı
2. **Modülerlik**: Security layer isteğe bağlı kurulabilir
3. **Bakım Kolaylığı**: Her modülün net sorumlulukları var
4. **Test Edilebilirlik**: Business logic bağımsız test edilebilir
5. **Esneklik**: Farklı kurumlar farklı security layer kullanabilir
6. **Migration Yok**: Data taşıma gerekmez

### ✨ Odoo'da Benzer Örnekler

Bu pattern Odoo'nun kendi modüllerinde de kullanılır:
- **sale** (core) → **sale_management** (menus/access)
- **account** (core) → **account_accountant** (full access)
- **stock** (core) → **stock_account** (accounting integration)
- **hr** (core) → **hr_attendance**, **hr_holidays** (specific features)

---

## 🏢 TEKNİK ORGANİZASYON YAPISI (İZOLE HİYERARŞİ)

### ⚠️ ÖNEMLİ: Model Yerleşimi
`technical_service.organization` modeli **CORE MODULE**'de (technical_service) tanımlanmalıdır çünkü:
- Bu bir business entity'dir (iş varlığı)
- Veri modeli ve iş mantığı içerir
- Presentation layer sadece görünüm ve erişim kontrolü yapmalıdır

### Core Module'e Eklenecek: technical_service.organization

#### A. Core Module (technical_service) - Model Tanımı:
```python
# /opt/odoo/custom-addons/technical_service/models/technical_service_organization.py
class TechnicalServiceOrganization(models.Model):
    _name = 'technical_service.organization'
    _description = 'Technical Service Organization Structure'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'

    # Temel alanlar
    name = fields.Char('Pozisyon Adı', required=True)
    complete_name = fields.Char('Tam Pozisyon', compute='_compute_complete_name', store=True)
    user_id = fields.Many2one('res.users', 'Kullanıcı')
    parent_id = fields.Many2one('technical_service.organization', 'Üst Pozisyon')
    child_ids = fields.One2many('technical_service.organization', 'parent_id', 'Alt Pozisyonlar')

    # Organizasyon tipleri
    organization_type = fields.Selection([
        ('cto', 'CTO/Teknik Direktör'),
        ('department_manager', 'Birim Yöneticisi'),
        ('team_leader', 'Takım Lideri'),
        ('senior_technician', 'Kıdemli Teknisyen'),
        ('technician', 'Teknisyen'),
        ('dispatcher', 'Dispatcher'),
        ('location_manager', 'Lokasyon Yöneticisi'),
        ('inventory_manager', 'Envanter Yöneticisi'),
    ], string='Organizasyon Tipi', required=True)

    department_type = fields.Selection([
        ('it', 'Bilgi İşlem'),
        ('facility', 'Tesis Yönetimi'),
        ('maintenance', 'Bakım Onarım'),
        ('support', 'Destek Hizmetleri'),
        ('housekeeping', 'Temizlik Hizmetleri')
    ], string='Birim')

    # İlişkiler
    location_ids = fields.Many2many('technical_service.campus', string='Sorumlu Lokasyonlar')
    team_ids = fields.One2many('maintenance.team', 'technical_org_id', string='Yönetilen Takımlar')

    # Business Logic Methods
    def get_subordinate_users(self):
        """Alt pozisyonlardaki tüm kullanıcıları getir"""
        # Business logic burada
        pass

    def get_managed_teams(self):
        """Yönetilen takımları getir"""
        # Business logic burada
        pass
```

#### B. Presentation Module - Sadece Görünüm ve Erişim:
```python
# /opt/odoo/custom-addons/technical_service_presentation/models/__init__.py
# BOŞ - Yeni model tanımı YOK!

# Sadece mevcut modelleri inherit edip, görünüm değişiklikleri yapabiliriz:
class MaintenanceRequestPresentation(models.Model):
    _inherit = 'maintenance.request'

    # Field-level access control için compute field'lar eklenebilir
    # Ama yeni stored field'lar CORE module'de tanımlanmalı
```

### Organizasyon Hiyerarşisi Örneği:
```
CTO/Teknik Direktör
├── Bilgi İşlem Müdürü
│   ├── Network Takım Lideri
│   │   ├── Kıdemli Network Teknisyeni
│   │   └── Network Teknisyenleri
│   └── Yazılım Destek Takım Lideri
│       └── Yazılım Destek Teknisyenleri
├── Tesis Yönetimi Müdürü
│   ├── Elektrik Takım Lideri
│   │   └── Elektrik Teknisyenleri
│   └── Mekanik Takım Lideri
│       └── Mekanik Teknisyenleri
├── Dispatcher (Talep Yönetimi)
└── Envanter Yöneticisi
```

---

## 👥 ROL TANIMLARI VE YETKİLENDİRME

### A. HR BAZLI ROLLER (Talep Açanlar)

#### 1. 👤 **Standart Kullanıcı (Standard User)**
- **Group ID**: `group_technical_service_user`
- **Kaynak**: HR Employee kayıtları
- **Temel Görev**: Talep oluşturan son kullanıcı
- **Yetkiler**:
  - Talep oluşturma
  - Kendi taleplerini görüntüleme
  - Talep durumunu takip etme
  - Yorum ekleme
- **Domain**: `[('create_uid', '=', user.id)]`
- **Inherits**: `base.group_user`

#### 2. 👔 **Departman Yöneticisi (HR Manager)**
- **Group ID**: `group_technical_service_hr_manager`
- **Kaynak**: HR hiyerarşisinden otomatik tespit (employee.parent_id)
- **Temel Görev**: HR'da yönetici konumunda olan kullanıcı
- **Yetkiler**:
  - Standart kullanıcı yetkileri
  - Altındaki çalışanların taleplerini görüntüleme
  - Altındaki çalışanlar için talep oluşturma
  - Departman performans raporları
- **Domain**:
  ```python
  ['|',
    ('create_uid', '=', user.id),
    ('employee_id.parent_id.user_id', '=', user.id)
  ]
  ```
- **Inherits**: `group_technical_service_user`

### B. TEKNİK ORGANİZASYON ROLLERİ (İzole Yapı)

#### 3. 🔑 **CTO/Teknik Direktör**
- **Group ID**: `group_technical_service_cto`
- **Kaynak**: Technical Organization (organization_type='cto')
- **Temel Görev**: Tüm teknik organizasyonun başı
- **Yetkiler**:
  - Tüm teknik operasyonları görüntüleme ve yönetme
  - Teknik organizasyon yapısını düzenleme
  - Birim yöneticilerini atama
  - Stratejik raporlar ve analizler
- **Domain**: `[(1, '=', 1)]` (Tüm kayıtlar)
- **Inherits**: `base.group_system`

#### 4. 🏭 **Birim Yöneticisi (Department Manager)**
- **Group ID**: `group_technical_service_department_manager`
- **Kaynak**: Technical Organization (organization_type='department_manager')
- **Temel Görev**: IT, Tesis, Bakım birimlerinin yöneticileri
- **Yetkiler**:
  - Kendi birimindeki tüm takımları yönetme
  - Takım liderlerini atama
  - Birim bazlı kaynak planlaması
  - SLA politikaları belirleme
  - Birim performans raporları
- **Domain**:
  ```python
  [('maintenance_team_id.department_type', '=',
    user.technical_org_id.department_type)]
  ```
- **Inherits**: `group_technical_service_user`

#### 5. 👷 **Takım Lideri (Team Leader)**
- **Group ID**: `group_technical_service_team_leader`
- **Kaynak**: Technical Organization (organization_type='team_leader')
- **Temel Görev**: Teknisyen ekiplerini yöneten kişiler
- **Yetkiler**:
  - Ekibindeki teknisyenleri yönetme
  - İş atama ve yeniden atama
  - Ekip vardiya planlaması
  - Günlük operasyon takibi
  - Ekip performans raporları
- **Domain**:
  ```python
  [('maintenance_team_id', 'in',
    user.technical_org_id.team_ids.ids)]
  ```
- **Inherits**: `group_technical_service_technician`

#### 6. 🔧 **Kıdemli Teknisyen (Senior Technician)**
- **Group ID**: `group_technical_service_senior_technician`
- **Kaynak**: Technical Organization (organization_type='senior_technician')
- **Temel Görev**: Deneyimli saha personeli
- **Yetkiler**:
  - Kompleks işleri çözme
  - Junior teknisyenlere mentorluk
  - Teknik dokümantasyon oluşturma
  - Önleyici bakım planlama
- **Domain**: `[('technician_user_id', '=', user.id)]`
- **Inherits**: `group_technical_service_technician`

#### 7. 🔨 **Teknisyen (Technician)**
- **Group ID**: `group_technical_service_technician`
- **Kaynak**: Technical Organization (organization_type='technician')
- **Temel Görev**: Saha personeli
- **Yetkiler**:
  - Kendisine atanan işleri görüntüleme
  - İş durumu güncelleme
  - Çalışma kayıtları girişi
  - Malzeme kullanımı kayıt
  - Fotoğraf/belge ekleme
- **Domain**: `[('technician_user_id', '=', user.id)]`
- **Inherits**: `group_technical_service_user`

#### 8. 📞 **Dispatcher (Talep Yönlendirici)**
- **Group ID**: `group_technical_service_dispatcher`
- **Kaynak**: Technical Organization (organization_type='dispatcher')
- **Temel Görev**: Gelen talepleri değerlendiren ve yönlendiren kişi
- **Yetkiler**:
  - Tüm talepleri görüntüleme
  - Talep önceliklendirme
  - Teknisyen/takım atama
  - İş emri oluşturma
  - SLA takibi
- **Domain**: `[(1, '=', 1)]` (tüm talepler)
- **Inherits**: `group_technical_service_user`

### C. ÖZEL ROLLER

#### 9. 🏢 **Lokasyon Yöneticisi (Location Manager)**
- **Group ID**: `group_technical_service_location_manager`
- **Kaynak**: Technical Organization (organization_type='location_manager')
- **Temel Görev**: Kampüs/Bina sorumlusu
- **Yetkiler**:
  - Lokasyon bazlı talep görüntüleme
  - Periyodik bakım planlaması
  - Lokasyon varlık yönetimi
  - Lokasyon bazlı raporlar
- **Domain**:
  ```python
  [('location_id', 'in',
    user.technical_org_id.location_ids.ids)]
  ```
- **Inherits**: `group_technical_service_user`

#### 10. 📦 **Envanter Yöneticisi (Inventory Manager)**
- **Group ID**: `group_technical_service_inventory_manager`
- **Kaynak**: Technical Organization (organization_type='inventory_manager')
- **Temel Görev**: Malzeme ve stok yönetimi
- **Yetkiler**:
  - Stok yönetimi
  - Malzeme talep onayları
  - Demirbaş takibi
  - Envanter raporları
- **Inherits**: `group_technical_service_user`

#### 11. 📊 **Raporlama Yetkilisi (Reporting Officer)**
- **Group ID**: `group_technical_service_reporting`
- **Kaynak**: Özel atama
- **Temel Görev**: Raporlama ve analiz
- **Yetkiler**:
  - Tüm raporlara erişim (salt okunur)
  - Dashboard görüntüleme
  - Veri dışa aktarma
  - Analitik görünümler
- **Domain**: `[(1, '=', 1)]` (read-only)
- **Inherits**: `group_technical_service_user`

---

## 📁 DOSYA YAPISI - DÜZELTME SONRASI

### 🔴 CORE MODULE (technical_service) - Business Logic:
```
technical_service/
├── models/
│   ├── technical_service_organization.py  # ⚠️ BURAYA TAŞINACAK
│   ├── technical_service_request.py       # Mevcut
│   ├── technical_service_work_order.py    # Mevcut
│   └── ...
├── views/
│   └── technical_service_organization_views.xml  # Temel CRUD view'ları
└── security/
    └── ir.model.access.csv  # Temel erişim hakları
```

### 🔵 PRESENTATION MODULE (technical_service_presentation) - Access & UI:
```
technical_service_presentation/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── # ❌ BURADA YENİ MODEL TANIMLANMAYACAK!
│       # ✅ Sadece inherit ile field-level access control
├── docs/
│   ├── MODULE_ARCHITECTURE.md (bu dosya)
│   ├── SECURITY_GROUPS.md
│   └── MENU_STRUCTURE.md
├── security/
│   ├── technical_service_groups.xml (11 rol tanımı)
│   ├── ir.model.access.csv (rol bazlı model erişim hakları)
│   └── record_rules.xml (domain bazlı kurallar)
├── views/
│   ├── technical_organization_inherited_views.xml  # View inheritance
│   ├── menu_structure.xml (rol bazlı menü yapısı)
│   ├── dashboard_views.xml (rol bazlı dashboard'lar)
│   └── inherited_views.xml (diğer view özelleştirmeleri)
└── data/
    ├── demo_organization.xml  # Demo organizasyon yapısı
    └── demo_users.xml (test kullanıcıları)
```

## 🔄 İKİ AŞAMALI YETKİLENDİRME SİSTEMİ

### Aşama 1: Rol Atama
```python
def assign_user_role(user):
    # 1. HR'dan kontrol et
    if user.employee_id:
        # HR yöneticisi mi?
        if user.employee_id.child_ids:
            user.groups_id += group_technical_service_hr_manager
        # Normal kullanıcı
        else:
            user.groups_id += group_technical_service_user

    # 2. Technical Organization'dan kontrol et
    tech_org = self.env['technical_service.organization'].search([
        ('user_id', '=', user.id)
    ], limit=1)

    if tech_org:
        # Organization type'a göre rol ata
        role_mapping = {
            'cto': group_technical_service_cto,
            'department_manager': group_technical_service_department_manager,
            'team_leader': group_technical_service_team_leader,
            'senior_technician': group_technical_service_senior_technician,
            'technician': group_technical_service_technician,
            'dispatcher': group_technical_service_dispatcher,
            'location_manager': group_technical_service_location_manager,
            'inventory_manager': group_technical_service_inventory_manager,
        }
        user.groups_id += role_mapping.get(tech_org.organization_type)
```

### Aşama 2: Domain Filtreleme
```python
# Hibrit domain örneği - HR Manager + Technical Organization
domain = ['|', '|',
    # Kendi talepleri
    ('create_uid', '=', user.id),
    # HR altındaki çalışanların talepleri
    ('employee_id', 'in', user.employee_id.child_ids.ids),
    # Technical org altındaki teknisyenlerin talepleri
    ('technician_user_id', 'in', user.technical_org_id.get_subordinate_users())
]
```

## 🔨 Uygulama Adımları - İMPLEMENTASYON ANALİZİ SONRASI

### ⚠️ ADIM 0: Core Module Güncellemesi (technical_service)
#### Eklenecek Yeni Özellikler:
- [ ] **technical_service_organization.py** model dosyası oluştur (🔴 YOK)
- [ ] Model'i technical_service/__init__.py'ye ekle
- [ ] technical_service/__manifest__.py'yi güncelle
- [ ] Temel CRUD view'larını ekle
- [ ] Basic security (ir.model.access.csv) ekle

#### Mevcut Modellere Eklenecekler:
- [ ] **maintenance.request**: `technical_org_id` field ekle
- [ ] **maintenance.team**: `technical_org_id` field ekle
- [ ] **res.users**: `technical_org_id` field ekle

### ADIM 1: Presentation Module Altyapısı
- [ ] technical_service_presentation klasörü oluştur
- [ ] __init__.py dosyası oluştur
- [ ] __manifest__.py dosyası oluştur
- [ ] technical_service modülüne dependency ekle
- [ ] Klasör yapısını oluştur (security/, views/, data/)

### ADIM 2: Security Groups Tanımlama
- [ ] technical_service_groups.xml oluştur
- [ ] 11 farklı rol tanımla:
  - [ ] 2 HR bazlı rol (Standard User, HR Manager)
  - [ ] 8 Technical Org bazlı rol (CTO, DPM, TML, etc.)
  - [ ] 1 Özel rol (Reporting)
- [ ] Groups arası inheritance ilişkileri kur

### ADIM 3: Menü Yapıları ve View Özelleştirmeleri

#### 3.1 Dashboard Menüleri (✅ Widget'lar mevcut)
- [ ] Benim Dashboard'ım - Mevcut widget'ı kullan
- [ ] Ekip Dashboard'ı - Team filter ekle
- [ ] Yönetim Dashboard'ı - Yeni KPI'lar ekle

#### 3.2 Servis Talepleri (✅ Model mevcut)
- [ ] Taleplerim - Domain filter: `[('create_uid', '=', user.id)]`
- [ ] Ekibimin Talepleri - HR hierarchy filter
- [ ] Atanmış Talepler - Domain: `[('technician_user_id', '=', user.id)]`
- [ ] Bekleyen Talepler - Domain: `[('stage_id.done', '=', False)]`

#### 3.3 İş Emirleri (✅ Model mevcut)
- [ ] İş Emirlerim - Technician filter ekle
- [ ] Ekip İş Emirleri - Team filter ekle

#### 3.4 Varlık Yönetimi (✅ Modeller mevcut)
- [ ] Inherit existing views
- [ ] Add role-based visibility

#### 3.5 Ekip Yönetimi (⚠️ Model var, view eksik)
- [ ] Teknisyenler - Create list/form views for team.member
- [ ] Vardiyalar - New shift management model needed

#### 3.6 Teknik Organizasyon (🔴 YOK)
- [ ] Organizasyon Yapısı - Tree view
- [ ] Pozisyon Yönetimi - Form views
- [ ] Rol Atamaları - User assignment wizard

#### 3.7 Lokasyon Yönetimi (✅ Tamamen mevcut)
- [ ] Sadece menü görünürlüğü ayarlanacak

#### 3.8 Envanter (⚠️ Kısmen var)
- [ ] Stock module entegrasyonu
- [ ] Inventory views inherit

#### 3.9 Raporlar (✅ Wizard mevcut)
- [ ] Dashboard widget'ları ekle
- [ ] Rol bazlı filtreler

#### 3.10 Konfigürasyon (✅ Settings mevcut)
- [ ] Menü görünürlüğü ayarla

### ADIM 4: Record Rules
- [ ] Her rol için domain tabanlı erişim kuralları
- [ ] Standart kullanıcı: `[('create_uid', '=', user.id)]`
- [ ] HR Manager: `['|', ('create_uid', '=', user.id), ('employee_id.parent_id.user_id', '=', user.id)]`
- [ ] Technician: `[('technician_user_id', '=', user.id)]`
- [ ] Team Leader: `[('maintenance_team_id.team_leader_id', '=', user.id)]`
- [ ] CTO: `[(1, '=', 1)]` - Tüm kayıtlar

### ADIM 5: Dashboard Özelleştirmeleri
- [ ] Mevcut dashboard widget'larını inherit et
- [ ] Rol bazlı KPI'lar ekle
- [ ] Team/Department filtreleri ekle
- [ ] Quick action buttons

### ADIM 6: Test ve Dokümantasyon
- [ ] Demo organizasyon yapısı oluştur
- [ ] Her rol için test kullanıcıları
- [ ] Test senaryoları dokümanı
- [ ] Kullanım kılavuzu

## 📊 İMPLEMENTASYON DURUM ÖZETİ

### Mevcut Durum İstatistikleri:
- ✅ **HAZIR MODELLER**: %60 (Request, Work Order, Asset, Team, SLA, Location)
- ⚠️ **VIEW/FİLTRE EKSİK**: %30 (Dashboard filtreleri, Domain rules)
- 🔴 **YAPILACAK**: %10 (Technical Organization, Vardiya)

### Kritik Eksikler:
1. **Technical Organization Model** - Core module'e eklenecek (ADIM 0)
2. **Domain Filtreleri** - Presentation layer'da eklenecek (ADIM 4)
3. **Rol Bazlı Menüler** - Security groups ile kontrol edilecek (ADIM 2-3)

## ⚠️ Kritik Kurallar

1. **Core Module Güncellemesi**: Sadece `technical_service.organization` modeli eklenecek
2. **Sadece Inherit**: Presentation layer'da var olan view ve modelleri sadece inherit edeceğiz
3. **Yeni Model Yok**: Presentation layer'da yeni model tanımlamayacağız (organization hariç)
4. **Business Logic Core'da**: Tüm iş mantığı core modülde kalacak
5. **Modüler Yapı**: Her dosya tek bir role odaklanacak

## 🎯 Beklenen Sonuçlar

- ✅ Rol bazlı erişim kontrolü
- ✅ Her kullanıcı sadece yetkili olduğu menüleri görecek
- ✅ Domain filtreleri ile veri güvenliği
- ✅ Modüler ve bakımı kolay yapı
- ✅ Test edilebilir kod
- ✅ Dokümante edilmiş süreçler

## 📊 Performans Kriterleri

- Login sonrası menü yüklenme: < 2 saniye
- Dashboard render süresi: < 3 saniye
- Talep listeleme: < 1 saniye (1000 kayıt için)
- Rol değişimi: Logout/Login gerektirmeden

## 🔄 Rollback Stratejisi

Eğer presentation layer sorun çıkarırsa:
1. Module'ü uninstall et
2. Core module normal çalışmaya devam eder
3. Data kaybı olmaz
4. Kullanıcılar base.group_user ile temel erişime sahip olur

---

## 📊 ROL-MENÜ ERİŞİM MATRİSİ (GÜNCELLENMİŞ - 11 ROL)

### Rol Kısaltmaları:
- **USR**: Standard User (HR)
- **HRM**: HR Manager
- **CTO**: CTO/Teknik Direktör
- **DPM**: Department Manager
- **TML**: Team Leader
- **SRT**: Senior Technician
- **TCH**: Technician
- **DSP**: Dispatcher
- **LCM**: Location Manager
- **INV**: Inventory Manager
- **RPT**: Reporting Officer

### Ana Menüler ve Alt Menüler

| Menü / Rol | USR | HRM | CTO | DPM | TML | SRT | TCH | DSP | LCM | INV | RPT |
|------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| **🏠 Dashboard** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| └─ Benim Dashboard'ım | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| └─ Ekip Dashboard'ı | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Yönetim Dashboard'ı | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| **📝 Servis Talepleri** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| └─ Yeni Talep | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| └─ Taleplerim | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Ekibimin Talepleri | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Atanmış Talepler | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| └─ Tüm Talepler | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| └─ Bekleyen Talepler | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **🔨 İş Emirleri** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| └─ Yeni İş Emri | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| └─ İş Emirlerim | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| └─ Ekip İş Emirleri | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Tüm İş Emirleri | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| **🏗️ Varlık Yönetimi** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| └─ Ekipmanlar | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| └─ Bakım Sözleşmeleri | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| └─ Periyodik Bakımlar | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **👥 Ekip Yönetimi** | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| └─ Teknisyenler | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| └─ Takımlar | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Vardiyalar | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Performans | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **🏢 Teknik Organizasyon** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Organizasyon Yapısı | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Pozisyon Yönetimi | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Rol Atamaları | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **📍 Lokasyon Yönetimi** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| └─ Kampüsler | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| └─ Binalar | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| └─ Alanlar | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **📦 Envanter** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| └─ Stok Durumu | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| └─ Malzeme Talepleri | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| └─ Demirbaşlar | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **📊 Raporlar** | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| └─ Talep Raporları | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| └─ Performans Raporları | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| └─ SLA Raporları | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| └─ Envanter Raporları | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| └─ Maliyet Raporları | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **⚙️ Konfigürasyon** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Genel Ayarlar | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ SLA Politikaları | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| └─ Kategoriler | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| └─ Kullanıcı Yönetimi | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Notlar:
- ✅ = Tam Erişim (Okuma/Yazma/Düzenleme/Silme - rol bazlı kısıtlamalarla)
- ❌ = Erişim Yok
- Her rol kendi domain filtreleri ile sınırlıdır (örn: User sadece kendi taleplerini görür)
- Manager rolü HR hiyerarşisine göre dinamik olarak belirlenir

### Test Senaryoları (11 Rol):
1. **USR - Standard User**: Sadece kendi taleplerini görmeli, yeni talep oluşturabilmeli
2. **HRM - HR Manager**: Altındaki çalışanların taleplerini görmeli ve yönetebilmeli (HR hiyerarşisi)
3. **CTO - CTO/Teknik Direktör**: Tüm teknik organizasyonu yönetebilmeli, rol atamaları yapabilmeli
4. **DPM - Department Manager**: Kendi birimindeki tüm takımları ve operasyonları yönetebilmeli
5. **TML - Team Leader**: Ekibinin tüm işlerini görmeli, teknisyenlere iş atayabilmeli
6. **SRT - Senior Technician**: Kendine atanan kompleks işleri çözebilmeli, mentorluk yapabilmeli
7. **TCH - Technician**: Kendine atanan işleri görmeli, durum güncelleyebilmeli
8. **DSP - Dispatcher**: Tüm talepleri görmeli, önceliklendirme ve atama yapabilmeli
9. **LCM - Location Manager**: Lokasyon bazlı talepleri ve periyodik bakımları yönetebilmeli
10. **INV - Inventory Manager**: Stok, malzeme ve demirbaş yönetimi yapabilmeli
11. **RPT - Reporting Officer**: Tüm raporları görüntüleyebilmeli (salt okunur)

## 🎯 ÖZET VE FAYDALAR

### İzole Teknik Organizasyon Yapısının Faydaları:
1. **HR Bağımsızlığı**: Teknik ekip HR değişikliklerinden etkilenmez
2. **Esnek Hiyerarşi**: CTO kendi organizasyonunu özgürce yapılandırabilir
3. **Rol Netliği**: Her pozisyonun net yetki ve sorumlulukları
4. **Kolay Yönetim**: Tek bir yerden (Technical Organization) tüm teknik roller yönetilir
5. **Hibrit Yapı**: HR (talep açanlar) + Technical Org (çözücüler) entegrasyonu

### Kritik Başarı Faktörleri:
- CTO/Admin rolünün doğru kişiye verilmesi
- Technical Organization hiyerarşisinin doğru kurulması
- HR ve Technical Org arasında net ayrım
- Domain rule'ların doğru yapılandırılması
- Test senaryolarının eksiksiz uygulanması