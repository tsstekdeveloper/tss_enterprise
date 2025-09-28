#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Technical Service Basit Demo Data Generator
Minimal ve çalışan örnek veri oluşturma scripti
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

print("\n" + "="*60)
print("TECHNICAL SERVICE - DEMO DATA (SIMPLE)")
print("="*60)

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
        return models.execute_kw(db, uid, password, model, 'create', [values])

    def write(model, ids, values):
        return models.execute_kw(db, uid, password, model, 'write', [ids, values])

    # Değişkenler
    created = {'count': 0}

    # 1. KAMPÜSLER
    print("\n[1] Kampüsler oluşturuluyor...")
    campus_ids = []

    campus1_id = create('technical_service.campus', {
        'name': 'Ana Kampüs',
        'code': 'MAIN',
        'address': 'İstanbul, Türkiye'
    })
    campus_ids.append(campus1_id)
    print(f"  ✓ Ana Kampüs (ID: {campus1_id})")
    created['count'] += 1

    campus2_id = create('technical_service.campus', {
        'name': 'Ar-Ge Kampüsü',
        'code': 'RND',
        'address': 'Teknopark, İstanbul'
    })
    campus_ids.append(campus2_id)
    print(f"  ✓ Ar-Ge Kampüsü (ID: {campus2_id})")
    created['count'] += 1

    # 2. BİNALAR
    print("\n[2] Binalar oluşturuluyor...")
    building_ids = []

    buildings = [
        {'name': 'A Blok', 'code': 'A-BLK', 'campus_id': campus1_id, 'floor_count': 5},
        {'name': 'B Blok', 'code': 'B-BLK', 'campus_id': campus1_id, 'floor_count': 3},
        {'name': 'C Blok', 'code': 'C-BLK', 'campus_id': campus1_id, 'floor_count': 4},
        {'name': 'İnovasyon Merkezi', 'code': 'INV', 'campus_id': campus2_id, 'floor_count': 6}
    ]

    for bld in buildings:
        bld_id = create('technical_service.building', bld)
        building_ids.append(bld_id)
        print(f"  ✓ {bld['name']} (ID: {bld_id})")
        created['count'] += 1

    # 3. DEPARTMANLAR
    print("\n[3] Departmanlar oluşturuluyor...")
    dept_ids = []

    departments = ['Bilgi İşlem', 'Üretim', 'İnsan Kaynakları', 'Teknik İşler', 'Ar-Ge']
    for dept_name in departments:
        existing = search('hr.department', [('name', '=', dept_name)])
        if not existing:
            dept_id = create('hr.department', {'name': dept_name})
            dept_ids.append(dept_id)
            print(f"  ✓ {dept_name} (ID: {dept_id})")
            created['count'] += 1
        else:
            dept_ids.append(existing[0])
            print(f"  • {dept_name} (mevcut)")

    # 4. ÇALIŞANLAR
    print("\n[4] Çalışanlar oluşturuluyor...")
    employee_ids = []

    employees = [
        {'name': 'Ali Teknisyen', 'job': 'IT Teknisyeni'},
        {'name': 'Ayşe Uzman', 'job': 'Network Uzmanı'},
        {'name': 'Mehmet Müdür', 'job': 'IT Müdürü'},
        {'name': 'Fatma Operatör', 'job': 'Üretim Operatörü'},
        {'name': 'Can Mühendis', 'job': 'Bakım Mühendisi'}
    ]

    for emp_data in employees:
        # Önce job position oluştur
        job_existing = search('hr.job', [('name', '=', emp_data['job'])])
        if not job_existing:
            job_id = create('hr.job', {'name': emp_data['job']})
        else:
            job_id = job_existing[0]

        # Employee oluştur
        emp_id = create('hr.employee', {
            'name': emp_data['name'],
            'job_id': job_id,
            'department_id': dept_ids[0] if dept_ids else False,
            'work_email': f"{emp_data['name'].lower().replace(' ', '.')}@company.com"
        })
        employee_ids.append(emp_id)
        print(f"  ✓ {emp_data['name']} - {emp_data['job']} (ID: {emp_id})")
        created['count'] += 1

    # 5. EKİPMAN KATEGORİLERİ
    print("\n[5] Ekipman kategorileri oluşturuluyor...")
    category_ids = []

    categories = ['Bilgisayarlar', 'Network Cihazları', 'Üretim Makineleri', 'HVAC Sistemleri']
    for cat_name in categories:
        existing = search('maintenance.equipment.category', [('name', '=', cat_name)])
        if not existing:
            cat_id = create('maintenance.equipment.category', {
                'name': cat_name,
                'technician_user_id': uid
            })
            category_ids.append(cat_id)
            print(f"  ✓ {cat_name} (ID: {cat_id})")
            created['count'] += 1
        else:
            category_ids.append(existing[0])
            print(f"  • {cat_name} (mevcut)")

    # 6. EKİPMANLAR
    print("\n[6] Ekipmanlar oluşturuluyor...")
    equipment_ids = []

    equipments = [
        {'name': 'Ana Sunucu', 'serial': 'SRV-001', 'category_id': category_ids[0] if category_ids else False},
        {'name': 'Firewall', 'serial': 'FW-001', 'category_id': category_ids[1] if category_ids else False},
        {'name': 'CNC Makinesi', 'serial': 'CNC-001', 'category_id': category_ids[2] if category_ids else False},
        {'name': 'Klima Sistemi', 'serial': 'HVAC-001', 'category_id': category_ids[3] if category_ids else False},
        {'name': 'Jeneratör', 'serial': 'GEN-001', 'category_id': category_ids[3] if category_ids else False}
    ]

    for eq_data in equipments:
        existing = search('maintenance.equipment', [('serial_no', '=', eq_data['serial'])])
        if not existing:
            eq_id = create('maintenance.equipment', {
                'name': eq_data['name'],
                'serial_no': eq_data['serial'],
                'category_id': eq_data['category_id'],
                'location': 'Ana Kampüs'
            })
            equipment_ids.append(eq_id)
            print(f"  ✓ {eq_data['name']} (ID: {eq_id})")
            created['count'] += 1
        else:
            equipment_ids.append(existing[0])
            print(f"  • {eq_data['name']} (mevcut)")

    # 7. SERVİS TALEPLERİ
    print("\n[7] Servis talepleri oluşturuluyor...")
    request_ids = []

    # İlk partner'ı requester olarak kullan
    partner_ids = search('res.partner', [('is_company', '=', False)])
    if not partner_ids:
        # Partner oluştur
        partner_id = create('res.partner', {
            'name': 'Demo Kullanıcı',
            'email': 'demo@company.com',
            'is_company': False
        })
    else:
        partner_id = partner_ids[0]

    requests = [
        {
            'name': 'Sunucu Erişim Problemi',
            'request_type': 'incident',
            'priority': 'critical',
            'description': 'Ana sunucuya erişilemiyor, acil müdahale gerekli!',
            'requester_id': partner_id,
            'building_id': building_ids[0] if building_ids else False,
            'equipment_id': equipment_ids[0] if equipment_ids else False,
            'state': 'new'
        },
        {
            'name': 'Network Yavaşlığı',
            'request_type': 'problem',
            'priority': 'high',
            'description': 'İnternet bağlantısı çok yavaş',
            'requester_id': partner_id,
            'building_id': building_ids[1] if building_ids else False,
            'state': 'assigned'
        },
        {
            'name': 'Yeni Bilgisayar Kurulumu',
            'request_type': 'service_request',
            'priority': 'medium',
            'description': 'Yeni personel için bilgisayar kurulumu',
            'requester_id': partner_id,
            'building_id': building_ids[0] if building_ids else False,
            'state': 'new'
        },
        {
            'name': 'Yazıcı Arızası',
            'request_type': 'incident',
            'priority': 'low',
            'description': 'Yazıcı kağıt sıkışması',
            'requester_id': partner_id,
            'building_id': building_ids[2] if building_ids else False,
            'state': 'resolved'
        },
        {
            'name': 'Aylık Bakım',
            'request_type': 'preventive',
            'priority': 'medium',
            'description': 'Planlı aylık sunucu bakımı',
            'requester_id': partner_id,
            'equipment_id': equipment_ids[0] if equipment_ids else False,
            'state': 'scheduled'
        },
        {
            'name': 'Klima Arızası',
            'request_type': 'incident',
            'priority': 'high',
            'description': 'Server odasında klima çalışmıyor',
            'requester_id': partner_id,
            'building_id': building_ids[2] if building_ids else False,
            'equipment_id': equipment_ids[3] if equipment_ids else False,
            'state': 'in_progress'
        },
        {
            'name': 'Firewall Güncelleme',
            'request_type': 'change',
            'priority': 'medium',
            'description': 'Güvenlik güncellemeleri yapılacak',
            'requester_id': partner_id,
            'equipment_id': equipment_ids[1] if equipment_ids else False,
            'state': 'pending_approval'
        },
        {
            'name': 'CNC Makinesi Bakım',
            'request_type': 'preventive',
            'priority': 'medium',
            'description': 'Haftalık rutin bakım',
            'requester_id': partner_id,
            'equipment_id': equipment_ids[2] if equipment_ids else False,
            'state': 'scheduled'
        }
    ]

    for req_data in requests:
        req_id = create('technical_service.request', req_data)
        request_ids.append(req_id)
        print(f"  ✓ {req_data['name']} [{req_data['state']}] (ID: {req_id})")
        created['count'] += 1

    # 8. İŞ EMİRLERİ
    print("\n[8] İş emirleri oluşturuluyor...")
    work_order_ids = []

    # Sadece uygun durumdaki talepler için
    for i, req_id in enumerate(request_ids[:5]):
        wo_data = {
            'request_id': req_id,
            'priority': 'high' if i < 2 else 'medium',
            'assigned_technician_id': employee_ids[i % len(employee_ids)] if employee_ids else False,
            'description': f'İş Emri #{i+1}',
            'state': 'assigned' if i % 2 == 0 else 'in_progress'
        }

        if wo_data['state'] == 'in_progress':
            wo_data['start_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        wo_id = create('technical_service.work_order', wo_data)
        work_order_ids.append(wo_id)
        print(f"  ✓ İş Emri WO-{wo_id:04d} [{wo_data['state']}]")
        created['count'] += 1

    # ÖZET
    print("\n" + "="*60)
    print(f"✅ TOPLAM {created['count']} KAYIT OLUŞTURULDU!")
    print("="*60)
    print("\n🎯 Sistem kullanıma hazır!")
    print("📊 Dashboard: http://localhost:8069")
    print("📋 Menü: Technical Service > Dashboard")

except xmlrpc.client.Fault as error:
    print(f"\n❌ Odoo Hatası: {error.faultString}")

except Exception as e:
    print(f"\n❌ Hata: {str(e)}")
    import traceback
    traceback.print_exc()