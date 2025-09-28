#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Technical Service Demo Data Generator
Satış sunumu için kapsamlı örnek veri oluşturma scripti
"""

import logging
from datetime import datetime, timedelta
import random

_logger = logging.getLogger(__name__)

def create_demo_data(env):
    """Ana veri oluşturma fonksiyonu"""

    print("\n" + "="*60)
    print("TECHNICAL SERVICE - DEMO DATA OLUŞTURMA")
    print("="*60)

    # 1. ŞIRKET BİLGİLERİNİ GÜNCELLE
    print("\n[1/10] Şirket bilgileri güncelleniyor...")
    try:
        company = env.company
        company.write({
            'name': 'TechnoFix Global Services A.Ş.',
            'street': 'Teknoloji Bulvarı No:42',
            'city': 'İstanbul',
            'zip': '34000',
            'phone': '+90 212 555 1234',
            'email': 'info@technofix.com.tr',
            'website': 'www.technofix.com.tr',
            'vat': 'TR1234567890'
        })
        print("✓ Şirket bilgileri güncellendi: TechnoFix Global Services A.Ş.")
    except Exception as e:
        print(f"✗ Hata: {str(e)}")

    # 2. DEPARTMANLAR
    print("\n[2/10] Departmanlar oluşturuluyor...")
    departments = {}
    dept_data = [
        'Bilgi İşlem',
        'Üretim',
        'İnsan Kaynakları',
        'Teknik İşler',
        'İdari İşler',
        'Ar-Ge',
        'Kalite Kontrol'
    ]

    Department = env['hr.department']
    for dept_name in dept_data:
        try:
            dept = Department.search([('name', '=', dept_name)], limit=1)
            if not dept:
                dept = Department.create({'name': dept_name})
            departments[dept_name] = dept
            print(f"  ✓ {dept_name} departmanı oluşturuldu")
        except Exception as e:
            print(f"  ✗ {dept_name} oluşturulamadı: {str(e)}")

    # 3. KULLANICILAR VE ÇALIŞANLAR
    print("\n[3/10] Kullanıcılar ve çalışanlar oluşturuluyor...")
    ResUsers = env['res.users']
    Employee = env['hr.employee']

    users_data = [
        # Service Managers
        {'name': 'Ahmet Yılmaz', 'login': 'ahmet.yilmaz@technofix.com', 'job': 'Servis Müdürü', 'dept': 'Teknik İşler'},

        # Team Leaders
        {'name': 'Mehmet Demir', 'login': 'mehmet.demir@technofix.com', 'job': 'IT Takım Lideri', 'dept': 'Bilgi İşlem'},
        {'name': 'Ayşe Kaya', 'login': 'ayse.kaya@technofix.com', 'job': 'Teknik Takım Lideri', 'dept': 'Teknik İşler'},

        # Technicians
        {'name': 'Ali Özkan', 'login': 'ali.ozkan@technofix.com', 'job': 'Kıdemli IT Teknisyeni', 'dept': 'Bilgi İşlem'},
        {'name': 'Fatma Şahin', 'login': 'fatma.sahin@technofix.com', 'job': 'Network Uzmanı', 'dept': 'Bilgi İşlem'},
        {'name': 'Can Aydın', 'login': 'can.aydin@technofix.com', 'job': 'Donanım Teknisyeni', 'dept': 'Bilgi İşlem'},
        {'name': 'Zeynep Arslan', 'login': 'zeynep.arslan@technofix.com', 'job': 'Elektrik Teknisyeni', 'dept': 'Teknik İşler'},
        {'name': 'Murat Çelik', 'login': 'murat.celik@technofix.com', 'job': 'HVAC Teknisyeni', 'dept': 'Teknik İşler'},
        {'name': 'Elif Güneş', 'login': 'elif.gunes@technofix.com', 'job': 'Junior Teknisyen', 'dept': 'Teknik İşler'},

        # Requesters
        {'name': 'Hakan Yıldız', 'login': 'hakan.yildiz@technofix.com', 'job': 'IT Müdürü', 'dept': 'Bilgi İşlem'},
        {'name': 'Seda Korkmaz', 'login': 'seda.korkmaz@technofix.com', 'job': 'Üretim Müdürü', 'dept': 'Üretim'},
        {'name': 'Burak Öztürk', 'login': 'burak.ozturk@technofix.com', 'job': 'İK Uzmanı', 'dept': 'İnsan Kaynakları'},
    ]

    employees = {}
    for user_data in users_data:
        try:
            # Kullanıcı oluştur veya bul
            user = ResUsers.search([('login', '=', user_data['login'])], limit=1)
            if not user:
                user = ResUsers.create({
                    'name': user_data['name'],
                    'login': user_data['login'],
                    'email': user_data['login'],
                    'password': 'demo123',  # Demo için basit şifre
                })

            # Çalışan kaydı oluştur
            employee = Employee.search([('user_id', '=', user.id)], limit=1)
            if not employee:
                employee = Employee.create({
                    'name': user_data['name'],
                    'user_id': user.id,
                    'job_id': env['hr.job'].search([('name', '=', user_data['job'])], limit=1).id or
                             env['hr.job'].create({'name': user_data['job']}).id,
                    'department_id': departments.get(user_data['dept']).id if user_data['dept'] in departments else False,
                    'work_email': user_data['login'],
                    'work_phone': f'+90 212 555 {random.randint(1000, 9999)}'
                })

            employees[user_data['name']] = employee
            print(f"  ✓ {user_data['name']} - {user_data['job']}")

        except Exception as e:
            print(f"  ✗ {user_data['name']} oluşturulamadı: {str(e)}")

    # 4. LOKASYONLAR (KAMPÜS VE BİNALAR)
    print("\n[4/10] Lokasyonlar oluşturuluyor...")
    Campus = env['technical_service.campus']
    Building = env['technical_service.building']

    campus_data = [
        {
            'name': 'Ana Kampüs - Levent',
            'code': 'MAIN-LEV',
            'address': 'Levent Mahallesi, Teknoloji Bulvarı No:42',
            'buildings': [
                {'name': 'A Blok - Yönetim Binası', 'code': 'A-BLK', 'floor_count': 5},
                {'name': 'B Blok - Üretim Tesisi', 'code': 'B-BLK', 'floor_count': 3},
                {'name': 'C Blok - IT Merkezi', 'code': 'C-BLK', 'floor_count': 4}
            ]
        },
        {
            'name': 'Ar-Ge Kampüsü - Teknopark',
            'code': 'RND-TEK',
            'address': 'İTÜ Teknokent, Maslak',
            'buildings': [
                {'name': 'İnovasyon Merkezi', 'code': 'INV-CTR', 'floor_count': 6},
                {'name': 'Test Laboratuvarı', 'code': 'TEST-LAB', 'floor_count': 2}
            ]
        }
    ]

    campuses = {}
    buildings = {}

    for campus_info in campus_data:
        try:
            campus = Campus.search([('code', '=', campus_info['code'])], limit=1)
            if not campus:
                campus = Campus.create({
                    'name': campus_info['name'],
                    'code': campus_info['code'],
                    'address': campus_info['address']
                })
            campuses[campus_info['code']] = campus
            print(f"  ✓ Kampüs: {campus_info['name']}")

            # Binaları oluştur
            for building_info in campus_info['buildings']:
                building = Building.search([
                    ('code', '=', building_info['code']),
                    ('campus_id', '=', campus.id)
                ], limit=1)
                if not building:
                    floors = []
                    for i in range(1, building_info['floor_count'] + 1):
                        floors.append(f"{i}. Kat")

                    building = Building.create({
                        'name': building_info['name'],
                        'code': building_info['code'],
                        'campus_id': campus.id,
                        'floor_count': building_info['floor_count'],
                        'floors': ', '.join(floors)
                    })
                buildings[building_info['code']] = building
                print(f"    ✓ Bina: {building_info['name']}")

        except Exception as e:
            print(f"  ✗ {campus_info['name']} oluşturulamadı: {str(e)}")

    # 5. SERVİS EKİPLERİ
    print("\n[5/10] Servis ekipleri oluşturuluyor...")
    Team = env['technical_service.team']

    teams_data = [
        {
            'name': 'IT Destek Ekibi',
            'code': 'IT-TEAM',
            'specialization': 'it',
            'shift_type': 'regular',
            'team_leader': 'Mehmet Demir',
            'members': ['Ali Özkan', 'Fatma Şahin', 'Can Aydın']
        },
        {
            'name': 'Teknik Destek Ekibi',
            'code': 'TECH-TEAM',
            'specialization': 'technical',
            'shift_type': '3_shifts',
            'team_leader': 'Ayşe Kaya',
            'members': ['Zeynep Arslan', 'Murat Çelik', 'Elif Güneş']
        },
        {
            'name': 'Acil Müdahale Ekibi',
            'code': 'EMERGENCY',
            'specialization': 'mixed',
            'shift_type': '24_7',
            'team_leader': 'Ahmet Yılmaz',
            'members': ['Can Aydın', 'Murat Çelik']
        }
    ]

    teams = {}
    for team_data in teams_data:
        try:
            team = Team.search([('code', '=', team_data['code'])], limit=1)
            if not team:
                # Ekip üyelerini bul
                member_ids = []
                for member_name in team_data['members']:
                    if member_name in employees:
                        member_ids.append(employees[member_name].id)

                # Takım liderini bul
                leader_id = False
                if team_data['team_leader'] in employees:
                    leader_id = employees[team_data['team_leader']].id

                # Kampüsleri ekle (tüm kampüsler)
                campus_ids = [(6, 0, [c.id for c in Campus.search([])])]

                team = Team.create({
                    'name': team_data['name'],
                    'code': team_data['code'],
                    'specialization': team_data['specialization'],
                    'shift_type': team_data['shift_type'],
                    'team_leader_id': leader_id,
                    'member_ids': [(6, 0, member_ids)],
                    'campus_ids': campus_ids,
                    'active': True
                })

            teams[team_data['code']] = team
            print(f"  ✓ {team_data['name']} ({len(team_data['members'])} üye)")

        except Exception as e:
            print(f"  ✗ {team_data['name']} oluşturulamadı: {str(e)}")

    # 6. EKİPMAN KATEGORİLERİ VE VARLIKLAR
    print("\n[6/10] Ekipman kategorileri ve varlıklar oluşturuluyor...")
    Category = env['maintenance.equipment.category']
    Equipment = env['maintenance.equipment']

    # Kategoriler
    categories_data = [
        {'name': 'Bilgisayar Ekipmanları', 'code': 'IT-COMP'},
        {'name': 'Network Ekipmanları', 'code': 'IT-NET'},
        {'name': 'Sunucular', 'code': 'IT-SRV'},
        {'name': 'Üretim Makineleri', 'code': 'PROD-MACH'},
        {'name': 'HVAC Sistemleri', 'code': 'FAC-HVAC'},
        {'name': 'Güç Sistemleri', 'code': 'FAC-POWER'}
    ]

    categories = {}
    for cat_data in categories_data:
        try:
            category = Category.search([('name', '=', cat_data['name'])], limit=1)
            if not category:
                category = Category.create({
                    'name': cat_data['name'],
                    'technician_user_id': env.user.id
                })
            categories[cat_data['code']] = category
            print(f"  ✓ Kategori: {cat_data['name']}")
        except Exception as e:
            print(f"  ✗ Kategori {cat_data['name']} oluşturulamadı: {str(e)}")

    # Ekipmanlar
    equipment_data = [
        # IT Ekipmanları
        {
            'name': 'Dell PowerEdge R750 - Ana Sunucu',
            'category': 'IT-SRV',
            'serial_no': 'DPE-R750-001',
            'model': 'PowerEdge R750',
            'location': 'C Blok - Server Room',
            'criticality': 'critical',
            'partner_id': 'Dell Technologies'
        },
        {
            'name': 'Fortinet FortiGate 600E - Firewall',
            'category': 'IT-NET',
            'serial_no': 'FG-600E-001',
            'model': 'FortiGate 600E',
            'location': 'C Blok - Network Room',
            'criticality': 'critical',
            'partner_id': 'Fortinet'
        },
        {
            'name': 'Cisco Catalyst 9300 - Core Switch',
            'category': 'IT-NET',
            'serial_no': 'CS-9300-001',
            'model': 'Catalyst 9300',
            'location': 'C Blok - Network Room',
            'criticality': 'high'
        },
        # Üretim Ekipmanları
        {
            'name': 'Haas VF-4 CNC Torna',
            'category': 'PROD-MACH',
            'serial_no': 'HAAS-VF4-001',
            'model': 'VF-4',
            'location': 'B Blok - Üretim Hattı 1',
            'criticality': 'critical'
        },
        {
            'name': 'Hydraulic Press 200T',
            'category': 'PROD-MACH',
            'serial_no': 'HP-200T-001',
            'model': 'HP-200T',
            'location': 'B Blok - Üretim Hattı 2',
            'criticality': 'high'
        },
        # Tesis Ekipmanları
        {
            'name': 'Daikin VRV IV Klima Sistemi',
            'category': 'FAC-HVAC',
            'serial_no': 'DAI-VRV-001',
            'model': 'VRV IV',
            'location': 'A Blok - Çatı',
            'criticality': 'medium'
        },
        {
            'name': 'Caterpillar 500kVA Jeneratör',
            'category': 'FAC-POWER',
            'serial_no': 'CAT-500-001',
            'model': '500kVA',
            'location': 'Enerji Odası',
            'criticality': 'critical'
        },
        {
            'name': 'APC Symmetra 80kVA UPS',
            'category': 'FAC-POWER',
            'serial_no': 'APC-80K-001',
            'model': 'Symmetra 80kVA',
            'location': 'C Blok - UPS Room',
            'criticality': 'critical'
        }
    ]

    equipments = []
    for eq_data in equipment_data:
        try:
            # Partner bul veya oluştur
            partner = None
            if 'partner_id' in eq_data:
                Partner = env['res.partner']
                partner = Partner.search([('name', '=', eq_data['partner_id'])], limit=1)
                if not partner:
                    partner = Partner.create({
                        'name': eq_data['partner_id'],
                        'is_company': True,
                        'supplier_rank': 1
                    })

            equipment = Equipment.search([('serial_no', '=', eq_data['serial_no'])], limit=1)
            if not equipment:
                equipment = Equipment.create({
                    'name': eq_data['name'],
                    'category_id': categories[eq_data['category']].id if eq_data['category'] in categories else False,
                    'serial_no': eq_data['serial_no'],
                    'model': eq_data.get('model', ''),
                    'location': eq_data.get('location', ''),
                    'partner_id': partner.id if partner else False,
                    'assign_date': datetime.now() - timedelta(days=random.randint(30, 365)),
                    'warranty_date': datetime.now() + timedelta(days=random.randint(180, 730))
                })
            equipments.append(equipment)
            print(f"  ✓ Ekipman: {eq_data['name']}")

        except Exception as e:
            print(f"  ✗ Ekipman {eq_data['name']} oluşturulamadı: {str(e)}")

    # 7. SLA POLİTİKALARI
    print("\n[7/10] SLA politikaları oluşturuluyor...")
    SLA = env['technical_service.sla']

    sla_data = [
        {
            'name': 'Standart SLA - Genel Kullanıcılar',
            'active': True,
            'business_hours_start': 8.0,
            'business_hours_end': 17.0,
            'working_days': 'weekdays',
            'priorities': [
                {'priority': 'critical', 'response_time': 0.5, 'resolution_time': 4},
                {'priority': 'high', 'response_time': 2, 'resolution_time': 8},
                {'priority': 'medium', 'response_time': 4, 'resolution_time': 24},
                {'priority': 'low', 'response_time': 8, 'resolution_time': 72}
            ]
        },
        {
            'name': 'Premium SLA - Üretim ve Kritik Sistemler',
            'active': True,
            'business_hours_start': 0.0,
            'business_hours_end': 23.99,
            'working_days': 'all',
            'priorities': [
                {'priority': 'critical', 'response_time': 0.25, 'resolution_time': 2},
                {'priority': 'high', 'response_time': 1, 'resolution_time': 4},
                {'priority': 'medium', 'response_time': 2, 'resolution_time': 12}
            ]
        },
        {
            'name': 'VIP SLA - Yönetim',
            'active': True,
            'business_hours_start': 7.0,
            'business_hours_end': 20.0,
            'working_days': 'weekdays',
            'priorities': [
                {'priority': 'critical', 'response_time': 0.25, 'resolution_time': 2},
                {'priority': 'high', 'response_time': 0.5, 'resolution_time': 4},
                {'priority': 'medium', 'response_time': 1, 'resolution_time': 8},
                {'priority': 'low', 'response_time': 2, 'resolution_time': 24}
            ]
        }
    ]

    slas = {}
    for sla_info in sla_data:
        try:
            sla = SLA.search([('name', '=', sla_info['name'])], limit=1)
            if not sla:
                # Priority matrix oluştur
                priority_matrix = []
                for pri in sla_info['priorities']:
                    priority_matrix.append((0, 0, {
                        'priority': pri['priority'],
                        'response_time': pri['response_time'],
                        'resolution_time': pri['resolution_time']
                    }))

                sla = SLA.create({
                    'name': sla_info['name'],
                    'active': sla_info['active'],
                    'business_hours_start': sla_info['business_hours_start'],
                    'business_hours_end': sla_info['business_hours_end'],
                    'working_days': sla_info['working_days'],
                    'priority_ids': priority_matrix,
                    'escalation_after': 75.0,
                    'escalation_team_id': teams.get('EMERGENCY').id if 'EMERGENCY' in teams else False
                })
            slas[sla_info['name']] = sla
            print(f"  ✓ SLA: {sla_info['name']}")

        except Exception as e:
            print(f"  ✗ SLA {sla_info['name']} oluşturulamadı: {str(e)}")

    # 8. BAKIM SÖZLEŞMELERİ
    print("\n[8/10] Bakım sözleşmeleri oluşturuluyor...")
    Contract = env['technical_service.contract']

    contracts_data = [
        {
            'name': 'Üretim Ekipmanları Yıllık Bakım',
            'contract_number': 'CNT-2024-001',
            'contract_type': 'amc',
            'start_date': datetime.now().date(),
            'end_date': (datetime.now() + timedelta(days=365)).date(),
            'total_value': 250000.0,
            'coverage_type': '24_7',
            'response_time': 2.0,
            'equipment_ids': ['HAAS-VF4-001', 'HP-200T-001']
        },
        {
            'name': 'IT Altyapı Bakım Sözleşmesi',
            'contract_number': 'CNT-2024-002',
            'contract_type': 'preventive',
            'start_date': datetime.now().date(),
            'end_date': (datetime.now() + timedelta(days=365)).date(),
            'total_value': 180000.0,
            'coverage_type': 'business_hours',
            'response_time': 4.0,
            'equipment_ids': ['DPE-R750-001', 'FG-600E-001', 'CS-9300-001']
        },
        {
            'name': 'Kritik Sistemler 7/24 Destek',
            'contract_number': 'CNT-2024-003',
            'contract_type': 'comprehensive',
            'start_date': datetime.now().date(),
            'end_date': (datetime.now() + timedelta(days=730)).date(),
            'total_value': 500000.0,
            'coverage_type': '24_7',
            'response_time': 1.0,
            'services_included': 'unlimited'
        }
    ]

    for contract_data in contracts_data:
        try:
            contract = Contract.search([('contract_number', '=', contract_data['contract_number'])], limit=1)
            if not contract:
                # Equipment'ları bul
                equipment_ids = []
                if 'equipment_ids' in contract_data:
                    for serial in contract_data['equipment_ids']:
                        eq = Equipment.search([('serial_no', '=', serial)], limit=1)
                        if eq:
                            equipment_ids.append(eq.id)

                contract = Contract.create({
                    'name': contract_data['name'],
                    'contract_number': contract_data['contract_number'],
                    'contract_type': contract_data['contract_type'],
                    'customer_id': env.company.partner_id.id,
                    'start_date': contract_data['start_date'],
                    'end_date': contract_data['end_date'],
                    'total_value': contract_data['total_value'],
                    'coverage_type': contract_data['coverage_type'],
                    'response_time': contract_data['response_time'],
                    'equipment_ids': [(6, 0, equipment_ids)] if equipment_ids else False,
                    'state': 'active'
                })
            print(f"  ✓ Sözleşme: {contract_data['name']}")

        except Exception as e:
            print(f"  ✗ Sözleşme {contract_data['name']} oluşturulamadı: {str(e)}")

    # 9. SERVİS TALEPLERİ
    print("\n[9/10] Servis talepleri oluşturuluyor...")
    Request = env['technical_service.request']

    requests_data = [
        # Kritik - Sunucu Arızası (Çözümleniyor)
        {
            'name': 'Ana Sunucu Erişim Problemi - KRİTİK',
            'request_type': 'incident',
            'priority': 'critical',
            'description': 'ERP sunucusuna erişilemiyor, tüm üretim durdu! Acil müdahale gerekiyor.',
            'requester': 'Hakan Yıldız',
            'equipment': 'DPE-R750-001',
            'location': 'C-BLK',
            'state': 'in_progress'
        },

        # Yüksek - Network Yavaşlığı (Atandı)
        {
            'name': 'Üretim Hattı Network Performans Sorunu',
            'request_type': 'problem',
            'priority': 'high',
            'description': 'Üretim hattında ciddi network yavaşlığı var. Veri transferi gecikiyor ve üretim aksamaya başladı.',
            'requester': 'Seda Korkmaz',
            'location': 'B-BLK',
            'state': 'assigned'
        },

        # Orta - Yeni Kullanıcı (Yeni)
        {
            'name': 'Yeni Personel IT Kurulum Talebi',
            'request_type': 'service_request',
            'priority': 'medium',
            'description': '''3 yeni personel için aşağıdaki kurulumlar gerekiyor:
            - Bilgisayar tahsisi ve kurulumu
            - Domain kullanıcısı oluşturma
            - E-posta hesabı açma
            - ERP ve diğer sistem yetkileri''',
            'requester': 'Burak Öztürk',
            'state': 'new'
        },

        # Düşük - Yazıcı (Çözümlendi)
        {
            'name': 'Yazıcı Kağıt Sıkışması',
            'request_type': 'incident',
            'priority': 'low',
            'description': '2. kat fotokopi makinesinde kağıt sıkışması, kullanıcılar yazdıramıyor.',
            'requester': 'Elif Güneş',
            'location': 'A-BLK',
            'state': 'resolved',
            'resolution_notes': 'Kağıt sıkışması giderildi, drum temizliği yapıldı.'
        },

        # Önleyici Bakım (Planlandı)
        {
            'name': 'Aylık Sunucu Bakımı - Ocak 2024',
            'request_type': 'preventive',
            'priority': 'medium',
            'description': 'Planlı aylık sunucu bakımı: Güncelleme, yedekleme kontrolü, performans analizi',
            'requester': 'Mehmet Demir',
            'equipment': 'DPE-R750-001',
            'state': 'scheduled',
            'scheduled_date': datetime.now() + timedelta(days=5)
        },

        # Change Request (Onay Bekliyor)
        {
            'name': 'Firewall Kural Güncelleme - VPN Erişimi',
            'request_type': 'change',
            'priority': 'high',
            'description': '''Yeni VPN kullanıcıları için firewall kuralı güncellenmeli:
            - 10 yeni uzaktan çalışan için VPN erişimi
            - Port açma: 1194/UDP
            - IP range: 192.168.100.0/24''',
            'requester': 'Mehmet Demir',
            'equipment': 'FG-600E-001',
            'state': 'pending_approval'
        },

        # Kritik - Klima Arızası (İptal Edildi)
        {
            'name': 'Server Room Klima Arızası',
            'request_type': 'incident',
            'priority': 'critical',
            'description': 'Server room sıcaklığı kritik seviyede! Klima sistemi çalışmıyor.',
            'requester': 'Ali Özkan',
            'location': 'C-BLK',
            'state': 'cancelled',
            'cancel_reason': 'Klima otomatik olarak devreye girdi, sorun kendiliğinden çözüldü.'
        },

        # Orta - Ekipman Değişimi (Tamamlandı)
        {
            'name': 'Eski Switch Değişimi',
            'request_type': 'service_request',
            'priority': 'medium',
            'description': '3. kat switch\'i eskidiği için yenisi ile değiştirilmeli.',
            'requester': 'Fatma Şahin',
            'location': 'A-BLK',
            'state': 'closed',
            'resolution_notes': 'Switch değişimi tamamlandı, konfigürasyon yüklendi, testler başarılı.'
        },

        # Yüksek - Elektrik Kesintisi (İlerlemede)
        {
            'name': 'B Blok Kısmi Elektrik Kesintisi',
            'request_type': 'incident',
            'priority': 'high',
            'description': 'B Blok 2. katta kısmi elektrik kesintisi var, üretim hattının yarısı çalışmıyor.',
            'requester': 'Seda Korkmaz',
            'location': 'B-BLK',
            'state': 'in_progress'
        },

        # Orta - Yedekleme Hatası (Atandı)
        {
            'name': 'Otomatik Yedekleme Başarısız',
            'request_type': 'problem',
            'priority': 'medium',
            'description': 'Son 3 gündür otomatik yedekleme işlemi başarısız oluyor. Log\'larda disk alanı hatası görünüyor.',
            'requester': 'Hakan Yıldız',
            'equipment': 'DPE-R750-001',
            'state': 'assigned'
        }
    ]

    created_requests = []
    for req_data in requests_data:
        try:
            # Requester'ı bul
            requester = False
            if req_data['requester'] in employees:
                requester = employees[req_data['requester']].user_id.partner_id.id

            # Equipment'ı bul
            equipment = False
            if 'equipment' in req_data:
                eq = Equipment.search([('serial_no', '=', req_data['equipment'])], limit=1)
                if eq:
                    equipment = eq.id

            # Building'i bul
            building = False
            if 'location' in req_data:
                bld = Building.search([('code', '=', req_data['location'])], limit=1)
                if bld:
                    building = bld.id

            # SLA belirle
            sla = False
            if req_data['priority'] == 'critical':
                sla = slas.get('Premium SLA - Üretim ve Kritik Sistemler', False)
            elif req_data['requester'] in ['Ahmet Yılmaz', 'Mehmet Demir', 'Ayşe Kaya']:
                sla = slas.get('VIP SLA - Yönetim', False)
            else:
                sla = slas.get('Standart SLA - Genel Kullanıcılar', False)

            request_vals = {
                'name': req_data['name'],
                'request_type': req_data['request_type'],
                'priority': req_data['priority'],
                'description': req_data['description'],
                'requester_id': requester,
                'equipment_id': equipment,
                'building_id': building,
                'state': req_data['state'],
                'sla_id': sla.id if sla else False
            }

            # Ek alanlar
            if 'resolution_notes' in req_data:
                request_vals['resolution_notes'] = req_data['resolution_notes']
            if 'cancel_reason' in req_data:
                request_vals['cancel_reason'] = req_data['cancel_reason']
            if 'scheduled_date' in req_data:
                request_vals['scheduled_date'] = req_data['scheduled_date']

            request = Request.create(request_vals)
            created_requests.append(request)
            print(f"  ✓ Talep: {req_data['name'][:50]}... [{req_data['state']}]")

        except Exception as e:
            print(f"  ✗ Talep {req_data['name'][:30]}... oluşturulamadı: {str(e)}")

    # 10. İŞ EMİRLERİ
    print("\n[10/10] İş emirleri oluşturuluyor...")
    WorkOrder = env['technical_service.work_order']

    # Sadece uygun durumdaki talepler için iş emri oluştur
    for request in created_requests:
        if request.state in ['assigned', 'in_progress', 'resolved', 'closed']:
            try:
                # Teknisyen seç
                technician = False
                if request.priority == 'critical':
                    technician = employees.get('Ali Özkan', False)
                elif request.request_type == 'incident':
                    technician = employees.get('Can Aydın', False)
                elif request.request_type == 'problem':
                    technician = employees.get('Fatma Şahin', False)
                else:
                    technician = employees.get('Elif Güneş', False)

                # Ekip seç
                team = False
                if 'network' in request.name.lower() or 'sunucu' in request.name.lower():
                    team = teams.get('IT-TEAM', False)
                elif 'elektrik' in request.name.lower() or 'klima' in request.name.lower():
                    team = teams.get('TECH-TEAM', False)
                else:
                    team = teams.get('IT-TEAM', False)

                wo_vals = {
                    'request_id': request.id,
                    'priority': request.priority,
                    'assigned_technician_id': technician.id if technician else False,
                    'team_id': team.id if team else False,
                    'description': f"İş emri: {request.name}"
                }

                # Durum bazlı ek bilgiler
                if request.state == 'in_progress':
                    wo_vals['state'] = 'in_progress'
                    wo_vals['start_datetime'] = datetime.now() - timedelta(hours=random.randint(1, 3))
                    wo_vals['actual_duration'] = random.randint(30, 180) / 60.0

                elif request.state in ['resolved', 'closed']:
                    wo_vals['state'] = 'done'
                    wo_vals['start_datetime'] = datetime.now() - timedelta(hours=random.randint(4, 8))
                    wo_vals['end_datetime'] = datetime.now() - timedelta(hours=random.randint(1, 3))
                    wo_vals['actual_duration'] = random.randint(60, 240) / 60.0
                    wo_vals['resolution_notes'] = request.resolution_notes if request.resolution_notes else 'Sorun çözüldü, sistem normal çalışıyor.'

                else:  # assigned
                    wo_vals['state'] = 'assigned'

                work_order = WorkOrder.create(wo_vals)
                print(f"  ✓ İş Emri: WO-{work_order.id:04d} - {request.name[:40]}...")

            except Exception as e:
                print(f"  ✗ İş emri oluşturulamadı: {str(e)}")

    print("\n" + "="*60)
    print("✅ DEMO VERİLERİ BAŞARIYLA OLUŞTURULDU!")
    print("="*60)

    # Özet bilgi
    print("\nOluşturulan Kayıtlar:")
    print(f"  • {len(employees)} Kullanıcı/Çalışan")
    print(f"  • {len(campuses)} Kampüs")
    print(f"  • {len(buildings)} Bina")
    print(f"  • {len(teams)} Servis Ekibi")
    print(f"  • {len(categories)} Ekipman Kategorisi")
    print(f"  • {len(equipments)} Ekipman")
    print(f"  • {len(slas)} SLA Politikası")
    print(f"  • {Contract.search_count([])} Bakım Sözleşmesi")
    print(f"  • {len(created_requests)} Servis Talebi")
    print(f"  • {WorkOrder.search_count([])} İş Emri")

    print("\n🎯 Sistem kullanıma hazır!")
    print("📊 Dashboard'u görüntülemek için: Technical Service > Dashboard")

    return True

# Script çalıştırıldığında
if __name__ == '__main__':
    print("Bu script Odoo shell içinde çalıştırılmalıdır.")
    print("Kullanım: /opt/odoo/venv/bin/python3 /opt/odoo/odoo18/odoo-bin shell -c /opt/odoo/odoo-dev.conf")
    print("Sonra: exec(open('/opt/odoo/custom-addons/technical_service/scripts/generate_demo_data.py').read())")
else:
    # Odoo shell içinde çalıştırılıyorsa
    try:
        create_demo_data(env)
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()