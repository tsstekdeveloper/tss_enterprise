#!/usr/bin/env python3
"""
Create comprehensive work orders for each maintenance request
"""

import xmlrpc.client
import sys
from datetime import datetime, timedelta
import random

# Odoo connection parameters
url = 'http://localhost:8069'
db = 'odoo_tech_service'
username = 'admin'
password = 'admin'

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

if not uid:
    print("Authentication failed!")
    sys.exit(1)

print(f"✅ Connected to Odoo (Database: {db}, UID: {uid})")

# Get all maintenance requests
requests = models.execute_kw(db, uid, password,
    'maintenance.request', 'search_read', [[]],
    {'fields': ['id', 'name', 'maintenance_team_id', 'technician_user_id', 'equipment_id']})

print(f"📋 Found {len(requests)} maintenance requests")

# Get employees for technician assignments
employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read', [[('user_id', '!=', False)]],
    {'fields': ['id', 'name', 'user_id']})

emp_map = {emp['user_id'][0]: emp['id'] for emp in employees if emp.get('user_id')}

# Define work orders for each request
work_order_templates = {
    '🔴 KRİTİK: Ana Sunucu Çöktü!': [
        {
            'name': 'WO-001: Acil Sistem Diagnostik',
            'x_work_type': 'diagnosis',
            'priority': 'urgent',
            'x_estimated_duration': 0.5,
            'x_work_performed': 'Sistem log analizi, hata kayıtları inceleme, donanım kontrolü',
            'x_root_cause': 'Disk alanı dolması nedeniyle sistem yanıt vermiyor',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-002: Disk Temizleme ve Optimizasyon',
            'x_work_type': 'repair',
            'priority': 'urgent',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Log dosyaları temizlendi, geçici dosyalar silindi, disk defragmentasyon yapıldı',
            'x_recommendations': 'Log rotation politikası uygulanmalı',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-003: Sistem Yeniden Başlatma',
            'x_work_type': 'repair',
            'priority': 'urgent',
            'x_estimated_duration': 0.5,
            'x_work_performed': 'Güvenli sistem restart, servis kontrolü',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-004: Performans Testi',
            'x_work_type': 'inspection',
            'priority': 'high',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Stress test, performans metrikleri alındı',
            'x_work_status': 'in_progress'
        },
        {
            'name': 'WO-005: Monitoring Kurulumu',
            'x_work_type': 'installation',
            'priority': 'medium',
            'x_estimated_duration': 2.0,
            'x_work_performed': 'Disk monitoring, alert sistemi kurulumu',
            'x_recommendations': 'Haftalık disk kullanım raporu takibi',
            'x_work_status': 'pending'
        }
    ],

    '❄️ Server Room Klima Arızası': [
        {
            'name': 'WO-010: Klima Sistemi Kontrolü',
            'x_work_type': 'diagnosis',
            'priority': 'urgent',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Kompresör kontrolü, gaz basıncı ölçümü, elektrik bağlantı kontrolü',
            'x_root_cause': 'Kompresör termal koruması devrede',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-011: Kompresör Onarımı',
            'x_work_type': 'repair',
            'priority': 'urgent',
            'x_estimated_duration': 3.0,
            'x_work_performed': 'Kompresör resetleme, yağ seviyesi kontrolü, filtre değişimi',
            'x_work_status': 'in_progress'
        },
        {
            'name': 'WO-012: Geçici Soğutma Kurulumu',
            'x_work_type': 'installation',
            'priority': 'urgent',
            'x_estimated_duration': 2.0,
            'x_work_performed': 'Portatif klima ünitesi kurulumu, hava sirkülasyon fanları yerleştirildi',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-013: Sıcaklık Monitoring',
            'x_work_type': 'inspection',
            'priority': 'high',
            'x_estimated_duration': 0.5,
            'x_work_performed': 'Sıcaklık sensörleri kontrolü, alarm limitlerinin ayarlanması',
            'x_recommendations': 'Yedek klima ünitesi alınması önerilir',
            'x_work_status': 'pending'
        }
    ],

    '⚡ B Blok Kısmi Elektrik Kesintisi': [
        {
            'name': 'WO-020: Elektrik Panosu Kontrolü',
            'x_work_type': 'diagnosis',
            'priority': 'high',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Ana pano ve tali pano kontrolleri, sigorta durumları',
            'x_root_cause': 'Faz dengesizliği nedeniyle otomatik sigorta atmış',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-021: Faz Dengeleme',
            'x_work_type': 'repair',
            'priority': 'high',
            'x_estimated_duration': 2.0,
            'x_work_performed': 'Yük dağılımı yeniden yapılandırıldı, fazlar dengelendi',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-022: Kablo Kontrolü',
            'x_work_type': 'inspection',
            'priority': 'medium',
            'x_estimated_duration': 1.5,
            'x_work_performed': 'Termal kamera ile kablo kontrolü, bağlantı noktaları sıkılık kontrolü',
            'x_recommendations': 'Eski kablo değişimi planlanmalı',
            'x_work_status': 'in_progress'
        }
    ],

    '⚠️ Network Performans Sorunu - Üretim Hattı': [
        {
            'name': 'WO-030: Network Analizi',
            'x_work_type': 'diagnosis',
            'priority': 'high',
            'x_estimated_duration': 2.0,
            'x_work_performed': 'Bandwidth kullanımı analizi, packet loss kontrolü, latency ölçümü',
            'x_root_cause': 'Switch port hızı 100Mbps\'e düşmüş',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-031: Switch Konfigürasyonu',
            'x_work_type': 'repair',
            'priority': 'high',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Port speed ayarı, duplex mode kontrolü, VLAN konfigürasyonu',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-032: Kablo Değişimi',
            'x_work_type': 'repair',
            'priority': 'medium',
            'x_estimated_duration': 2.0,
            'x_work_performed': 'CAT5 kablolar CAT6 ile değiştirildi',
            'x_recommendations': 'Fiber optik altyapıya geçiş değerlendirilmeli',
            'x_work_status': 'pending'
        }
    ],

    '💾 Otomatik Yedekleme Başarısız': [
        {
            'name': 'WO-040: Backup Script Kontrolü',
            'x_work_type': 'diagnosis',
            'priority': 'high',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Script syntax kontrolü, cron job kontrolü, log analizi',
            'x_root_cause': 'Hedef disk alanı yetersiz',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-041: Disk Alanı Genişletme',
            'x_work_type': 'repair',
            'priority': 'high',
            'x_estimated_duration': 2.0,
            'x_work_performed': 'Eski backup dosyaları arşivlendi, retention policy uygulandı',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-042: Backup Testi',
            'x_work_type': 'inspection',
            'priority': 'medium',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Manuel backup testi, restore testi',
            'x_recommendations': 'Cloud backup çözümü değerlendirilmeli',
            'x_work_status': 'pending'
        }
    ],

    '🔐 Firewall Kural Güncellemesi - VPN': [
        {
            'name': 'WO-050: Mevcut Kural Analizi',
            'x_work_type': 'inspection',
            'priority': 'medium',
            'x_estimated_duration': 1.5,
            'x_work_performed': 'Aktif kurallar dökümante edildi, kullanılmayan kurallar tespit edildi',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-051: VPN Kural Güncelleme',
            'x_work_type': 'maintenance',
            'priority': 'high',
            'x_estimated_duration': 2.0,
            'x_work_performed': 'Yeni VPN subnet eklendi, port forwarding kuralları güncellendi',
            'x_recommendations': 'Quarterly kural review yapılmalı',
            'x_work_status': 'in_progress'
        }
    ],

    '⚙️ CNC Makinesi Periyodik Bakım': [
        {
            'name': 'WO-060: Mekanik Kontroller',
            'x_work_type': 'maintenance',
            'priority': 'low',
            'x_estimated_duration': 2.0,
            'x_work_performed': 'Rulman kontrolü, kayış gerginlik ayarı, yağlama',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-061: Elektrik Sistemleri',
            'x_work_type': 'inspection',
            'priority': 'low',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Motor sıcaklık kontrolü, kablo bağlantıları kontrolü',
            'x_work_status': 'pending'
        },
        {
            'name': 'WO-062: Kalibrasyon',
            'x_work_type': 'maintenance',
            'priority': 'medium',
            'x_estimated_duration': 3.0,
            'x_work_performed': 'Eksen kalibrasyonu, hassasiyet testleri',
            'x_recommendations': '3 aylık periyodik bakım takvimine alınmalı',
            'x_work_status': 'pending'
        }
    ],

    '📋 Yeni Personel IT Kurulumu (3 kişi)': [
        {
            'name': 'WO-070: Bilgisayar Hazırlık',
            'x_work_type': 'installation',
            'priority': 'medium',
            'x_estimated_duration': 3.0,
            'x_work_performed': 'Windows kurulumu, Office kurulumu, antivirus kurulumu',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-071: Kullanıcı Hesapları',
            'x_work_type': 'installation',
            'priority': 'medium',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'AD hesapları oluşturuldu, email hesapları aktive edildi',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-072: Network ve Yazıcı',
            'x_work_type': 'installation',
            'priority': 'low',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Network sürücüleri bağlandı, yazıcılar tanımlandı',
            'x_work_status': 'in_progress'
        }
    ],

    '🔧 Aylık Sunucu Bakımı - Ocak 2024': [
        {
            'name': 'WO-080: Sistem Güncellemeleri',
            'x_work_type': 'maintenance',
            'priority': 'medium',
            'x_estimated_duration': 2.0,
            'x_work_performed': 'OS güncellemeleri, security patch kurulumu',
            'x_work_status': 'pending'
        },
        {
            'name': 'WO-081: Backup Kontrolü',
            'x_work_type': 'inspection',
            'priority': 'medium',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Backup integrity kontrolü, restore testi',
            'x_work_status': 'pending'
        }
    ],

    '🖨️ 2. Kat Yazıcı Kağıt Sıkışması': [
        {
            'name': 'WO-090: Kağıt Temizleme',
            'x_work_type': 'repair',
            'priority': 'low',
            'x_estimated_duration': 0.5,
            'x_work_performed': 'Sıkışan kağıt çıkarıldı, sensör temizliği yapıldı',
            'x_work_status': 'completed'
        },
        {
            'name': 'WO-091: Yazıcı Bakımı',
            'x_work_type': 'maintenance',
            'priority': 'low',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Toner değişimi, drum ünitesi temizliği',
            'x_recommendations': 'Aylık temizlik yapılmalı',
            'x_work_status': 'pending'
        }
    ],

    'fvfgfg.': [
        {
            'name': 'WO-100: Genel Kontrol',
            'x_work_type': 'inspection',
            'priority': 'low',
            'x_estimated_duration': 1.0,
            'x_work_performed': 'Test work order',
            'x_work_status': 'pending'
        }
    ]
}

print("\n🔧 Creating work orders for maintenance requests...")
print("="*60)

created_count = 0
base_date = datetime.now()

for request in requests:
    request_name = request['name']

    if request_name in work_order_templates:
        wo_templates = work_order_templates[request_name]

        print(f"\n📋 Request: {request_name[:40]}")

        # Get technician employee ID
        tech_employee_id = None
        if request.get('technician_user_id'):
            tech_employee_id = emp_map.get(request['technician_user_id'][0])

        for i, wo_template in enumerate(wo_templates):
            # Calculate scheduled date (spread work orders over next days)
            scheduled_date = base_date + timedelta(days=random.randint(0, 3), hours=random.randint(8, 17))

            work_order_data = {
                'name': wo_template['name'],
                'x_request_id': request['id'],
                'x_work_type': wo_template['x_work_type'],
                'priority': wo_template.get('priority', 'medium'),
                'x_estimated_duration': wo_template.get('x_estimated_duration', 1.0),
                'x_scheduled_date': scheduled_date.strftime('%Y-%m-%d %H:%M:%S'),
                'x_work_status': wo_template.get('x_work_status', 'pending'),
                'description': wo_template.get('x_work_performed', ''),
                'x_work_performed': wo_template.get('x_work_performed', ''),
                'x_root_cause': wo_template.get('x_root_cause', ''),
                'x_recommendations': wo_template.get('x_recommendations', ''),
                'x_safety_checklist_completed': wo_template.get('x_work_status') == 'completed',
            }

            # Add team and technician
            if request.get('maintenance_team_id'):
                work_order_data['team_id'] = request['maintenance_team_id'][0]

            if tech_employee_id:
                work_order_data['x_technician_id'] = tech_employee_id

            # Add equipment if available
            if request.get('equipment_id'):
                work_order_data['asset_id'] = request['equipment_id'][0]

            # Set dates for completed work orders
            if wo_template.get('x_work_status') == 'completed':
                start_time = scheduled_date - timedelta(hours=wo_template.get('x_estimated_duration', 1))
                work_order_data['x_start_datetime'] = start_time.strftime('%Y-%m-%d %H:%M:%S')
                work_order_data['x_end_datetime'] = scheduled_date.strftime('%Y-%m-%d %H:%M:%S')
            elif wo_template.get('x_work_status') == 'in_progress':
                work_order_data['x_start_datetime'] = scheduled_date.strftime('%Y-%m-%d %H:%M:%S')

            try:
                wo_id = models.execute_kw(db, uid, password,
                    'technical_service.work_order', 'create', [work_order_data])

                created_count += 1
                status_icon = {
                    'pending': '⏳',
                    'in_progress': '🔄',
                    'completed': '✅',
                    'paused': '⏸️',
                    'cancelled': '❌'
                }.get(wo_template.get('x_work_status', 'pending'), '❓')

                print(f"  {status_icon} Created: {wo_template['name'][:30]:30} [{wo_template['x_work_type']:12}] {wo_template.get('x_estimated_duration', 1)}h")

            except Exception as e:
                print(f"  ❌ Error creating {wo_template['name']}: {str(e)[:50]}")

print("\n" + "="*60)
print(f"✅ Created {created_count} work orders")

# Verification
print("\n📊 WORK ORDER SUMMARY")
print("="*60)

# Get work order statistics
work_orders = models.execute_kw(db, uid, password,
    'technical_service.work_order', 'search_read', [[]],
    {'fields': ['x_request_id', 'x_work_status', 'x_work_type']})

# Group by request
request_wo_count = {}
status_count = {}
type_count = {}

for wo in work_orders:
    # Count by request
    req_id = wo['x_request_id'][0] if wo.get('x_request_id') else 'None'
    request_wo_count[req_id] = request_wo_count.get(req_id, 0) + 1

    # Count by status
    status = wo.get('x_work_status', 'unknown')
    status_count[status] = status_count.get(status, 0) + 1

    # Count by type
    work_type = wo.get('x_work_type', 'unknown')
    type_count[work_type] = type_count.get(work_type, 0) + 1

print("\n📈 Status Distribution:")
for status, count in sorted(status_count.items()):
    print(f"  • {status:15}: {count:3} work orders")

print("\n🔧 Type Distribution:")
for work_type, count in sorted(type_count.items()):
    print(f"  • {work_type:15}: {count:3} work orders")

print("\n📋 Work Orders per Request:")
for request in requests[:5]:  # Show first 5
    req_id = request['id']
    count = request_wo_count.get(req_id, 0)
    print(f"  • {request['name'][:35]:35}: {count} WO")

print("\n✅ Work order creation completed!")
print(f"📍 Database: {db}")