#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Technical Service - Çalışan Demo Data Generator
Mevcut model yapısına uygun demo veriler
"""

import xmlrpc.client
import ssl
from datetime import datetime, timedelta
import random

# SSL doğrulamasını devre dışı bırak
ssl._create_default_https_context = ssl._create_unverified_context

# Bağlantı bilgileri
url = 'http://localhost:8069'
db = 'odoo_tech_service'
username = 'admin'
password = 'admin'

print("\n" + "="*70)
print("🚀 TECHNICAL SERVICE - ÇALIŞAN DEMO VERİLER")
print("="*70)

try:
    # Bağlantı
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("❌ Kimlik doğrulama başarısız!")
        exit(1)

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print("✅ Bağlantı başarılı!")

    def search(model, domain):
        return models.execute_kw(db, uid, password, model, 'search', [domain])

    def create(model, values):
        try:
            return models.execute_kw(db, uid, password, model, 'create', [values])
        except Exception as e:
            print(f"    ⚠️ Hata: {str(e)[:100]}")
            return False

    def write(model, ids, values):
        return models.execute_kw(db, uid, password, model, 'write', [ids, values])

    def read(model, ids, fields):
        return models.execute_kw(db, uid, password, model, 'read', [ids], {'fields': fields})

    # Veri saklama
    data = {
        'teams': [],
        'equipment': [],
        'requests': [],
        'tasks': []
    }

    # ================================================
    # 1. MAINTENANCE TEAMS (Var olan model)
    # ================================================
    print("\n[1] 👥 Bakım Ekipleri oluşturuluyor...")

    teams_data = [
        {'name': 'IT Destek Ekibi', 'company_id': 1},
        {'name': 'Teknik Ekip', 'company_id': 1},
        {'name': 'Acil Müdahale Ekibi', 'company_id': 1},
        {'name': 'Elektrik-Mekanik Ekibi', 'company_id': 1},
        {'name': 'Network Uzmanları', 'company_id': 1},
        {'name': 'Bina Bakım Ekibi', 'company_id': 1}
    ]

    for team_data in teams_data:
        team_existing = search('maintenance.team', [('name', '=', team_data['name'])])
        if not team_existing:
            team_id = create('maintenance.team', team_data)
            if team_id:
                data['teams'].append(team_id)
                print(f"  ✓ {team_data['name']}")

    # ================================================
    # 2. GELİŞTİRİLMİŞ EKİPMANLAR
    # ================================================
    print("\n[2] 🔧 Detaylı Ekipmanlar oluşturuluyor...")

    # Kategorileri al
    categories = {}
    cat_names = ['Sunucular', 'Network Cihazları', 'Bilgisayarlar', 'Üretim Makineleri',
                 'HVAC Sistemleri', 'Güç Sistemleri', 'Yazıcı ve Tarayıcılar']

    for cat_name in cat_names:
        cat_ids = search('maintenance.equipment.category', [('name', '=', cat_name)])
        if cat_ids:
            categories[cat_name] = cat_ids[0]
        else:
            cat_id = create('maintenance.equipment.category', {
                'name': cat_name,
                'technician_user_id': uid
            })
            if cat_id:
                categories[cat_name] = cat_id

    # Detaylı ekipmanlar
    equipment_list = [
        # Kritik Sunucular
        {
            'name': 'DELL R750 - ERP Ana Sunucu',
            'serial_no': 'DELL-R750-ERP-001',
            'category_id': categories.get('Sunucular'),
            'location': 'C Blok - Server Room Rack A1',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][0] if data['teams'] else False,
            'cost': 125000.0,
            'note': 'Kritik Sistem - 7/24 Monitoring\nRAM: 256GB\nCPU: Dual Xeon Gold\nStorage: 20TB SSD RAID10',
            'warranty_date': (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d'),
            'maintenance_duration': 4.0,
            'maintenance_count': 12
        },
        {
            'name': 'IBM Power9 - SAP HANA Database',
            'serial_no': 'IBM-P9-HANA-002',
            'category_id': categories.get('Sunucular'),
            'location': 'C Blok - Server Room Rack A2',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][0] if data['teams'] else False,
            'cost': 450000.0,
            'note': 'Kritik Sistem - In-Memory Database\nRAM: 2TB\nCPU: POWER9 24-core\nStorage: 50TB NVMe',
            'warranty_date': (datetime.now() + timedelta(days=1095)).strftime('%Y-%m-%d'),
            'maintenance_duration': 6.0,
            'maintenance_count': 24
        },

        # Network Cihazları
        {
            'name': 'Cisco Nexus 9500 - Core Switch',
            'serial_no': 'CISCO-N9500-CORE',
            'category_id': categories.get('Network Cihazları'),
            'location': 'C Blok - Network Room',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][4] if len(data['teams']) > 4 else False,
            'cost': 185000.0,
            'note': '100Gbps Backbone\n48x 10Gbps SFP+\n6x 100Gbps QSFP28\nRedundant Power',
            'warranty_date': (datetime.now() + timedelta(days=1095)).strftime('%Y-%m-%d')
        },
        {
            'name': 'Fortinet FortiGate 3000D - Main Firewall',
            'serial_no': 'FGT-3000D-MAIN',
            'category_id': categories.get('Network Cihazları'),
            'location': 'C Blok - Security Room',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][4] if len(data['teams']) > 4 else False,
            'cost': 95000.0,
            'note': 'Enterprise Firewall\nThroughput: 200Gbps\nSSL Inspection: 40Gbps\nHA Active-Active',
            'warranty_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        },

        # Üretim Makineleri
        {
            'name': 'DMG MORI NLX 2500 - CNC Torna',
            'serial_no': 'DMG-NLX2500-01',
            'category_id': categories.get('Üretim Makineleri'),
            'location': 'B Blok - Üretim Hattı 1',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][1] if len(data['teams']) > 1 else False,
            'cost': 850000.0,
            'note': 'High Precision CNC\nMax Diameter: 366mm\nMax Length: 705mm\nSpindle: 5000 RPM\nTool Positions: 12',
            'warranty_date': (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d'),
            'maintenance_duration': 8.0,
            'maintenance_count': 52
        },
        {
            'name': 'TRUMPF TruLaser 5030 Fiber',
            'serial_no': 'TRUMPF-5030F-01',
            'category_id': categories.get('Üretim Makineleri'),
            'location': 'B Blok - Lazer Kesim',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][1] if len(data['teams']) > 1 else False,
            'cost': 1200000.0,
            'note': '8kW Fiber Laser\nCutting Area: 3000x1500mm\nMax Thickness: 25mm Steel\nPositioning Speed: 140m/min',
            'warranty_date': (datetime.now() + timedelta(days=1095)).strftime('%Y-%m-%d')
        },

        # HVAC Sistemleri
        {
            'name': 'Carrier AquaSnap 30RQP - Chiller Unit',
            'serial_no': 'CARRIER-30RQP-DC01',
            'category_id': categories.get('HVAC Sistemleri'),
            'location': 'Çatı - Chiller Platformu',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][3] if len(data['teams']) > 3 else False,
            'cost': 280000.0,
            'note': 'Data Center Cooling\nCapacity: 500kW\nEER: 3.2\nRefrigerant: R410A\nFree Cooling Option',
            'warranty_date': (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d'),
            'maintenance_duration': 4.0,
            'maintenance_count': 12
        },

        # Güç Sistemleri
        {
            'name': 'Caterpillar C1000 - Ana Jeneratör',
            'serial_no': 'CAT-C1000-MAIN',
            'category_id': categories.get('Güç Sistemleri'),
            'location': 'Jeneratör Binası',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][3] if len(data['teams']) > 3 else False,
            'cost': 450000.0,
            'note': 'Prime Power: 1000kVA\nStandby: 1100kVA\nFuel Tank: 5000L\nAutomatic Transfer Switch\nParallel Operation Ready',
            'warranty_date': (datetime.now() + timedelta(days=1095)).strftime('%Y-%m-%d'),
            'maintenance_duration': 6.0,
            'maintenance_count': 26
        },
        {
            'name': 'Schneider Galaxy VX 500kVA - UPS System',
            'serial_no': 'SCH-GALVX500-DC',
            'category_id': categories.get('Güç Sistemleri'),
            'location': 'C Blok - UPS Room',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][3] if len(data['teams']) > 3 else False,
            'cost': 320000.0,
            'note': 'Modular UPS\nCapacity: 500kVA\nEfficiency: 99%\nBattery Runtime: 30min\nRedundancy: N+1',
            'warranty_date': (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d')
        },

        # Bilgisayar ve Çevre Birimleri
        {
            'name': 'Dell Precision 7920 - CAD Workstation',
            'serial_no': 'DELL-7920-CAD-015',
            'category_id': categories.get('Bilgisayarlar'),
            'location': 'Ar-Ge Ofisi 301',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][0] if data['teams'] else False,
            'cost': 35000.0,
            'note': 'Dual Xeon / 128GB RAM / Quadro RTX 5000',
            'warranty_date': (datetime.now() + timedelta(days=1095)).strftime('%Y-%m-%d')
        },
        {
            'name': 'HP DesignJet T1700 - Plotter',
            'serial_no': 'HP-T1700-PLOT-01',
            'category_id': categories.get('Yazıcı ve Tarayıcılar'),
            'location': 'Teknik Ofis',
            'technician_user_id': uid,
            'maintenance_team_id': data['teams'][0] if data['teams'] else False,
            'cost': 45000.0,
            'note': '44-inch Plotter\n2400x1200 dpi\n6-color ink system',
            'warranty_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        }
    ]

    for eq_data in equipment_list:
        eq_existing = search('maintenance.equipment', [('serial_no', '=', eq_data['serial_no'])])
        if not eq_existing:
            eq_id = create('maintenance.equipment', eq_data)
            if eq_id:
                data['equipment'].append(eq_id)
                print(f"  ✓ {eq_data['name']}")

    # ================================================
    # 3. DETAYLI BAKIM TALEPLERİ
    # ================================================
    print("\n[3] 📋 Detaylı Bakım Talepleri oluşturuluyor...")

    # Employee'leri al
    employee_ids = search('hr.employee', [])

    # Partner'ları al veya oluştur (requester için)
    partner_ids = search('res.partner', [('is_company', '=', False)])[:10]

    detailed_requests = [
        # KRİTİK - Sunucu Çökmesi
        {
            'name': '🔴 [P1-CRITICAL] ERP Sunucu Tamamen Çöktü - İŞLETME DURDU!',
            'description': '''=== KRITIK DURUM - DERHAL MÜDAHALE ===

OLAY ZAMANI: 09:45
BILDIREN: Üretim Müdürü
DURUM: ERP sunucusu tamamen erişilemez

SEMPTOMLAR:
- Blue Screen of Death (BSOD) hatası
- Error Code: KERNEL_DATA_INPAGE_ERROR
- Otomatik restart döngüsüne girdi
- Son 3 restart denemesi başarısız

ETKİ ANALİZİ:
- 150+ kullanıcı sistemde çalışamıyor
- Üretim planlaması durdu
- Satış faturaları kesilemiyor
- Lojistik sevkiyatlar beklemede
- Tahmini kayıp: 50.000 TL/saat

İLK MÜDAHALE:
09:50 - Fiziksel kontrol yapıldı
09:55 - RAM modülleri kontrol edildi
10:00 - Yedek sunucuya geçiş deneniyor
10:05 - RAID controller hatası tespit edildi

GÜNCEL DURUM:
- Yedek sunucu hazırlanıyor (ETA: 30 dakika)
- Son backup: Bu sabah 03:00 (6 saat önce)
- Veri kaybı riski: Düşük

YAPILACAKLAR:
1. RAID rebuild işlemi başlatılacak
2. Arızalı disk değiştirilecek
3. Sistem restore edilecek
4. Test ve doğrulama yapılacak

TAHMİNİ ÇÖZÜM SÜRESİ: 2-3 saat''',
            'priority': '3',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][0] if data['equipment'] else False,
            'employee_id': employee_ids[0] if employee_ids else False,
            'requester_id': partner_ids[0] if partner_ids else False,
            'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][0] if data['teams'] else False
        },

        # KRİTİK - Siber Güvenlik
        {
            'name': '🔒 [P1-SECURITY] Ransomware Saldırısı Tespit Edildi!',
            'description': '''=== GÜVENLİK İHLALİ - ACİL ===

TESPIT ZAMANI: 11:30
KAYNAK: Security Operations Center (SOC)
THREAT LEVEL: CRITICAL

SALDIRI DETAYLARI:
- Ransomware türü: LockBit 3.0 variant
- Etkilenen sistemler: File Server, Backup Server
- Şifrelenmiş dosya sayısı: 15,000+
- Fidye notu bulundu: 100 BTC talep

ETKİLENEN SİSTEMLER:
✓ FS-01 File Server - %60 encrypted
✓ BKP-02 Backup Server - %30 encrypted
✓ DB-Test - Isolated (güvende)
✓ ERP Production - Isolated (güvende)

ALINAN ÖNLEMLER:
11:35 - Tüm sistemler network'ten izole edildi
11:40 - Incident Response Team aktive edildi
11:45 - Clean backup'lar kontrol ediliyor
11:50 - Law enforcement bilgilendirildi

KURTARMA PLANI:
1. Temiz backup'lardan restore
2. Tüm sistemlerde malware scan
3. Güvenlik patch'leri uygulama
4. Network segmentasyon güncelleme
5. Kullanıcı credential reset

RTO: 24 saat
RPO: 12 saat (last clean backup)''',
            'priority': '3',
            'maintenance_type': 'corrective',
            'employee_id': employee_ids[1] if len(employee_ids) > 1 else False,
            'requester_id': partner_ids[1] if len(partner_ids) > 1 else False,
            'request_date': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][4] if len(data['teams']) > 4 else False
        },

        # YÜKSEK - Üretim Hattı
        {
            'name': '⚠️ [P2-HIGH] CNC Makine Anormal Titreşim - Kalite Sorunu',
            'description': '''ÜRETIM KRİZİ - ACİL MÜDAHALE

MAKINE: DMG MORI NLX 2500
LOKASYON: B Blok - Üretim Hattı 1
OPERATÖR: Murat Can

SORUN:
- Anormal titreşim seviyeleri (8.5 mm/s RMS)
- Normal limit: 2.8 mm/s
- Ürün kalitesi bozuldu
- Surface finish out of tolerance

ÜRETİM ETKİSİ:
- 50 parça hurda (değer: 25,000 TL)
- Üretim hızı %60 düştü
- Müşteri siparişi risk altında

İLK TESPİTLER:
□ Spindle bearing kontrolü - Aşınma var
□ Tool holder kontrolü - Normal
□ Coolant flow - Normal
□ Foundation check - Minor looseness detected

ÇÖZÜM PLANI:
1. Makine durdurulacak (15:00)
2. Spindle bearing değişimi
3. Foundation bolts sıkılacak
4. Vibration analiz tekrarı
5. Test run ve kalibrasyon

Parça siparişi verildi (ETA: 2 saat)
Tahmini duruş: 4 saat''',
            'priority': '2',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][4] if len(data['equipment']) > 4 else False,
            'employee_id': employee_ids[2] if len(employee_ids) > 2 else False,
            'requester_id': partner_ids[2] if len(partner_ids) > 2 else False,
            'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][1] if len(data['teams']) > 1 else False
        },

        # PLANLI BAKIM
        {
            'name': '📅 [PM-SCHEDULED] Q4 2024 Data Center Komple Bakım',
            'description': '''YILLIK KAPSAMLI BAKIM PROGRAMI

KAPSAM: Data Center tüm sistemler
TARIH: 25-26 Ocak 2024 (Hafta sonu)
SÜRE: 16 saat
DOWNTIME: 8 saat (gece vardiyası)

BAKIM PLANI:

=== CUMARTESI (25 Ocak) ===
08:00 - Hazırlık ve backup kontrol
09:00 - UPS batarya testleri ve değişim
11:00 - Jeneratör load bank testi
14:00 - HVAC sistemleri bakım
16:00 - Elektrik pano temizlik ve termal görüntüleme
18:00 - Network kablolama düzenleme

=== PAZAR (26 Ocak) ===
02:00 - PRODUCTION SYSTEMS OFFLINE
02:30 - Server firmware updates
04:00 - Storage system maintenance
05:00 - Network equipment updates
06:00 - Security patches
07:00 - System restart ve test
08:00 - PRODUCTION SYSTEMS ONLINE
09:00 - Validation testleri
10:00 - Bakım raporu

TAKIM:
- Internal IT Team (5 kişi)
- Vendor Support (3 kişi)
- Electrical Contractor (2 kişi)
- HVAC Specialist (2 kişi)

MALZEMELER:
✓ UPS Bataryalar (40 adet) - Hazır
✓ Air filters (20 adet) - Hazır
✓ Cleaning supplies - Hazır
✓ Spare parts kit - Hazır

RİSK DEĞERLENDİRME: Düşük
BACKUP PLAN: Hazır
ROLLBACK PROSEDÜR: Dokümante edildi''',
            'priority': '1',
            'maintenance_type': 'preventive',
            'schedule_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'employee_id': employee_ids[3] if len(employee_ids) > 3 else False,
            'requester_id': partner_ids[3] if len(partner_ids) > 3 else False,
            'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][0] if data['teams'] else False
        },

        # NETWORK SORUNU
        {
            'name': '🌐 [P2-NETWORK] Core Switch CPU %95 - Network Yavaşlaması',
            'description': '''NETWORK PERFORMANS KRİZİ

CİHAZ: Cisco Nexus 9500
PROBLEM BAŞLANGIÇ: 13:45
SEVİYE: HIGH

MEVCUT DURUM:
- CPU Usage: 95% (Normal: 30-40%)
- Memory Usage: 78%
- Packet Loss: 12%
- Latency: 250ms (Normal: <5ms)

ETKİLENEN ALANLAR:
• Tüm kampüs (500+ kullanıcı)
• ERP yavaşlama
• VoIP kalite sorunu
• Video konferans kesintileri

LOG ANALİZİ:
13:45:23 - Spanning-tree topology change
13:45:45 - MAC flapping detected VLAN 100
13:46:12 - Storm control triggered Port 1/1/5
13:47:00 - High CPU interrupt detected

MUHTEMEL SEBEPLER:
1. Broadcast storm (En olası)
2. Routing loop
3. DDoS attack
4. Hardware malfunction

ÇÖZÜM ADIIMLARI:
[✓] Port 1/1/5 disabled
[✓] Storm control limits adjusted
[⏳] Analyzing traffic patterns
[ ] Firmware bug check
[ ] Hardware diagnostic

Vendor case açıldı: #SR-2024-0125''',
            'priority': '2',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][2] if len(data['equipment']) > 2 else False,
            'employee_id': employee_ids[4] if len(employee_ids) > 4 else False,
            'requester_id': partner_ids[4] if len(partner_ids) > 4 else False,
            'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][4] if len(data['teams']) > 4 else False
        },

        # HVAC KRİZİ
        {
            'name': '❄️ [P1-HVAC] Data Center Soğutma Sistemi Arızası - Sıcaklık 42°C!',
            'description': '''TERMAL KRİZ - ACİL MÜDAHALE

LOKASYON: C Blok - Data Center
ALARM ZAMANI: 14:15
KRİTİK SEVİYE: EXTREME

SICAKLIK DEĞERLERİ:
- Cold Aisle: 38°C (Normal: 22°C)
- Hot Aisle: 52°C (Normal: 35°C)
- Server Inlet: 42°C (CRITICAL!)
- Humidity: 25% (Normal: 45-55%)

CHILLER DURUMU:
- Unit 1: FAULT - Compressor failure
- Unit 2: OFFLINE - Maintenance
- Emergency Unit: STARTING (ETA: 10 min)

ALINAN ÖNLEMLER:
14:16 - Non-critical servers shutdown başladı
14:18 - Portable AC units (4x) devrede
14:20 - Emergency chiller startup initiated
14:22 - Vendor emergency service çağrıldı

SERVER DURUMU:
[SHUTDOWN] Test servers (5x)
[SHUTDOWN] Development servers (3x)
[RUNNING-HOT] Production servers (8x)
[CRITICAL] Storage arrays (3x)

TERMAL RİSK:
- Hardware damage riski: YÜKSEK
- Auto-shutdown tetiklenebilir
- Data corruption olasılığı

EYLEM PLANI:
1. Emergency cooling maximize
2. Critical system migration to DR site
3. Compressor replacement (ETA: 3 saat)
4. Gradual system restoration

Vendor ETA: 45 dakika
Tahmini çözüm: 4 saat''',
            'priority': '3',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][6] if len(data['equipment']) > 6 else False,
            'employee_id': employee_ids[5] if len(employee_ids) > 5 else False,
            'requester_id': partner_ids[5] if len(partner_ids) > 5 else False,
            'request_date': (datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][3] if len(data['teams']) > 3 else False
        },

        # ELEKTRİK KESİNTİSİ
        {
            'name': '⚡ [P2-POWER] Kısmi Güç Kaybı - UPS Bypass Modda',
            'description': '''ELEKTRİK ALTYAPI SORUNU

OLAY: Faz kaybı ve UPS arızası
ZAMAN: 15:30
LOKASYON: C Blok

ELEKTRİK DURUMU:
- L1 Fazı: OK (230V)
- L2 Fazı: LOST (0V)
- L3 Fazı: OK (228V)
- Nötr: OK

UPS DURUMU:
- Mode: BYPASS (Kritik!)
- Battery: 100% (Not in use)
- Load: 65% (280kVA)
- Alarm: Input Phase Lost

ETKİ:
• UPS koruması yok
• Power quality sorunları
• Ani kesinti riski yüksek

JENERATÖR:
- Status: Standby Ready
- Fuel: 4,500L (90%)
- Last test: 5 days ago
- Auto-transfer: ENABLED

YAPILAN İŞLEMLER:
[✓] TEDAŞ bildirimi yapıldı
[✓] Critical loads redistribution
[✓] Generator pre-heating started
[⏳] UPS service mode analizi
[ ] Phase rotation check

TEDAŞ ETA: 2 saat
Risk Level: HIGH''',
            'priority': '2',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][8] if len(data['equipment']) > 8 else False,
            'employee_id': employee_ids[6] if len(employee_ids) > 6 else False,
            'requester_id': partner_ids[6] if len(partner_ids) > 6 else False,
            'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][3] if len(data['teams']) > 3 else False
        },

        # DATABASE SORUNU
        {
            'name': '💾 [P2-DATABASE] Oracle DB Performance Degradation - Response Time 10x',
            'description': '''DATABASE KRİTİK PERFORMANS SORUNU

DATABASE: ORCL-PROD-01
VERSION: Oracle 19c Enterprise
HOST: IBM Power9 Server

PERFORMANS METRİKLERİ:
- Avg Response Time: 3,200ms (Normal: 300ms)
- Active Sessions: 450 (Normal: 50-100)
- CPU Wait: 85%
- I/O Wait: 65%
- Blocking Sessions: 23

TOP WAIT EVENTS:
1. db file sequential read (45%)
2. log file sync (22%)
3. buffer busy waits (18%)
4. latch: cache buffers chains (15%)

AWR ANALİZİ:
- Execution Plan değişimi tespit edildi
- Statistics stale (30 days old)
- Tablespace USERS %98 full
- Redo log switches: 45/hour (high)

KULLANICI ETKİSİ:
• ERP işlemleri 10x yavaş
• Rapor timeout'ları
• Batch job'lar kuyrukta
• User complaints: 50+

ÇÖZÜM PLANI:
1. [RUNNING] Kill blocking sessions
2. [RUNNING] Gather statistics
3. [PLANNED] Add tablespace datafile
4. [PLANNED] SQL tuning advisor
5. [PLANNED] Index rebuild (after hours)

DBA Team: 2 kişi aktif
Vendor Support: Case #SR-4567890
Tahmini çözüm: 2-3 saat''',
            'priority': '2',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][1] if len(data['equipment']) > 1 else False,
            'employee_id': employee_ids[7] if len(employee_ids) > 7 else False,
            'requester_id': partner_ids[7] if len(partner_ids) > 7 else False,
            'request_date': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][0] if data['teams'] else False
        },

        # LAZER KESİM MAKİNESİ
        {
            'name': '🔥 [P3-PRODUCTION] Lazer Kesim Kalite Sorunu - Müşteri Şikayeti',
            'description': '''ÜRETIM KALITE ALARMI

MAKINE: TRUMPF TruLaser 5030 Fiber
PROBLEM: Kesim kalitesi düşüşü
MÜSTERI: ABC Automotive (VIP)

KALITE SORUNLARI:
- Kesim kenarı pürüzlü (Ra >12.5)
- Kesim açısı hatası (>3°)
- Dross formation yüksek
- Dimensional tolerance aşımı

TEST SONUÇLARI:
Material: 10mm Mild Steel
- Cutting speed: 1.8 m/min (Normal: 2.5)
- Laser power: 8000W
- Focus position: +2mm (checked)
- Assist gas: O2 6 bar (OK)
- Nozzle condition: Worn (!)

KONT ROL CHECKLIS T:
[✓] Lens contamination - Cleaned
[✓] Nozzle alignment - Adjusted
[✓] Beam alignment - OK
[!] Nozzle wear - REPLACE NEEDED
[!] Resonator power - 92% (Declining)
[?] Chiller temperature - Checking

SİPARIŞ DURUMU:
- Deadline: Tomorrow 14:00
- Remaining: 200 parts
- Completed: 150 parts (50 rejected)

AKSIYON:
1. Nozzle değişimi (stock'ta var)
2. Resonator tune-up
3. Test cuts
4. Quality validation
5. Production restart

Teknisyen atandı: 2 kişi
Tahmini süre: 3 saat''',
            'priority': '1',
            'maintenance_type': 'corrective',
            'equipment_id': data['equipment'][5] if len(data['equipment']) > 5 else False,
            'employee_id': employee_ids[8] if len(employee_ids) > 8 else False,
            'requester_id': partner_ids[8] if len(partner_ids) > 8 else False,
            'request_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][1] if len(data['teams']) > 1 else False
        },

        # YEDEKLEME SORUNU
        {
            'name': '💾 [P2-BACKUP] Kritik Backup Failure - 5 Gündür Yedek Yok!',
            'description': '''YEDEKLEME KRİZİ - VERİ KAYBI RİSKİ

BACKUP SYSTEM: Veeam Backup & Replication v12
SON BAŞARILI YEDEK: 5 gün önce (19 Ocak)

FAILED JOBS:
- JOB_DAILY_FULL: Failed (5 days)
- JOB_HOURLY_INCREMENT: Failed (5 days)
- JOB_SQL_LOGS: Failed (3 days)
- JOB_FILESERVER: Failed (5 days)

ERROR DETAILS:
"Failed to create snapshot: Insufficient system resources"
"Target repository is unavailable"
"Network path not found: \\backup-nas\repo1"

REPOSITORY STATUS:
- NAS-01: OFFLINE (Hardware failure)
- NAS-02: FULL (0.5TB free of 50TB)
- Cloud: DISCONNECTED (License expired)
- Tape: WORKING (but slow)

VERİ RİSK ANALİZİ:
Critical Systems at Risk:
• ERP Database: 5 days RPO (SLA: 24h) ❌
• File Server: 5 days RPO (SLA: 24h) ❌
• Email: 3 days RPO (SLA: 12h) ❌
• Source Code: Protected (Git) ✅

ÇÖZÜM ADILMLARI:
1. [IN PROGRESS] NAS-01 disk replacement
2. [DONE] NAS-02 old backups cleanup (freed 5TB)
3. [PENDING] Cloud license renewal
4. [RUNNING] Manual backup to tape
5. [PLANNED] Backup infrastructure redesign

Recovery Actions:
- Emergency backup to external drives
- Vendor support ticket: #VEE-2024-8901
- Management escalation done

ETA: 6-8 saat''',
            'priority': '2',
            'maintenance_type': 'corrective',
            'employee_id': employee_ids[9] if len(employee_ids) > 9 else False,
            'requester_id': partner_ids[9] if len(partner_ids) > 9 else False,
            'request_date': (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'),
            'maintenance_team_id': data['teams'][0] if data['teams'] else False
        }
    ]

    for req_data in detailed_requests:
        req_id = create('maintenance.request', req_data)
        if req_id:
            data['requests'].append(req_id)
            priority_label = {
                '3': 'KRİTİK',
                '2': 'YÜKSEK',
                '1': 'ORTA',
                '0': 'DÜŞÜK'
            }.get(req_data.get('priority', '1'), 'NORMAL')
            print(f"  ✓ [{priority_label}] {req_data['name'][:50]}...")

    # ================================================
    # 4. PROJECT TASKS (İŞ EMİRLERİ)
    # ================================================
    print("\n[4] 📝 İş Emirleri (Project Tasks) oluşturuluyor...")

    # Project bul veya oluştur
    project_ids = search('project.project', [('name', '=', 'Teknik Servis İşleri')])
    if not project_ids:
        project_id = create('project.project', {
            'name': 'Teknik Servis İşleri',
            'company_id': 1
        })
    else:
        project_id = project_ids[0]

    # İlk 5 request için detaylı iş emri
    for i, req_id in enumerate(data['requests'][:5]):
        try:
            req_info = read('maintenance.request', [req_id], ['name', 'description', 'priority'])
            if req_info:
                req = req_info[0]

                task_data = {
                    'name': f"WO-2024-{i+200:04d}: {req['name'][:50]}",
                    'project_id': project_id,
                    'description': f"<h3>Maintenance Request</h3>{req.get('description', '')}",
                    'priority': '1' if req.get('priority') == '3' else '0',
                    'user_ids': [(6, 0, [uid])],
                    'planned_hours': random.randint(2, 8),
                    'date_deadline': (datetime.now() + timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d')
                }

                task_id = create('project.task', task_data)
                if task_id:
                    data['tasks'].append(task_id)
                    print(f"  ✓ İş Emri: WO-2024-{i+200:04d}")

        except Exception as e:
            print(f"  ✗ İş emri hatası: {str(e)[:80]}")

    # ================================================
    # ÖZET RAPOR
    # ================================================
    print("\n" + "="*70)
    print("📊 ÖZET RAPOR")
    print("="*70)

    print(f"""
    ✓ Maintenance Teams     : {len(data['teams'])} ekip
    ✓ Equipment (Detaylı)   : {len(data['equipment'])} ekipman
    ✓ Maintenance Requests  : {len(data['requests'])} talep
    ✓ Project Tasks         : {len(data['tasks'])} iş emri

    TOPLAM: {sum([len(data[key]) for key in data.keys()])} kayıt
    """)

    print("\n✅ TÜM VERİLER BAŞARIYLA OLUŞTURULDU!")
    print("\n🌐 Erişim:")
    print(f"  URL: {url}")
    print(f"  DB : {db}")
    print(f"  User: {username} / {password}")

    print("\n📱 Görüntülemek için:")
    print("  • Maintenance > Maintenance Requests")
    print("  • Maintenance > Equipment")
    print("  • Maintenance > Teams")
    print("  • Project > All Tasks")

except Exception as e:
    print(f"\n❌ Hata: {str(e)}")
    import traceback
    traceback.print_exc()