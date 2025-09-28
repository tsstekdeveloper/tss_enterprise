#!/usr/bin/env python3
"""
Add skills to service teams
"""

import psycopg2

# Team skills data
team_skills = {
    1: """🎯 Takım Yetkinlikleri:
• Elektrik sistemleri bakımı ve onarımı
• Mekanik sistemler troubleshooting
• HVAC sistem yönetimi ve optimizasyonu
• Bina otomasyon sistemleri (BMS)
• Yangın alarm ve güvenlik sistemleri
• Jeneratör ve UPS bakımı
• Asansör bakım koordinasyonu
• Enerji verimliliği projeleri
• Periyodik bakım planlama""",

    2: """🎯 Takım Yetkinlikleri:
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
• Office 365 yönetimi""",

    3: """🎯 Takım Yetkinlikleri:
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
• Termal görüntüleme""",

    4: """🎯 Takım Yetkinlikleri:
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
• Risk değerlendirmesi""",

    5: """🎯 Takım Yetkinlikleri:
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
• Harmonik filtre sistemleri""",

    6: """🎯 Takım Yetkinlikleri:
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
• Network dokümantasyonu""",

    7: """🎯 Takım Yetkinlikleri:
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

print("📝 Adding skills to teams...")

try:
    conn = psycopg2.connect(
        host="localhost",
        database="odoo_tech_service",
        user="odoo_dev",
        password="odoo_dev"
    )
    cur = conn.cursor()

    # First check if x_skills column exists
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'maintenance_team'
        AND column_name = 'x_skills'
    """)

    if not cur.fetchone():
        # Add x_skills column if it doesn't exist
        print("Adding x_skills column to maintenance_team table...")
        cur.execute("""
            ALTER TABLE maintenance_team
            ADD COLUMN x_skills TEXT
        """)
        conn.commit()
        print("✅ x_skills column added")

    # Update each team with skills
    for team_id, skills in team_skills.items():
        cur.execute("""
            UPDATE maintenance_team
            SET x_skills = %s
            WHERE id = %s
        """, (skills, team_id))
        print(f"✅ Updated team {team_id} with skills")

    conn.commit()

    # Show final summary
    cur.execute("""
        SELECT t.id,
               CASE
                   WHEN t.name::text LIKE '%{%' THEN
                       (t.name::json->>'en_US')
                   ELSE
                       t.name::text
               END as team_name,
               COUNT(DISTINCT mtm.hr_employee_id) as member_count,
               CASE WHEN t.x_skills IS NOT NULL THEN 'Yes' ELSE 'No' END as has_skills,
               LEFT(t.x_skills, 50) as skills_preview
        FROM maintenance_team t
        LEFT JOIN maintenance_team_hr_employee_rel mtm ON t.id = mtm.maintenance_team_id
        GROUP BY t.id, t.name, t.x_skills
        ORDER BY t.id
    """)

    print("\n📊 Final Team Summary:")
    print("=" * 80)
    for row in cur.fetchall():
        print(f"Team {row[0]}: {row[1]}")
        print(f"  - Members: {row[2]}")
        print(f"  - Skills defined: {row[3]}")
        if row[4]:
            print(f"  - Preview: {row[4]}...")
        print()

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Database error: {str(e)}")

print("✅ Skills successfully added to all teams!")