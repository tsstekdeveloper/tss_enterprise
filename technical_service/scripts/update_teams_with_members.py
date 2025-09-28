#!/usr/bin/env python3
"""
Update Service Teams with Members and Skills
"""

import xmlrpc.client
import sys
from datetime import datetime

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

# First, get all employees
print("\n📋 Getting employees...")
employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read', [[]],
    {'fields': ['id', 'name', 'department_id', 'job_id', 'work_email']})

print(f"Found {len(employees)} employees")
for emp in employees:
    print(f"  - {emp['name']} (ID: {emp['id']})")

# Get all teams
print("\n📋 Getting service teams...")
teams = models.execute_kw(db, uid, password,
    'maintenance.team', 'search_read', [[]],
    {'fields': ['id', 'name', 'member_ids']})

print(f"Found {len(teams)} teams")

# Define team-member assignments with skills
team_assignments = {
    'İç Bakım': {
        'members': [],  # Will be filled with employee IDs
        'skills': [
            'Elektrik sistemleri bakımı',
            'Mekanik sistemler onarımı',
            'HVAC sistem yönetimi',
            'Bina otomasyon sistemleri',
            'Yangın alarm sistemleri',
            'Jeneratör bakımı',
            'Asansör bakım koordinasyonu'
        ],
        'member_names': ['Ahmet Yılmaz', 'Mehmet Kaya', 'Ayşe Demir']  # Names to match
    },
    'IT Destek Ekibi': {
        'members': [],
        'skills': [
            'Windows/Linux sistem yönetimi',
            'Network yapılandırma ve troubleshooting',
            'Veritabanı yönetimi (PostgreSQL, MySQL)',
            'Bulut servisleri (AWS, Azure)',
            'Cybersecurity ve firewall yönetimi',
            'Backup ve disaster recovery',
            'ERP sistem desteği (Odoo)',
            'Help desk ve kullanıcı desteği',
            'Donanım bakım ve onarımı'
        ],
        'member_names': ['Fatma Şahin', 'Ali Özkan', 'Zeynep Arslan']
    },
    'Teknik Ekip': {
        'members': [],
        'skills': [
            'CNC makine programlama',
            'PLC programlama (Siemens, Allen Bradley)',
            'Endüstriyel robot programlama',
            'Hidrolik/Pnömatik sistemler',
            'Elektrik motor bakımı',
            'Güç elektroniği',
            'Otomasyon sistemleri',
            'Kalibrasyon ve ölçüm'
        ],
        'member_names': ['Mustafa Çelik', 'Hasan Yıldırım']
    },
    'Acil Müdahale Ekibi': {
        'members': [],
        'skills': [
            '7/24 acil müdahale',
            'Kriz yönetimi',
            'İlk yardım sertifikası',
            'Yangın söndürme eğitimi',
            'Tehlikeli madde yönetimi',
            'Elektrik kesinti müdahalesi',
            'Su baskını müdahalesi',
            'Güvenlik sistem arızaları'
        ],
        'member_names': ['Ahmet Yılmaz', 'Ali Özkan', 'Mustafa Çelik', 'Hasan Yıldırım']  # Multiple teams
    },
    'Elektrik-Mekanik Ekibi': {
        'members': [],
        'skills': [
            'Orta gerilim sistemleri',
            'Trafo bakımı',
            'Kompanzasyon sistemleri',
            'UPS sistemleri',
            'Soğutma sistemleri',
            'Havalandırma sistemleri',
            'Pompa ve vana sistemleri',
            'Kaynak ve torna işlemleri'
        ],
        'member_names': ['Mehmet Kaya', 'Emre Aydın', 'Can Koç']
    },
    'Network Uzmanları': {
        'members': [],
        'skills': [
            'Cisco network yönetimi',
            'Firewall yapılandırma (Fortinet, Palo Alto)',
            'VPN kurulumu ve yönetimi',
            'WiFi altyapısı yönetimi',
            'Network monitoring (PRTG, Zabbix)',
            'VLAN yapılandırma',
            'Load balancer yönetimi',
            'Network güvenliği ve penetrasyon testleri'
        ],
        'member_names': ['Fatma Şahin', 'Zeynep Arslan', 'Selin Öztürk']
    },
    'Bina Bakım Ekibi': {
        'members': [],
        'skills': [
            'Sıhhi tesisat bakımı',
            'Boya ve badana işleri',
            'Cam ve doğrama bakımı',
            'Çatı izolasyon kontrolü',
            'Peyzaj ve bahçe bakımı',
            'Temizlik koordinasyonu',
            'Atık yönetimi',
            'İç mekan düzenlemeleri'
        ],
        'member_names': ['Ayşe Demir', 'Emre Aydın', 'Can Koç', 'Selin Öztürk']
    }
}

# Match employees to teams based on names
for emp in employees:
    emp_name = emp['name']
    for team_name, team_data in team_assignments.items():
        if emp_name in team_data['member_names']:
            team_data['members'].append(emp['id'])

# Update teams with members and create skill records
for team in teams:
    team_name = team['name']

    if team_name in team_assignments:
        assignment = team_assignments[team_name]

        if assignment['members']:
            print(f"\n🔧 Updating team: {team_name}")

            # Update team with members
            current_members = team['member_ids'] or []
            new_members = list(set(current_members + assignment['members']))

            models.execute_kw(db, uid, password,
                'maintenance.team', 'write',
                [[team['id']], {'member_ids': [(6, 0, new_members)]}])

            print(f"   ✅ Added {len(assignment['members'])} members to team")

            # Add skills as a note or in description field if available
            # Since there's no specific skill field, we'll add them to the team's internal notes
            skills_text = "🎯 Takım Yetkinlikleri:\n" + "\n".join([f"• {skill}" for skill in assignment['skills']])

            # Check if there's a notes field
            team_fields = models.execute_kw(db, uid, password,
                'maintenance.team', 'fields_get', [], {'attributes': ['string', 'type']})

            if 'note' in team_fields:
                models.execute_kw(db, uid, password,
                    'maintenance.team', 'write',
                    [[team['id']], {'note': skills_text}])
                print(f"   ✅ Added {len(assignment['skills'])} skills to team notes")
            elif 'x_notes' in team_fields:
                models.execute_kw(db, uid, password,
                    'maintenance.team', 'write',
                    [[team['id']], {'x_notes': skills_text}])
                print(f"   ✅ Added {len(assignment['skills'])} skills to team notes")
            else:
                print(f"   ⚠️  No notes field found, skills not added")

# Create some employees if we don't have enough
if len(employees) < 10:
    print("\n👥 Creating additional employees...")

    new_employees = [
        {'name': 'Ahmet Yılmaz', 'job_title': 'Bakım Teknisyeni', 'work_email': 'ahmet.yilmaz@technofix.com'},
        {'name': 'Mehmet Kaya', 'job_title': 'Elektrik Teknisyeni', 'work_email': 'mehmet.kaya@technofix.com'},
        {'name': 'Fatma Şahin', 'job_title': 'Network Uzmanı', 'work_email': 'fatma.sahin@technofix.com'},
        {'name': 'Ali Özkan', 'job_title': 'IT Destek Uzmanı', 'work_email': 'ali.ozkan@technofix.com'},
        {'name': 'Ayşe Demir', 'job_title': 'Bina Bakım Sorumlusu', 'work_email': 'ayse.demir@technofix.com'},
        {'name': 'Mustafa Çelik', 'job_title': 'Mekanik Teknisyen', 'work_email': 'mustafa.celik@technofix.com'},
        {'name': 'Zeynep Arslan', 'job_title': 'Sistem Yöneticisi', 'work_email': 'zeynep.arslan@technofix.com'},
        {'name': 'Hasan Yıldırım', 'job_title': 'Otomasyon Teknisyeni', 'work_email': 'hasan.yildirim@technofix.com'},
        {'name': 'Emre Aydın', 'job_title': 'Elektrik-Mekanik Teknisyen', 'work_email': 'emre.aydin@technofix.com'},
        {'name': 'Can Koç', 'job_title': 'Genel Bakım Personeli', 'work_email': 'can.koc@technofix.com'},
        {'name': 'Selin Öztürk', 'job_title': 'IT Helpdesk', 'work_email': 'selin.ozturk@technofix.com'}
    ]

    created_employees = []
    for emp_data in new_employees:
        try:
            emp_id = models.execute_kw(db, uid, password,
                'hr.employee', 'create', [{
                    'name': emp_data['name'],
                    'job_id': False,  # Will be set if job positions exist
                    'work_email': emp_data['work_email']
                }])
            created_employees.append({'id': emp_id, 'name': emp_data['name']})
            print(f"   ✅ Created employee: {emp_data['name']}")
        except Exception as e:
            print(f"   ⚠️  Could not create {emp_data['name']}: {str(e)}")

    # Now assign these new employees to teams
    if created_employees:
        print("\n🔄 Assigning new employees to teams...")

        # Re-fetch teams
        teams = models.execute_kw(db, uid, password,
            'maintenance.team', 'search_read', [[]],
            {'fields': ['id', 'name', 'member_ids']})

        for team in teams:
            team_name = team['name']

            if team_name in team_assignments:
                assignment = team_assignments[team_name]
                members_to_add = []

                for emp in created_employees:
                    if emp['name'] in assignment['member_names']:
                        members_to_add.append(emp['id'])

                if members_to_add:
                    current_members = team['member_ids'] or []
                    new_members = list(set(current_members + members_to_add))

                    models.execute_kw(db, uid, password,
                        'maintenance.team', 'write',
                        [[team['id']], {'member_ids': [(6, 0, new_members)]}])

                    print(f"   ✅ Added {len(members_to_add)} members to {team_name}")

                    # Also add skills
                    skills_text = "🎯 Takım Yetkinlikleri:\n" + "\n".join([f"• {skill}" for skill in assignment['skills']])

                    try:
                        models.execute_kw(db, uid, password,
                            'maintenance.team', 'write',
                            [[team['id']], {'note': skills_text}])
                        print(f"   ✅ Added skills to {team_name}")
                    except:
                        pass

# Final summary
print("\n📊 Final Summary:")
teams = models.execute_kw(db, uid, password,
    'maintenance.team', 'search_read', [[]],
    {'fields': ['name', 'member_ids']})

for team in teams:
    member_count = len(team['member_ids']) if team['member_ids'] else 0
    print(f"   - {team['name']}: {member_count} members")

print(f"\n✅ Team update complete!")