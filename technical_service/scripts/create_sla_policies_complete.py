#!/usr/bin/env python3
"""
SLA Policy Creator for Technical Service Module
Creates complete SLA policies with priority lines
"""

import xmlrpc.client
import sys
from datetime import datetime, timedelta

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

# Define SLA policies to create
sla_policies = [
    {
        'name': 'Kurumsal Premium SLA (7/24)',
        'x_apply_to': 'all',
        'active': True,
        'x_include_weekends': True,
        'x_enable_escalation': True,
        'x_business_hours_start': 0.0,  # 00:00
        'x_business_hours_end': 24.0,   # 24:00 (7/24 support)
        'x_timezone': 'Europe/Istanbul',
        'lines': [
            {'x_priority': 'p1', 'x_response_time': 0.5, 'x_resolution_time': 4,
             'x_after_hours_response': 1, 'x_after_hours_resolution': 6},  # Kritik
            {'x_priority': 'p2', 'x_response_time': 2, 'x_resolution_time': 8,
             'x_after_hours_response': 4, 'x_after_hours_resolution': 12},  # Yüksek
            {'x_priority': 'p3', 'x_response_time': 4, 'x_resolution_time': 24,
             'x_after_hours_response': 8, 'x_after_hours_resolution': 48},  # Normal
            {'x_priority': 'p4', 'x_response_time': 8, 'x_resolution_time': 72,
             'x_after_hours_response': 24, 'x_after_hours_resolution': 96},  # Düşük
        ]
    },
    {
        'name': 'Standart İş Saatleri SLA',
        'x_apply_to': 'all',
        'active': True,
        'x_include_weekends': False,
        'x_enable_escalation': True,
        'x_business_hours_start': 9.0,   # 09:00
        'x_business_hours_end': 18.0,    # 18:00
        'x_timezone': 'Europe/Istanbul',
        'lines': [
            {'x_priority': 'p1', 'x_response_time': 1, 'x_resolution_time': 8,
             'x_after_hours_response': 2, 'x_after_hours_resolution': 16},  # Kritik
            {'x_priority': 'p2', 'x_response_time': 4, 'x_resolution_time': 16,
             'x_after_hours_response': 8, 'x_after_hours_resolution': 24},  # Yüksek
            {'x_priority': 'p3', 'x_response_time': 8, 'x_resolution_time': 48,
             'x_after_hours_response': 16, 'x_after_hours_resolution': 72},  # Normal
            {'x_priority': 'p4', 'x_response_time': 24, 'x_resolution_time': 120,
             'x_after_hours_response': 48, 'x_after_hours_resolution': 168},  # Düşük
        ]
    },
    {
        'name': 'Ekonomik SLA',
        'x_apply_to': 'all',
        'active': True,
        'x_include_weekends': False,
        'x_enable_escalation': False,
        'x_business_hours_start': 10.0,  # 10:00
        'x_business_hours_end': 17.0,   # 17:00
        'x_timezone': 'Europe/Istanbul',
        'lines': [
            {'x_priority': 'p1', 'x_response_time': 2, 'x_resolution_time': 16,
             'x_after_hours_response': 4, 'x_after_hours_resolution': 24},  # Kritik
            {'x_priority': 'p2', 'x_response_time': 8, 'x_resolution_time': 32,
             'x_after_hours_response': 16, 'x_after_hours_resolution': 48},  # Yüksek
            {'x_priority': 'p3', 'x_response_time': 16, 'x_resolution_time': 96,
             'x_after_hours_response': 32, 'x_after_hours_resolution': 144},  # Normal
            {'x_priority': 'p4', 'x_response_time': 48, 'x_resolution_time': 240,
             'x_after_hours_response': 96, 'x_after_hours_resolution': 336},  # Düşük
        ]
    },
    {
        'name': 'VIP Özel Destek SLA',
        'x_apply_to': 'all',
        'active': True,
        'x_include_weekends': True,
        'x_enable_escalation': True,
        'x_business_hours_start': 0.0,   # 00:00
        'x_business_hours_end': 24.0,    # 24:00
        'x_timezone': 'Europe/Istanbul',
        'lines': [
            {'x_priority': 'p1', 'x_response_time': 0.25, 'x_resolution_time': 2,
             'x_after_hours_response': 0.5, 'x_after_hours_resolution': 3},  # Kritik - 15 dakika yanıt
            {'x_priority': 'p2', 'x_response_time': 1, 'x_resolution_time': 4,
             'x_after_hours_response': 2, 'x_after_hours_resolution': 6},  # Yüksek
            {'x_priority': 'p3', 'x_response_time': 2, 'x_resolution_time': 12,
             'x_after_hours_response': 4, 'x_after_hours_resolution': 24},  # Normal
            {'x_priority': 'p4', 'x_response_time': 4, 'x_resolution_time': 48,
             'x_after_hours_response': 8, 'x_after_hours_resolution': 72},  # Düşük
        ]
    }
]

# Get company_id
company_id = models.execute_kw(db, uid, password,
    'res.company', 'search', [[]], {'limit': 1})[0]

# Create SLA policies
created_sla_ids = []
for sla_data in sla_policies:
    print(f"\n📝 Creating SLA Policy: {sla_data['name']}")

    # Extract lines for separate creation
    lines = sla_data.pop('lines', [])

    # Add company_id
    sla_data['company_id'] = company_id

    # Create SLA policy
    sla_id = models.execute_kw(db, uid, password,
        'technical_service.sla', 'create', [sla_data])

    created_sla_ids.append(sla_id)
    print(f"   ✅ Created SLA Policy ID: {sla_id}")

    # Create SLA lines
    for line in lines:
        line['sla_id'] = sla_id
        line_id = models.execute_kw(db, uid, password,
            'technical_service.sla.line', 'create', [line])

        priority_map = {'p1': 'Kritik', 'p2': 'Yüksek', 'p3': 'Normal', 'p4': 'Düşük'}
        priority_name = priority_map.get(line['x_priority'], line['x_priority'])
        print(f"      ➕ Added line for {priority_name} priority: {line['x_response_time']}h response, {line['x_resolution_time']}h resolution")

print(f"\n✅ Successfully created {len(created_sla_ids)} SLA policies")

# Now link some maintenance requests to these SLA policies
print("\n🔗 Linking SLA policies to maintenance requests...")

# Get all maintenance requests
request_ids = models.execute_kw(db, uid, password,
    'maintenance.request', 'search', [[]], {'limit': 100})

if request_ids:
    # Distribute SLA policies across requests based on priority
    for i, request_id in enumerate(request_ids[:20]):  # Update first 20 requests
        # Get request priority
        request = models.execute_kw(db, uid, password,
            'maintenance.request', 'read', [request_id], {'fields': ['priority', 'name']})

        if request:
            request = request[0]
            priority = request.get('priority', '1')

            # Assign SLA policy based on priority
            if priority == '3':  # Kritik
                sla_id = created_sla_ids[3] if len(created_sla_ids) > 3 else created_sla_ids[0]  # VIP SLA
            elif priority == '2':  # Yüksek
                sla_id = created_sla_ids[0]  # Premium SLA
            elif priority == '1':  # Normal
                sla_id = created_sla_ids[1]  # Standart SLA
            else:  # Düşük
                sla_id = created_sla_ids[2] if len(created_sla_ids) > 2 else created_sla_ids[1]  # Ekonomik SLA

            # Update request with SLA policy
            models.execute_kw(db, uid, password,
                'maintenance.request', 'write', [[request_id], {'x_sla_policy_id': sla_id}])

            print(f"   ✅ Linked request '{request['name']}' to SLA policy ID {sla_id}")

print("\n✅ SLA setup complete!")

# Verify by counting records
sla_count = models.execute_kw(db, uid, password,
    'technical_service.sla', 'search_count', [[]])
line_count = models.execute_kw(db, uid, password,
    'technical_service.sla.line', 'search_count', [[]])

print(f"\n📊 Final counts:")
print(f"   - SLA Policies: {sla_count}")
print(f"   - SLA Lines: {line_count}")
print(f"   - Database: {db}")