#!/usr/bin/env python3
"""
Fix team member assignments using XML-RPC
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

# Get all employees (exclude Administrator)
employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read', [[('id', '!=', 1)]],
    {'fields': ['id', 'name'], 'order': 'id'})

print(f"\n📋 Found {len(employees)} employees")

# Get all teams
teams = models.execute_kw(db, uid, password,
    'maintenance.team', 'search_read', [[]],
    {'fields': ['id', 'name', 'member_ids'], 'order': 'id'})

print(f"📋 Found {len(teams)} teams")

# Distribute employees to teams
team_assignments = {
    1: [2, 3, 4, 5, 6],      # İç Bakım - 5 members
    2: [7, 8, 9, 10, 11],    # IT Destek - 5 members
    3: [12, 13, 14, 15, 16, 17], # Teknik Ekip - 6 members
    4: [18, 19, 20, 21, 22, 23, 24, 25], # Acil Müdahale - 8 members
    5: [26, 27, 28, 29, 30], # Elektrik-Mekanik - 5 members
    6: [31, 32, 33, 34],     # Network Uzmanları - 4 members
    7: [35, 36, 2, 3]        # Bina Bakım - 4 members (some shared with team 1)
}

print("\n🔧 Assigning team members...")

for team_id, employee_ids in team_assignments.items():
    try:
        # Filter valid employee IDs
        valid_emp_ids = [emp_id for emp_id in employee_ids if emp_id <= len(employees) + 1 and emp_id != 1]

        if valid_emp_ids:
            # Write member_ids to team
            result = models.execute_kw(db, uid, password,
                'maintenance.team', 'write',
                [[team_id], {
                    'member_ids': [(6, 0, valid_emp_ids)]
                }])

            # Get team name for display
            team = models.execute_kw(db, uid, password,
                'maintenance.team', 'read', [team_id], {'fields': ['name']})[0]
            team_name = team['name']
            if isinstance(team_name, dict):
                team_name = team_name.get('en_US', str(team_name))

            print(f"✅ Team {team_id} ({team_name}): Assigned {len(valid_emp_ids)} members")

            # Show member names
            member_names = models.execute_kw(db, uid, password,
                'hr.employee', 'read', [valid_emp_ids], {'fields': ['name']})
            for member in member_names:
                print(f"   • {member['name']}")

    except Exception as e:
        print(f"❌ Error updating team {team_id}: {str(e)}")

print("\n📊 Final verification...")

# Verify all teams have members
teams_after = models.execute_kw(db, uid, password,
    'maintenance.team', 'search_read', [[]],
    {'fields': ['id', 'name', 'member_ids'], 'order': 'id'})

print("\n" + "="*60)
print("TEAM SUMMARY:")
print("="*60)

for team in teams_after:
    team_name = team['name']
    if isinstance(team_name, dict):
        team_name = team_name.get('en_US', str(team_name))

    member_count = len(team.get('member_ids', []))
    status = "✅" if member_count > 0 else "❌"

    print(f"{status} Team {team['id']}: {team_name} - {member_count} members")

print("\n✅ Team member assignment complete!")
print(f"📍 Database: {db}")