#!/usr/bin/env python3
"""
Create checklists for work orders with various parameters
Each work order will have 1-8 checklist items with different completion statuses
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

# Get all work orders
work_orders = models.execute_kw(db, uid, password,
    'technical_service.work_order', 'search_read', [[]],
    {'fields': ['id', 'name', 'x_work_type'], 'order': 'id'})

print(f"📋 Found {len(work_orders)} work orders")

# Define checklist templates based on work type
checklist_templates = {
    'diagnosis': [
        {'item': '🔍 Görsel kontrol ve ilk değerlendirme', 'priority': 'high'},
        {'item': '📊 Sistem loglarını kontrol et', 'priority': 'medium'},
        {'item': '🧪 Test prosedürlerini uygula', 'priority': 'high'},
        {'item': '📝 Arıza kodlarını kaydet', 'priority': 'high'},
        {'item': '🔧 Gerekli yedek parçaları tespit et', 'priority': 'medium'},
        {'item': '📸 Arıza fotoğraflarını çek', 'priority': 'low'},
        {'item': '📋 Tanı raporunu hazırla', 'priority': 'high'},
        {'item': '✅ Müşteri onayı al', 'priority': 'high'}
    ],
    'repair': [
        {'item': '🛡️ Güvenlik prosedürlerini uygula', 'priority': 'critical'},
        {'item': '🔌 Sistemi güvenli modda kapat', 'priority': 'critical'},
        {'item': '🔧 Arızalı parçayı sök', 'priority': 'high'},
        {'item': '📦 Yeni parçayı kontrol et', 'priority': 'high'},
        {'item': '⚙️ Yeni parçayı monte et', 'priority': 'high'},
        {'item': '🔩 Bağlantıları ve torku kontrol et', 'priority': 'medium'},
        {'item': '🧪 İşlevsellik testini yap', 'priority': 'critical'},
        {'item': '📝 Onarım formunu doldur', 'priority': 'medium'}
    ],
    'maintenance': [
        {'item': '📋 Bakım kontrol listesini hazırla', 'priority': 'medium'},
        {'item': '🧹 Ekipman temizliği yap', 'priority': 'low'},
        {'item': '🛢️ Yağ seviyelerini kontrol et', 'priority': 'high'},
        {'item': '🔧 Gevşek bağlantıları sıkıştır', 'priority': 'medium'},
        {'item': '📏 Kalibrasyon kontrolü yap', 'priority': 'high'},
        {'item': '🎯 Performans testleri uygula', 'priority': 'medium'},
        {'item': '📝 Bakım etiketini güncelle', 'priority': 'low'}
    ],
    'inspection': [
        {'item': '👁️ Genel görsel inceleme', 'priority': 'medium'},
        {'item': '📏 Ölçüm ve tolerans kontrolü', 'priority': 'high'},
        {'item': '🌡️ Sıcaklık kontrolü', 'priority': 'medium'},
        {'item': '🔊 Ses ve titreşim analizi', 'priority': 'medium'},
        {'item': '⚡ Elektrik bağlantı kontrolü', 'priority': 'high'},
        {'item': '📊 Performans değerlendirmesi', 'priority': 'medium'}
    ],
    'installation': [
        {'item': '📍 Kurulum yerini hazırla', 'priority': 'high'},
        {'item': '📦 Paket kontrolü ve açma', 'priority': 'medium'},
        {'item': '📖 Kurulum kılavuzunu incele', 'priority': 'low'},
        {'item': '🔌 Elektrik bağlantılarını yap', 'priority': 'critical'},
        {'item': '🌐 Network konfigürasyonu', 'priority': 'high'},
        {'item': '⚙️ İlk çalıştırma ve konfigürasyon', 'priority': 'critical'},
        {'item': '🧪 Test ve doğrulama', 'priority': 'critical'},
        {'item': '👨‍🏫 Kullanıcı eğitimi ver', 'priority': 'medium'}
    ],
    'calibration': [
        {'item': '🎯 Referans standartları hazırla', 'priority': 'high'},
        {'item': '🌡️ Ortam koşullarını kontrol et', 'priority': 'medium'},
        {'item': '📏 Kalibrasyon prosedürünü uygula', 'priority': 'critical'},
        {'item': '📊 Sapma değerlerini kaydet', 'priority': 'high'},
        {'item': '🔧 Gerekli ayarlamaları yap', 'priority': 'high'},
        {'item': '✅ Doğrulama testini yap', 'priority': 'critical'},
        {'item': '📜 Kalibrasyon sertifikası hazırla', 'priority': 'high'}
    ],
    'upgrade': [
        {'item': '💾 Mevcut sistemi yedekle', 'priority': 'critical'},
        {'item': '📋 Uyumluluk kontrolü yap', 'priority': 'high'},
        {'item': '🔄 Güncelleme paketini indir', 'priority': 'medium'},
        {'item': '⏸️ Sistemi maintenance moduna al', 'priority': 'high'},
        {'item': '🚀 Güncellemeyi uygula', 'priority': 'critical'},
        {'item': '🧪 Sistem testlerini çalıştır', 'priority': 'critical'},
        {'item': '📝 Güncelleme loglarını kontrol et', 'priority': 'medium'},
        {'item': '✅ Sistemi production moduna al', 'priority': 'high'}
    ],
    'emergency': [
        {'item': '🚨 Acil durum prosedürlerini başlat', 'priority': 'critical'},
        {'item': '🛡️ Güvenlik önlemlerini al', 'priority': 'critical'},
        {'item': '📞 İlgili birimleri bilgilendir', 'priority': 'critical'},
        {'item': '🔧 Acil müdahaleyi gerçekleştir', 'priority': 'critical'},
        {'item': '📝 Olay raporunu hazırla', 'priority': 'high'}
    ]
}

# Default checklist for undefined work types
default_checklist = [
    {'item': '📋 İş emrini kontrol et', 'priority': 'medium'},
    {'item': '🔍 Durum değerlendirmesi yap', 'priority': 'high'},
    {'item': '🔧 Gerekli işlemi uygula', 'priority': 'high'},
    {'item': '✅ Kalite kontrolü yap', 'priority': 'high'},
    {'item': '📝 İş tamamlama formu doldur', 'priority': 'medium'}
]

print("\n🔧 Creating checklists for work orders...")
print("="*60)

created_count = 0
completion_date = datetime.now()

for wo in work_orders:
    work_type = wo.get('x_work_type', 'other')

    # Get appropriate checklist template
    if work_type in checklist_templates:
        template = checklist_templates[work_type]
    else:
        template = default_checklist

    # Randomly select number of checklist items (1-8)
    num_items = random.randint(1, min(8, len(template)))
    selected_items = random.sample(template, num_items)

    # Create checklist items for this work order
    items_created = 0
    for idx, item in enumerate(selected_items):
        # Randomly determine completion status
        is_done = random.choice([True, True, True, False])  # 75% completion rate

        checklist_data = {
            'work_order_id': wo['id'],
            'name': item['item'],
            'description': f"Detaylı açıklama: {item['item']}",
            'is_done': is_done,
            'sequence': idx + 1
        }

        # Add completion date if done
        if is_done:
            # Random completion time in the last 7 days
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            comp_date = completion_date - timedelta(days=days_ago, hours=hours_ago)
            checklist_data['done_date'] = comp_date.strftime('%Y-%m-%d %H:%M:%S')
            checklist_data['notes'] = random.choice([
                'Kontrol tamamlandı, sorun yok',
                'İşlem başarıyla gerçekleştirildi',
                'Test sonuçları normal',
                'Standartlara uygun',
                'Onaylandı ve doğrulandı',
                'Müşteri tarafından kabul edildi',
                'Teknik şartnamelere uygun'
            ])
        else:
            checklist_data['notes'] = random.choice([
                'Beklemede',
                'Yedek parça bekleniyor',
                'Onay bekleniyor',
                'Test aşamasında',
                'İşlem devam ediyor',
                '',
                ''
            ])

        try:
            models.execute_kw(db, uid, password,
                'technical_service.work_order.checklist', 'create', [checklist_data])
            items_created += 1
        except Exception as e:
            print(f"❌ Error creating checklist item for {wo['name']}: {str(e)[:50]}")

    if items_created > 0:
        completion_percent = (len([i for i in selected_items[:items_created] if random.choice([True, True, True, False])]) / items_created) * 100

        # Update work order checklist progress
        try:
            models.execute_kw(db, uid, password,
                'technical_service.work_order', 'write',
                [[wo['id']], {'x_checklist_progress': completion_percent}])
        except:
            pass  # Field might not exist

        status = "✅" if completion_percent == 100 else "🔄"
        print(f"{status} {wo['name'][:30]:30} - {items_created:2} items ({completion_percent:.0f}% complete)")
        created_count += 1

print("\n" + "="*60)
print(f"✅ Created checklists for {created_count} work orders")

# Verification
print("\n📊 CHECKLIST SUMMARY")
print("="*60)

# Get checklist statistics
all_checklists = models.execute_kw(db, uid, password,
    'technical_service.work_order.checklist', 'search_read', [[]],
    {'fields': ['work_order_id', 'is_done', 'name']})

# Group by work order
wo_stats = {}
for item in all_checklists:
    wo_id = item['work_order_id'][0] if item['work_order_id'] else None
    if wo_id:
        if wo_id not in wo_stats:
            wo_stats[wo_id] = {'total': 0, 'done': 0}
        wo_stats[wo_id]['total'] += 1
        if item['is_done']:
            wo_stats[wo_id]['done'] += 1

# Display summary
print("\n📋 Checklist Distribution:")
print(f"  • Total Work Orders with Checklists: {len(wo_stats)}")
print(f"  • Total Checklist Items: {len(all_checklists)}")
print(f"  • Average Items per Work Order: {len(all_checklists)/len(wo_stats) if wo_stats else 0:.1f}")

done_count = len([i for i in all_checklists if i['is_done']])
print(f"\n✅ Completion Status:")
print(f"  • Completed Items: {done_count}")
print(f"  • Pending Items: {len(all_checklists) - done_count}")
print(f"  • Overall Completion: {(done_count/len(all_checklists)*100) if all_checklists else 0:.1f}%")

# Show some sample checklist items
print(f"\n📝 Sample Checklist Items:")
for item in all_checklists[:5]:
    status = "✅" if item['is_done'] else "⬜"
    wo_name = item['work_order_id'][1] if item['work_order_id'] else 'Unknown'
    print(f"  {status} {item['name'][:50]:50} ({wo_name[:20]})")

print("\n✅ Work order checklists created successfully!")
print(f"📍 Database: {db}")