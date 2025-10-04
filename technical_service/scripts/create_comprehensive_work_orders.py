#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import random
from datetime import datetime, timedelta

# Connection parameters
url = 'http://localhost:8069'
db = 'odoo_clean_no_demo'
username = 'admin'
password = 'admin'

# XML-RPC connection
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Work order templates by request type
WORK_ORDER_TEMPLATES = {
    'server': {
        'diagnosis': {
            'name': 'Sunucu Arıza Teşhisi',
            'description': 'Sunucu sisteminin detaylı analizi ve sorun tespiti',
            'work_type': 'diagnosis',
            'estimated_duration': 2.0,
            'checklist': [
                'Sunucu donanım durumunu kontrol et',
                'CPU ve RAM kullanımını analiz et',
                'Disk alanı ve I/O performansını kontrol et',
                'Sistem loglarını incele',
                'Network bağlantı durumunu test et',
                'Güvenlik duvarı ve port ayarlarını kontrol et',
                'Servis durumlarını kontrol et',
                'Backup sistemini kontrol et'
            ]
        },
        'repair': {
            'name': 'Sunucu Onarım ve Optimizasyon',
            'description': 'Tespit edilen sorunların giderilmesi ve sistem optimizasyonu',
            'work_type': 'repair',
            'estimated_duration': 3.0,
            'checklist': [
                'Arızalı servisleri yeniden başlat',
                'Sistem güncellemelerini yükle',
                'Disk temizliği yap',
                'Log dosyalarını arşivle',
                'Performans ayarlarını optimize et',
                'Güvenlik yamalarını uygula',
                'Backup prosedürünü test et'
            ]
        },
        'testing': {
            'name': 'Sunucu Performans Testi',
            'description': 'Onarım sonrası kapsamlı performans ve stabilite testleri',
            'work_type': 'inspection',
            'estimated_duration': 1.5,
            'checklist': [
                'Yük testi (stress test) uygula',
                'Servis yanıt sürelerini ölç',
                'Kaynak kullanım grafiklerini kontrol et',
                'Failover senaryosunu test et',
                'Backup/restore sürecini doğrula',
                'Dokümantasyonu güncelle'
            ]
        }
    },
    'network': {
        'diagnosis': {
            'name': 'Network Altyapı Analizi',
            'description': 'Ağ bağlantı sorunlarının detaylı incelenmesi',
            'work_type': 'diagnosis',
            'estimated_duration': 2.5,
            'checklist': [
                'Switch ve router durumlarını kontrol et',
                'VLAN konfigürasyonunu incele',
                'IP çakışmalarını kontrol et',
                'DNS ve DHCP servislerini test et',
                'Bandwidth kullanımını analiz et',
                'Paket kaybı testleri yap',
                'Güvenlik duvarı loglarını incele',
                'Kablolama durumunu kontrol et'
            ]
        },
        'configuration': {
            'name': 'Network Konfigürasyon ve Optimizasyon',
            'description': 'Ağ ayarlarının düzenlenmesi ve performans iyileştirme',
            'work_type': 'repair',
            'estimated_duration': 3.5,
            'checklist': [
                'QoS ayarlarını yapılandır',
                'VLAN segmentasyonunu optimize et',
                'Routing tablolarını güncelle',
                'Access Control List (ACL) düzenle',
                'Port security ayarlarını yap',
                'Spanning Tree protokolünü optimize et',
                'Network monitoring araçlarını kur'
            ]
        },
        'testing': {
            'name': 'Network Performans ve Güvenlik Testi',
            'description': 'Ağ performansı ve güvenlik testleri',
            'work_type': 'inspection',
            'estimated_duration': 2.0,
            'checklist': [
                'Throughput testleri yap',
                'Latency ölçümleri al',
                'Güvenlik açığı taraması yap',
                'WiFi sinyal gücünü test et',
                'Failover senaryolarını test et',
                'Load balancing kontrolü yap'
            ]
        }
    },
    'electrical': {
        'inspection': {
            'name': 'Elektrik Sistemleri Güvenlik Denetimi',
            'description': 'Elektrik tesisatı ve güvenlik sistemlerinin kontrolü',
            'work_type': 'inspection',
            'estimated_duration': 2.0,
            'checklist': [
                'Ana pano ve sigortaları kontrol et',
                'Topraklama direncini ölç',
                'Kaçak akım testleri yap',
                'Acil durum aydınlatmalarını test et',
                'UPS sistemlerini kontrol et',
                'Jeneratör otomatik devreye girişini test et',
                'Elektrik kablolarının yalıtım durumunu kontrol et',
                'Termal kamera ile ısı kontrolü yap'
            ]
        },
        'repair': {
            'name': 'Elektrik Arıza Onarımı',
            'description': 'Tespit edilen elektrik sorunlarının giderilmesi',
            'work_type': 'repair',
            'estimated_duration': 4.0,
            'checklist': [
                'Arızalı sigortaları değiştir',
                'Gevşek bağlantıları sıkılaştır',
                'Hasarlı kabloları yenile',
                'Kontaktör ve röleleri kontrol et',
                'Pano temizliği ve bakımı yap',
                'Etiketleme ve işaretlemeleri güncelle',
                'Test ve ölçüm raporlarını hazırla'
            ]
        },
        'safety_check': {
            'name': 'Elektrik Güvenlik Sertifikasyonu',
            'description': 'Yasal uyumluluk ve güvenlik sertifikası hazırlığı',
            'work_type': 'inspection',
            'estimated_duration': 1.5,
            'checklist': [
                'Tüm test sonuçlarını derle',
                'Uygunsuzlukları raporla',
                'Güvenlik etiketlerini kontrol et',
                'Acil durum prosedürlerini gözden geçir',
                'Sertifika belgelerini hazırla'
            ]
        }
    },
    'elevator': {
        'inspection': {
            'name': 'Asansör Periyodik Kontrol',
            'description': 'Yasal zorunlu periyodik kontrol ve güvenlik denetimi',
            'work_type': 'inspection',
            'estimated_duration': 3.0,
            'checklist': [
                'Kabin ve kapı güvenlik sistemlerini test et',
                'Acil durum butonlarını test et',
                'Halat ve makara sistemini kontrol et',
                'Fren sistemini test et',
                'Hız regülatörünü kontrol et',
                'Aşırı yük sensörlerini test et',
                'Kabin aydınlatması ve havalandırmasını kontrol et',
                'Ses ve görüntülü iletişim sistemini test et'
            ]
        },
        'maintenance': {
            'name': 'Asansör Bakım ve Yağlama',
            'description': 'Rutin bakım ve yağlama işlemleri',
            'work_type': 'maintenance',
            'estimated_duration': 2.5,
            'checklist': [
                'Ray ve kılavuz sistemini yağla',
                'Motor yağ seviyesini kontrol et',
                'Kapı mekanizmasını yağla ve ayarla',
                'Halat gerginliğini kontrol et',
                'Kumanda panosu temizliği yap',
                'Kabin temizliği ve dezenfeksiyonu',
                'Bakım etiketini güncelle'
            ]
        },
        'repair': {
            'name': 'Asansör Arıza Giderme',
            'description': 'Bildirilen arızaların giderilmesi',
            'work_type': 'repair',
            'estimated_duration': 4.0,
            'checklist': [
                'Arıza kodlarını oku ve analiz et',
                'Sensörleri test et ve kalibre et',
                'Kontaktörleri kontrol et',
                'Kapı motorunu test et',
                'Acil durum sistemlerini test et',
                'Yazılım güncellemelerini yap',
                'Test sürüşü yap',
                'Arıza raporunu hazırla'
            ]
        }
    },
    'hvac': {
        'inspection': {
            'name': 'HVAC Sistem Kontrolü',
            'description': 'İklimlendirme sistemlerinin kapsamlı kontrolü',
            'work_type': 'inspection',
            'estimated_duration': 2.0,
            'checklist': [
                'Sıcaklık sensörlerini kalibre et',
                'Hava debisi ölçümlerini yap',
                'Kompresör basınçlarını kontrol et',
                'Soğutucu gaz kaçak testi yap',
                'Drenaj sistemini kontrol et',
                'Elektrik bağlantılarını kontrol et',
                'Termostat ayarlarını kontrol et'
            ]
        },
        'maintenance': {
            'name': 'HVAC Periyodik Bakım',
            'description': 'Filtreleme ve temizlik işlemleri',
            'work_type': 'maintenance',
            'estimated_duration': 3.0,
            'checklist': [
                'Hava filtrelerini değiştir',
                'Evaporatör ve kondenser temizliği yap',
                'Fan kayışlarını kontrol et',
                'Yağlama noktalarını yağla',
                'Soğutucu gaz seviyesini kontrol et',
                'Otomasyon sistemini kalibre et',
                'Enerji verimliliği raporu hazırla'
            ]
        },
        'repair': {
            'name': 'HVAC Arıza Onarımı',
            'description': 'Soğutma/ısıtma arızalarının giderilmesi',
            'work_type': 'repair',
            'estimated_duration': 4.5,
            'checklist': [
                'Kompresör testlerini yap',
                'Gaz dolumu yap',
                'Termostatı değiştir/kalibre et',
                'Fan motorunu kontrol et',
                'Kontrol kartını test et',
                'Sistem performans testleri yap',
                'Garanti belgelerini güncelle'
            ]
        }
    },
    'printer': {
        'diagnosis': {
            'name': 'Yazıcı Arıza Teşhisi',
            'description': 'Yazıcı sorunlarının detaylı analizi',
            'work_type': 'diagnosis',
            'estimated_duration': 1.0,
            'checklist': [
                'Bağlantı testleri yap (USB/Network)',
                'Driver durumunu kontrol et',
                'Kağıt yolu sensörlerini test et',
                'Toner/mürekkep seviyelerini kontrol et',
                'Print head durumunu kontrol et',
                'Firmware versiyonunu kontrol et'
            ]
        },
        'repair': {
            'name': 'Yazıcı Onarım ve Temizlik',
            'description': 'Yazıcı mekanik bakım ve onarımı',
            'work_type': 'repair',
            'estimated_duration': 2.0,
            'checklist': [
                'Kağıt yolunu temizle',
                'Pickup roller temizliği/değişimi',
                'Fuser unit kontrolü ve temizliği',
                'Toner/mürekkep kartuş değişimi',
                'Kalibrasyon işlemi yap',
                'Test sayfası yazdır'
            ]
        },
        'calibration': {
            'name': 'Yazıcı Kalibrasyon',
            'description': 'Baskı kalitesi optimizasyonu',
            'work_type': 'maintenance',
            'estimated_duration': 1.5,
            'checklist': [
                'Renk kalibrasyonu yap',
                'Kağıt hizalama ayarları',
                'Baskı yoğunluğu ayarları',
                'Network ayarlarını optimize et',
                'Kullanıcı eğitimi ver'
            ]
        }
    },
    'office_equipment': {
        'assessment': {
            'name': 'Ofis Ekipman İhtiyaç Analizi',
            'description': 'Mevcut durum değerlendirmesi ve ihtiyaç tespiti',
            'work_type': 'inspection',
            'estimated_duration': 1.5,
            'checklist': [
                'Mevcut ekipman envanteri çıkar',
                'Kullanım ömrü analizini yap',
                'Kullanıcı ihtiyaçlarını belirle',
                'Bütçe analizi yap',
                'Tedarikçi araştırması yap',
                'Teknik şartname hazırla'
            ]
        },
        'installation': {
            'name': 'Yeni Ekipman Kurulumu',
            'description': 'Yeni ofis ekipmanlarının kurulumu ve konfigürasyonu',
            'work_type': 'installation',
            'estimated_duration': 3.0,
            'checklist': [
                'Ekipman teslim alımı ve kontrolü',
                'Fiziksel kurulum ve montaj',
                'Elektrik ve network bağlantıları',
                'Yazılım kurulumu ve lisanslama',
                'Konfigürasyon ve özelleştirme',
                'Kullanıcı hesapları oluşturma',
                'Test ve doğrulama',
                'Kullanıcı eğitimi'
            ]
        }
    },
    'ups_generator': {
        'testing': {
            'name': 'UPS/Jeneratör Yük Testi',
            'description': 'Kesintisiz güç kaynağı ve jeneratör performans testleri',
            'work_type': 'inspection',
            'estimated_duration': 3.0,
            'checklist': [
                'Batarya kapasitesi testi',
                'Otomatik transfer testi',
                'Yük altında çalışma testi',
                'Bypass fonksiyon testi',
                'Alarm sistemlerini test et',
                'Soğutma sistemini kontrol et',
                'Yakıt seviyesi ve kalitesi kontrolü',
                'Acil durdurma testleri'
            ]
        },
        'maintenance': {
            'name': 'UPS/Jeneratör Periyodik Bakım',
            'description': 'Rutin bakım ve kontrol işlemleri',
            'work_type': 'maintenance',
            'estimated_duration': 4.0,
            'checklist': [
                'Batarya voltaj kontrolü',
                'Bağlantı noktaları temizliği',
                'Hava filtresi değişimi',
                'Yağ ve yakıt filtresi değişimi',
                'Soğutma suyu kontrolü',
                'Kayış gerginliği kontrolü',
                'Egzoz sistemi kontrolü',
                'Test çalıştırması ve kayıt'
            ]
        },
        'repair': {
            'name': 'UPS/Jeneratör Arıza Onarımı',
            'description': 'Güç sistemleri arıza giderme',
            'work_type': 'repair',
            'estimated_duration': 5.0,
            'checklist': [
                'Arıza teşhis testleri',
                'Batarya değişimi',
                'İnverter kartı kontrolü',
                'Şarj ünitesi kontrolü',
                'Transfer switch onarımı',
                'Kontrol paneli kalibrasyonu',
                'Tam yük testi',
                'Garanti ve servis kayıtları güncelleme'
            ]
        }
    },
    'safety_system': {
        'testing': {
            'name': 'Güvenlik Sistemleri Testi',
            'description': 'Yangın ve güvenlik sistemlerinin kapsamlı testi',
            'work_type': 'inspection',
            'estimated_duration': 3.5,
            'checklist': [
                'Yangın algılama sensörlerini test et',
                'Yangın söndürme sistemini kontrol et',
                'Acil çıkış aydınlatmalarını test et',
                'Sesli ve ışıklı alarm sistemlerini test et',
                'Sprinkler sistemi basınç testi',
                'Duman tahliye sistemini test et',
                'Acil anons sistemini test et',
                'İtfaiye bağlantı noktalarını kontrol et'
            ]
        },
        'inspection': {
            'name': 'Güvenlik Denetimi ve Sertifikasyon',
            'description': 'Yasal uyumluluk ve sertifikasyon denetimi',
            'work_type': 'inspection',
            'estimated_duration': 2.5,
            'checklist': [
                'Yangın tüplerinin doluluk kontrolü',
                'Yangın dolapları ekipman kontrolü',
                'Acil durum planlarını gözden geçir',
                'Tahliye tatbikatı planla',
                'Güvenlik kamera sistemini kontrol et',
                'Access kontrol sistemini test et',
                'Sertifika ve ruhsat kontrolü',
                'Denetim raporu hazırla'
            ]
        },
        'certification': {
            'name': 'Güvenlik Sertifikası Yenileme',
            'description': 'Periyodik sertifika yenileme işlemleri',
            'work_type': 'maintenance',
            'estimated_duration': 2.0,
            'checklist': [
                'Test raporlarını derle',
                'Eksiklik listesi oluştur',
                'Düzeltici faaliyetleri tamamla',
                'Yetkili firma ile koordinasyon',
                'Belge başvurusu hazırla',
                'Onay sürecini takip et'
            ]
        }
    },
    'it_setup': {
        'hardware': {
            'name': 'IT Donanım Kurulumu',
            'description': 'Bilgisayar ve çevre birimlerinin kurulumu',
            'work_type': 'installation',
            'estimated_duration': 2.0,
            'checklist': [
                'Donanım bileşenlerini kontrol et',
                'Masaüstü/laptop fiziksel kurulum',
                'Monitör ve çevre birimleri bağlantısı',
                'BIOS/UEFI ayarları',
                'RAM ve disk testleri',
                'Network bağlantı ayarları',
                'Güç yönetimi ayarları'
            ]
        },
        'software': {
            'name': 'Yazılım Yükleme ve Konfigürasyon',
            'description': 'İşletim sistemi ve uygulama yazılımları kurulumu',
            'work_type': 'installation',
            'estimated_duration': 3.0,
            'checklist': [
                'İşletim sistemi kurulumu',
                'Driver yüklemeleri',
                'Güvenlik yazılımları kurulumu',
                'Office uygulamaları kurulumu',
                'Domain/Active Directory bağlantısı',
                'Email hesabı konfigürasyonu',
                'Yazıcı ve paylaşım ayarları',
                'Backup konfigürasyonu'
            ]
        },
        'testing': {
            'name': 'Sistem Test ve Optimizasyon',
            'description': 'Kurulum sonrası test ve performans ayarları',
            'work_type': 'inspection',
            'estimated_duration': 1.5,
            'checklist': [
                'Donanım uyumluluk testleri',
                'Network bağlantı testleri',
                'Yazılım lisans kontrolü',
                'Güvenlik taraması',
                'Performans optimizasyonu',
                'Kullanıcı erişim testleri',
                'Dokümantasyon hazırlama'
            ]
        }
    }
}

def get_request_type(request_name):
    """Determine request type from request name"""
    name_lower = request_name.lower()

    if 'sunucu' in name_lower or 'server' in name_lower:
        return 'server'
    elif 'ağ' in name_lower or 'network' in name_lower or 'internet' in name_lower:
        return 'network'
    elif 'elektrik' in name_lower or 'kesinti' in name_lower:
        return 'electrical'
    elif 'asansör' in name_lower:
        return 'elevator'
    elif 'klima' in name_lower or 'soğutma' in name_lower or 'ısıtma' in name_lower:
        return 'hvac'
    elif 'yazıcı' in name_lower or 'printer' in name_lower:
        return 'printer'
    elif 'bilgisayar' in name_lower or 'laptop' in name_lower or 'monitör' in name_lower:
        return 'it_setup'
    elif 'ups' in name_lower or 'jeneratör' in name_lower or 'güç' in name_lower:
        return 'ups_generator'
    elif 'yangın' in name_lower or 'güvenlik' in name_lower or 'alarm' in name_lower:
        return 'safety_system'
    elif 'ofis' in name_lower or 'mobilya' in name_lower or 'ekipman' in name_lower:
        return 'office_equipment'
    else:
        # Default to IT setup for undefined types
        return 'it_setup'

def create_work_orders_for_request(request_id, request_name, technician_ids):
    """Create 2-3 work orders for a maintenance request"""
    request_type = get_request_type(request_name)
    templates = WORK_ORDER_TEMPLATES.get(request_type, WORK_ORDER_TEMPLATES['it_setup'])

    # Get template keys for this type
    template_keys = list(templates.keys())

    # Determine number of work orders (2 or 3)
    num_work_orders = random.choice([2, 3])

    # Select templates to use
    selected_templates = random.sample(template_keys, min(num_work_orders, len(template_keys)))

    created_work_orders = []

    for i, template_key in enumerate(selected_templates):
        template = templates[template_key]

        # Randomly select technician
        technician_id = random.choice(technician_ids) if technician_ids else False

        # Randomly select status
        status = random.choice(['pending', 'in_progress'])

        # Create scheduled date (spread across next 30 days)
        scheduled_date = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(8, 17))

        # Prepare work order data
        work_order_data = {
            'name': f"{template['name']} - Request #{request_id}",
            'description': template['description'],
            'x_request_id': request_id,
            'x_technician_id': technician_id,
            'x_work_type': template['work_type'],
            'x_estimated_duration': template['estimated_duration'],
            'x_scheduled_date': scheduled_date.strftime('%Y-%m-%d %H:%M:%S'),
            'x_work_status': status,
            'priority': random.choice(['low', 'medium', 'high']),
            'estimated_hours': template['estimated_duration']
        }

        # If status is in_progress, set start datetime
        if status == 'in_progress':
            work_order_data['x_start_datetime'] = (scheduled_date - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        try:
            # Create work order
            work_order_id = models.execute_kw(db, uid, password,
                'technical_service.work_order', 'create', [work_order_data])

            # Create checklist items
            checklist_items = template.get('checklist', [])
            # Randomly select 5-8 items from checklist
            num_items = random.randint(5, min(8, len(checklist_items)))
            selected_items = random.sample(checklist_items, num_items)

            for seq, item in enumerate(selected_items, 1):
                checklist_data = {
                    'work_order_id': work_order_id,
                    'sequence': seq * 10,
                    'name': item,
                    'is_done': False if status == 'pending' else random.choice([True, False]),
                }

                # If item is done, set completion date
                if checklist_data['is_done']:
                    checklist_data['done_date'] = scheduled_date.strftime('%Y-%m-%d %H:%M:%S')
                    checklist_data['notes'] = random.choice([
                        'Tamamlandı, sorun yok',
                        'Kontrol edildi ve onaylandı',
                        'Test başarılı',
                        'Düzeltme yapıldı',
                        'Standartlara uygun'
                    ])

                models.execute_kw(db, uid, password,
                    'technical_service.work_order.checklist', 'create', [checklist_data])

            created_work_orders.append(work_order_id)
            print(f"  ✓ Work order created: {work_order_data['name']} (ID: {work_order_id})")

        except Exception as e:
            print(f"  ✗ Error creating work order for request {request_id}: {e}")

    return created_work_orders

def main():
    print("=" * 60)
    print("COMPREHENSIVE WORK ORDER CREATION")
    print("=" * 60)

    # Get all maintenance requests
    try:
        requests = models.execute_kw(db, uid, password,
            'maintenance.request', 'search_read',
            [[]],
            {'fields': ['id', 'name'], 'order': 'id'})

        print(f"Found {len(requests)} maintenance requests")

        # Get existing work orders to check which requests already have them
        existing_work_orders = models.execute_kw(db, uid, password,
            'technical_service.work_order', 'search_read',
            [[]],
            {'fields': ['x_request_id']})

        # Count work orders per request
        work_orders_per_request = {}
        for wo in existing_work_orders:
            if wo['x_request_id']:
                req_id = wo['x_request_id'][0]
                work_orders_per_request[req_id] = work_orders_per_request.get(req_id, 0) + 1

        print(f"Found {len(existing_work_orders)} existing work orders")

        # Get available technicians
        technicians = models.execute_kw(db, uid, password,
            'hr.employee', 'search_read',
            [[]],
            {'fields': ['id', 'name']})

        technician_ids = [t['id'] for t in technicians]
        print(f"Found {len(technician_ids)} technicians available")

        # Track statistics
        requests_needing_orders = []
        requests_with_orders = []

        # Categorize requests
        for request in requests:
            req_id = request['id']
            wo_count = work_orders_per_request.get(req_id, 0)

            if wo_count == 0:
                requests_needing_orders.append(request)
            else:
                requests_with_orders.append((request, wo_count))

        print(f"\nRequests WITHOUT work orders: {len(requests_needing_orders)}")
        print(f"Requests WITH work orders: {len(requests_with_orders)}")

        # Show existing work order distribution
        if requests_with_orders:
            print("\nExisting work order distribution:")
            for req, count in requests_with_orders[:5]:  # Show first 5
                print(f"  - Request #{req['id']}: {req['name'][:50]} - {count} orders")

        # Create work orders for requests that don't have any
        print("\n" + "=" * 60)
        print("CREATING WORK ORDERS FOR REQUESTS WITHOUT ANY")
        print("=" * 60)

        total_created = 0
        for request in requests_needing_orders:
            print(f"\nRequest #{request['id']}: {request['name']}")
            created = create_work_orders_for_request(
                request['id'],
                request['name'],
                technician_ids
            )
            total_created += len(created)

        # Summary
        print("\n" + "=" * 60)
        print("CREATION SUMMARY")
        print("=" * 60)
        print(f"Total requests processed: {len(requests_needing_orders)}")
        print(f"Total work orders created: {total_created}")
        print(f"Average work orders per request: {total_created/len(requests_needing_orders):.1f}" if requests_needing_orders else "N/A")

        # Final verification
        print("\n" + "=" * 60)
        print("FINAL VERIFICATION")
        print("=" * 60)

        # Get updated counts
        all_work_orders = models.execute_kw(db, uid, password,
            'technical_service.work_order', 'search_read',
            [[]],
            {'fields': ['x_request_id', 'x_work_status']})

        final_count_per_request = {}
        status_distribution = {'pending': 0, 'in_progress': 0, 'completed': 0, 'cancelled': 0, 'paused': 0}

        for wo in all_work_orders:
            if wo['x_request_id']:
                req_id = wo['x_request_id'][0]
                final_count_per_request[req_id] = final_count_per_request.get(req_id, 0) + 1

            if wo['x_work_status']:
                status_distribution[wo['x_work_status']] = status_distribution.get(wo['x_work_status'], 0) + 1

        # Check how many requests now have at least 2 work orders
        requests_with_sufficient_orders = sum(1 for count in final_count_per_request.values() if count >= 2)

        print(f"Total work orders in system: {len(all_work_orders)}")
        print(f"Requests with work orders: {len(final_count_per_request)}/{len(requests)}")
        print(f"Requests with 2+ work orders: {requests_with_sufficient_orders}/{len(requests)}")

        print("\nWork order status distribution:")
        for status, count in status_distribution.items():
            if count > 0:
                print(f"  - {status}: {count}")

        # List any requests still without enough work orders
        insufficient_requests = []
        for request in requests:
            wo_count = final_count_per_request.get(request['id'], 0)
            if wo_count < 2:
                insufficient_requests.append((request['id'], request['name'], wo_count))

        if insufficient_requests:
            print(f"\n⚠️  Requests with less than 2 work orders ({len(insufficient_requests)}):")
            for req_id, req_name, count in insufficient_requests[:10]:  # Show first 10
                print(f"  - Request #{req_id}: {req_name[:50]} ({count} orders)")
        else:
            print("\n✓ All requests have at least 2 work orders!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()