#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Technical Service - Veri Kontrolü
Oluşturulan verileri kontrol eder
"""

import xmlrpc.client
import ssl

# SSL doğrulamasını devre dışı bırak
ssl._create_default_https_context = ssl._create_unverified_context

# Bağlantı bilgileri
url = 'http://localhost:8069'
db = 'odoo_tech_service'
username = 'admin'
password = 'admin'

print("\n" + "="*60)
print("TECHNICAL SERVICE - VERİ KONTROLÜ")
print("="*60)

try:
    # Bağlantı
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')

    # Version kontrolü
    version = common.version()
    print(f"\n✅ Odoo Versiyonu: {version['server_version']}")

    # Authenticate
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("❌ Kimlik doğrulama başarısız!")
        print(f"   Database: {db}")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        exit(1)

    print(f"✅ Bağlantı başarılı! (UID: {uid})")

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    def count_records(model_name):
        """Model'deki kayıt sayısını döndürür"""
        try:
            count = models.execute_kw(db, uid, password, model_name, 'search_count', [[]])
            return count
        except Exception as e:
            return f"Hata: {str(e)[:50]}"

    def get_sample_records(model_name, fields, limit=3):
        """Model'den örnek kayıtlar getirir"""
        try:
            records = models.execute_kw(
                db, uid, password,
                model_name, 'search_read',
                [[]],
                {'fields': fields, 'limit': limit}
            )
            return records
        except Exception as e:
            return []

    # Kontrol edilecek modeller
    print("\n📊 KAYIT SAYILARI:")
    print("-" * 40)

    models_to_check = [
        ('res.users', 'Kullanıcılar'),
        ('hr.employee', 'Çalışanlar'),
        ('hr.department', 'Departmanlar'),
        ('maintenance.equipment', 'Ekipmanlar'),
        ('maintenance.equipment.category', 'Ekipman Kategorileri'),
        ('maintenance.request', 'Bakım Talepleri'),
        ('maintenance.team', 'Bakım Ekipleri'),
        ('project.project', 'Projeler'),
        ('project.task', 'Görevler (İş Emirleri)'),
        ('technical_service.campus', 'Kampüsler'),
        ('technical_service.building', 'Binalar'),
    ]

    total_records = 0
    for model, label in models_to_check:
        count = count_records(model)
        if isinstance(count, int):
            total_records += count
            print(f"  • {label:30} : {count:5} kayıt")
        else:
            print(f"  • {label:30} : {count}")

    print("-" * 40)
    print(f"  TOPLAM: {total_records} kayıt")

    # ÖRNEK KAYITLAR
    print("\n📝 ÖRNEK KAYITLAR:")
    print("=" * 60)

    # Bakım Talepleri
    print("\n🔧 BAKIM TALEPLERİ:")
    requests = get_sample_records('maintenance.request', ['name', 'priority', 'request_date', 'description'], 5)
    if requests:
        for i, req in enumerate(requests, 1):
            priority_map = {'0': 'Düşük', '1': 'Normal', '2': 'Yüksek', '3': 'KRİTİK'}
            priority = priority_map.get(str(req.get('priority', '1')), 'Normal')
            print(f"\n  [{i}] {req['name']}")
            print(f"      Öncelik: {priority}")
            print(f"      Tarih: {req.get('request_date', 'N/A')}")
            desc_preview = req.get('description', '')[:100] if req.get('description') else 'Açıklama yok'
            if desc_preview:
                desc_preview = desc_preview.replace('\n', ' ')
            print(f"      Açıklama: {desc_preview}...")
    else:
        print("  Bakım talebi bulunamadı.")

    # Ekipmanlar
    print("\n💻 EKİPMANLAR:")
    equipments = get_sample_records('maintenance.equipment', ['name', 'serial_no', 'location'], 5)
    if equipments:
        for eq in equipments:
            print(f"  • {eq['name']:30} | Seri: {eq.get('serial_no', 'N/A'):15} | Lokasyon: {eq.get('location', 'N/A')}")
    else:
        print("  Ekipman bulunamadı.")

    # Kampüs ve Binalar
    print("\n🏢 LOKASYONLAR:")

    # Kampüsler
    campuses = get_sample_records('technical_service.campus', ['name', 'code', 'address'])
    if campuses:
        print("  Kampüsler:")
        for campus in campuses:
            print(f"    • {campus['name']} ({campus['code']}) - {campus.get('address', 'N/A')}")

    # Binalar
    buildings = get_sample_records('technical_service.building', ['name', 'code', 'campus_id', 'floor_count'])
    if buildings:
        print("  Binalar:")
        for building in buildings:
            campus_name = building.get('campus_id')[1] if building.get('campus_id') else 'N/A'
            print(f"    • {building['name']} ({building['code']}) - Kampüs: {campus_name} - {building.get('floor_count', 0)} kat")

    # Çalışanlar
    print("\n👥 ÇALIŞANLAR:")
    employees = get_sample_records('hr.employee', ['name', 'job_id', 'department_id', 'work_email'], 5)
    if employees:
        for emp in employees:
            job = emp.get('job_id')[1] if emp.get('job_id') else 'N/A'
            dept = emp.get('department_id')[1] if emp.get('department_id') else 'N/A'
            print(f"  • {emp['name']:20} | {job:20} | {dept:15}")
    else:
        print("  Çalışan bulunamadı.")

    # Projeler ve Görevler
    print("\n📋 İŞ EMİRLERİ (Project Tasks):")
    tasks = get_sample_records('project.task', ['name', 'project_id', 'priority', 'stage_id'], 5)
    if tasks:
        for task in tasks:
            project = task.get('project_id')[1] if task.get('project_id') else 'N/A'
            stage = task.get('stage_id')[1] if task.get('stage_id') else 'N/A'
            priority = '⭐' if task.get('priority') == '1' else '  '
            print(f"  {priority} {task['name'][:50]:50} | Proje: {project:15} | Durum: {stage}")
    else:
        print("  İş emri bulunamadı.")

    # ÖZET
    print("\n" + "="*60)
    print("📈 DURUM ÖZETİ:")
    print("="*60)

    if total_records > 0:
        print("✅ Veriler başarıyla oluşturulmuş!")
        print(f"   Toplam {total_records} kayıt bulundu.")
        print("\n🌐 Web arayüzünden görüntülemek için:")
        print(f"   URL: {url}")
        print(f"   Kullanıcı: {username}")
        print(f"   Şifre: {password}")
        print(f"   Database: {db}")
        print("\n📍 Menü yolları:")
        print("   • Bakım Talepleri: Maintenance > Maintenance Requests")
        print("   • Ekipmanlar: Maintenance > Equipment")
        print("   • İş Emirleri: Project > All Tasks")
        print("   • Dashboard: Technical Service > Dashboard")
    else:
        print("⚠️ Veri bulunamadı!")
        print("   generate_demo_simple.py ve generate_maintenance_requests.py")
        print("   scriptlerini çalıştırdığınızdan emin olun.")

except xmlrpc.client.Fault as error:
    print(f"\n❌ Odoo Hatası:")
    print(f"   {error.faultString}")
    print("\nOlası sebepler:")
    print("  1. Odoo servisi çalışmıyor olabilir")
    print("  2. Database adı yanlış olabilir")
    print("  3. Kullanıcı adı/şifre hatalı olabilir")
    print(f"\nKullanılan bilgiler:")
    print(f"  URL: {url}")
    print(f"  Database: {db}")
    print(f"  Username: {username}")
    print(f"  Password: {password}")

except Exception as e:
    print(f"\n❌ Beklenmeyen hata: {str(e)}")
    import traceback
    traceback.print_exc()