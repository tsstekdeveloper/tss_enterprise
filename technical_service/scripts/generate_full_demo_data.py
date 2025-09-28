#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Technical Service - Kapsamlı Demo Data Generator
Tüm modül özelliklerini gösteren zengin demo veriler
"""

import xmlrpc.client
import ssl
from datetime import datetime, timedelta
import random

# SSL doğrulamasını devre dışı bırak
ssl._create_default_https_context = ssl._create_unverified_context

# Bağlantı bilgileri
url = 'http://localhost:8069'
db = 'odoo_tech_service'
username = 'admin'
password = 'admin'

print("\n" + "="*70)
print("🚀 TECHNICAL SERVICE - KAPSAMLI DEMO DATA OLUŞTURMA")
print("="*70)

try:
    # Bağlantı
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("❌ Kimlik doğrulama başarısız!")
        exit(1)

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print("✅ Bağlantı başarılı!")

    def search(model, domain):
        return models.execute_kw(db, uid, password, model, 'search', [domain])

    def create(model, values):
        try:
            return models.execute_kw(db, uid, password, model, 'create', [values])
        except Exception as e:
            print(f"    ⚠️ Hata ({model}): {str(e)[:100]}")
            return False

    def write(model, ids, values):
        return models.execute_kw(db, uid, password, model, 'write', [ids, values])

    def read(model, ids, fields):
        return models.execute_kw(db, uid, password, model, 'read', [ids], {'fields': fields})

    # Veri saklama
    data = {
        'departments': {},
        'employees': {},
        'users': {},
        'campuses': {},
        'buildings': {},
        'teams': {},
        'team_members': [],
        'categories': {},
        'equipment': [],
        'slas': {},
        'sla_lines': [],
        'contracts': [],
        'requests': [],
        'work_orders': [],
        'spare_parts': [],
        'knowledge': []
    }

    # ================================================
    # 1. ŞIRKET VE DEPARTMANLAR
    # ================================================
    print("\n[1] 🏢 Şirket ve Departmanlar oluşturuluyor...")

    # Şirket güncelle
    company_ids = search('res.company', [])
    if company_ids:
        company_id = company_ids[0]
        write('res.company', [company_id], {
            'name': 'TechnoFix Global Services A.Ş.',
            'street': 'Teknoloji Bulvarı No:42',
            'city': 'İstanbul',
            'phone': '+90 212 555 1234'
        })
        print("  ✓ Şirket güncellendi")

    # Departmanlar
    departments = [
        'Bilgi İşlem',
        'Üretim',
        'İnsan Kaynakları',
        'Teknik İşler',
        'İdari İşler',
        'Ar-Ge',
        'Satış',
        'Pazarlama',
        'Muhasebe',
        'Kalite Kontrol',
        'Lojistik',
        'Satın Alma'
    ]

    for dept_name in departments:
        existing = search('hr.department', [('name', '=', dept_name)])
        if not existing:
            dept_id = create('hr.department', {
                'name': dept_name,
                'company_id': company_id
            })
            if dept_id:
                data['departments'][dept_name] = dept_id
                print(f"  ✓ {dept_name}")

    # ================================================
    # 2. KULLANICILAR VE ÇALIŞANLAR
    # ================================================
    print("\n[2] 👥 Kullanıcılar ve Çalışanlar oluşturuluyor...")

    employees_data = [
        # Yönetim
        {'name': 'Ahmet Yılmaz', 'email': 'ahmet.yilmaz@technofix.com', 'job': 'Genel Müdür', 'dept': 'İdari İşler', 'phone': '5551001001'},
        {'name': 'Mehmet Demir', 'email': 'mehmet.demir@technofix.com', 'job': 'IT Müdürü', 'dept': 'Bilgi İşlem', 'phone': '5551002002'},
        {'name': 'Ayşe Kaya', 'email': 'ayse.kaya@technofix.com', 'job': 'Teknik Müdür', 'dept': 'Teknik İşler', 'phone': '5551003003'},

        # Takım Liderleri
        {'name': 'Fatma Şahin', 'email': 'fatma.sahin@technofix.com', 'job': 'Network Takım Lideri', 'dept': 'Bilgi İşlem', 'phone': '5552001001'},
        {'name': 'Ali Özkan', 'email': 'ali.ozkan@technofix.com', 'job': 'Donanım Takım Lideri', 'dept': 'Bilgi İşlem', 'phone': '5552002002'},
        {'name': 'Veli Çelik', 'email': 'veli.celik@technofix.com', 'job': 'Elektrik Takım Lideri', 'dept': 'Teknik İşler', 'phone': '5552003003'},

        # IT Teknisyenler
        {'name': 'Can Aydın', 'email': 'can.aydin@technofix.com', 'job': 'Senior Network Admin', 'dept': 'Bilgi İşlem', 'phone': '5553001001'},
        {'name': 'Cem Yıldız', 'email': 'cem.yildiz@technofix.com', 'job': 'Sistem Yöneticisi', 'dept': 'Bilgi İşlem', 'phone': '5553002002'},
        {'name': 'Deniz Arslan', 'email': 'deniz.arslan@technofix.com', 'job': 'Database Admin', 'dept': 'Bilgi İşlem', 'phone': '5553003003'},
        {'name': 'Elif Güneş', 'email': 'elif.gunes@technofix.com', 'job': 'Junior Developer', 'dept': 'Bilgi İşlem', 'phone': '5553004004'},
        {'name': 'Emre Koç', 'email': 'emre.koc@technofix.com', 'job': 'Help Desk Uzmanı', 'dept': 'Bilgi İşlem', 'phone': '5553005005'},

        # Teknik Personel
        {'name': 'Gül Yılmaz', 'email': 'gul.yilmaz@technofix.com', 'job': 'Elektrik Teknisyeni', 'dept': 'Teknik İşler', 'phone': '5554001001'},
        {'name': 'Hakan Demir', 'email': 'hakan.demir@technofix.com', 'job': 'Mekanik Teknisyeni', 'dept': 'Teknik İşler', 'phone': '5554002002'},
        {'name': 'İrem Kaya', 'email': 'irem.kaya@technofix.com', 'job': 'HVAC Teknisyeni', 'dept': 'Teknik İşler', 'phone': '5554003003'},
        {'name': 'Kaan Öz', 'email': 'kaan.oz@technofix.com', 'job': 'Bina Bakım Teknisyeni', 'dept': 'Teknik İşler', 'phone': '5554004004'},

        # Üretim Personeli
        {'name': 'Leyla Ak', 'email': 'leyla.ak@technofix.com', 'job': 'Üretim Müdürü', 'dept': 'Üretim', 'phone': '5555001001'},
        {'name': 'Murat Can', 'email': 'murat.can@technofix.com', 'job': 'Üretim Operatörü', 'dept': 'Üretim', 'phone': '5555002002'},
        {'name': 'Nalan Er', 'email': 'nalan.er@technofix.com', 'job': 'Kalite Kontrol Uzmanı', 'dept': 'Kalite Kontrol', 'phone': '5555003003'},

        # Destek Personel
        {'name': 'Okan Sel', 'email': 'okan.sel@technofix.com', 'job': 'İK Uzmanı', 'dept': 'İnsan Kaynakları', 'phone': '5556001001'},
        {'name': 'Pınar Tan', 'email': 'pinar.tan@technofix.com', 'job': 'Muhasebe Uzmanı', 'dept': 'Muhasebe', 'phone': '5556002002'},
        {'name': 'Rıza Ün', 'email': 'riza.un@technofix.com', 'job': 'Satın Alma Uzmanı', 'dept': 'Satın Alma', 'phone': '5556003003'},
        {'name': 'Seda Var', 'email': 'seda.var@technofix.com', 'job': 'Satış Temsilcisi', 'dept': 'Satış', 'phone': '5556004004'},
        {'name': 'Tuna Yel', 'email': 'tuna.yel@technofix.com', 'job': 'Pazarlama Uzmanı', 'dept': 'Pazarlama', 'phone': '5556005005'},
        {'name': 'Umut Zor', 'email': 'umut.zor@technofix.com', 'job': 'Lojistik Uzmanı', 'dept': 'Lojistik', 'phone': '5556006006'},
        {'name': 'Volkan Al', 'email': 'volkan.al@technofix.com', 'job': 'Güvenlik Görevlisi', 'dept': 'İdari İşler', 'phone': '5556007007'}
    ]

    for emp_data in employees_data:
        # Kullanıcı oluştur/bul
        user_existing = search('res.users', [('login', '=', emp_data['email'])])
        if not user_existing:
            user_id = create('res.users', {
                'name': emp_data['name'],
                'login': emp_data['email'],
                'email': emp_data['email'],
                'password': 'demo123'
            })
            if user_id:
                data['users'][emp_data['name']] = user_id
        else:
            data['users'][emp_data['name']] = user_existing[0]

        # Job position
        job_existing = search('hr.job', [('name', '=', emp_data['job'])])
        if not job_existing:
            job_id = create('hr.job', {'name': emp_data['job']})
        else:
            job_id = job_existing[0]

        # Employee oluştur
        if data['users'].get(emp_data['name']):
            emp_existing = search('hr.employee', [('user_id', '=', data['users'][emp_data['name']])])
            if not emp_existing:
                dept_id = search('hr.department', [('name', '=', emp_data['dept'])])
                emp_id = create('hr.employee', {
                    'name': emp_data['name'],
                    'user_id': data['users'][emp_data['name']],
                    'job_id': job_id,
                    'department_id': dept_id[0] if dept_id else False,
                    'work_email': emp_data['email'],
                    'work_phone': emp_data.get('phone', ''),
                    'mobile_phone': '+90 ' + emp_data.get('phone', '')
                })
                if emp_id:
                    data['employees'][emp_data['name']] = emp_id
                    print(f"  ✓ {emp_data['name']} - {emp_data['job']}")

    # ================================================
    # 3. KAMPÜSLER VE BİNALAR
    # ================================================
    print("\n[3] 🏢 Kampüsler ve Binalar oluşturuluyor...")

    campus_data = [
        {
            'name': 'Ana Kampüs - Levent',
            'code': 'MAIN-LEV',
            'address': 'Levent Mahallesi, Teknoloji Bulvarı No:42, Beşiktaş/İstanbul',
            'phone': '+90 212 555 1000',
            'email': 'levent@technofix.com',
            'manager': 'Ahmet Yılmaz',
            'buildings': [
                {'name': 'A Blok - Yönetim Binası', 'code': 'A-BLK', 'floor_count': 5, 'manager': 'Volkan Al'},
                {'name': 'B Blok - Üretim Tesisi', 'code': 'B-BLK', 'floor_count': 3, 'manager': 'Leyla Ak'},
                {'name': 'C Blok - IT Merkezi', 'code': 'C-BLK', 'floor_count': 4, 'manager': 'Mehmet Demir'},
                {'name': 'D Blok - Depo ve Lojistik', 'code': 'D-BLK', 'floor_count': 2, 'manager': 'Umut Zor'}
            ]
        },
        {
            'name': 'Ar-Ge Kampüsü - Teknopark',
            'code': 'RND-TEK',
            'address': 'İTÜ Ayazağa Kampüsü, Teknokent, Maslak/İstanbul',
            'phone': '+90 212 555 2000',
            'email': 'arge@technofix.com',
            'manager': 'Ayşe Kaya',
            'buildings': [
                {'name': 'İnovasyon Merkezi', 'code': 'INV-CTR', 'floor_count': 6, 'manager': 'Deniz Arslan'},
                {'name': 'Test Laboratuvarı', 'code': 'TEST-LAB', 'floor_count': 2, 'manager': 'Nalan Er'},
                {'name': 'Prototip Atölyesi', 'code': 'PROTO-WS', 'floor_count': 1, 'manager': 'Hakan Demir'}
            ]
        },
        {
            'name': 'Anadolu Yakası Kampüs',
            'code': 'ASIA-KMP',
            'address': 'Ataşehir, Finans Merkezi, İstanbul',
            'phone': '+90 216 555 3000',
            'email': 'anadolu@technofix.com',
            'manager': 'Fatma Şahin',
            'buildings': [
                {'name': 'E Blok - Satış Ofisi', 'code': 'E-BLK', 'floor_count': 3, 'manager': 'Seda Var'},
                {'name': 'F Blok - Müşteri Hizmetleri', 'code': 'F-BLK', 'floor_count': 2, 'manager': 'Emre Koç'}
            ]
        }
    ]

    for campus_info in campus_data:
        # Manager employee ID bul
        manager_emp_id = False
        if campus_info['manager'] in data['employees']:
            manager_emp_id = data['employees'][campus_info['manager']]

        # Kampüs oluştur
        campus_existing = search('technical_service.campus', [('code', '=', campus_info['code'])])
        if not campus_existing:
            campus_id = create('technical_service.campus', {
                'name': campus_info['name'],
                'code': campus_info['code'],
                'address': campus_info['address'],
                'phone': campus_info.get('phone', ''),
                'email': campus_info.get('email', ''),
                'manager_id': manager_emp_id
            })
            if campus_id:
                data['campuses'][campus_info['code']] = campus_id
                print(f"  ✓ Kampüs: {campus_info['name']}")

                # Binalar
                for bldg in campus_info['buildings']:
                    bldg_manager_id = False
                    if bldg['manager'] in data['employees']:
                        bldg_manager_id = data['employees'][bldg['manager']]

                    building_id = create('technical_service.building', {
                        'name': bldg['name'],
                        'code': bldg['code'],
                        'campus_id': campus_id,
                        'floor_count': bldg['floor_count'],
                        'manager_id': bldg_manager_id
                    })
                    if building_id:
                        data['buildings'][bldg['code']] = building_id
                        print(f"    ✓ Bina: {bldg['name']}")

    # ================================================
    # 4. SERVİS EKİPLERİ VE ÜYELER
    # ================================================
    print("\n[4] 👥 Servis Ekipleri ve Üyeler oluşturuluyor...")

    teams_data = [
        {
            'name': 'IT Network Ekibi',
            'code': 'IT-NET',
            'x_specialization': 'it',
            'x_shift_type': 'regular',
            'team_leader': 'Fatma Şahin',
            'members': ['Can Aydın', 'Cem Yıldız', 'Deniz Arslan'],
            'skills': ['Network', 'Firewall', 'Routing', 'Switching'],
            'x_auto_assign': True
        },
        {
            'name': 'IT Donanım Ekibi',
            'code': 'IT-HW',
            'x_specialization': 'it',
            'x_shift_type': 'regular',
            'team_leader': 'Ali Özkan',
            'members': ['Elif Güneş', 'Emre Koç'],
            'skills': ['Hardware', 'Desktop', 'Laptop', 'Printer'],
            'x_auto_assign': True
        },
        {
            'name': 'Elektrik-Mekanik Ekibi',
            'code': 'ELEC-MECH',
            'x_specialization': 'technical',
            'x_shift_type': '2_shifts',
            'team_leader': 'Veli Çelik',
            'members': ['Gül Yılmaz', 'Hakan Demir', 'İrem Kaya'],
            'skills': ['Electrical', 'Mechanical', 'HVAC', 'Generator'],
            'x_auto_assign': True
        },
        {
            'name': 'Bina Bakım Ekibi',
            'code': 'BUILD-MAINT',
            'x_specialization': 'facility',
            'x_shift_type': 'regular',
            'team_leader': 'Kaan Öz',
            'members': ['Kaan Öz'],
            'skills': ['Building', 'Plumbing', 'Carpentry', 'Painting'],
            'x_auto_assign': False
        },
        {
            'name': '7/24 Acil Müdahale',
            'code': 'EMERGENCY',
            'x_specialization': 'mixed',
            'x_shift_type': '24_7',
            'team_leader': 'Mehmet Demir',
            'members': ['Can Aydın', 'Gül Yılmaz'],
            'skills': ['Emergency', 'Critical', 'All'],
            'x_auto_assign': True
        }
    ]

    for team_data in teams_data:
        # Team leader employee ID
        leader_id = data['employees'].get(team_data['team_leader'], False)

        # Team oluştur
        team_existing = search('technical_service.team', [('code', '=', team_data['code'])])
        if not team_existing:
            # Tüm kampüsleri ekle
            all_campus_ids = list(data['campuses'].values())

            team_id = create('technical_service.team', {
                'name': team_data['name'],
                'code': team_data['code'],
                'x_specialization': team_data['x_specialization'],
                'x_shift_type': team_data['x_shift_type'],
                'team_leader_id': leader_id,
                'x_campus_ids': [(6, 0, all_campus_ids)],
                'x_auto_assign': team_data.get('x_auto_assign', True),
                'x_assignment_method': 'rotation',
                'active': True
            })

            if team_id:
                data['teams'][team_data['code']] = team_id
                print(f"  ✓ Ekip: {team_data['name']}")

                # Team members ekle
                for member_name in team_data['members']:
                    if member_name in data['employees']:
                        member_id = create('technical_service.team_member', {
                            'team_id': team_id,
                            'employee_id': data['employees'][member_name],
                            'x_skill_level': random.choice(['junior', 'mid', 'senior', 'expert']),
                            'x_is_available': True,
                            'x_availability_status': 'available'
                        })
                        if member_id:
                            print(f"    ✓ Üye: {member_name}")

    # ================================================
    # 5. EKİPMAN KATEGORİLERİ VE EKİPMANLAR
    # ================================================
    print("\n[5] 🔧 Ekipman Kategorileri ve Ekipmanlar oluşturuluyor...")

    # Kategoriler
    categories_data = [
        {'name': 'Sunucular', 'code': 'SRV', 'color': 1},
        {'name': 'Network Cihazları', 'code': 'NET', 'color': 2},
        {'name': 'Bilgisayarlar', 'code': 'PC', 'color': 3},
        {'name': 'Yazıcı ve Tarayıcılar', 'code': 'PRINT', 'color': 4},
        {'name': 'Üretim Makineleri', 'code': 'PROD', 'color': 5},
        {'name': 'HVAC Sistemleri', 'code': 'HVAC', 'color': 6},
        {'name': 'Güç Sistemleri', 'code': 'POWER', 'color': 7},
        {'name': 'Güvenlik Sistemleri', 'code': 'SEC', 'color': 8},
        {'name': 'Telekomünikasyon', 'code': 'TELCO', 'color': 9}
    ]

    for cat_data in categories_data:
        cat_existing = search('maintenance.equipment.category', [('name', '=', cat_data['name'])])
        if not cat_existing:
            cat_id = create('maintenance.equipment.category', {
                'name': cat_data['name'],
                'technician_user_id': uid,
                'color': cat_data.get('color', 1)
            })
            if cat_id:
                data['categories'][cat_data['code']] = cat_id
                print(f"  ✓ Kategori: {cat_data['name']}")

    # Ekipmanlar
    equipment_data = [
        # Sunucular
        {'name': 'Dell PowerEdge R750 - ERP Sunucu', 'serial': 'DPE-R750-001', 'category': 'SRV', 'location': 'C-BLK', 'critical': True, 'cost': 85000},
        {'name': 'HP ProLiant DL380 - Mail Sunucu', 'serial': 'HP-DL380-002', 'category': 'SRV', 'location': 'C-BLK', 'critical': True, 'cost': 75000},
        {'name': 'IBM Power System - Database', 'serial': 'IBM-PWR-003', 'category': 'SRV', 'location': 'C-BLK', 'critical': True, 'cost': 120000},

        # Network
        {'name': 'Cisco Catalyst 9300 - Core Switch', 'serial': 'CS-9300-001', 'category': 'NET', 'location': 'C-BLK', 'critical': True, 'cost': 45000},
        {'name': 'Fortinet FortiGate 600E', 'serial': 'FG-600E-001', 'category': 'NET', 'location': 'C-BLK', 'critical': True, 'cost': 35000},
        {'name': 'Aruba 5400R - Distribution Switch', 'serial': 'ARB-5400-002', 'category': 'NET', 'location': 'A-BLK', 'critical': False, 'cost': 25000},

        # Bilgisayarlar
        {'name': 'Dell OptiPlex 7090 - CEO PC', 'serial': 'PC-CEO-001', 'category': 'PC', 'location': 'A-BLK', 'critical': False, 'cost': 8500},
        {'name': 'Lenovo ThinkPad X1 Carbon', 'serial': 'LTP-X1-025', 'category': 'PC', 'location': 'A-BLK', 'critical': False, 'cost': 12000},

        # Üretim
        {'name': 'Haas VF-4 CNC Torna', 'serial': 'HAAS-VF4-001', 'category': 'PROD', 'location': 'B-BLK', 'critical': True, 'cost': 450000},
        {'name': 'TRUMPF TruLaser 3030', 'serial': 'TRU-3030-001', 'category': 'PROD', 'location': 'B-BLK', 'critical': True, 'cost': 680000},
        {'name': 'ABB IRB 6700 Robot', 'serial': 'ABB-6700-001', 'category': 'PROD', 'location': 'B-BLK', 'critical': True, 'cost': 320000},

        # HVAC
        {'name': 'Daikin VRV IV Klima Sistemi', 'serial': 'DAI-VRV-001', 'category': 'HVAC', 'location': 'A-BLK', 'critical': False, 'cost': 120000},
        {'name': 'Carrier 30XA Chiller', 'serial': 'CAR-30XA-001', 'category': 'HVAC', 'location': 'C-BLK', 'critical': True, 'cost': 180000},

        # Güç Sistemleri
        {'name': 'Caterpillar 500kVA Jeneratör', 'serial': 'CAT-500-001', 'category': 'POWER', 'location': 'POWER-ROOM', 'critical': True, 'cost': 280000},
        {'name': 'APC Symmetra 80kVA UPS', 'serial': 'APC-80K-001', 'category': 'POWER', 'location': 'C-BLK', 'critical': True, 'cost': 95000},
        {'name': 'Schneider Electric Trafo 1250kVA', 'serial': 'SCH-1250-001', 'category': 'POWER', 'location': 'POWER-ROOM', 'critical': True, 'cost': 150000},

        # Güvenlik
        {'name': 'Hikvision NVR DS-96128NI', 'serial': 'HIK-NVR-001', 'category': 'SEC', 'location': 'SEC-ROOM', 'critical': False, 'cost': 25000},
        {'name': 'Honeywell Galaxy Alarm', 'serial': 'HON-GAL-001', 'category': 'SEC', 'location': 'SEC-ROOM', 'critical': False, 'cost': 15000}
    ]

    for eq_data in equipment_data:
        eq_existing = search('maintenance.equipment', [('serial_no', '=', eq_data['serial'])])
        if not eq_existing:
            # Building ID bul
            building_id = data['buildings'].get(eq_data['location'], False)

            # Rastgele teknisyen ata
            tech_ids = list(data['employees'].values())
            tech_user_id = data['users'][random.choice(list(data['users'].keys()))]

            eq_id = create('maintenance.equipment', {
                'name': eq_data['name'],
                'serial_no': eq_data['serial'],
                'category_id': data['categories'].get(eq_data['category'], False),
                'location': eq_data['location'],
                'technician_user_id': tech_user_id,
                'cost': eq_data.get('cost', 0),
                'note': f"Critical equipment: {eq_data.get('critical', False)}",
                'warranty_date': (datetime.now() + timedelta(days=random.randint(180, 1095))).strftime('%Y-%m-%d')
            })
            if eq_id:
                data['equipment'].append(eq_id)
                print(f"  ✓ Ekipman: {eq_data['name']}")

    # ================================================
    # 6. SLA POLİTİKALARI
    # ================================================
    print("\n[6] ⏱️ SLA Politikaları oluşturuluyor...")

    sla_policies = [
        {
            'name': 'Kritik Sistemler SLA (7/24)',
            'x_apply_to': 'all',
            'x_business_hours_start': 0.0,
            'x_business_hours_end': 23.99,
            'x_include_weekends': True,
            'x_timezone': 'Europe/Istanbul',
            'x_enable_escalation': True,
            'priorities': [
                {'priority': 'critical', 'response': 15, 'resolution': 120},  # 15 dk - 2 saat
                {'priority': 'high', 'response': 30, 'resolution': 240},      # 30 dk - 4 saat
                {'priority': 'medium', 'response': 120, 'resolution': 480},    # 2 saat - 8 saat
                {'priority': 'low', 'response': 240, 'resolution': 960}        # 4 saat - 16 saat
            ]
        },
        {
            'name': 'Standart SLA (Mesai Saatleri)',
            'x_apply_to': 'all',
            'x_business_hours_start': 8.0,
            'x_business_hours_end': 18.0,
            'x_include_weekends': False,
            'x_timezone': 'Europe/Istanbul',
            'x_enable_escalation': True,
            'priorities': [
                {'priority': 'critical', 'response': 30, 'resolution': 240},   # 30 dk - 4 saat
                {'priority': 'high', 'response': 120, 'resolution': 480},      # 2 saat - 8 saat
                {'priority': 'medium', 'response': 240, 'resolution': 1440},   # 4 saat - 24 saat
                {'priority': 'low', 'response': 480, 'resolution': 2880}       # 8 saat - 48 saat
            ]
        },
        {
            'name': 'VIP SLA (Yönetim)',
            'x_apply_to': 'specific',
            'x_business_hours_start': 7.0,
            'x_business_hours_end': 20.0,
            'x_include_weekends': True,
            'x_timezone': 'Europe/Istanbul',
            'x_enable_escalation': True,
            'priorities': [
                {'priority': 'critical', 'response': 10, 'resolution': 60},    # 10 dk - 1 saat
                {'priority': 'high', 'response': 20, 'resolution': 120},       # 20 dk - 2 saat
                {'priority': 'medium', 'response': 60, 'resolution': 240},     # 1 saat - 4 saat
                {'priority': 'low', 'response': 120, 'resolution': 480}        # 2 saat - 8 saat
            ]
        }
    ]

    for sla_data in sla_policies:
        sla_existing = search('technical_service.sla', [('name', '=', sla_data['name'])])
        if not sla_existing:
            sla_id = create('technical_service.sla', {
                'name': sla_data['name'],
                'active': True,
                'x_apply_to': sla_data['x_apply_to'],
                'x_business_hours_start': sla_data['x_business_hours_start'],
                'x_business_hours_end': sla_data['x_business_hours_end'],
                'x_include_weekends': sla_data['x_include_weekends'],
                'x_timezone': sla_data['x_timezone'],
                'x_enable_escalation': sla_data['x_enable_escalation'],
                'x_escalation_after': 75.0,
                'company_id': company_id
            })

            if sla_id:
                data['slas'][sla_data['name']] = sla_id
                print(f"  ✓ SLA: {sla_data['name']}")

                # SLA Lines (Priority Matrix)
                for priority_data in sla_data['priorities']:
                    line_id = create('technical_service.sla_line', {
                        'sla_id': sla_id,
                        'x_priority': priority_data['priority'],
                        'x_response_time': priority_data['response'],
                        'x_resolution_time': priority_data['resolution']
                    })
                    if line_id:
                        print(f"    ✓ Priority: {priority_data['priority']}")

    # ================================================
    # 7. BAKIM SÖZLEŞMELERİ
    # ================================================
    print("\n[7] 📄 Bakım Sözleşmeleri oluşturuluyor...")

    # Partner (müşteri) oluştur
    partners_data = [
        {'name': 'ABC Üretim A.Ş.', 'is_company': True, 'vat': 'TR1234567890', 'phone': '02125551111'},
        {'name': 'XYZ Teknoloji Ltd.', 'is_company': True, 'vat': 'TR0987654321', 'phone': '02165552222'},
        {'name': 'DEF Lojistik', 'is_company': True, 'vat': 'TR1122334455', 'phone': '02125553333'}
    ]

    partner_ids = []
    for partner_data in partners_data:
        partner_existing = search('res.partner', [('vat', '=', partner_data['vat'])])
        if not partner_existing:
            partner_id = create('res.partner', partner_data)
            if partner_id:
                partner_ids.append(partner_id)
                print(f"  ✓ Müşteri: {partner_data['name']}")

    # Sözleşmeler
    contracts_data = [
        {
            'name': 'Kritik Sistemler 7/24 Bakım Sözleşmesi',
            'x_contract_number': 'CNT-2024-001',
            'x_contract_type': 'comprehensive',
            'customer_id': partner_ids[0] if partner_ids else False,
            'x_start_date': datetime.now(),
            'x_end_date': datetime.now() + timedelta(days=365),
            'x_total_value': 500000.0,
            'x_monthly_value': 41666.67,
            'x_coverage_type': '24_7',
            'x_response_time': 0.25,  # 15 dakika
            'x_services_included': 'unlimited',
            'x_spare_parts_included': True,
            'state': 'active'
        },
        {
            'name': 'Üretim Ekipmanları Yıllık Bakım',
            'x_contract_number': 'CNT-2024-002',
            'x_contract_type': 'amc',
            'customer_id': partner_ids[0] if partner_ids else False,
            'x_start_date': datetime.now(),
            'x_end_date': datetime.now() + timedelta(days=365),
            'x_total_value': 250000.0,
            'x_monthly_value': 20833.33,
            'x_coverage_type': 'business_hours',
            'x_response_time': 2.0,  # 2 saat
            'x_services_included': '12',
            'x_spare_parts_included': False,
            'state': 'active'
        },
        {
            'name': 'IT Altyapı Destek Sözleşmesi',
            'x_contract_number': 'CNT-2024-003',
            'x_contract_type': 'preventive',
            'customer_id': partner_ids[1] if len(partner_ids) > 1 else False,
            'x_start_date': datetime.now(),
            'x_end_date': datetime.now() + timedelta(days=180),
            'x_total_value': 120000.0,
            'x_monthly_value': 20000.0,
            'x_coverage_type': 'business_hours',
            'x_response_time': 4.0,  # 4 saat
            'x_services_included': '6',
            'x_spare_parts_included': False,
            'state': 'active'
        }
    ]

    for contract_data in contracts_data:
        contract_existing = search('technical_service.contract', [('x_contract_number', '=', contract_data['x_contract_number'])])
        if not contract_existing:
            # Tarih formatla
            contract_data['x_start_date'] = contract_data['x_start_date'].strftime('%Y-%m-%d')
            contract_data['x_end_date'] = contract_data['x_end_date'].strftime('%Y-%m-%d')

            # Equipment'ları ekle
            if data['equipment']:
                contract_data['x_equipment_ids'] = [(6, 0, random.sample(data['equipment'], min(5, len(data['equipment']))))]

            contract_id = create('technical_service.contract', contract_data)
            if contract_id:
                data['contracts'].append(contract_id)
                print(f"  ✓ Sözleşme: {contract_data['name']}")

    # ================================================
    # 8. YEDEK PARÇA STOK
    # ================================================
    print("\n[8] 📦 Yedek Parça Stok Tanımları...")

    spare_parts = [
        {'name': 'RAM DDR4 16GB', 'code': 'SP-RAM-16', 'qty': 25, 'price': 1200},
        {'name': 'SSD 500GB', 'code': 'SP-SSD-500', 'qty': 15, 'price': 2500},
        {'name': 'HDD 2TB', 'code': 'SP-HDD-2T', 'qty': 20, 'price': 1800},
        {'name': 'Network Cable Cat6', 'code': 'SP-CAT6', 'qty': 500, 'price': 15},
        {'name': 'Power Supply 650W', 'code': 'SP-PSU-650', 'qty': 10, 'price': 850},
        {'name': 'Keyboard USB', 'code': 'SP-KB-USB', 'qty': 50, 'price': 120},
        {'name': 'Mouse USB', 'code': 'SP-MS-USB', 'qty': 50, 'price': 80},
        {'name': 'Monitor Cable HDMI', 'code': 'SP-HDMI', 'qty': 100, 'price': 45},
        {'name': 'Printer Toner HP', 'code': 'SP-TNR-HP', 'qty': 30, 'price': 450},
        {'name': 'Air Filter HVAC', 'code': 'SP-FILT-AC', 'qty': 100, 'price': 150},
        {'name': 'Fuse 16A', 'code': 'SP-FUSE-16', 'qty': 200, 'price': 25},
        {'name': 'LED Panel 60x60', 'code': 'SP-LED-60', 'qty': 50, 'price': 280}
    ]

    for part_data in spare_parts:
        product_existing = search('product.product', [('default_code', '=', part_data['code'])])
        if not product_existing:
            product_id = create('product.product', {
                'name': part_data['name'],
                'default_code': part_data['code'],
                'type': 'product',
                'list_price': part_data['price'],
                'standard_price': part_data['price'] * 0.7,
                'categ_id': 1  # Default category
            })
            if product_id:
                data['spare_parts'].append(product_id)
                print(f"  ✓ Yedek Parça: {part_data['name']}")

    # ================================================
    # 9. GELİŞMİŞ BAKIM TALEPLERİ
    # ================================================
    print("\n[9] 📋 Gelişmiş Bakım Talepleri oluşturuluyor...")

    # İlk requester'ları bul/oluştur
    requesters = []
    for user_name in list(data['users'].keys())[:10]:
        partner = search('res.partner', [('name', '=', user_name)])
        if partner:
            requesters.append(partner[0])
        else:
            partner_id = create('res.partner', {
                'name': user_name,
                'email': f"{user_name.lower().replace(' ', '.')}@technofix.com",
                'is_company': False
            })
            if partner_id:
                requesters.append(partner_id)

    advanced_requests = [
        # Kritik Durumlar
        {
            'name': '🔴 [KRİTİK] Ana Sunucu Disk Arızası - Veri Kaybı Riski!',
            'description': '''ACIL DURUM - DERHAL MÜDAHALE!

Durum: Ana ERP sunucusunda RAID disk arızası tespit edildi
Sunucu: Dell PowerEdge R750 (DPE-R750-001)
Lokasyon: C Blok Server Room
Hata Kodu: RAID Controller Error - Disk 3 Failed
Risk: Yüksek - Veri kaybı riski var

Etkilenen Sistemler:
- ERP (150+ kullanıcı)
- E-posta servisi
- Dosya paylaşım

İlk Müdahale:
- Hot spare disk devreye alındı
- Rebuild işlemi başlatıldı (%12 tamamlandı)
- Yedekleme kontrolü yapılıyor

DERHAL yedek disk temin edilmeli!''',
            'priority': '3',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][0] if data['equipment'] else False,
            'employee_id': data['employees'].get('Can Aydın', False),
            'request_date': datetime.now() - timedelta(minutes=30)
        },

        # Planlı Bakım
        {
            'name': '🔧 [PLANLI] Q1 2024 Sunucu Bakımları',
            'description': '''Üç Aylık Periyodik Bakım Planı

Kapsam:
1. Tüm sunucular için firmware güncellemeleri
2. Disk health check ve SMART testleri
3. Bellek ve CPU stres testleri
4. Network performans testleri
5. Backup sistemleri kontrolü
6. UPS batarya testleri

Planlanan Tarih: Bu Cumartesi 02:00-06:00
Tahmini Süre: 4 saat
Etkilenen Kullanıcılar: Tüm şirket (duyuru yapıldı)

Bakım Ekibi: IT Network Ekibi + Vendor Desteği''',
            'priority': '1',
            'maintenance_type': 'preventive',
            'schedule_date': datetime.now() + timedelta(days=3),
            'employee_id': data['employees'].get('Mehmet Demir', False),
            'request_date': datetime.now() - timedelta(days=1)
        },

        # Network Problemi
        {
            'name': '⚠️ [YÜKSEK] B Blok Network Timeout Sorunu',
            'description': '''Üretim hattında network gecikmeleri bildiriliyor.

Semptomlar:
- Ping süreleri: 500ms+ (Normal: <5ms)
- Packet loss: %15
- Bağlantı kopmaları (intermittent)

Etkilenen Alan: B Blok 2. ve 3. kat
Başlangıç: 14:30
Etkilenen Kullanıcı: 35 kişi

İlk Analiz:
- Switch CPU kullanımı %95
- Broadcast storm şüphesi
- Loop olasılığı araştırılıyor''',
            'priority': '2',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][3] if len(data['equipment']) > 3 else False,
            'employee_id': data['employees'].get('Fatma Şahin', False),
            'request_date': datetime.now() - timedelta(hours=2)
        },

        # Klima Arızası
        {
            'name': '❄️ [KRİTİK] Server Room Sıcaklık Alarmı - 38°C!',
            'description': '''KRİTİK SICAKLIK ALARMI!

Mevcut Durum:
- Server Room Sıcaklık: 38°C (Kritik eşik: 35°C)
- Nem: %65 (Normal: %40-50)
- Chiller Durumu: OFFLINE
- Hata Kodu: E05 - Kompresör Arızası

Alınan Önlemler:
- Kritik olmayan sunucular kapatıldı
- Portatif klima devreye alındı (2 adet)
- Kapılar açık tutuluyor

RİSK: Sunucu donanım hasarı
Acil servis ekibi yolda (ETA: 20 dakika)''',
            'priority': '3',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][11] if len(data['equipment']) > 11 else False,
            'employee_id': data['employees'].get('İrem Kaya', False),
            'request_date': datetime.now() - timedelta(minutes=45)
        },

        # Yeni Kurulum
        {
            'name': '📦 [KURULUM] 25 Kişilik Yeni Ofis IT Altyapısı',
            'description': '''Yeni açılan satış ofisi için komple IT kurulum

Gereksinimler:
- 25 adet workstation kurulumu
  * 15 Desktop (Dell OptiPlex)
  * 10 Laptop (ThinkPad)
- Network altyapısı
  * 1 adet 48 port switch
  * Wi-Fi access point (3 adet)
  * Firewall konfigürasyonu
- Yazıcı/Tarayıcı (2 adet)
- Projeksiyon sistemi (toplantı odası)
- IP telefon (25 adet)

Lokasyon: E Blok 3. kat
Teslim Tarihi: 2 hafta
Bütçe: Onaylandı (450.000 TL)''',
            'priority': '1',
            'maintenance_type': 'preventive',
            'employee_id': data['employees'].get('Ali Özkan', False),
            'request_date': datetime.now() - timedelta(days=2)
        },

        # Güvenlik Güncellemesi
        {
            'name': '🔒 [GÜVENLİK] Kritik Firewall Patch Güncellemesi',
            'description': '''ZORUNLU GÜVENLİK GÜNCELLEMESİ

Vendor: Fortinet
Model: FortiGate 600E
Güncelleme: FortiOS 7.2.8 (Critical Security Patch)

Düzeltilen Açıklar:
- CVE-2024-12345 (CVSS: 9.8/10) - RCE vulnerability
- CVE-2024-12346 (CVSS: 8.5/10) - Authentication bypass
- CVE-2024-12347 (CVSS: 7.2/10) - Privilege escalation

Planlama:
- Test ortamında denendi: ✓
- Backup alındı: ✓
- Rollback planı hazır: ✓
- Uygulama zamanı: Bu gece 23:00-00:00

Risk: Düşük (test edildi)
Downtime: Max 15 dakika''',
            'priority': '2',
            'maintenance_type': 'preventive',
            'equipment_id': data['equipment'][4] if len(data['equipment']) > 4 else False,
            'employee_id': data['employees'].get('Can Aydın', False),
            'request_date': datetime.now() - timedelta(hours=5)
        },

        # Performans Sorunu
        {
            'name': '🐌 [PERFORMANS] ERP Sistemi Aşırı Yavaş',
            'description': '''Kullanıcılardan yoğun şikayet var!

Sorun:
- Login süresi: 2-3 dakika (Normal: 5-10 saniye)
- Rapor açılma: 5+ dakika
- Kayıt işlemleri timeout veriyor

İlk Analiz:
- Database CPU: %100 (sürekli)
- Disk I/O: 950 MB/s (bottleneck)
- Active sessions: 245 (Normal: 100-150)
- Slow queries tespit edildi

Şüpheli Sebepler:
1. Index corruption
2. Statistics güncelleme gerekiyor
3. Disk fragmentasyonu
4. Kötü optimize edilmiş sorgular

Acil müdahale başlatılıyor...''',
            'priority': '2',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][2] if len(data['equipment']) > 2 else False,
            'employee_id': data['employees'].get('Deniz Arslan', False),
            'request_date': datetime.now() - timedelta(hours=1)
        },

        # Elektrik Kesintisi
        {
            'name': '⚡ [ARIZA] A Blok 2. Kat Kısmi Elektrik Kesintisi',
            'description': '''Elektrik kesintisi rapor edildi

Etkilenen Alan:
- A Blok 2. kat doğu kanadı
- 12 ofis
- 25 kullanıcı

Tespit:
- Ana şalter: Normal
- UPS: Bypass modda
- Sigorta: F-24 atmış
- Kaçak akım rölesi: Devrede

Muhtemel Sebep:
- Yüksek yük (klima + ısıtıcılar)
- Eski kablolama
- Faz dengesizliği

Geçici Çözüm:
- Jeneratörden besleme yapıldı
- Non-kritik yükler kapatıldı

Kalıcı çözüm için elektrik müteahhit çağrıldı.''',
            'priority': '2',
            'maintenance_type': 'corrective',
            'employee_id': data['employees'].get('Gül Yılmaz', False),
            'request_date': datetime.now() - timedelta(hours=3)
        },

        # Veri Yedekleme Hatası
        {
            'name': '💾 [HATA] Kritik Backup İşlemi 3 Gündür Başarısız',
            'description': '''YEDEKLEME HATASI - ACİL MÜDAHALE

Sistem: Veeam Backup & Replication
Son Başarılı Backup: 3 gün önce

Hata Detayları:
- Job: DAILY_FULL_BACKUP
- Error: "Insufficient storage space"
- Repository: NAS-BACKUP-01
- Kullanılan Alan: 95% (18.5 TB / 20 TB)

Risk Analizi:
- 3 günlük veri yedeksiz
- RPO ihlali (SLA: 24 saat)
- Kritik sistemler risk altında

Çözüm Planı:
1. Eski yedekleri temizle (6 ay üzeri)
2. Deduplication oranını artır
3. Yeni storage ekle (acil satın alma)
4. Manuel backup başlat

Tahmini çözüm: 4 saat''',
            'priority': '3',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][1] if len(data['equipment']) > 1 else False,
            'employee_id': data['employees'].get('Cem Yıldız', False),
            'request_date': datetime.now() - timedelta(hours=6)
        },

        # CNC Makine Bakımı
        {
            'name': '⚙️ [BAKIM] CNC Torna Aylık Periyodik Bakım',
            'description': '''Planlı Makine Bakımı

Makine: Haas VF-4 CNC Torna
Seri No: HAAS-VF4-001
Çalışma Saati: 8,456 saat
Son Bakım: 30 gün önce

Yapılacaklar:
□ Yağ seviyesi kontrolü ve değişimi
□ Filtre değişimi (yağ, hava, hidrolik)
□ Rulman yağlama
□ Encoder temizliği
□ Spindle alignment kontrolü
□ Coolant sistemi temizliği
□ Way temizliği ve yağlama
□ Elektrik bağlantı kontrolü
□ Program backup
□ Kalibrasyon testi

Süre: 2 saat
Üretim Durumu: Durdurulacak''',
            'priority': '1',
            'maintenance_type': 'preventive',
            'equipment_id': data['equipment'][8] if len(data['equipment']) > 8 else False,
            'schedule_date': datetime.now() + timedelta(days=1),
            'employee_id': data['employees'].get('Hakan Demir', False),
            'request_date': datetime.now() - timedelta(days=1)
        }
    ]

    for req_data in advanced_requests:
        try:
            # Requester seç
            req_data['requester_id'] = random.choice(requesters) if requesters else False

            # Building seç
            req_data['building_id'] = random.choice(list(data['buildings'].values())) if data['buildings'] else False

            # SLA seç (priority'ye göre)
            if req_data['priority'] == '3':  # Critical
                req_data['sla_id'] = data['slas'].get('Kritik Sistemler SLA (7/24)', False)
            elif req_data['priority'] == '2':  # High
                req_data['sla_id'] = data['slas'].get('Standart SLA (Mesai Saatleri)', False)
            else:
                req_data['sla_id'] = data['slas'].get('VIP SLA (Yönetim)', False)

            # Tarih formatla
            req_data['request_date'] = req_data['request_date'].strftime('%Y-%m-%d %H:%M:%S')
            if 'schedule_date' in req_data:
                req_data['schedule_date'] = req_data['schedule_date'].strftime('%Y-%m-%d')

            req_id = create('maintenance.request', req_data)
            if req_id:
                data['requests'].append(req_id)
                print(f"  ✓ Talep: {req_data['name'][:60]}...")
        except Exception as e:
            print(f"  ✗ Talep hatası: {str(e)[:80]}")

    # ================================================
    # 10. İŞ EMİRLERİ (WORK ORDERS)
    # ================================================
    print("\n[10] 📝 İş Emirleri (Work Orders) oluşturuluyor...")

    # Project oluştur/bul
    project_ids = search('project.project', [('name', '=', 'Teknik Servis İşleri')])
    if not project_ids:
        project_id = create('project.project', {
            'name': 'Teknik Servis İşleri',
            'company_id': company_id,
            'partner_id': company_id
        })
    else:
        project_id = project_ids[0]

    # İlk 7 request için iş emri oluştur
    for i, req_id in enumerate(data['requests'][:7]):
        try:
            # Request bilgilerini oku
            req_info = read('maintenance.request', [req_id], ['name', 'description', 'priority', 'employee_id'])
            if req_info:
                req = req_info[0]

                # Teknisyen seç
                assigned_user = random.choice(list(data['users'].values()))

                # Durum belirle
                stages = ['new', 'in_progress', 'done', 'cancelled']
                stage_weights = [0.2, 0.4, 0.3, 0.1]
                stage = random.choices(stages, weights=stage_weights)[0]

                task_data = {
                    'name': f"WO-2024-{i+100:04d}: {req['name'][:60]}",
                    'project_id': project_id,
                    'description': req.get('description', ''),
                    'priority': '1' if req.get('priority') == '3' else '0',
                    'user_ids': [(6, 0, [assigned_user])],
                    'planned_hours': random.randint(1, 8),
                    'date_deadline': (datetime.now() + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d')
                }

                task_id = create('project.task', task_data)
                if task_id:
                    data['work_orders'].append(task_id)
                    print(f"  ✓ İş Emri: WO-2024-{i+100:04d} [{stage}]")

        except Exception as e:
            print(f"  ✗ İş emri hatası: {str(e)[:80]}")

    # ================================================
    # ÖZET RAPOR
    # ================================================
    print("\n" + "="*70)
    print("📊 DEMO DATA ÖZET RAPORU")
    print("="*70)

    summary = [
        ('Çalışanlar', len(data['employees'])),
        ('Kampüsler', len(data['campuses'])),
        ('Binalar', len(data['buildings'])),
        ('Servis Ekipleri', len(data['teams'])),
        ('Ekipman Kategorileri', len(data['categories'])),
        ('Ekipmanlar', len(data['equipment'])),
        ('SLA Politikaları', len(data['slas'])),
        ('Bakım Sözleşmeleri', len(data['contracts'])),
        ('Bakım Talepleri', len(data['requests'])),
        ('İş Emirleri', len(data['work_orders'])),
        ('Yedek Parçalar', len(data['spare_parts']))
    ]

    total = 0
    for label, count in summary:
        print(f"  ✓ {label:25} : {count:5} kayıt")
        total += count

    print("-" * 50)
    print(f"  📈 TOPLAM                 : {total:5} kayıt")

    print("\n" + "="*70)
    print("✅ TÜM DEMO VERİLER BAŞARIYLA OLUŞTURULDU!")
    print("="*70)

    print("\n🌐 Web Arayüzü:")
    print(f"  URL      : {url}")
    print(f"  Database : {db}")
    print(f"  Kullanıcı: {username}")
    print(f"  Şifre    : {password}")

    print("\n📱 Menü Yapısı:")
    print("  • Technical Service")
    print("    ├── Dashboard")
    print("    ├── Service Management")
    print("    │   ├── Service Requests")
    print("    │   └── Work Orders")
    print("    ├── Asset Management")
    print("    │   ├── Assets/Equipment")
    print("    │   └── Maintenance Contracts")
    print("    ├── Reporting")
    print("    └── Configuration")
    print("        ├── Campuses")
    print("        ├── Buildings")
    print("        ├── SLA Policies")
    print("        └── Service Teams")

    print("\n💡 Demo Senaryoları:")
    print("  1. Kritik sunucu arızası takibi")
    print("  2. Planlı bakım yönetimi")
    print("  3. SLA performans analizi")
    print("  4. Ekip iş yükü dengeleme")
    print("  5. Sözleşme takibi")
    print("  6. Yedek parça yönetimi")

    print("\n🎯 Sistem kullanıma hazır!")

except xmlrpc.client.Fault as error:
    print(f"\n❌ Odoo Hatası: {error.faultString}")

except Exception as e:
    print(f"\n❌ Beklenmeyen hata: {str(e)}")
    import traceback
    traceback.print_exc()