#!/usr/bin/env python3
"""
Assign technicians to maintenance requests based on their team membership
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

# Get all maintenance requests with their teams
requests = models.execute_kw(db, uid, password,
    'maintenance.request', 'search_read', [[]],
    {'fields': ['id', 'name', 'maintenance_team_id', 'technician_user_id', 'priority']})

print(f"📋 Found {len(requests)} maintenance requests")

# Specific technician assignments based on expertise and workload
technician_assignments = [
    {'request': '⚙️ CNC Makinesi Periyodik Bakım', 'technician': 'Ali Özkan', 'reason': 'CNC uzmanı'},
    {'request': '💾 Otomatik Yedekleme Başarısız', 'technician': 'Zeynep Arslan', 'reason': 'Backup sistemleri uzmanı'},
    {'request': '⚡ B Blok Kısmi Elektrik Kesintisi', 'technician': 'Kaan Öz', 'reason': 'Elektrik sistemleri'},
    {'request': '❄️ Server Room Klima Arızası', 'technician': 'Cem Yıldız', 'reason': 'Acil müdahale ekibi lideri'},
    {'request': '🔐 Firewall Kural Güncellemesi - VPN', 'technician': 'Pınar Tan', 'reason': 'Network güvenlik uzmanı'},
    {'request': '🔧 Aylık Sunucu Bakımı - Ocak 2024', 'technician': 'Murat Çelik', 'reason': 'Server yönetimi'},
    {'request': '🖨️ 2. Kat Yazıcı Kağıt Sıkışması', 'technician': 'Can Aydın', 'reason': 'Donanım desteği'},
    {'request': '📋 Yeni Personel IT Kurulumu (3 kişi)', 'technician': 'Elif Güneş', 'reason': 'Kullanıcı kurulum uzmanı'},
    {'request': '⚠️ Network Performans Sorunu - Üretim Hattı', 'technician': 'Rıza Ün', 'reason': 'Network performans uzmanı'},
    {'request': '🔴 KRİTİK: Ana Sunucu Çöktü!', 'technician': 'Veli Çelik', 'reason': 'Kritik sistem uzmanı'},
    {'request': 'fvfgfg.', 'technician': 'Ahmet Yılmaz', 'reason': 'Genel bakım'},
]

# Get all users to find technician user IDs
all_users = models.execute_kw(db, uid, password,
    'res.users', 'search_read', [[('active', '=', True)]],
    {'fields': ['id', 'name', 'partner_id']})

# Get partner names for better matching
user_map = {}
for user in all_users:
    if user.get('partner_id'):
        partner = models.execute_kw(db, uid, password,
            'res.partner', 'read', [user['partner_id'][0]], {'fields': ['name']})[0]
        user_map[partner['name']] = user['id']
        # Also map by user name
        user_map[user['name']] = user['id']

print(f"📋 Found {len(user_map)} users")

print("\n🔧 Assigning technicians to maintenance requests...")
print("="*60)

updated_count = 0
for assignment in technician_assignments:
    # Find the request
    matching_requests = [r for r in requests if r['name'] == assignment['request']]

    if matching_requests:
        request = matching_requests[0]

        # Find technician user ID
        tech_user_id = user_map.get(assignment['technician'])

        if tech_user_id:
            try:
                # Update request with technician
                models.execute_kw(db, uid, password,
                    'maintenance.request', 'write',
                    [[request['id']], {'technician_user_id': tech_user_id}])

                print(f"✅ {request['name'][:35]:35} → {assignment['technician']:20} ({assignment['reason']})")
                updated_count += 1

            except Exception as e:
                print(f"❌ Error updating {request['name']}: {str(e)}")
        else:
            print(f"⚠️  Technician not found: {assignment['technician']} for {request['name'][:30]}")
    else:
        print(f"⚠️  Request not found: {assignment['request'][:30]}")

print("\n" + "="*60)
print(f"✅ Assigned {updated_count} technicians to maintenance requests")

# Final verification
print("\n📊 FINAL ASSIGNMENTS")
print("="*60)

# Get updated requests
updated_requests = models.execute_kw(db, uid, password,
    'maintenance.request', 'search_read', [[]],
    {'fields': ['name', 'maintenance_team_id', 'technician_user_id', 'priority'],
     'order': 'priority desc, id'})

print("\n{:40} {:30} {:25}".format("Request", "Team", "Technician"))
print("-"*95)

for req in updated_requests:
    req_name = req['name'][:38]

    team = req.get('maintenance_team_id')
    if team:
        team_name = team[1] if isinstance(team, list) else 'No Team'
        if isinstance(team_name, dict):
            team_name = team_name.get('en_US', str(team_name))
    else:
        team_name = '❌ Unassigned'
    team_name = team_name[:28]

    tech = req.get('technician_user_id')
    tech_name = tech[1][:23] if tech else '❌ No Technician'

    priority_icons = {'0': '🟢', '1': '🔵', '2': '🟡', '3': '🔴'}
    priority_icon = priority_icons.get(req.get('priority', '1'), '⚪')

    print(f"{priority_icon} {req_name:38} {team_name:28} {tech_name:23}")

print("\n" + "="*60)
print("✅ Technician assignments completed successfully!")
print(f"📍 Database: {db}")