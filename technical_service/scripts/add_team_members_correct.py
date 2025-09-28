#!/usr/bin/env python3
"""
Add team members using the correct technical_service.team_member model
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

# Get all employees with their user_ids
all_employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read', [[('id', '!=', 1)]],
    {'fields': ['id', 'name', 'user_id'], 'order': 'name'})

print(f"📋 Found {len(all_employees)} employees")

# Create employee name to ID and user_id mapping
emp_data = {emp['name']: {'id': emp['id'], 'user_id': emp.get('user_id', False)} for emp in all_employees}

# Define team members (similar to Ali Özkan's entry)
team_members = {
    1: [  # Internal Maintenance
        'Ahmet Yılmaz', 'Mehmet Demir', 'Ayşe Kaya', 'Fatma Şahin'
    ],
    2: [  # IT Destek Ekibi
        'Can Aydın', 'Zeynep Arslan', 'Murat Çelik', 'Elif Güneş', 'Hakan Yıldız'
    ],
    3: [  # Teknik Ekip (Ali Özkan already exists, add others)
        'Seda Korkmaz', 'Burak Öztürk', 'Ali Teknisyen', 'Ayşe Uzman', 'Mehmet Müdür'
    ],
    4: [  # Acil Müdahale Ekibi
        'Can Mühendis', 'Veli Çelik', 'Cem Yıldız', 'Deniz Arslan',
        'Gül Yılmaz', 'Hakan Demir', 'İrem Kaya'
    ],
    5: [  # Elektrik-Mekanik Ekibi
        'Kaan Öz', 'Leyla Ak', 'Murat Can', 'Nalan Er', 'Okan Sel'
    ],
    6: [  # Network Uzmanları
        'Pınar Tan', 'Rıza Ün', 'Seda Var', 'Tuna Yel', 'Fatma Şahin'
    ],
    7: [  # Bina Bakım Ekibi
        'Umut Zor', 'Volkan Al', 'Emre Koç', 'Fatma Operatör'
    ]
}

print("\n🔧 Creating team members using technical_service.team_member model...")
print("="*60)

# Get existing team members to avoid duplicates
existing_members = models.execute_kw(db, uid, password,
    'technical_service.team.member', 'search_read', [[]],
    {'fields': ['team_id', 'employee_id']})

existing_map = {}
for member in existing_members:
    key = (member['team_id'][0] if member['team_id'] else 0,
           member['employee_id'][0] if member['employee_id'] else 0)
    existing_map[key] = True

created_count = 0
for team_id, member_names in team_members.items():
    team_created = 0

    for member_name in member_names:
        if member_name in emp_data:
            emp_id = emp_data[member_name]['id']
            user_id = emp_data[member_name]['user_id']

            # Check if this member already exists in this team
            if (team_id, emp_id) in existing_map:
                print(f"   ⚠️  {member_name} already in team {team_id}")
                continue

            # Prepare member data similar to Ali Özkan's record
            member_data = {
                'team_id': team_id,
                'employee_id': emp_id,
                'user_id': user_id[0] if user_id else False,
                'x_skill_level': 'mid',  # Default to mid-level
                'x_availability_status': 'available',
                'x_shift': 'day',
                'x_is_available': True,
            }

            # Adjust skill levels for some members
            if 'Müdür' in member_name or 'Uzman' in member_name:
                member_data['x_skill_level'] = 'senior'
            elif 'Operatör' in member_name or 'Teknisyen' in member_name:
                member_data['x_skill_level'] = 'junior'

            try:
                # Create team member record
                member_id = models.execute_kw(db, uid, password,
                    'technical_service.team.member', 'create', [member_data])

                team_created += 1
                created_count += 1
                skill_level = member_data['x_skill_level'].upper()
                print(f"   ✅ {member_name} added to team {team_id} [{skill_level}]")

            except Exception as e:
                print(f"   ❌ Error adding {member_name}: {str(e)}")
        else:
            print(f"   ⚠️  {member_name} not found in employees")

    if team_created > 0:
        print(f"   📊 Team {team_id}: Added {team_created} new members")

print("\n" + "="*60)
print(f"✅ Created {created_count} new team member records")

# Verify final state
print("\n📊 FINAL VERIFICATION")
print("="*60)

teams = models.execute_kw(db, uid, password,
    'maintenance.team', 'search_read', [[]],
    {'fields': ['id', 'name'], 'order': 'id'})

for team in teams:
    team_name = team['name']
    if isinstance(team_name, dict):
        team_name = team_name.get('en_US', str(team_name))

    # Get team members from technical_service.team_member
    members = models.execute_kw(db, uid, password,
        'technical_service.team.member', 'search_read',
        [[('team_id', '=', team['id'])]],
        {'fields': ['employee_id', 'x_skill_level', 'x_shift', 'x_is_available']})

    print(f"\n{team_name} (Team ID: {team['id']})")
    print("-" * 40)

    if members:
        for member in members:
            emp_name = member['employee_id'][1] if member['employee_id'] else 'Unknown'
            skill = member.get('x_skill_level', '').upper()
            shift = member.get('x_shift', 'day')
            available = "✅" if member.get('x_is_available') else "❌"
            print(f"  • {emp_name:20} [{skill:6}] {shift:5} {available}")
    else:
        print("  ❌ No members")

print("\n" + "="*60)
print("✅ Team members successfully added using technical_service.team_member model!")
print(f"📍 Database: {db}")