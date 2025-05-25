
---

# 📌 Öğrenci Bilgi Sistemi

> Bu proje, öğrenci kayıt, ders bilgileri ve not takibinin yapılabildiği kapsamlı bir öğrenci bilgi yönetim sistemidir.

---

## 🧾 Proje Tanıtımı

Öğrenci Bilgi Sistemi, okullarda öğrenci ve ders bilgilerini yönetmek için geliştirilmiş bir web uygulamasıdır.
Flask framework kullanılarak hazırlanmış olup, öğrenci kayıtları oluşturma, ders atama, not girme ve raporlama gibi işlevleri içerir.
Kullanıcı dostu arayüzü sayesinde eğitim kurumlarının veri takibini kolaylaştırır.

---

## 🚀 Proje Özellikleri

* 🔐 Öğrenci ve öğretmen kullanıcı yönetimi (kayıt, giriş)
* 🎓 Öğrenci bilgileri ekleme, düzenleme, silme
* 📚 Ders ve sınıf tanımlamaları yapabilme
* 📝 Öğrencilerin derslere kayıt edilmesi ve not girilmesi
* 📊 Notlar üzerinden öğrenci başarı durumunun raporlanması
* 🔎 Öğrenci ve ders arama, filtreleme özellikleri
* 💾 Veritabanı ile kalıcı veri saklama

---

## ⚙️ Kurulum ve Çalıştırma

### ✅ Gereksinimler

Bu projeyi çalıştırmak için bilgisayarınızda aşağıdaki yazılımlar kurulu olmalıdır:

* Python 3.x
* pip paket yöneticisi

Ayrıca aşağıdaki Python kütüphaneleri kullanılmaktadır:

* flask
* flask\_sqlalchemy
* flask\_wtf
* wtforms

> Not: Bu kütüphaneleri `requirements.txt` dosyasından aşağıdaki komutla otomatik olarak yükleyebilirsiniz:

```bash
pip install -r requirements.txt
```

### 🚀 Uygulamayı Başlatma

Proje dizininde terminal açarak aşağıdaki komutu çalıştırın:

```bash
python app.py
```

Uygulama varsayılan olarak tarayıcınızda [http://127.0.0.1:5000/](http://127.0.0.1:5000/) adresinde çalışacaktır.

---
📦ogrenci_bilgi_sistemi/
├── app.py                            # Ana Flask uygulama dosyası
├── instance/
│   └── okul.db                       # SQLite veritabanı dosyası
├── static/
│   ├── css/
│   │   └── style.css                 # Stil dosyaları
│   └── js/                           # (Varsa) JavaScript dosyaları
├── templates/
│   ├── base.html                     # Tüm sayfalar için temel şablon
│   ├── giris.html                    # Login sayfası
│   ├── anasayfa.html                 # Kullanıcı paneli / dashboard
│   ├── profil.html
│   ├── dersler.html
│   ├── ders_ekle.html
│   ├── ders_duzenle.html
│   ├── ogrenciler.html
│   ├── ogrenci_ekle.html
│   ├── ogrenci_duzenle.html
│   ├── notlar.html
│   ├── not_ekle.html
│   ├── not_duzenle.html
│   └── istatistikler.html
├── veritabani.json                   # (İsteğe bağlı) veri yedeği veya yapılandırması
├── requirements.txt                  # Gerekli pip paketleri (Flask vs.)
└── README.md                         # Proje açıklaması



```

---
