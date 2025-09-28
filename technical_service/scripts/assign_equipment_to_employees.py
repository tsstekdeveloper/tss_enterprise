#!/usr/bin/env python3
"""
Assign equipment to employees with locations and asset types
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

# Get or create campus and buildings
print("\n🏢 Setting up locations...")

# Create campus if not exists
campus_search = models.execute_kw(db, uid, password,
    'technical_service.campus', 'search', [[('name', '=', 'Ana Kampüs')]])

if not campus_search:
    campus_id = models.execute_kw(db, uid, password,
        'technical_service.campus', 'create', [{
            'name': 'Ana Kampüs',
            'code': 'MAIN',
            'x_address': 'Organize Sanayi Bölgesi, Ankara'
        }])
    print(f"  ✅ Created campus: Ana Kampüs")
else:
    campus_id = campus_search[0]

# Create buildings if not exist
buildings = [
    {'name': 'A Blok - Yönetim', 'code': 'A-BLK'},
    {'name': 'B Blok - Üretim', 'code': 'B-BLK'},
    {'name': 'C Blok - IT/Destek', 'code': 'C-BLK'},
    {'name': 'D Blok - Depo/Lojistik', 'code': 'D-BLK'}
]

building_ids = {}
for building in buildings:
    building_search = models.execute_kw(db, uid, password,
        'technical_service.building', 'search', [[('name', '=', building['name'])]])

    if not building_search:
        building_id = models.execute_kw(db, uid, password,
            'technical_service.building', 'create', [{
                'name': building['name'],
                'code': building['code'],
                'campus_id': campus_id,
                'floor_count': 3
            }])
        print(f"  ✅ Created building: {building['name']}")
        building_ids[building['name']] = building_id
    else:
        building_ids[building['name']] = building_search[0]

# Get all equipment
equipment_list = models.execute_kw(db, uid, password,
    'maintenance.equipment', 'search_read', [[]],
    {'fields': ['id', 'name'], 'order': 'name'})

print(f"\n📦 Found {len(equipment_list)} equipment items")

# Get all employees
employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read', [[('id', '!=', 1)]],
    {'fields': ['id', 'name'], 'order': 'name'})

print(f"👥 Found {len(employees)} employees")

# Define equipment assignments with realistic data
equipment_assignments = {
    'Dell PowerEdge R750 - Ana Sunucu': {
        'employee': 'Zeynep Arslan',  # IT Sistem Yöneticisi
        'asset_type': 'it_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '3',
        'room': 'Server Room',
        'manufacturer': 'Dell Technologies',
        'warranty_months': 36,
        'technician': 'Murat Çelik'
    },
    'Fortiinet FortiGate 600E': {
        'employee': 'Pınar Tan',  # Network Uzmanı
        'asset_type': 'it_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '3',
        'room': 'Network Room',
        'manufacturer': 'Fortinet',
        'warranty_months': 24,
        'technician': 'Rıza Ün'
    },
    'Cisco Catalyst 9300': {
        'employee': 'Rıza Ün',  # Network Uzmanı
        'asset_type': 'it_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '3',
        'room': 'Network Room',
        'manufacturer': 'Cisco Systems',
        'warranty_months': 36,
        'technician': 'Pınar Tan'
    },
    'Haas VF-4 CNC Torna': {
        'employee': 'Ali Özkan',  # CNC Operatörü (Teknik Ekip)
        'asset_type': 'facility_equipment',
        'building': 'B Blok - Üretim',
        'floor': '1',
        'room': 'CNC Atölyesi',
        'manufacturer': 'Haas Automation',
        'warranty_months': 24,
        'technician': 'Mehmet Müdür'
    },
    'Daikin VRV IV Klima': {
        'employee': 'Emre Koç',  # Bina Bakım
        'asset_type': 'facility_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '3',
        'room': 'Server Room',
        'manufacturer': 'Daikin',
        'warranty_months': 60,
        'technician': 'Kaan Öz'
    },
    'Caterpillar 500KVA Jeneratör': {
        'employee': 'Kaan Öz',  # Elektrik-Mekanik Ekibi
        'asset_type': 'facility_equipment',
        'building': 'D Blok - Depo/Lojistik',
        'floor': '0',
        'room': 'Jeneratör Odası',
        'manufacturer': 'Caterpillar',
        'warranty_months': 24,
        'technician': 'Leyla Ak'
    },
    'APC Symmetra 80kVA UPS': {
        'employee': 'Leyla Ak',  # Elektrik-Mekanik Ekibi
        'asset_type': 'it_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '3',
        'room': 'UPS Room',
        'manufacturer': 'APC by Schneider',
        'warranty_months': 36,
        'technician': 'Kaan Öz'
    },
    'Ana Sunucu': {
        'employee': 'Murat Çelik',  # IT Destek
        'asset_type': 'it_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '3',
        'room': 'Server Room',
        'manufacturer': 'IBM',
        'warranty_months': 48,
        'technician': 'Zeynep Arslan'
    },
    'Firewall': {
        'employee': 'Fatma Şahin',  # Network Uzmanları
        'asset_type': 'it_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '3',
        'room': 'Network Room',
        'manufacturer': 'Palo Alto Networks',
        'warranty_months': 36,
        'technician': 'Pınar Tan'
    },
    'CNC Makinesi': {
        'employee': 'Ali Teknisyen',  # Teknik Ekip
        'asset_type': 'facility_equipment',
        'building': 'B Blok - Üretim',
        'floor': '1',
        'room': 'Üretim Salonu',
        'manufacturer': 'DMG Mori',
        'warranty_months': 24,
        'technician': 'Ali Özkan'
    },
    'Klima Sistemi': {
        'employee': 'Volkan Al',  # Bina Bakım
        'asset_type': 'facility_equipment',
        'building': 'A Blok - Yönetim',
        'floor': '2',
        'room': 'Klima Dairesi',
        'manufacturer': 'Mitsubishi',
        'warranty_months': 36,
        'technician': 'Emre Koç'
    },
    'Jeneratör': {
        'employee': 'Nalan Er',  # Elektrik-Mekanik
        'asset_type': 'facility_equipment',
        'building': 'D Blok - Depo/Lojistik',
        'floor': '0',
        'room': 'Yedek Jeneratör',
        'manufacturer': 'Cummins',
        'warranty_months': 24,
        'technician': 'Kaan Öz'
    },
    'Cisco Nexus 9500 - Core Switch': {
        'employee': 'Seda Var',  # Network Uzmanları
        'asset_type': 'it_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '3',
        'room': 'Core Network Room',
        'manufacturer': 'Cisco Systems',
        'warranty_months': 60,
        'technician': 'Rıza Ün'
    },
    'Fortinet FortiGate 3000D - Main Firewall': {
        'employee': 'Tuna Yel',  # Network Uzmanları
        'asset_type': 'it_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '3',
        'room': 'Security Room',
        'manufacturer': 'Fortinet',
        'warranty_months': 36,
        'technician': 'Pınar Tan'
    },
    'TRUMPF TruLaser 5030 Fiber': {
        'employee': 'Burak Öztürk',  # Teknik Ekip
        'asset_type': 'facility_equipment',
        'building': 'B Blok - Üretim',
        'floor': '1',
        'room': 'Lazer Kesim',
        'manufacturer': 'TRUMPF',
        'warranty_months': 24,
        'technician': 'Ali Teknisyen'
    },
    'Schneider Galaxy VX 500kVA - UPS System': {
        'employee': 'Okan Sel',  # Elektrik-Mekanik
        'asset_type': 'it_equipment',
        'building': 'C Blok - IT/Destek',
        'floor': '0',
        'room': 'Main UPS Room',
        'manufacturer': 'Schneider Electric',
        'warranty_months': 36,
        'technician': 'Leyla Ak'
    },
    'Dell Precision 7920 - CAD Workstation': {
        'employee': 'Can Aydın',  # IT Destek
        'asset_type': 'it_equipment',
        'building': 'B Blok - Üretim',
        'floor': '2',
        'room': 'Tasarım Ofisi',
        'manufacturer': 'Dell Technologies',
        'warranty_months': 36,
        'technician': 'Elif Güneş'
    },
    'HP DesignJet T1700 - Plotter': {
        'employee': 'Elif Güneş',  # IT Destek
        'asset_type': 'it_equipment',
        'building': 'B Blok - Üretim',
        'floor': '2',
        'room': 'Tasarım Ofisi',
        'manufacturer': 'HP Inc.',
        'warranty_months': 12,
        'technician': 'Can Aydın'
    }
}

# Create employee name to ID mapping
emp_map = {emp['name']: emp['id'] for emp in employees}

print("\n🔧 Assigning equipment to employees and locations...")
print("="*60)

updated_count = 0
purchase_date_base = datetime.now() - timedelta(days=365)  # Base purchase date (1 year ago)

for equipment in equipment_list:
    equip_name = equipment['name']

    if equip_name in equipment_assignments:
        assignment = equipment_assignments[equip_name]

        # Find employee ID
        employee_id = emp_map.get(assignment['employee'])
        technician_id = emp_map.get(assignment.get('technician'))

        if employee_id:
            # Calculate dates
            purchase_days_ago = random.randint(30, 730)  # Between 1 month and 2 years ago
            purchase_date = purchase_date_base + timedelta(days=random.randint(-365, 0))
            assignment_date = purchase_date + timedelta(days=random.randint(1, 30))

            warranty_start = purchase_date
            warranty_end = purchase_date + timedelta(days=assignment['warranty_months'] * 30)

            # Determine warranty status
            today = datetime.now().date()
            if warranty_end.date() >= today:
                warranty_status = 'in_warranty'
            else:
                warranty_status = 'expired'

            # Calculate depreciation
            purchase_value = random.randint(5000, 500000)  # Random purchase value
            months_owned = (datetime.now() - purchase_date).days / 30
            depreciation_rate = 20.0  # 20% per year
            current_value = max(purchase_value * (1 - (depreciation_rate/100) * (months_owned/12)), purchase_value * 0.1)

            update_data = {
                'x_assigned_employee_id': employee_id,
                'x_asset_type': assignment['asset_type'],
                'x_campus_id': campus_id,
                'x_building_id': building_ids.get(assignment['building']),
                'x_floor': assignment['floor'],
                'x_room': assignment['room'],
                'x_manufacturer': assignment['manufacturer'],
                'x_purchase_date': purchase_date.strftime('%Y-%m-%d'),
                'x_purchase_value': purchase_value,
                'x_current_value': round(current_value, 2),
                'x_depreciation_rate': depreciation_rate,
                'x_assignment_date': assignment_date.strftime('%Y-%m-%d'),
                'x_warranty_start_date': warranty_start.strftime('%Y-%m-%d'),
                'x_warranty_end_date': warranty_end.strftime('%Y-%m-%d'),
                'x_warranty_status': warranty_status,
                'x_asset_code': f"AST-{equipment['id']:04d}",
                'x_barcode': f"8690000{equipment['id']:06d}",
                'active': True
            }

            # Add maintenance info for some equipment
            if assignment['asset_type'] == 'facility_equipment':
                last_maintenance = datetime.now() - timedelta(days=random.randint(30, 90))
                next_maintenance = datetime.now() + timedelta(days=random.randint(30, 90))
                update_data['x_last_maintenance_date'] = last_maintenance.strftime('%Y-%m-%d')
                update_data['x_next_maintenance_date'] = next_maintenance.strftime('%Y-%m-%d')
                update_data['x_maintenance_frequency'] = random.choice(['monthly', 'quarterly', 'semi_annual'])

            try:
                models.execute_kw(db, uid, password,
                    'maintenance.equipment', 'write',
                    [[equipment['id']], update_data])

                asset_type_display = {
                    'it_equipment': 'IT',
                    'facility_equipment': 'Facility',
                    'vehicle': 'Vehicle',
                    'furniture': 'Furniture',
                    'tool': 'Tool'
                }.get(assignment['asset_type'], 'Other')

                print(f"✅ {equip_name[:30]:30} → {assignment['employee']:20} [{asset_type_display:8}] {assignment['building'][:15]}")
                updated_count += 1

            except Exception as e:
                print(f"❌ Error updating {equip_name}: {str(e)[:50]}")
        else:
            print(f"⚠️  Employee not found: {assignment['employee']} for {equip_name[:30]}")

print("\n" + "="*60)
print(f"✅ Updated {updated_count} equipment items")

# Verification
print("\n📊 EQUIPMENT ASSIGNMENT SUMMARY")
print("="*60)

# Get updated equipment
updated_equipment = models.execute_kw(db, uid, password,
    'maintenance.equipment', 'search_read', [[]],
    {'fields': ['name', 'x_assigned_employee_id', 'x_asset_type', 'x_building_id', 'x_warranty_status'],
     'order': 'x_asset_type, name'})

# Group by asset type
asset_type_groups = {}
for equip in updated_equipment:
    asset_type = equip.get('x_asset_type', 'unassigned')
    if asset_type not in asset_type_groups:
        asset_type_groups[asset_type] = []
    asset_type_groups[asset_type].append(equip)

print("\n📦 Equipment by Type:")
for asset_type, items in sorted(asset_type_groups.items()):
    type_display = {
        'it_equipment': '💻 IT Equipment',
        'facility_equipment': '🏭 Facility Equipment',
        'vehicle': '🚗 Vehicle',
        'furniture': '🪑 Furniture',
        'tool': '🔧 Tool',
        'unassigned': '❓ Unassigned'
    }.get(asset_type, asset_type)

    print(f"\n{type_display} ({len(items)} items):")
    for item in items[:3]:  # Show first 3
        employee = item.get('x_assigned_employee_id')
        emp_name = employee[1][:20] if employee else '❌ Unassigned'
        building = item.get('x_building_id')
        building_name = building[1][:15] if building else 'No Location'

        print(f"  • {item['name'][:30]:30} - {emp_name:20} @ {building_name}")

    if len(items) > 3:
        print(f"  ... and {len(items) - 3} more")

# Assignment statistics
assigned_count = len([e for e in updated_equipment if e.get('x_assigned_employee_id')])
with_location = len([e for e in updated_equipment if e.get('x_building_id')])
with_warranty = len([e for e in updated_equipment if e.get('x_warranty_status') == 'in_warranty'])

print("\n📊 Statistics:")
print(f"  • Total Equipment: {len(updated_equipment)}")
print(f"  • Assigned to Employees: {assigned_count}")
print(f"  • With Location Data: {with_location}")
print(f"  • Under Warranty: {with_warranty}")

print("\n✅ Equipment assignment completed!")
print(f"📍 Database: {db}")