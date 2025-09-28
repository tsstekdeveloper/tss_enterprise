# Technical Service Management - Setup Guide
## Temel Tanımlar ve Kurulum Kılavuzu

Bu kılavuz, Technical Service modülünün tam fonksiyonel hale gelmesi için yapılması gereken tüm temel tanımları sıralı olarak açıklamaktadır.

---

## 📋 Önkoşullar

1. Odoo 18 kurulu ve çalışıyor olmalı
2. Technical Service modülü yüklenmiş olmalı
3. Admin yetkilerine sahip bir kullanıcı ile giriş yapılmış olmalı

---

## 🚀 Kurulum Adımları (Sıralı)

### ADIM 1: Şirket Bilgilerini Güncelleme
**Menü:** Settings > Companies > Companies

1. Şirket adını güncelleyin
2. Adres bilgilerini girin
3. Logo yükleyin
4. İletişim bilgilerini tamamlayın

**Neden Önemli:** Raporlarda ve bildirimlerde kullanılacak

---

### ADIM 2: Kullanıcı ve Grupları Tanımlama
**Menü:** Settings > Users & Companies > Users

#### 2.1 Kullanıcı Rolleri Oluşturma
Aşağıdaki rolleri tanımlayın:

1. **Service Manager** (Servis Müdürü)
   - Tüm modül yetkilerine sahip
   - Raporları görüntüleme
   - SLA tanımlama
   - Ekip yönetimi

2. **Team Leader** (Takım Lideri)
   - İş emri atama
   - Ekip yönetimi
   - Performans izleme

3. **Technician** (Teknisyen)
   - İş emri görüntüleme/güncelleme
   - Zaman kaydı girişi
   - Malzeme kullanımı

4. **Requester** (Talep Eden)
   - Servis talebi oluşturma
   - Talep durumu görüntüleme

#### 2.2 Her rol için kullanıcı oluşturma
- En az 1 manager
- En az 2 team leader
- En az 4 technician
- En az 2 requester

**Neden Önemli:** İş akışları ve yetkilendirme için gerekli

---

### ADIM 3: Lokasyon Tanımları
**Menü:** Technical Service > Configuration > Campuses & Buildings

#### 3.1 Kampüs Tanımlama
1. **Ana Kampüs**
   - Kod: MAIN
   - Adres bilgileri
   - Yönetici atama

2. **Diğer Lokasyonlar** (varsa)
   - Her lokasyon için kod
   - Adres ve iletişim

#### 3.2 Bina Tanımlama
Her kampüs için:
1. **Ana Bina** (A Blok, B Blok vb.)
   - Kod: A-BLK
   - Kat sayısı
   - Bina yöneticisi

2. **Kat ve Oda Bilgileri**
   - Metin olarak girilecek (1. Kat, 2. Kat vb.)
   - Oda numaraları

**Neden Önemli:** Servis taleplerinin lokasyon bazlı takibi için

---

### ADIM 4: Departman Tanımları
**Menü:** Settings > Users & Companies > Departments

Örnek departmanlar:
1. **Bilgi İşlem**
2. **Teknik İşler**
3. **İnsan Kaynakları**
4. **Üretim**
5. **İdari İşler**

**Neden Önemli:** Talep sahipleri ve teknisyen atamaları için

---

### ADIM 5: Service Teams (Servis Ekipleri) Oluşturma
**Menü:** Technical Service > Configuration > Service Teams

#### 5.1 IT Destek Ekibi
- **Kod:** IT-TEAM
- **Uzmanlık:** IT
- **Vardiya:** Regular (08:00-17:00)
- **Üyeler:** IT teknisyenleri
- **Kampüsler:** Tüm kampüsler

#### 5.2 Teknik Destek Ekibi
- **Kod:** TECH-TEAM
- **Uzmanlık:** Technical
- **Vardiya:** Shifts (3 vardiya)
- **Üyeler:** Teknik teknisyenler
- **Kampüsler:** Ana kampüs

#### 5.3 Genel Destek Ekibi
- **Kod:** GEN-TEAM
- **Uzmanlık:** Mixed
- **Vardiya:** Regular
- **Üyeler:** Çok yönlü teknisyenler

**Neden Önemli:** İş emri atamaları ve yük dengeleme için

---

### ADIM 6: Equipment Categories (Ekipman Kategorileri)
**Menü:** Maintenance > Configuration > Equipment Categories

Örnek kategoriler:
1. **Bilgisayar Ekipmanları**
   - Desktop
   - Laptop
   - Server

2. **Network Ekipmanları**
   - Switch
   - Router
   - Firewall

3. **Üretim Ekipmanları**
   - CNC Makinesi
   - Pres
   - Konveyör

4. **Tesis Ekipmanları**
   - Klima
   - Jeneratör
   - UPS

**Neden Önemli:** Ekipman sınıflandırması ve SLA tanımları için

---

### ADIM 7: SLA Policies (Hizmet Seviyesi Anlaşmaları)
**Menü:** Technical Service > Configuration > SLA Policies

#### 7.1 Standart SLA
- **Ad:** Standard SLA
- **Aktif:** ✓
- **Uygulama:** All Requests
- **İş Saatleri:** 08:00 - 17:00
- **İş Günleri:** Pazartesi-Cuma

**Priority Matrix:**

| Priority | Response Time | Resolution Time |
|----------|--------------|-----------------|
| P1 (Critical) | 30 dakika | 4 saat |
| P2 (High) | 2 saat | 8 saat |
| P3 (Medium) | 4 saat | 24 saat |
| P4 (Low) | 8 saat | 72 saat |

#### 7.2 Premium SLA (VIP Müşteriler için)
- **Ad:** Premium SLA
- **Response/Resolution süreleri %50 daha kısa**

**Escalation Rules:**
- Level 1: %75 süre dolduğunda → Team Leader
- Level 2: %90 süre dolduğunda → Manager
- Level 3: SLA ihlalinde → Director

**Neden Önemli:** Servis kalitesi ve performans takibi için

---

### ADIM 8: Asset/Equipment Tanımlama
**Menü:** Technical Service > Asset Management > Assets/Equipment

En az 10 örnek ekipman tanımlayın:

#### 8.1 IT Ekipmanı Örneği
- **Asset Code:** IT-001
- **Name:** Dell OptiPlex 7090
- **Category:** Desktop
- **Model:** OptiPlex 7090
- **Serial:** ABC123456
- **Location:** Ana Kampüs > A Blok > 2. Kat > Oda 201
- **Assigned Employee:** John Doe
- **Department:** Bilgi İşlem

#### 8.2 Üretim Ekipmanı Örneği
- **Asset Code:** PROD-001
- **Name:** CNC Torna Makinesi
- **Category:** CNC Makinesi
- **Warranty:** Active (2025-12-31'e kadar)
- **Maintenance Team:** Teknik Ekip

**Neden Önemli:** Ekipman bazlı servis takibi için

---

### ADIM 9: Maintenance Contracts (Bakım Sözleşmeleri)
**Menü:** Technical Service > Asset Management > Maintenance Contracts

Örnek sözleşme:
- **Contract Number:** CNT-2024-001
- **Customer:** Ana Firma
- **Type:** AMC (Annual Maintenance Contract)
- **Start Date:** 01/01/2024
- **End Date:** 31/12/2024
- **Value:** 100,000 TL
- **Service Included:** Unlimited
- **Response Time:** 2 saat
- **Coverage:** 24/7

**Covered Equipment:** Kritik ekipmanları ekleyin

**Neden Önemli:** Sözleşmeli müşteri takibi ve faturalandırma

---

### ADIM 10: Request Types ve Categories
**Menü:** Technical Service > Configuration > Settings

Sistem varsayılan olarak şu tipleri içerir:
- Incident
- Service Request
- Problem
- Change Request
- Preventive Maintenance

**Category örnekleri ekleyin:**
- Hardware
- Software
- Network
- Access Request
- Installation

---

### ADIM 11: Notification Templates (Bildirim Şablonları)
**Menü:** Settings > Technical > Email > Email Templates

Oluşturulması gereken şablonlar:

1. **Service Request Created**
   - Talep oluşturulduğunda talep sahibine

2. **Work Order Assigned**
   - İş emri atandığında teknisyene

3. **SLA Warning**
   - SLA süresi yaklaştığında ilgililere

4. **Request Resolved**
   - Talep çözümlendiğinde talep sahibine

**Neden Önemli:** Otomatik bilgilendirmeler için

---

### ADIM 12: Raporlama Görünümleri
**Menü:** Technical Service > Reporting

Test edilmesi gereken raporlar:
1. Service Dashboard
2. Team Performance
3. Asset Analysis
4. SLA Performance

---

## ✅ Kontrol Listesi

Kurulum tamamlandıktan sonra aşağıdaki kontrolleri yapın:

### Temel Tanımlar
- [ ] En az 2 kampüs tanımlandı
- [ ] En az 4 bina tanımlandı
- [ ] En az 5 departman tanımlandı
- [ ] En az 10 kullanıcı oluşturuldu
- [ ] En az 3 servis ekibi oluşturuldu
- [ ] En az 4 ekipman kategorisi tanımlandı
- [ ] En az 1 SLA politikası aktif
- [ ] En az 10 ekipman tanımlandı
- [ ] En az 1 bakım sözleşmesi oluşturuldu

### Fonksiyonel Testler
- [ ] Servis talebi oluşturabiliyorum
- [ ] İş emri oluşturuluyor
- [ ] Teknisyen ataması yapılabiliyor
- [ ] SLA takibi çalışıyor
- [ ] Bildirimler gönderiliyor
- [ ] Raporlar görüntülenebiliyor

---

## 🎯 Test Senaryoları

### Senaryo 1: IT Ekipman Arızası
1. Requester olarak giriş yapın
2. Yeni service request oluşturun:
   - Type: Incident
   - Category: Hardware
   - Priority: High (P2)
   - Description: "Bilgisayar açılmıyor"
3. Talebin otomatik olarak IT ekibine atandığını kontrol edin
4. SLA süresinin hesaplandığını doğrulayın

### Senaryo 2: Yeni Ekipman Kurulumu
1. Service request oluşturun:
   - Type: Service Request
   - Category: Installation
   - Priority: Medium (P3)
2. Work order oluşturulduğunu kontrol edin
3. Teknisyen olarak işe başla/bitir aksiyonlarını test edin

### Senaryo 3: Periyodik Bakım
1. Preventive maintenance talebi oluşturun
2. Bakım checklistini doldurun
3. Kullanılan malzemeleri girin
4. Süre kaydı yapın

---

## 📊 Önerilen KPI'lar

Sistem kullanıma başladıktan sonra takip edilmesi gereken metrikler:

1. **First Response Time** - İlk yanıt süresi
2. **Resolution Time** - Çözüm süresi
3. **SLA Compliance Rate** - SLA uyum oranı
4. **Customer Satisfaction Score** - Müşteri memnuniyeti
5. **Technician Utilization** - Teknisyen kullanım oranı
6. **Repeat Request Rate** - Tekrar eden talep oranı
7. **Preventive vs Corrective Ratio** - Önleyici/Düzeltici bakım oranı

---

## 🆘 Sorun Giderme

### Sorun: Menüler görünmüyor
**Çözüm:** Kullanıcı gruplarını kontrol edin, gerekli yetkileri verin

### Sorun: SLA hesaplanmıyor
**Çözüm:**
1. SLA Policy'nin aktif olduğundan emin olun
2. İş saatleri ve günlerinin doğru tanımlandığını kontrol edin
3. Request type için SLA tanımlı mı kontrol edin

### Sorun: Email bildirimleri gitmiyor
**Çözüm:**
1. Outgoing mail server tanımlı mı kontrol edin
2. Email template'leri kontrol edin
3. User'ların email adresleri tanımlı mı kontrol edin

---

## 📚 Ek Kaynaklar

- **Kullanıcı Kılavuzu:** `/opt/odoo/custom-addons/technical_service/docs/USER_GUIDE.md`
- **Teknik Dokümantasyon:** `/opt/odoo/custom-addons/technical_service/README.md`
- **API Dokümantasyonu:** Hazırlanacak

---

## 📞 Destek

Sorularınız için:
- **Modül Sorumlusu:** Technical Service Team
- **Email:** support@example.com
- **Dokümantasyon:** `/opt/odoo/custom-addons/technical_service/docs/`

---

**Versiyon:** 1.0.0
**Son Güncelleme:** Eylül 2024
**Hazırlayan:** Technical Service Team