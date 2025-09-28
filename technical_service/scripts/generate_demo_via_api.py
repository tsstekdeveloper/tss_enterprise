#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Technical Service Demo Data Generator via API
Satış sunumu için kapsamlı örnek veri oluşturma scripti
"""

import xmlrpc.client
import ssl
from datetime import datetime, timedelta
import random
import sys

# SSL doğrulamasını devre dışı bırak (development için)
ssl._create_default_https_context = ssl._create_unverified_context

# Bağlantı bilgileri
url = 'http://localhost:8069'
db = 'odoo_tech_service'
username = 'admin'
password = 'admin'

print("\n" + "="*60)
print("TECHNICAL SERVICE - DEMO DATA OLUŞTURMA (API)")
print("="*60)

try:
    # Bağlantı kur
    print("\n[*] Odoo'ya bağlanılıyor...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("❌ Kimlik doğrulama başarısız! Kullanıcı adı/şifre kontrol edin.")
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print("✅ Bağlantı başarılı!")

    # Helper fonksiyonlar
    def search(model, domain):
        """Model'de arama yap"""
        return models.execute_kw(db, uid, password, model, 'search', [domain])

    def search_read(model, domain, fields):
        """Model'de arama yap ve alanları oku"""
        return models.execute_kw(db, uid, password, model, 'search_read', [domain], {'fields': fields})

    def read(model, ids, fields):
        """Kayıtları oku"""
        return models.execute_kw(db, uid, password, model, 'read', [ids], {'fields': fields})

    def create(model, values):
        """Yeni kayıt oluştur"""
        return models.execute_kw(db, uid, password, model, 'create', [values])

    def write(model, ids, values):
        """Kayıtları güncelle"""
        return models.execute_kw(db, uid, password, model, 'write', [ids, values])

    def execute(model, method, *args):
        """Model metodunu çalıştır"""
        return models.execute_kw(db, uid, password, model, method, list(args))

    # Data storage
    created_data = {
        'departments': {},
        'users': {},
        'employees': {},
        'campuses': {},
        'buildings': {},
        'teams': {},
        'categories': {},
        'equipment': [],
        'slas': {},
        'contracts': [],
        'requests': [],
        'work_orders': []
    }

    # 1. ŞİRKET BİLGİLERİNİ GÜNCELLE
    print("\n[1/10] Şirket bilgileri güncelleniyor...")
    try:
        company_id = search('res.company', [])[0]
        write('res.company', [company_id], {
            'name': 'TechnoFix Global Services A.Ş.',
            'street': 'Teknoloji Bulvarı No:42',
            'city': 'İstanbul',
            'zip': '34000',
            'phone': '+90 212 555 1234',
            'email': 'info@technofix.com.tr',
            'website': 'www.technofix.com.tr',
            'vat': 'TR1234567890'
        })
        print("  ✓ Şirket bilgileri güncellendi")
    except Exception as e:
        print(f"  ✗ Hata: {str(e)}")

    # 2. DEPARTMANLAR
    print("\n[2/10] Departmanlar oluşturuluyor...")
    dept_names = [
        'Bilgi İşlem',
        'Üretim',
        'İnsan Kaynakları',
        'Teknik İşler',
        'İdari İşler',
        'Ar-Ge',
        'Kalite Kontrol'
    ]

    for dept_name in dept_names:
        try:
            dept_ids = search('hr.department', [('name', '=', dept_name)])
            if not dept_ids:
                dept_id = create('hr.department', {'name': dept_name})
                created_data['departments'][dept_name] = dept_id
                print(f"  ✓ {dept_name}")
            else:
                created_data['departments'][dept_name] = dept_ids[0]
                print(f"  • {dept_name} (mevcut)")
        except Exception as e:
            print(f"  ✗ {dept_name}: {str(e)}")

    # 3. KULLANICILAR VE ÇALIŞANLAR
    print("\n[3/10] Kullanıcılar ve çalışanlar oluşturuluyor...")
    users_data = [
        {'name': 'Ahmet Yılmaz', 'login': 'ahmet.yilmaz@technofix.com', 'job': 'Servis Müdürü', 'dept': 'Teknik İşler'},
        {'name': 'Mehmet Demir', 'login': 'mehmet.demir@technofix.com', 'job': 'IT Takım Lideri', 'dept': 'Bilgi İşlem'},
        {'name': 'Ayşe Kaya', 'login': 'ayse.kaya@technofix.com', 'job': 'Teknik Takım Lideri', 'dept': 'Teknik İşler'},
        {'name': 'Ali Özkan', 'login': 'ali.ozkan@technofix.com', 'job': 'Kıdemli IT Teknisyeni', 'dept': 'Bilgi İşlem'},
        {'name': 'Fatma Şahin', 'login': 'fatma.sahin@technofix.com', 'job': 'Network Uzmanı', 'dept': 'Bilgi İşlem'},
        {'name': 'Can Aydın', 'login': 'can.aydin@technofix.com', 'job': 'Donanım Teknisyeni', 'dept': 'Bilgi İşlem'},
        {'name': 'Zeynep Arslan', 'login': 'zeynep.arslan@technofix.com', 'job': 'Elektrik Teknisyeni', 'dept': 'Teknik İşler'},
        {'name': 'Murat Çelik', 'login': 'murat.celik@technofix.com', 'job': 'HVAC Teknisyeni', 'dept': 'Teknik İşler'},
        {'name': 'Elif Güneş', 'login': 'elif.gunes@technofix.com', 'job': 'Junior Teknisyen', 'dept': 'Teknik İşler'},
        {'name': 'Hakan Yıldız', 'login': 'hakan.yildiz@technofix.com', 'job': 'IT Müdürü', 'dept': 'Bilgi İşlem'},
        {'name': 'Seda Korkmaz', 'login': 'seda.korkmaz@technofix.com', 'job': 'Üretim Müdürü', 'dept': 'Üretim'},
        {'name': 'Burak Öztürk', 'login': 'burak.ozturk@technofix.com', 'job': 'İK Uzmanı', 'dept': 'İnsan Kaynakları'},
    ]

    for user_data in users_data:
        try:
            # Kullanıcı var mı kontrol et
            user_ids = search('res.users', [('login', '=', user_data['login'])])

            if not user_ids:
                # Yeni kullanıcı oluştur
                user_id = create('res.users', {
                    'name': user_data['name'],
                    'login': user_data['login'],
                    'email': user_data['login'],
                    'password': 'demo123'
                })
                created_data['users'][user_data['name']] = user_id
                print(f"  ✓ {user_data['name']} - {user_data['job']}")
            else:
                created_data['users'][user_data['name']] = user_ids[0]
                print(f"  • {user_data['name']} (mevcut)")

            # Employee kaydı
            emp_ids = search('hr.employee', [('user_id', '=', created_data['users'][user_data['name']])])
            if not emp_ids:
                # Job position oluştur/bul
                job_ids = search('hr.job', [('name', '=', user_data['job'])])
                if not job_ids:
                    job_id = create('hr.job', {'name': user_data['job']})
                else:
                    job_id = job_ids[0]

                emp_id = create('hr.employee', {
                    'name': user_data['name'],
                    'user_id': created_data['users'][user_data['name']],
                    'job_id': job_id,
                    'department_id': created_data['departments'].get(user_data['dept'], False),
                    'work_email': user_data['login']
                })
                created_data['employees'][user_data['name']] = emp_id
            else:
                created_data['employees'][user_data['name']] = emp_ids[0]

        except Exception as e:
            print(f"  ✗ {user_data['name']}: {str(e)}")

    # 4. LOKASYONLAR
    print("\n[4/10] Lokasyonlar oluşturuluyor...")
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

    for campus_info in campus_data:
        try:
            campus_ids = search('technical_service.campus', [('code', '=', campus_info['code'])])
            if not campus_ids:
                campus_id = create('technical_service.campus', {
                    'name': campus_info['name'],
                    'code': campus_info['code'],
                    'address': campus_info['address']
                })
                created_data['campuses'][campus_info['code']] = campus_id
                print(f"  ✓ Kampüs: {campus_info['name']}")
            else:
                campus_id = campus_ids[0]
                created_data['campuses'][campus_info['code']] = campus_id
                print(f"  • Kampüs: {campus_info['name']} (mevcut)")

            # Binaları oluştur
            for building_info in campus_info['buildings']:
                building_ids = search('technical_service.building', [
                    ('code', '=', building_info['code']),
                    ('campus_id', '=', campus_id)
                ])
                if not building_ids:
                    floors = ', '.join([f"{i}. Kat" for i in range(1, building_info['floor_count'] + 1)])
                    building_id = create('technical_service.building', {
                        'name': building_info['name'],
                        'code': building_info['code'],
                        'campus_id': campus_id,
                        'floor_count': building_info['floor_count'],
                        'floors': floors
                    })
                    created_data['buildings'][building_info['code']] = building_id
                    print(f"    ✓ Bina: {building_info['name']}")
                else:
                    created_data['buildings'][building_info['code']] = building_ids[0]

        except Exception as e:
            print(f"  ✗ {campus_info['name']}: {str(e)}")

    # 5. SERVİS EKİPLERİ
    print("\n[5/10] Servis ekipleri oluşturuluyor...")
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

    for team_data in teams_data:
        try:
            team_ids = search('technical_service.team', [('code', '=', team_data['code'])])
            if not team_ids:
                # Üyeleri bul
                member_ids = []
                for member_name in team_data['members']:
                    if member_name in created_data['employees']:
                        member_ids.append(created_data['employees'][member_name])

                # Lider
                leader_id = created_data['employees'].get(team_data['team_leader'], False)

                # Tüm kampüsleri ekle
                all_campus_ids = list(created_data['campuses'].values())

                team_id = create('technical_service.team', {
                    'name': team_data['name'],
                    'code': team_data['code'],
                    'specialization': team_data['specialization'],
                    'shift_type': team_data['shift_type'],
                    'team_leader_id': leader_id,
                    'member_ids': [(6, 0, member_ids)],
                    'campus_ids': [(6, 0, all_campus_ids)],
                    'active': True
                })
                created_data['teams'][team_data['code']] = team_id
                print(f"  ✓ {team_data['name']} ({len(member_ids)} üye)")
            else:
                created_data['teams'][team_data['code']] = team_ids[0]
                print(f"  • {team_data['name']} (mevcut)")

        except Exception as e:
            print(f"  ✗ {team_data['name']}: {str(e)}")

    # 6. EKİPMAN KATEGORİLERİ VE EKİPMANLAR
    print("\n[6/10] Ekipman kategorileri ve ekipmanlar oluşturuluyor...")

    # Kategoriler
    categories_info = [
        'Sunucular',
        'Network Ekipmanları',
        'Bilgisayarlar',
        'Üretim Makineleri',
        'HVAC Sistemleri',
        'Güç Sistemleri'
    ]

    for cat_name in categories_info:
        try:
            cat_ids = search('maintenance.equipment.category', [('name', '=', cat_name)])
            if not cat_ids:
                cat_id = create('maintenance.equipment.category', {
                    'name': cat_name,
                    'technician_user_id': uid
                })
                created_data['categories'][cat_name] = cat_id
                print(f"  ✓ Kategori: {cat_name}")
            else:
                created_data['categories'][cat_name] = cat_ids[0]

        except Exception as e:
            print(f"  ✗ Kategori {cat_name}: {str(e)}")

    # Ekipmanlar
    equipment_list = [
        {'name': 'Dell PowerEdge R750 - Ana Sunucu', 'category': 'Sunucular', 'serial': 'DPE-R750-001'},
        {'name': 'Fortinet FortiGate 600E', 'category': 'Network Ekipmanları', 'serial': 'FG-600E-001'},
        {'name': 'Cisco Catalyst 9300', 'category': 'Network Ekipmanları', 'serial': 'CS-9300-001'},
        {'name': 'Haas VF-4 CNC Torna', 'category': 'Üretim Makineleri', 'serial': 'HAAS-VF4-001'},
        {'name': 'Daikin VRV IV Klima', 'category': 'HVAC Sistemleri', 'serial': 'DAI-VRV-001'},
        {'name': 'Caterpillar 500kVA Jeneratör', 'category': 'Güç Sistemleri', 'serial': 'CAT-500-001'},
        {'name': 'APC Symmetra 80kVA UPS', 'category': 'Güç Sistemleri', 'serial': 'APC-80K-001'}
    ]

    for eq_info in equipment_list:
        try:
            eq_ids = search('maintenance.equipment', [('serial_no', '=', eq_info['serial'])])
            if not eq_ids:
                eq_id = create('maintenance.equipment', {
                    'name': eq_info['name'],
                    'category_id': created_data['categories'].get(eq_info['category'], False),
                    'serial_no': eq_info['serial'],
                    'location': 'Ana Kampüs'
                })
                created_data['equipment'].append(eq_id)
                print(f"  ✓ Ekipman: {eq_info['name']}")
            else:
                created_data['equipment'].append(eq_ids[0])

        except Exception as e:
            print(f"  ✗ Ekipman {eq_info['name']}: {str(e)}")

    # 7. SLA POLİTİKALARI
    print("\n[7/10] SLA politikaları oluşturuluyor...")
    sla_policies = [
        {
            'name': 'Standart SLA',
            'priorities': [
                ('critical', 0.5, 4),
                ('high', 2, 8),
                ('medium', 4, 24),
                ('low', 8, 72)
            ]
        },
        {
            'name': 'Premium SLA',
            'priorities': [
                ('critical', 0.25, 2),
                ('high', 1, 4),
                ('medium', 2, 12)
            ]
        }
    ]

    for sla_info in sla_policies:
        try:
            sla_ids = search('technical_service.sla', [('name', '=', sla_info['name'])])
            if not sla_ids:
                # Priority matrix oluştur
                priority_lines = []
                for priority, response, resolution in sla_info['priorities']:
                    priority_lines.append((0, 0, {
                        'priority': priority,
                        'response_time': response,
                        'resolution_time': resolution
                    }))

                sla_id = create('technical_service.sla', {
                    'name': sla_info['name'],
                    'active': True,
                    'business_hours_start': 8.0,
                    'business_hours_end': 17.0,
                    'working_days': 'weekdays',
                    'priority_ids': priority_lines,
                    'escalation_after': 75.0
                })
                created_data['slas'][sla_info['name']] = sla_id
                print(f"  ✓ SLA: {sla_info['name']}")
            else:
                created_data['slas'][sla_info['name']] = sla_ids[0]

        except Exception as e:
            print(f"  ✗ SLA {sla_info['name']}: {str(e)}")

    # 8. BAKIM SÖZLEŞMELERİ
    print("\n[8/10] Bakım sözleşmeleri oluşturuluyor...")

    # Company partner ID'yi al
    company_ids = search('res.company', [])
    if company_ids:
        company_data = read('res.company', company_ids[0], ['partner_id'])
        company_partner_id = company_data[0]['partner_id'][0] if company_data else False
    else:
        company_partner_id = False

    contracts_info = [
        {
            'name': 'Üretim Ekipmanları Yıllık Bakım',
            'number': 'CNT-2024-001',
            'type': 'amc',
            'value': 250000.0
        },
        {
            'name': 'IT Altyapı Bakım Sözleşmesi',
            'number': 'CNT-2024-002',
            'type': 'preventive',
            'value': 180000.0
        }
    ]

    for contract_info in contracts_info:
        try:
            contract_ids = search('technical_service.contract', [('contract_number', '=', contract_info['number'])])
            if not contract_ids:
                start_date = datetime.now().strftime('%Y-%m-%d')
                end_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

                contract_id = create('technical_service.contract', {
                    'name': contract_info['name'],
                    'contract_number': contract_info['number'],
                    'contract_type': contract_info['type'],
                    'customer_id': company_partner_id,
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_value': contract_info['value'],
                    'coverage_type': '24_7',
                    'response_time': 2.0,
                    'state': 'active'
                })
                created_data['contracts'].append(contract_id)
                print(f"  ✓ Sözleşme: {contract_info['name']}")
            else:
                created_data['contracts'].append(contract_ids[0])

        except Exception as e:
            print(f"  ✗ Sözleşme {contract_info['name']}: {str(e)}")

    # 9. SERVİS TALEPLERİ
    print("\n[9/10] Servis talepleri oluşturuluyor...")

    requests_info = [
        {
            'name': 'Ana Sunucu Erişim Problemi - KRİTİK',
            'type': 'incident',
            'priority': 'critical',
            'description': 'ERP sunucusuna erişilemiyor, tüm üretim durdu!',
            'state': 'in_progress'
        },
        {
            'name': 'Network Performans Sorunu',
            'type': 'problem',
            'priority': 'high',
            'description': 'Üretim hattında network yavaşlığı var.',
            'state': 'assigned'
        },
        {
            'name': 'Yeni Personel IT Kurulumu',
            'type': 'service_request',
            'priority': 'medium',
            'description': '3 yeni personel için bilgisayar ve sistem kurulumu.',
            'state': 'new'
        },
        {
            'name': 'Yazıcı Kağıt Sıkışması',
            'type': 'incident',
            'priority': 'low',
            'description': '2. kat yazıcıda kağıt sıkışması.',
            'state': 'resolved'
        },
        {
            'name': 'Aylık Sunucu Bakımı',
            'type': 'preventive',
            'priority': 'medium',
            'description': 'Planlı aylık sunucu bakımı.',
            'state': 'scheduled'
        },
        {
            'name': 'Firewall Kural Güncelleme',
            'type': 'change',
            'priority': 'high',
            'description': 'Yeni VPN kullanıcıları için firewall kuralı.',
            'state': 'pending_approval'
        },
        {
            'name': 'B Blok Elektrik Kesintisi',
            'type': 'incident',
            'priority': 'high',
            'description': 'B Blok 2. katta kısmi elektrik kesintisi.',
            'state': 'in_progress'
        },
        {
            'name': 'Yedekleme Hatası',
            'type': 'problem',
            'priority': 'medium',
            'description': 'Otomatik yedekleme başarısız.',
            'state': 'assigned'
        }
    ]

    # Requester için ilk partner'ı kullan
    partner_ids = search('res.partner', [('is_company', '=', False)], limit=1)
    requester_id = partner_ids[0] if partner_ids else False

    for req_info in requests_info:
        try:
            # SLA seç
            sla_id = False
            if req_info['priority'] == 'critical':
                sla_id = created_data['slas'].get('Premium SLA', False)
            else:
                sla_id = created_data['slas'].get('Standart SLA', False)

            # Building seç
            building_id = list(created_data['buildings'].values())[0] if created_data['buildings'] else False

            req_id = create('technical_service.request', {
                'name': req_info['name'],
                'request_type': req_info['type'],
                'priority': req_info['priority'],
                'description': req_info['description'],
                'requester_id': requester_id,
                'building_id': building_id,
                'state': req_info['state'],
                'sla_id': sla_id
            })

            created_data['requests'].append(req_id)
            print(f"  ✓ Talep: {req_info['name'][:40]}... [{req_info['state']}]")

        except Exception as e:
            print(f"  ✗ Talep {req_info['name'][:30]}...: {str(e)}")

    # 10. İŞ EMİRLERİ
    print("\n[10/10] İş emirleri oluşturuluyor...")

    # İlerleme durumundaki talepler için iş emri oluştur
    for i, req_id in enumerate(created_data['requests'][:5]):  # İlk 5 talep için
        try:
            # Teknisyen seç
            tech_id = list(created_data['employees'].values())[i % len(created_data['employees'])] if created_data['employees'] else False

            # Ekip seç
            team_id = list(created_data['teams'].values())[0] if created_data['teams'] else False

            wo_id = create('technical_service.work_order', {
                'request_id': req_id,
                'priority': 'high',
                'assigned_technician_id': tech_id,
                'team_id': team_id,
                'description': f'İş Emri #{i+1}',
                'state': 'assigned' if i % 2 == 0 else 'in_progress'
            })

            created_data['work_orders'].append(wo_id)
            print(f"  ✓ İş Emri: WO-{wo_id:04d}")

        except Exception as e:
            print(f"  ✗ İş emri oluşturulamadı: {str(e)}")

    # ÖZET
    print("\n" + "="*60)
    print("✅ DEMO VERİLERİ BAŞARIYLA OLUŞTURULDU!")
    print("="*60)
    print("\nOluşturulan Kayıtlar:")
    print(f"  • {len(created_data['users'])} Kullanıcı")
    print(f"  • {len(created_data['departments'])} Departman")
    print(f"  • {len(created_data['campuses'])} Kampüs")
    print(f"  • {len(created_data['buildings'])} Bina")
    print(f"  • {len(created_data['teams'])} Servis Ekibi")
    print(f"  • {len(created_data['categories'])} Ekipman Kategorisi")
    print(f"  • {len(created_data['equipment'])} Ekipman")
    print(f"  • {len(created_data['slas'])} SLA Politikası")
    print(f"  • {len(created_data['contracts'])} Bakım Sözleşmesi")
    print(f"  • {len(created_data['requests'])} Servis Talebi")
    print(f"  • {len(created_data['work_orders'])} İş Emri")

    print("\n🎯 Sistem kullanıma hazır!")
    print("📊 Dashboard: http://localhost:8069")
    print("👤 Kullanıcı: admin / Şifre: admin")
    print("\n📋 Menü: Technical Service > Dashboard")

except xmlrpc.client.Fault as error:
    print(f"\n❌ Odoo Hatası: {error.faultString}")
    print("\nÇözüm önerileri:")
    print("1. Odoo servisinin çalıştığından emin olun")
    print("2. Veritabanı adının doğru olduğunu kontrol edin")
    print("3. Technical Service modülünün yüklendiğinden emin olun")

except Exception as e:
    print(f"\n❌ Beklenmeyen hata: {str(e)}")
    import traceback
    traceback.print_exc()