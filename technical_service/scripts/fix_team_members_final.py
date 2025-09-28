#!/usr/bin/env python3
"""
Final fix for team member assignments - Ali Özkan to Teknik Ekip as reference
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

# Get all employees
all_employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read', [[('id', '!=', 1)]],  # Exclude Administrator
    {'fields': ['id', 'name'], 'order': 'id'})

print(f"📋 Found {len(all_employees)} employees")

# Create employee name to ID mapping
emp_map = {emp['name']: emp['id'] for emp in all_employees}

# Define complete team assignments (following user's manual entry pattern)
team_assignments = {
    1: {  # Internal Maintenance
        'name': 'Internal Maintenance / İç Bakım',
        'members': ['Ahmet Yılmaz', 'Mehmet Demir', 'Ayşe Kaya', 'Fatma Şahin', 'Emre Koç']
    },
    2: {  # IT Destek Ekibi
        'name': 'IT Destek Ekibi',
        'members': ['Can Aydın', 'Zeynep Arslan', 'Murat Çelik', 'Elif Güneş', 'Hakan Yıldız']
    },
    3: {  # Teknik Ekip - Ali Özkan referans alındı
        'name': 'Teknik Ekip',
        'members': ['Ali Özkan', 'Seda Korkmaz', 'Burak Öztürk', 'Ali Teknisyen', 'Ayşe Uzman', 'Mehmet Müdür']
    },
    4: {  # Acil Müdahale Ekibi
        'name': 'Acil Müdahale Ekibi',
        'members': ['Can Mühendis', 'Veli Çelik', 'Cem Yıldız', 'Deniz Arslan', 'Gül Yılmaz', 'Hakan Demir', 'İrem Kaya', 'Fatma Operatör']
    },
    5: {  # Elektrik-Mekanik Ekibi
        'name': 'Elektrik-Mekanik Ekibi',
        'members': ['Kaan Öz', 'Leyla Ak', 'Murat Can', 'Nalan Er', 'Okan Sel']
    },
    6: {  # Network Uzmanları
        'name': 'Network Uzmanları',
        'members': ['Pınar Tan', 'Rıza Ün', 'Seda Var', 'Tuna Yel']
    },
    7: {  # Bina Bakım Ekibi
        'name': 'Bina Bakım Ekibi',
        'members': ['Umut Zor', 'Volkan Al', 'Ayşe Kaya', 'Mehmet Demir']
    }
}

print("\n🔧 Assigning team members (Ali Özkan pattern)...")
print("="*60)

for team_id, config in team_assignments.items():
    # Get employee IDs
    member_ids = []
    missing_members = []

    for member_name in config['members']:
        if member_name in emp_map:
            member_ids.append(emp_map[member_name])
        else:
            missing_members.append(member_name)

    if missing_members:
        print(f"⚠️  Team {team_id} ({config['name']}): Missing employees: {', '.join(missing_members)}")

    if member_ids:
        try:
            # Clear and set new members
            result = models.execute_kw(db, uid, password,
                'maintenance.team', 'write',
                [[team_id], {
                    'member_ids': [(6, 0, member_ids)]  # Replace all members
                }])

            print(f"✅ Team {team_id} ({config['name']}): {len(member_ids)} members assigned")

            # Show member names
            for member_name in config['members']:
                if member_name in emp_map:
                    print(f"   • {member_name}")

        except Exception as e:
            print(f"❌ Error updating team {team_id}: {str(e)}")

print("\n" + "="*60)
print("📊 FINAL VERIFICATION")
print("="*60)

# Verify Ali Özkan is in Teknik Ekip
ali_id = emp_map.get('Ali Özkan')
if ali_id:
    teams_with_ali = models.execute_kw(db, uid, password,
        'maintenance.team', 'search_read',
        [[('member_ids', 'in', ali_id)]],
        {'fields': ['name']})

    print(f"\n🔍 Ali Özkan'ın bulunduğu takımlar:")
    for team in teams_with_ali:
        team_name = team['name']
        if isinstance(team_name, dict):
            team_name = team_name.get('en_US', str(team_name))
        print(f"   • {team_name}")

# Final summary
teams = models.execute_kw(db, uid, password,
    'maintenance.team', 'search_read', [[]],
    {'fields': ['id', 'name', 'member_ids'], 'order': 'id'})

print("\n📊 ÖZET:")
print("-"*40)

total_unique_members = set()
for team in teams:
    team_name = team['name']
    if isinstance(team_name, dict):
        team_name = team_name.get('en_US', str(team_name))

    member_ids = team.get('member_ids', [])
    total_unique_members.update(member_ids)

    member_count = len(member_ids)
    status = "✅" if member_count > 0 else "❌"
    print(f"{status} Team {team['id']}: {team_name} - {member_count} üye")

print("-"*40)
print(f"📊 Toplam: {len(teams)} takım, {len(total_unique_members)} benzersiz üye")
print(f"📍 Veritabanı: {db}")
print("\n✅ Takım üyeleri başarıyla atandı!")