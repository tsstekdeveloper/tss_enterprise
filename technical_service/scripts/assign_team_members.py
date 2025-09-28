#!/usr/bin/env python3
"""
Assign employees to service teams and add skills
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

# Get all employees
print("\n📋 Getting employees...")
employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read', [[]],
    {'fields': ['id', 'name']})

employee_ids = [emp['id'] for emp in employees if emp['id'] != 1]  # Exclude Administrator
print(f"Found {len(employee_ids)} employees (excluding Administrator)")

# Get all teams
print("\n📋 Getting service teams...")
teams = models.execute_kw(db, uid, password,
    'maintenance.team', 'search_read', [[]],
    {'fields': ['id', 'name']})

# Team assignments with skills
team_configs = [
    {
        'id': 1,  # İç Bakım / Internal Maintenance
        'member_count': 4,
        'skills': """🎯 Takım Yetkinlikleri:
• Elektrik sistemleri bakımı ve onarımı
• Mekanik sistemler troubleshooting
• HVAC sistem yönetimi ve optimizasyonu
• Bina otomasyon sistemleri (BMS)
• Yangın alarm ve güvenlik sistemleri
• Jeneratör ve UPS bakımı
• Asansör bakım koordinasyonu
• Enerji verimliliği projeleri
• Periyodik bakım planlama"""
    },
    {
        'id': 2,  # IT Destek Ekibi
        'member_count': 5,
        'skills': """🎯 Takım Yetkinlikleri:
• Windows Server ve Linux sistem yönetimi
• Active Directory ve domain yönetimi
• Network yapılandırma ve troubleshooting
• Veritabanı yönetimi (PostgreSQL, MySQL, MSSQL)
• Bulut servisleri (AWS, Azure, Google Cloud)
• Cybersecurity ve firewall yönetimi
• Backup ve disaster recovery planlaması
• ERP sistem desteği (Odoo, SAP)
• Help desk ve kullanıcı desteği
• Donanım kurulum ve bakımı
• Virtualization (VMware, Hyper-V)
• Office 365 yönetimi"""
    },
    {
        'id': 3,  # Teknik Ekip
        'member_count': 6,
        'skills': """🎯 Takım Yetkinlikleri:
• CNC makine programlama ve operasyon
• PLC programlama (Siemens S7, Allen Bradley)
• Endüstriyel robot programlama (ABB, KUKA, Fanuc)
• SCADA sistem yönetimi
• Hidrolik/Pnömatik sistem bakımı
• AC/DC motor bakım ve sarımı
• Güç elektroniği ve sürücü sistemleri
• Otomasyon panel tasarımı
• Kalibrasyon ve metroloji
• Predictive maintenance teknikleri
• Vibrasyon analizi
• Termal görüntüleme"""
    },
    {
        'id': 4,  # Acil Müdahale Ekibi
        'member_count': 8,
        'skills': """🎯 Takım Yetkinlikleri:
• 7/24 acil müdahale kapasitesi
• Kriz yönetimi ve koordinasyon
• İlk yardım ve CPR sertifikası
• Yangın söndürme sistem bilgisi
• Tehlikeli madde yönetimi (HAZMAT)
• Elektrik kesinti müdahalesi
• Su baskını ve sızıntı müdahalesi
• Doğalgaz kaçağı müdahalesi
• Güvenlik sistem arızaları
• Acil durum eylem planı uygulama
• İletişim ve raporlama
• Risk değerlendirmesi"""
    },
    {
        'id': 5,  # Elektrik-Mekanik Ekibi
        'member_count': 5,
        'skills': """🎯 Takım Yetkinlikleri:
• Orta gerilim (OG) sistemleri
• Trafo test ve bakımı
• Kompanzasyon sistem optimizasyonu
• Kesintisiz güç kaynakları (UPS)
• Chiller ve soğutma sistemleri
• Kompresör ve basınçlı hava sistemleri
• Pompa, fan ve vana sistemleri
• Kaynak işlemleri (TIG, MIG, Elektrik ark)
• Torna, freze ve metal işleme
• Yalıtım ve izolasyon kontrolleri
• Enerji analizörleri kullanımı
• Harmonik filtre sistemleri"""
    },
    {
        'id': 6,  # Network Uzmanları
        'member_count': 4,
        'skills': """🎯 Takım Yetkinlikleri:
• Cisco network altyapısı yönetimi
• Firewall yapılandırma (Fortinet, Palo Alto, Checkpoint)
• VPN kurulum ve yönetimi (Site-to-Site, Client VPN)
• WiFi altyapısı tasarımı ve optimizasyonu
• Network monitoring (PRTG, Zabbix, Nagios)
• VLAN ve subnetting yapılandırma
• Load balancer ve traffic shaping
• Network güvenliği ve penetrasyon testleri
• SD-WAN çözümleri
• BGP, OSPF routing protokolleri
• QoS yapılandırma
• Network dokümantasyonu"""
    },
    {
        'id': 7,  # Bina Bakım Ekibi
        'member_count': 6,
        'skills': """🎯 Takım Yetkinlikleri:
• Sıhhi tesisat bakım ve onarımı
• Su arıtma sistemleri
• Boya, badana ve duvar kaplama
• Cam, doğrama ve cephe bakımı
• Çatı ve yalıtım kontrolleri
• Peyzaj ve bahçe bakımı
• Temizlik hizmetleri koordinasyonu
• Atık yönetimi ve geri dönüşüm
• İç mekan tasarım ve düzenleme
• Güvenlik kamera sistemleri
• Kart geçiş sistemleri
• Otopark yönetimi"""
    }
]

# Shuffle employee IDs for random distribution
random.shuffle(employee_ids)

# Assign employees to teams
employee_index = 0
for team_config in team_configs:
    team_id = team_config['id']
    member_count = min(team_config['member_count'], len(employee_ids) - employee_index)

    if member_count > 0:
        # Get employees for this team
        team_members = employee_ids[employee_index:employee_index + member_count]
        employee_index += member_count

        # Update team with members
        try:
            models.execute_kw(db, uid, password,
                'maintenance.team', 'write',
                [[team_id], {'member_ids': [(6, 0, team_members)]}])

            # Get team name for display
            team = models.execute_kw(db, uid, password,
                'maintenance.team', 'read', [team_id], {'fields': ['name']})[0]

            print(f"\n✅ Team {team_id} updated:")
            print(f"   - Assigned {member_count} members")

            # Get member names for display
            assigned_members = models.execute_kw(db, uid, password,
                'hr.employee', 'read', [team_members], {'fields': ['name']})
            for member in assigned_members:
                print(f"     • {member['name']}")

        except Exception as e:
            print(f"\n❌ Error updating team {team_id}: {str(e)}")

# Add skills to teams using direct SQL for x_skills field
import psycopg2

print("\n📝 Adding skills to teams...")
try:
    conn = psycopg2.connect(
        host="localhost",
        database="odoo_tech_service",
        user="odoo_dev",
        password="odoo_dev"
    )
    cur = conn.cursor()

    for team_config in team_configs:
        # First check if x_skills column exists
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'maintenance_team'
            AND column_name = 'x_skills'
        """)

        if not cur.fetchone():
            # Add x_skills column if it doesn't exist
            cur.execute("""
                ALTER TABLE maintenance_team
                ADD COLUMN IF NOT EXISTS x_skills TEXT
            """)
            conn.commit()

        # Update team with skills
        cur.execute("""
            UPDATE maintenance_team
            SET x_skills = %s
            WHERE id = %s
        """, (team_config['skills'], team_config['id']))

    conn.commit()
    print("✅ Skills added to all teams")

    # Show final summary
    cur.execute("""
        SELECT t.id, t.name,
               COUNT(DISTINCT mtm.hr_employee_id) as member_count,
               CASE WHEN t.x_skills IS NOT NULL THEN 'Yes' ELSE 'No' END as has_skills
        FROM maintenance_team t
        LEFT JOIN maintenance_team_hr_employee_rel mtm ON t.id = mtm.maintenance_team_id
        GROUP BY t.id, t.name, t.x_skills
        ORDER BY t.id
    """)

    print("\n📊 Final Team Summary:")
    print("-" * 60)
    for row in cur.fetchall():
        team_name = row[1]
        if isinstance(team_name, dict):
            team_name = team_name.get('en_US', str(team_name))
        print(f"Team {row[0]}: {team_name}")
        print(f"  - Members: {row[2]}")
        print(f"  - Skills defined: {row[3]}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Database error: {str(e)}")

print("\n✅ Team assignment complete!")