# Okul Zil Programı

PyQt5 + SQLite3 ile yazılmış, haftanın 7 gününe ayrı ayrı ders ve teneffüs zamanı tanımlayabilen, tanımlanan saatlerde otomatik zil çalan masaüstü uygulaması.

## Özellikler

- 7 güne (Pazartesi → Pazar) sınırsız sayıda ders / teneffüs aralığı ekleme
- Her aralık için başlangıç saati ve dakika cinsinden süre tanımlama
- Liste üzerinden çift tıklayarak hızlı düzenleme veya silme
- Sistem saati ile senkron çalışan arka-plan thread’i → zamanı geldiğinde otomatik zil
- Sesler: `zil_sesleri/` klasörüne koyduğunuz `ders.wav` ve `teneffus.wav` dosyaları çalınır (dosya yoksa bip sesi)
- Ses klasörünü istediğiniz yere taşıyabilir / değiştirebilirsiniz
- Windows, Linux, macOS (PyQt5 kurulu olduğu sürece) uyumlu

## Gereksinimler

- Python ≥ 3.7
- pip paketleri:
  ```bash
  pip install PyQt5
  ```

## Hızlı Başlangıç

1. Depoyu klonla veya ZIP ile indir:
   ```bash
   git clone https://github.com/ainsoft-tech/ZilProgrami.git
   cd okul-zil-programi
   ```

2. Gerekli kütüphane:
   ```bash
   pip install -r requirements.txt   # sadece PyQt5 satırı var
   ```

3. Ses dosyalarını hazırla (isteğe bağlı):
   ```
   okul-zil-programi/
   ├─ main.py
   ├─ zil_sesleri/
   │  ├─ ders.wav
   │  └─ teneffus.wav
   ```

4. Çalıştır:
   ```bash
   python main.py
   ```

5. Kullanım:
   - Gün seç → Saat & süre gir → **+ Ders** veya **+ Teneffüs** ile kaydet
   - Listedeki kaydı çift tıkla → düzenle → **Güncelle**
   - **Seçileni Sil** ile kaldır
   - Program açık kaldığı sürece tanımlı saatlerde otomatik zil çalar

## Klasör Yapısı

```
okul-zil-programi/
├─ main.py              # tek dosya, tüm uygulama
├─ zil_programi.db      # otomatik oluşur (SQLite)
├─ zil_sesleri/         # seslerin konduğu klasör
│  ├─ ders.wav
│  └─ teneffus.wav
└─ requirements.txt     # PyQt5
```

## Ses Dosyaları

Kullanıcı kendi ses dosyalarını yüklemelidir.

## Veritabanı

- Tek tablo: `zil`
- Kolonlar:
  - `id`       : PRIMARY KEY
  - `gun`      : 0 (Pazartesi) … 6 (Pazar)
  - `tur`      : 'DERS' | 'TENEFFUS'
  - `bas_saat` : 'HH:MM'
  - `sure`     : dakika (int)

## İpuçları

- Aynı gün içinde saatler çakışırsa **ilk eşleşme** çalır
- Zil sesini değiştirmek: yeni `.wav`ları `zil_sesleri/` içine koyun ve programı yeniden başlatın
- Çoklu kullanıcı: veritabanı dosyasını paylaşabilirsiniz (aynı ağ yolu)
- Otomatik başlatma: `main.py` yolunu işletim sistemi başlangıç programlarına ekleyin

## Lisans

MIT – her türlü kullanım, dağıtım ve değiştirme serbesttir.

## Katkı

- Hata bildirimi: **Issues** sekmesi
- Geliştirme: **Fork** → pull request gönderin
