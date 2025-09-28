#!/usr/bin/env python3
"""
Assign teams to service requests based on request type and content
"""

import xmlrpc.client
import sys
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
    {'fields': ['id', 'name', 'description', 'priority', 'maintenance_team_id', 'technician_user_id']})

print(f"📋 Found {len(requests)} maintenance requests")

# Get all teams
teams = models.execute_kw(db, uid, password,
    'maintenance.team', 'search_read', [[]],
    {'fields': ['id', 'name'], 'order': 'id'})

team_map = {}
for team in teams:
    team_name = team['name']
    if isinstance(team_name, dict):
        team_name = team_name.get('en_US', str(team_name))
    team_map[team['id']] = team_name

# Get team members for technician assignment
team_members = {}
for team_id in team_map.keys():
    members = models.execute_kw(db, uid, password,
        'technical_service.team.member', 'search_read',
        [[('team_id', '=', team_id)]],
        {'fields': ['employee_id', 'user_id']})

    team_members[team_id] = [(m['employee_id'][0] if m['employee_id'] else None,
                               m['user_id'][0] if m['user_id'] else None) for m in members]

# Define assignment logic based on request content
def determine_team_and_tech(request):
    """Determine appropriate team and technician based on request details"""
    name = request['name'].lower()
    desc = (request.get('description') or '').lower()
    priority = request.get('priority', '1')

    team_id = None

    # Analyze request content and assign appropriate team
    if any(word in name + desc for word in ['cnc', 'makine', 'torna', 'freze', 'mekanik', 'üretim']):
        team_id = 3  # Teknik Ekip
    elif any(word in name + desc for word in ['elektrik', 'trafo', 'sigorta', 'kablo', 'voltaj', 'güç']):
        team_id = 5  # Elektrik-Mekanik Ekibi
    elif any(word in name + desc for word in ['network', 'ağ', 'internet', 'wifi', 'switch', 'router', 'firewall']):
        team_id = 6  # Network Uzmanları
    elif any(word in name + desc for word in ['bilgisayar', 'yazılım', 'program', 'windows', 'office', 'yazıcı', 'printer', 'yedekleme', 'backup']):
        team_id = 2  # IT Destek Ekibi
    elif any(word in name + desc for word in ['klima', 'kalorifer', 'tesisat', 'su', 'bina', 'asansör', 'temizlik']):
        team_id = 7  # Bina Bakım Ekibi
    elif any(word in name + desc for word in ['sunucu', 'server', 'kritik', 'acil', 'emergency']) or priority in ['2', '3']:
        team_id = 4  # Acil Müdahale Ekibi
    else:
        # Default assignment based on priority
        if priority == '3':  # Kritik
            team_id = 4  # Acil Müdahale Ekibi
        elif priority == '2':  # Yüksek
            team_id = random.choice([1, 3, 5])  # İç Bakım, Teknik, Elektrik-Mekanik
        else:
            team_id = 1  # İç Bakım (default)

    # Get a technician from the assigned team
    technician_user_id = None
    if team_id and team_id in team_members and team_members[team_id]:
        # Select a technician from the team (round-robin would be better but using random for simplicity)
        member = random.choice(team_members[team_id])
        technician_user_id = member[1]  # user_id

    return team_id, technician_user_id

# Assignment mapping
assignments = [
    {'name': '⚙️ CNC Makinesi Periyodik Bakım', 'team_id': 3, 'desc': 'Teknik Ekip - CNC/Makine bakımı'},
    {'name': '💾 Otomatik Yedekleme Başarısız', 'team_id': 2, 'desc': 'IT Destek - Backup sorunu'},
    {'name': '⚡ B Blok Kısmi Elektrik Kesintisi', 'team_id': 5, 'desc': 'Elektrik-Mekanik - Elektrik arızası'},
    {'name': '❄️ Server Room Klima Arızası', 'team_id': 4, 'desc': 'Acil Müdahale - Kritik klima'},
    {'name': '🔐 Firewall Kural Güncellemesi - VPN', 'team_id': 6, 'desc': 'Network Uzmanları - Firewall/VPN'},
    {'name': '🔧 Aylık Sunucu Bakımı - Ocak 2024', 'team_id': 2, 'desc': 'IT Destek - Server bakımı'},
    {'name': '🖨️ 2. Kat Yazıcı Kağıt Sıkışması', 'team_id': 2, 'desc': 'IT Destek - Yazıcı sorunu'},
    {'name': '📋 Yeni Personel IT Kurulumu (3 kişi)', 'team_id': 2, 'desc': 'IT Destek - Kurulum'},
    {'name': '⚠️ Network Performans Sorunu - Üretim Hattı', 'team_id': 6, 'desc': 'Network Uzmanları - Network sorunu'},
    {'name': '🔴 KRİTİK: Ana Sunucu Çöktü!', 'team_id': 4, 'desc': 'Acil Müdahale - Kritik sunucu'},
    {'name': 'fvfgfg.', 'team_id': 1, 'desc': 'İç Bakım - Genel'},
]

print("\n🔧 Assigning teams to maintenance requests...")
print("="*60)

updated_count = 0
for assignment in assignments:
    # Find the request
    matching_requests = [r for r in requests if r['name'] == assignment['name']]

    if matching_requests:
        request = matching_requests[0]

        # Get a technician from the team
        tech_user_id = None
        if assignment['team_id'] in team_members and team_members[assignment['team_id']]:
            member = random.choice(team_members[assignment['team_id']])
            tech_user_id = member[1]  # user_id

        # Update request
        update_data = {
            'maintenance_team_id': assignment['team_id']
        }

        if tech_user_id:
            update_data['technician_user_id'] = tech_user_id

        try:
            models.execute_kw(db, uid, password,
                'maintenance.request', 'write',
                [[request['id']], update_data])

            team_name = team_map.get(assignment['team_id'], 'Unknown')
            tech_info = f", Tech User ID: {tech_user_id}" if tech_user_id else ""
            print(f"✅ {request['name'][:40]:40} → {team_name:25} {assignment['desc']}")
            updated_count += 1

        except Exception as e:
            print(f"❌ Error updating {request['name']}: {str(e)}")
    else:
        print(f"⚠️  Request not found: {assignment['name']}")

print("\n" + "="*60)
print(f"✅ Updated {updated_count} maintenance requests with team assignments")

# Verification
print("\n📊 FINAL VERIFICATION")
print("="*60)

# Get updated requests
updated_requests = models.execute_kw(db, uid, password,
    'maintenance.request', 'search_read', [[]],
    {'fields': ['name', 'maintenance_team_id', 'technician_user_id', 'priority'], 'order': 'priority desc, id'})

# Group by team
team_assignments = {}
for req in updated_requests:
    team = req.get('maintenance_team_id')
    if team:
        team_name = team[1] if isinstance(team, list) else 'No Team'
        if isinstance(team_name, dict):
            team_name = team_name.get('en_US', str(team_name))
    else:
        team_name = 'Unassigned'

    if team_name not in team_assignments:
        team_assignments[team_name] = []

    tech = req.get('technician_user_id')
    tech_name = tech[1] if tech else 'No Technician'

    priority_map = {'0': 'Low', '1': 'Normal', '2': 'High', '3': 'Critical'}
    priority = priority_map.get(req.get('priority', '1'), 'Normal')

    team_assignments[team_name].append({
        'name': req['name'][:30],
        'technician': tech_name,
        'priority': priority
    })

for team_name, reqs in sorted(team_assignments.items()):
    print(f"\n{team_name} ({len(reqs)} requests):")
    print("-" * 50)
    for req in reqs[:3]:  # Show first 3
        print(f"  • {req['name']:30} [{req['priority']:8}]")
    if len(reqs) > 3:
        print(f"  ... and {len(reqs) - 3} more")

print("\n" + "="*60)
print("✅ Team assignments completed successfully!")
print(f"📍 Database: {db}")