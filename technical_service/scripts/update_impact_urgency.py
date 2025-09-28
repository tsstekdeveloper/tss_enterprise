#!/usr/bin/env python3
"""
Update impact and urgency fields for maintenance requests
Priority will be automatically calculated based on impact × urgency matrix
"""

import xmlrpc.client
import sys

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

# Define impact and urgency for each request based on their nature
request_updates = [
    {
        'name': '🔴 KRİTİK: Ana Sunucu Çöktü!',
        'impact': 'critical',  # Entire system affected
        'urgency': 'critical',  # Immediate action needed
        'expected_priority': 'P1 - Critical',
        'reason': 'Tüm sistem etkilendi, acil müdahale gerekli'
    },
    {
        'name': '❄️ Server Room Klima Arızası',
        'impact': 'high',      # Floor/Building affected (server room)
        'urgency': 'critical',  # Immediate (servers can overheat)
        'expected_priority': 'P1 - Critical',
        'reason': 'Sunucu odası kritik sıcaklık riski'
    },
    {
        'name': '⚡ B Blok Kısmi Elektrik Kesintisi',
        'impact': 'high',      # Floor/Building affected
        'urgency': 'high',     # Urgent
        'expected_priority': 'P1 - Critical',
        'reason': 'Bina/kat etkilendi, acil çözüm gerekli'
    },
    {
        'name': '⚠️ Network Performans Sorunu - Üretim Hattı',
        'impact': 'high',      # Floor/Building (production line)
        'urgency': 'medium',   # Normal (performance issue, not outage)
        'expected_priority': 'P1 - Critical',
        'reason': 'Üretim hattı etkilendi'
    },
    {
        'name': '💾 Otomatik Yedekleme Başarısız',
        'impact': 'medium',    # Department affected (IT systems)
        'urgency': 'high',     # Urgent (data at risk)
        'expected_priority': 'P1 - Critical',
        'reason': 'Veri kaybı riski, hızlı çözüm gerekli'
    },
    {
        'name': '🔐 Firewall Kural Güncellemesi - VPN',
        'impact': 'medium',    # Department (remote users)
        'urgency': 'medium',   # Normal (planned update)
        'expected_priority': 'P2 - High',
        'reason': 'Uzaktan çalışanlar etkilendi, planlı güncelleme'
    },
    {
        'name': '⚙️ CNC Makinesi Periyodik Bakım',
        'impact': 'low',       # Single machine
        'urgency': 'low',      # Can wait (periodic maintenance)
        'expected_priority': 'P4 - Low',
        'reason': 'Planlı periyodik bakım, bekleyebilir'
    },
    {
        'name': '📋 Yeni Personel IT Kurulumu (3 kişi)',
        'impact': 'low',       # Single users (new employees)
        'urgency': 'medium',   # Normal
        'expected_priority': 'P3 - Medium',
        'reason': 'Yeni personel kurulumu, normal öncelik'
    },
    {
        'name': '🔧 Aylık Sunucu Bakımı - Ocak 2024',
        'impact': 'medium',    # Department (server maintenance)
        'urgency': 'low',      # Can wait (scheduled)
        'expected_priority': 'P3 - Medium',
        'reason': 'Planlı bakım, zamanlanmış'
    },
    {
        'name': '🖨️ 2. Kat Yazıcı Kağıt Sıkışması',
        'impact': 'low',       # Single device
        'urgency': 'medium',   # Normal
        'expected_priority': 'P3 - Medium',
        'reason': 'Tek cihaz etkilendi, alternatif yazıcılar var'
    },
    {
        'name': 'fvfgfg.',
        'impact': 'low',       # Unknown/test
        'urgency': 'low',      # Can wait
        'expected_priority': 'P4 - Low',
        'reason': 'Test/belirsiz talep'
    }
]

# Get all maintenance requests
requests = models.execute_kw(db, uid, password,
    'maintenance.request', 'search_read', [[]],
    {'fields': ['id', 'name', 'x_impact', 'x_urgency']})

print(f"📋 Found {len(requests)} maintenance requests")

print("\n🔧 Updating impact and urgency fields...")
print("="*80)
print(f"{'Request':40} {'Impact':12} {'Urgency':12} {'Priority':15}")
print("-"*80)

# Priority matrix based on impact × urgency
priority_matrix = {
    ('low', 'low'): 'p4',
    ('low', 'medium'): 'p3',
    ('low', 'high'): 'p2',
    ('low', 'critical'): 'p2',
    ('medium', 'low'): 'p3',
    ('medium', 'medium'): 'p2',
    ('medium', 'high'): 'p1',
    ('medium', 'critical'): 'p1',
    ('high', 'low'): 'p2',
    ('high', 'medium'): 'p1',
    ('high', 'high'): 'p1',
    ('high', 'critical'): 'p1',
    ('critical', 'low'): 'p1',
    ('critical', 'medium'): 'p1',
    ('critical', 'high'): 'p1',
    ('critical', 'critical'): 'p1',
}

updated_count = 0
for update in request_updates:
    # Find the request
    matching_requests = [r for r in requests if r['name'] == update['name']]

    if matching_requests:
        request = matching_requests[0]

        # Update impact and urgency
        update_data = {
            'x_impact': update['impact'],
            'x_urgency': update['urgency']
        }

        try:
            models.execute_kw(db, uid, password,
                'maintenance.request', 'write',
                [[request['id']], update_data])

            # Calculate expected priority
            expected_priority = priority_matrix.get((update['impact'], update['urgency']), 'p3')
            priority_display = {
                'p1': 'P1-Critical',
                'p2': 'P2-High',
                'p3': 'P3-Medium',
                'p4': 'P4-Low'
            }[expected_priority]

            impact_display = update['impact'].capitalize()
            urgency_display = update['urgency'].capitalize()

            print(f"{update['name'][:38]:38} {impact_display:12} {urgency_display:12} → {priority_display:15}")
            updated_count += 1

        except Exception as e:
            print(f"❌ Error updating {request['name']}: {str(e)}")
    else:
        print(f"⚠️  Request not found: {update['name']}")

print("-"*80)
print(f"✅ Updated {updated_count} requests with impact and urgency values")

# Verify the priority calculations
print("\n📊 VERIFICATION - Priority Matrix Results")
print("="*80)

# Get updated requests to see the computed priorities
updated_requests = models.execute_kw(db, uid, password,
    'maintenance.request', 'search_read', [[]],
    {'fields': ['name', 'x_impact', 'x_urgency', 'x_priority_level', 'priority'],
     'order': 'x_priority_level'})

print("\n{:40} {:10} {:10} {:12} {}".format("Request", "Impact", "Urgency", "Auto Priority", "Reason"))
print("-"*90)

impact_icons = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🟠',
    'critical': '🔴'
}

urgency_icons = {
    'low': '💤',
    'medium': '⏱️',
    'high': '⚡',
    'critical': '🚨'
}

priority_colors = {
    'p1': '🔴 P1-Critical',
    'p2': '🟡 P2-High',
    'p3': '🔵 P3-Medium',
    'p4': '🟢 P4-Low'
}

for req in updated_requests:
    req_name = req['name'][:38]
    impact = req.get('x_impact', 'low')
    urgency = req.get('x_urgency', 'low')
    priority = req.get('x_priority_level', 'p3')

    impact_icon = impact_icons.get(impact, '⚪')
    urgency_icon = urgency_icons.get(urgency, '⚪')
    priority_display = priority_colors.get(priority, '⚪ Unknown')

    # Find reason from our updates
    reason = next((u['reason'] for u in request_updates if u['name'] == req['name']), '')

    print(f"{req_name:38} {impact_icon} {impact:8} {urgency_icon} {urgency:8} {priority_display:15}")
    if reason:
        print(f"{'':38} └→ {reason}")

print("\n" + "="*80)
print("📈 Priority Distribution:")
print("-"*40)

# Count priorities
priority_counts = {}
for req in updated_requests:
    priority = req.get('x_priority_level', 'unknown')
    priority_counts[priority] = priority_counts.get(priority, 0) + 1

for priority in ['p1', 'p2', 'p3', 'p4']:
    if priority in priority_counts:
        display = priority_colors.get(priority, priority)
        print(f"  {display}: {priority_counts[priority]} requests")

print("\n✅ Impact and urgency configuration completed!")
print(f"📍 Database: {db}")