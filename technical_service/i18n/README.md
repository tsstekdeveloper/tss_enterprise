# Technical Service Module - Çeviri Dosyaları

## 📁 Dosyalar

### 1. **tr.po** - Türkçe Çeviri
- Tam Türkçe çeviri içerir
- 400+ çevrilmiş metin
- Tüm modül özelliklerini kapsar

### 2. **technical_service.pot** - Çeviri Şablonu
- Yeni diller için temel şablon
- Boş çeviri alanları içerir
- Diğer dillere kolayca kopyalanabilir

## 🌐 Desteklenen Diller

Şu anda desteklenen:
- **Türkçe (tr)** - %100 tamamlandı
- **İngilizce** - Varsayılan (kod içinde)

## 📋 Çeviri Kategorileri

### Menüler
- Ana menü ve alt menüler
- Service Management
- Asset Management
- Configuration

### Model Alanları
- Service Request alanları
- Work Order alanları
- SLA ve Contract alanları
- Campus ve Building alanları
- Team ve Asset alanları

### Seçim Listeleri
- Request Type (Incident, Service Request, Problem...)
- Priority Levels (P1-P4)
- Work Status (Pending, In Progress, Completed...)
- Contract Types (AMC, Warranty, On-Call...)
- Asset Types (IT, Production, Office...)

### Butonlar ve Aksiyonlar
- Start Work / İşe Başla
- Complete Work / İşi Tamamla
- Cancel / İptal
- Create / Oluştur

### Mesajlar ve Uyarılar
- SLA uyarıları
- Başarı mesajları
- Hata mesajları
- Bilgilendirmeler

### Raporlar
- Work Order Report
- Service Request Report
- SLA Performance Report

### E-posta Şablonları
- Service Request Created
- Work Order Assigned
- SLA Warning

## 🔧 Kullanım

### Türkçe'yi Aktif Etme

1. **Ayarlar > Çeviriler > Diller** menüsüne gidin
2. Türkçe'yi aktif edin (yoksa yükleyin)
3. Kullanıcı tercihlerinden dili Türkçe olarak seçin

### Çevirileri Güncelleme

```bash
# POT dosyasını güncelle (yeni metinler için)
cd /opt/odoo/custom-addons/technical_service
python3 /opt/odoo/odoo18/odoo-bin -d odoo_dev --i18n-export=i18n/technical_service.pot --modules=technical_service

# Türkçe çeviriyi güncelle
python3 /opt/odoo/odoo18/odoo-bin -d odoo_dev --i18n-import=i18n/tr.po --language=tr --modules=technical_service
```

### Yeni Dil Ekleme

1. `technical_service.pot` dosyasını kopyalayın
2. Yeni dil kodunu kullanarak adlandırın (örn: `de.po` Almanca için)
3. Çevirileri doldurun
4. Yukarıdaki import komutunu kullanarak yükleyin

## 📊 Çeviri İstatistikleri

| Kategori | Toplam | Çevrilen (TR) |
|----------|--------|---------------|
| Menüler | 15 | 15 |
| Model Alanları | 150+ | 150+ |
| Seçim Listeleri | 80+ | 80+ |
| Butonlar | 10+ | 10+ |
| Mesajlar | 20+ | 20+ |
| Raporlar | 5+ | 5+ |
| **TOPLAM** | **400+** | **400+** |

## 🔍 Önemli Çeviri Kuralları

### Tutarlılık
- "Service Request" her zaman "Servis Talebi"
- "Work Order" her zaman "İş Emri"
- "Asset" her zaman "Varlık"
- "Equipment" her zaman "Ekipman"

### Kısaltmalar
- SLA - SLA (değiştirilmedi)
- CAPA - CAPA (değiştirilmedi)
- IT - BT (Bilgi Teknolojileri)

### Tarih/Saat Formatları
- Tarihler: GG.AA.YYYY
- Saatler: SS:DD (24 saat formatı)

## 🐛 Bilinen Sorunlar

1. **Dinamik içerikler**: JavaScript ile oluşturulan bazı metinler çevrilmemiş olabilir
2. **Rapor başlıkları**: Bazı PDF rapor başlıkları İngilizce kalabilir
3. **Hata mesajları**: Sistem seviyesi hata mesajları Odoo'nun kendi çevirilerine bağlıdır

## 📝 Katkıda Bulunma

Çeviri hatası veya eksiklik bulursanız:
1. `tr.po` dosyasını düzenleyin
2. Test edin
3. Pull request gönderin

## 📞 İletişim

Çeviri konusunda sorularınız için:
- Modül Sorumlusu: Technical Service Team
- E-posta: support@example.com

---

**Son Güncelleme**: Eylül 2024
**Versiyon**: 1.0.0