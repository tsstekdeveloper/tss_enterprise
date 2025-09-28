#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Technical Service Demo - Maintenance Request Generator
maintenance.request modelini kullanarak demo veriler oluşturur
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
print("TECHNICAL SERVICE - MAINTENANCE REQUESTS")
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

    def read(model, ids, fields):
        return models.execute_kw(db, uid, password, model, 'read', [ids], {'fields': fields})

    # Mevcut verileri al
    equipment_ids = search('maintenance.equipment', [])
    employee_ids = search('hr.employee', [])
    building_ids = search('technical_service.building', [])
    campus_ids = search('technical_service.campus', [])

    print(f"\nMevcut veriler:")
    print(f"  • {len(equipment_ids)} Ekipman")
    print(f"  • {len(employee_ids)} Çalışan")
    print(f"  • {len(building_ids)} Bina")
    print(f"  • {len(campus_ids)} Kampüs")

    # MAINTENANCE REQUESTS OLUŞTUR
    print("\n[MAINTENANCE REQUESTS] Bakım talepleri oluşturuluyor...")
    request_ids = []

    requests_data = [
        # Kritik Durumlar
        {
            'name': '🔴 KRİTİK: Ana Sunucu Çöktü!',
            'description': '''ACIL DURUM!

Ana ERP sunucusu yanıt vermiyor. Tüm şirket operasyonları durdu!
- Sistem: Dell PowerEdge R750
- Lokasyon: C Blok Server Room
- Son erişim: 10 dakika önce
- Etkilenen kullanıcı sayısı: 150+

DERHAL MÜDAHALE GEREKİYOR!''',
            'request_date': datetime.now(),
            'priority': '3',  # Maintenance'de priority: 0=Low, 1=Normal, 2=High, 3=Urgent
            'maintenance_type': 'corrective',
            'equipment_id': equipment_ids[0] if equipment_ids else False,
            'employee_id': employee_ids[0] if employee_ids else False
        },

        # Yüksek Öncelik
        {
            'name': '⚠️ Network Performans Sorunu - Üretim Hattı',
            'description': '''Üretim hattında ciddi network gecikmeleri yaşanıyor.

- Lokasyon: B Blok Üretim
- Başlangıç: 2 saat önce
- Etki: %70 yavaşlama
- Üretim kaybı: Saatte 100 adet

Network ekibi acil müdahale etmeli!''',
            'request_date': datetime.now() - timedelta(hours=2),
            'priority': '2',
            'maintenance_type': 'corrective',
            'equipment_id': equipment_ids[1] if len(equipment_ids) > 1 else False,
            'employee_id': employee_ids[1] if len(employee_ids) > 1 else False
        },

        # Normal Öncelik - Servis Talebi
        {
            'name': '📋 Yeni Personel IT Kurulumu (3 kişi)',
            'description': '''İK departmanından gelen talep:

3 yeni personel için ekipman hazırlanması:
1. Ahmet Yılmaz - Muhasebe
2. Fatma Demir - Satış
3. Ali Kaya - Pazarlama

Gereksinimler:
- Laptop/Desktop tahsisi
- Office 365 lisansı
- ERP kullanıcı hesabı
- E-posta hesabı
- Telefon hattı

Başlangıç tarihi: Pazartesi''',
            'request_date': datetime.now(),
            'priority': '1',
            'maintenance_type': 'preventive',
            'employee_id': employee_ids[2] if len(employee_ids) > 2 else False
        },

        # Düşük Öncelik
        {
            'name': '🖨️ 2. Kat Yazıcı Kağıt Sıkışması',
            'description': 'A Blok 2. kattaki HP yazıcıda tekrarlayan kağıt sıkışması. Drum temizliği gerekebilir.',
            'request_date': datetime.now() - timedelta(hours=1),
            'priority': '0',
            'maintenance_type': 'corrective',
            'employee_id': employee_ids[3] if len(employee_ids) > 3 else False
        },

        # Planlı Bakım
        {
            'name': '🔧 Aylık Sunucu Bakımı - Ocak 2024',
            'description': '''Rutin aylık bakım planı:

1. Sistem güncellemeleri kontrolü
2. Disk alanı temizliği
3. Log dosyaları arşivleme
4. Yedekleme kontrolü
5. Performans analizi
6. Güvenlik taraması

Planlanan tarih: Bu Cumartesi 02:00-06:00''',
            'request_date': datetime.now(),
            'schedule_date': datetime.now() + timedelta(days=3),
            'priority': '1',
            'maintenance_type': 'preventive',
            'equipment_id': equipment_ids[0] if equipment_ids else False,
            'employee_id': employee_ids[0] if employee_ids else False
        },

        # Change Request
        {
            'name': '🔐 Firewall Kural Güncellemesi - VPN',
            'description': '''Güvenlik ekibinden gelen değişiklik talebi:

10 yeni uzaktan çalışan için VPN erişimi açılacak:
- Port: 1194/UDP
- Protokol: OpenVPN
- IP Range: 192.168.100.0/24
- Güvenlik: 2FA zorunlu

Risk: Düşük
Test ortamı: Hazır
Rollback planı: Mevcut''',
            'request_date': datetime.now(),
            'priority': '2',
            'maintenance_type': 'preventive',
            'equipment_id': equipment_ids[1] if len(equipment_ids) > 1 else False,
            'employee_id': employee_ids[1] if len(employee_ids) > 1 else False
        },

        # HVAC Sorunu
        {
            'name': '❄️ Server Room Klima Arızası',
            'description': '''KRİTİK SICAKLIK UYARISI!

Server room sıcaklığı: 32°C (Normal: 20-22°C)
Klima sistemi yanıt vermiyor.
Acil soğutma gerekiyor!

Geçici önlem: Taşınabilir klima kuruldu''',
            'request_date': datetime.now() - timedelta(hours=3),
            'priority': '3',
            'maintenance_type': 'corrective',
            'equipment_id': equipment_ids[3] if len(equipment_ids) > 3 else False,
            'employee_id': employee_ids[2] if len(employee_ids) > 2 else False
        },

        # Elektrik Problemi
        {
            'name': '⚡ B Blok Kısmi Elektrik Kesintisi',
            'description': '''B Blok 2. katta voltaj düşüklüğü:

- Etkilenen alan: Üretim hattı sol kanat
- Voltaj: 180V (Normal: 220V)
- Başlangıç: 14:30
- Etki: 3 makine durdu

Elektrik panosu kontrol edilmeli''',
            'request_date': datetime.now() - timedelta(hours=1),
            'priority': '2',
            'maintenance_type': 'corrective',
            'employee_id': employee_ids[4] if len(employee_ids) > 4 else False
        },

        # Yedekleme Hatası
        {
            'name': '💾 Otomatik Yedekleme Başarısız',
            'description': '''Son 3 gün yedekleme alınamadı:

Error: Insufficient disk space
- Kullanılan alan: 95%
- Gerekli alan: 500GB
- Mevcut alan: 50GB

Eski yedekler temizlenmeli ve disk alanı artırılmalı''',
            'request_date': datetime.now() - timedelta(days=1),
            'priority': '2',
            'maintenance_type': 'corrective',
            'equipment_id': equipment_ids[0] if equipment_ids else False,
            'employee_id': employee_ids[0] if equipment_ids else False
        },

        # CNC Bakımı
        {
            'name': '⚙️ CNC Makinesi Periyodik Bakım',
            'description': '''Haftalık rutin bakım:

- Yağlama noktaları kontrolü
- Filtre temizliği
- Kalibrasyon kontrolü
- Güvenlik sistemleri testi
- Parça aşınma kontrolü''',
            'request_date': datetime.now(),
            'schedule_date': datetime.now() + timedelta(days=1),
            'priority': '1',
            'maintenance_type': 'preventive',
            'equipment_id': equipment_ids[2] if len(equipment_ids) > 2 else False,
            'employee_id': employee_ids[4] if len(employee_ids) > 4 else False
        }
    ]

    created_count = 0
    for req_data in requests_data:
        try:
            # Schedule date varsa string'e çevir
            if 'schedule_date' in req_data:
                req_data['schedule_date'] = req_data['schedule_date'].strftime('%Y-%m-%d')

            # Request date'i string'e çevir
            req_data['request_date'] = req_data['request_date'].strftime('%Y-%m-%d')

            req_id = create('maintenance.request', req_data)
            request_ids.append(req_id)

            # Priority string'i text'e çevir görüntüleme için
            priority_text = {
                '0': 'Düşük',
                '1': 'Normal',
                '2': 'Yüksek',
                '3': 'KRİTİK'
            }.get(req_data['priority'], 'Normal')

            print(f"  ✓ [{priority_text}] {req_data['name'][:50]}...")
            created_count += 1

        except Exception as e:
            print(f"  ✗ {req_data['name'][:30]}...: {str(e)}")

    # Maintenance Teams oluştur (opsiyonel)
    print("\n[MAINTENANCE TEAMS] Bakım ekipleri kontrolü...")
    team_ids = search('maintenance.team', [])

    if not team_ids:
        print("  Bakım ekipleri oluşturuluyor...")

        teams_data = [
            {'name': 'IT Destek Ekibi', 'company_id': 1},
            {'name': 'Teknik Ekip', 'company_id': 1},
            {'name': 'Acil Müdahale', 'company_id': 1}
        ]

        for team_data in teams_data:
            try:
                team_id = create('maintenance.team', team_data)
                print(f"    ✓ {team_data['name']}")
            except Exception as e:
                print(f"    ✗ {team_data['name']}: {str(e)}")
    else:
        print(f"  • {len(team_ids)} ekip mevcut")

    # Project Tasks (Work Orders) oluştur
    print("\n[PROJECT TASKS] İş emirleri oluşturuluyor...")

    # İlk birkaç request için task oluştur
    for i, req_id in enumerate(request_ids[:5]):
        try:
            # Request bilgilerini oku
            req_info = read('maintenance.request', [req_id], ['name', 'description', 'priority'])
            if req_info:
                req = req_info[0]

                # Project bul veya oluştur
                project_ids = search('project.project', [('name', '=', 'Teknik Servis')])
                if not project_ids:
                    project_id = create('project.project', {
                        'name': 'Teknik Servis',
                        'company_id': 1
                    })
                else:
                    project_id = project_ids[0]

                # Task oluştur
                task_data = {
                    'name': f"WO-{i+1:04d}: {req['name'][:50]}",
                    'project_id': project_id,
                    'description': req['description'],
                    'priority': '1' if req['priority'] == '3' else '0',
                    'user_ids': [(6, 0, [uid])],  # Admin'e ata
                }

                task_id = create('project.task', task_data)
                print(f"  ✓ İş Emri: WO-{i+1:04d}")

        except Exception as e:
            print(f"  ✗ İş Emri WO-{i+1:04d}: {str(e)}")

    # ÖZET
    print("\n" + "="*60)
    print(f"✅ DEMO VERİLERİ OLUŞTURULDU!")
    print("="*60)
    print(f"\nOluşturulan kayıtlar:")
    print(f"  • {created_count} Bakım Talebi")
    print(f"  • {min(5, len(request_ids))} İş Emri (Project Task)")

    print("\n📊 Görüntülemek için:")
    print("  • Bakım Talepleri: Maintenance > Maintenance Requests")
    print("  • İş Emirleri: Project > Tasks")
    print("  • Dashboard: Technical Service > Dashboard")

    print("\n💡 İpucu: Farklı önceliklere ve durumlara sahip talepler oluşturuldu.")
    print("   Filtreleme ve gruplama özelliklerini test edebilirsiniz.")

except xmlrpc.client.Fault as error:
    print(f"\n❌ Odoo Hatası: {error.faultString}")

except Exception as e:
    print(f"\n❌ Hata: {str(e)}")
    import traceback
    traceback.print_exc()