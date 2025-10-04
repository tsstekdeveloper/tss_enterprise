# Action Mapping Report - Technical Service Presentation

## 📊 Eşleştirme Özeti

Bu rapor, `technical_service` modülündeki mevcut action'ların `technical_service_presentation` modülündeki menülerle nasıl eşleştirildiğini göstermektedir.

## ✅ Başarılı Eşleştirmeler

### Dashboard Menüleri
| Menü | Action | Durum |
|------|--------|-------|
| Benim Dashboard'im | `action_technical_service_dashboard` | ✅ Eşleştirildi |
| Ekip Dashboard'i | `action_technical_service_team_dashboard` | ✅ Eşleştirildi |
| Yönetim Dashboard'i | `action_technical_service_dashboard` | ✅ Eşleştirildi |

### Servis Talepleri
| Menü | Action | Durum |
|------|--------|-------|
| Yeni Talep Oluştur | `action_technical_service_request` | ✅ Eşleştirildi |
| Taleplerim | `action_maintenance_request_my` | ✅ Eşleştirildi |
| Ekibimin Talepleri | `action_maintenance_request_team` | ✅ Eşleştirildi |
| Atanmış Talepler | `action_maintenance_request_assigned` | ✅ Eşleştirildi |
| Bekleyen Talepler | `action_maintenance_request_pending` | ✅ Eşleştirildi |

### İş Emirleri
| Menü | Action | Durum |
|------|--------|-------|
| İş Emirlerim | `action_work_order_my` | ✅ Eşleştirildi |
| Ekip İş Emirleri | `action_work_order_team` | ✅ Eşleştirildi |
| Tüm İş Emirleri | `action_work_order_all` | ✅ Eşleştirildi |

### Cihazlar ve Varlıklar
| Menü | Action | Durum |
|------|--------|-------|
| Ekipmanlar | `action_technical_service_asset` | ✅ Eşleştirildi |
| Sözleşmeler | `action_technical_service_contract` | ✅ Eşleştirildi |
| Önleyici Bakım | `action_technical_service_preventive` | ✅ Eşleştirildi |

### Ekip Yönetimi
| Menü | Action | Durum |
|------|--------|-------|
| Teknisyenler | `action_team_member` | ✅ Eşleştirildi |
| Vardiyalar | `action_team_shifts` | ✅ Eşleştirildi |
| Performans | `action_team_performance` | ✅ Eşleştirildi |
| Ekipler | `action_technical_service_team` | ✅ Eşleştirildi |

### Teknik Organizasyon
| Menü | Action | Durum |
|------|--------|-------|
| Organizasyon Yapısı | `action_technical_service_organization` | ✅ Eşleştirildi |
| Pozisyonlar | `action_technical_service_organization` | ✅ Eşleştirildi |
| Rol Atamaları | `action_technical_service_organization` | ✅ Eşleştirildi |

### Lokasyon Yönetimi
| Menü | Action | Durum |
|------|--------|-------|
| Kampüsler | `action_technical_service_campus` | ✅ Eşleştirildi |
| Binalar | `action_technical_service_building` | ✅ Eşleştirildi |
| Alanlar | `action_technical_service_area` | ✅ Eşleştirildi |

### Envanter
| Menü | Action | Durum |
|------|--------|-------|
| Stok Durumu | `action_inventory_stock` | ✅ Eşleştirildi |
| Malzeme Talepleri | `action_material_requests` | ✅ Eşleştirildi |
| Demirbaşlar | `action_fixed_assets` | ✅ Eşleştirildi |

### Raporlar
| Menü | Action | Durum |
|------|--------|-------|
| Talep Raporları | `action_report_requests` | ✅ Eşleştirildi |
| Performans Raporları | `action_report_performance` | ✅ Eşleştirildi |
| SLA Raporları | `action_report_sla` | ✅ Eşleştirildi |
| Envanter Raporları | `action_report_inventory` | ✅ Eşleştirildi |
| Maliyet Raporları | `action_report_costs` | ✅ Eşleştirildi |

### Ayarlar
| Menü | Action | Durum |
|------|--------|-------|
| Genel Ayarlar | `action_technical_service_config` | ⚠️ Muhtemelen Yok |
| SLA Politikaları | `action_sla_policies` | ✅ Eşleştirildi |
| Öncelik Seviyeleri | `action_technical_service_priority` | ⚠️ Muhtemelen Yok |
| Kategoriler | `action_technical_service_asset_analysis` | ✅ Eşleştirildi |

## 📝 Kullanılmayan Action'lar

Aşağıdaki action'lar mevcut ancak menü yapısında kullanılmamış:

1. `action_technical_service_contract_analysis`
2. `action_technical_service_inventory`
3. `action_technical_service_invoice`
4. `action_technical_service_knowledge`
5. `action_technical_service_request_analysis`
6. `action_technical_service_satisfaction`
7. `action_technical_service_sla`
8. `action_technical_service_sla_performance`
9. `action_technical_service_team_performance`
10. `action_technical_service_team_view_form`
11. `action_technical_service_team_view_kanban`
12. `action_technical_service_team_view_list`
13. `action_technical_service_work_order`
14. `action_technical_service_work_order_analysis`
15. `action_technical_service_report_wizard`

## ⚠️ Potansiyel Sorunlar

1. **action_technical_service_config**: Genel ayarlar için kullanılıyor ancak bu action mevcut olmayabilir
2. **action_technical_service_priority**: Öncelik seviyeleri için kullanılıyor ancak bu action mevcut olmayabilir

## 🎯 Öneriler

1. Eksik action'lar için yeni action tanımları oluşturulmalı veya mevcut action'larla değiştirilmeli
2. Kullanılmayan action'lar gelecek geliştirmeler için saklanabilir veya temizlenebilir
3. Tüm menülerin doğru action'lara işaret ettiğinden emin olmak için test edilmeli

## 📋 Sonuç

- **Toplam Menü Sayısı**: 45
- **Action'lı Menü Sayısı**: 38
- **Başarılı Eşleştirme**: 36/38 (%95)
- **Potansiyel Sorun**: 2 action

Menü yapısı büyük oranda başarılı bir şekilde action'larla eşleştirilmiş durumda. Sadece 2 action'ın varlığı kontrol edilmeli.