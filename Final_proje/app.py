from flask import jsonify
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import statistics

# Uygulama ve veritabanı yapılandırması
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ogrencibilgisistemi2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///okul.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Veritabanı modelleri
class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(80), unique=True, nullable=False)
    parola_hash = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'ogrenci', 'ogretmen', 'yonetici'
    
    def parola_ayarla(self, parola):
        self.parola_hash = generate_password_hash(parola)
    
    def parola_kontrol(self, parola):
        return check_password_hash(self.parola_hash, parola)

class Ogrenci(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    yas = db.Column(db.Integer)
    sinif = db.Column(db.String(10))
    telefon = db.Column(db.String(15))
    email = db.Column(db.String(100))
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'))
    
    notlar = db.relationship('Not', backref='ogrenci', lazy=True)

class Ders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    ogretmen_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'))
    
    notlar = db.relationship('Not', backref='ders', lazy=True)
    
    @property
    def not_ortalamasi(self):
        tum_notlar = [not_.deger for not_ in self.notlar]
        if tum_notlar:
            return sum(tum_notlar) / len(tum_notlar)
        return 0

class Not(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ogrenci_id = db.Column(db.Integer, db.ForeignKey('ogrenci.id'), nullable=False)
    ders_id = db.Column(db.Integer, db.ForeignKey('ders.id'), nullable=False)
    deger = db.Column(db.Float, nullable=False)
    aciklama = db.Column(db.String(200))

# Veritabanı oluşturma ve örnek veriler
def veritabani_olustur():
    with app.app_context():
        db.create_all()
        
        # Eğer veritabanı boşsa örnek veriler ekle
        if not Kullanici.query.first():
            # Örnek kullanıcılar
            admin = Kullanici(kullanici_adi='admin')
            admin.parola_ayarla('admin123')
            admin.rol = 'yonetici'
            
            ogretmen = Kullanici(kullanici_adi='ogretmen')
            ogretmen.parola_ayarla('ogretmen123')
            ogretmen.rol = 'ogretmen'
            
            ogrenci = Kullanici(kullanici_adi='ogrenci')
            ogrenci.parola_ayarla('ogrenci123')
            ogrenci.rol = 'ogrenci'
            
            db.session.add_all([admin, ogretmen, ogrenci])
            db.session.commit()
            
            # Örnek öğrenci
            ornek_ogrenci = Ogrenci(
                ad='Ali', 
                soyad='Yılmaz', 
                yas=15, 
                sinif='9-A', 
                telefon='555-123-4567', 
                email='ali.yilmaz@okul.com',
                kullanici_id=ogrenci.id
            )
            
            db.session.add(ornek_ogrenci)
            db.session.commit()
            
            # Örnek dersler
            matematik = Ders(ad='Matematik', ogretmen_id=ogretmen.id)
            fizik = Ders(ad='Fizik', ogretmen_id=ogretmen.id)
            
            db.session.add_all([matematik, fizik])
            db.session.commit()
            
            # Örnek notlar
            not1 = Not(ogrenci_id=ornek_ogrenci.id, ders_id=matematik.id, deger=85, aciklama='1. Sınav')
            not2 = Not(ogrenci_id=ornek_ogrenci.id, ders_id=fizik.id, deger=90, aciklama='1. Sınav')
            
            db.session.add_all([not1, not2])
            db.session.commit()

# Güvenlik dekotarörü - yetki kontrolü
def login_required(roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'kullanici_id' not in session:
                flash('Bu sayfaya erişmek için giriş yapmalısınız', 'danger')
                return redirect(url_for('giris'))
            
            if roles and session['rol'] not in roles:
                flash('Bu sayfaya erişim yetkiniz yok', 'danger')
                return redirect(url_for('anasayfa'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rotalar ve görünümler
@app.route('/')
def anasayfa():
    if 'kullanici_id' in session:
        return render_template('anasayfa.html', rol=session.get('rol'))
    return redirect(url_for('giris'))

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        kullanici_adi = request.form.get('kullanici_adi')
        parola = request.form.get('parola')
        
        kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
        
        if kullanici and kullanici.parola_kontrol(parola):
            session['kullanici_id'] = kullanici.id
            session['kullanici_adi'] = kullanici.kullanici_adi
            session['rol'] = kullanici.rol
            flash(f'Hoş geldiniz, {kullanici.kullanici_adi}!', 'success')
            return redirect(url_for('anasayfa'))
        
        flash('Kullanıcı adı veya parola hatalı', 'danger')
    
    return render_template('giris.html')

@app.route('/cikis')
def cikis():
    session.clear()
    flash('Başarıyla çıkış yaptınız', 'success')
    return redirect(url_for('giris'))

# Öğrenci İşlemleri
@app.route('/ogrenciler')
@login_required(roles=['yonetici', 'ogretmen'])
def ogrenciler():
    ogrenciler = Ogrenci.query.all()
    return render_template('ogrenciler.html', ogrenciler=ogrenciler)

@app.route('/ogrenci/ekle', methods=['GET', 'POST'])
@login_required(roles=['yonetici'])
def ogrenci_ekle():
    if request.method == 'POST':
        ad = request.form.get('ad')
        soyad = request.form.get('soyad')
        yas = request.form.get('yas')
        sinif = request.form.get('sinif')
        telefon = request.form.get('telefon')
        email = request.form.get('email')
        kullanici_adi = request.form.get('kullanici_adi')
        parola = request.form.get('parola')
        
        # Kullanıcı oluştur
        yeni_kullanici = Kullanici(kullanici_adi=kullanici_adi, rol='ogrenci')
        yeni_kullanici.parola_ayarla(parola)
        db.session.add(yeni_kullanici)
        db.session.commit()
        
        # Öğrenci oluştur
        yeni_ogrenci = Ogrenci(
            ad=ad,
            soyad=soyad,
            yas=yas,
            sinif=sinif,
            telefon=telefon,
            email=email,
            kullanici_id=yeni_kullanici.id
        )
        
        db.session.add(yeni_ogrenci)
        db.session.commit()
        
        flash('Öğrenci başarıyla eklendi', 'success')
        return redirect(url_for('ogrenciler'))
    
    return render_template('ogrenci_ekle.html')

@app.route('/ogrenci/duzenle/<int:id>', methods=['GET', 'POST'])
@login_required(roles=['yonetici'])
def ogrenci_duzenle(id):
    ogrenci = Ogrenci.query.get_or_404(id)
    
    if request.method == 'POST':
        ogrenci.ad = request.form.get('ad')
        ogrenci.soyad = request.form.get('soyad')
        ogrenci.yas = request.form.get('yas')
        ogrenci.sinif = request.form.get('sinif')
        ogrenci.telefon = request.form.get('telefon')
        ogrenci.email = request.form.get('email')
        
        db.session.commit()
        flash('Öğrenci bilgileri güncellendi', 'success')
        return redirect(url_for('ogrenciler'))
    
    return render_template('ogrenci_duzenle.html', ogrenci=ogrenci)

@app.route('/ogrenci/sil/<int:id>')
@login_required(roles=['yonetici'])
def ogrenci_sil(id):
    ogrenci = Ogrenci.query.get_or_404(id)
    kullanici = Kullanici.query.get(ogrenci.kullanici_id)
    
    # İlişkili notları sil
    Not.query.filter_by(ogrenci_id=id).delete()
    
    # Öğrenciyi sil
    db.session.delete(ogrenci)
    
    # İlişkili kullanıcıyı sil
    if kullanici:
        db.session.delete(kullanici)
    
    db.session.commit()
    flash('Öğrenci kaydı silindi', 'success')
    return redirect(url_for('ogrenciler'))

# Ders İşlemleri
@app.route('/dersler')
@login_required(roles=['yonetici', 'ogretmen'])
def dersler():
    dersler = Ders.query.all()
    return render_template('dersler.html', dersler=dersler)

@app.route('/ders/ekle', methods=['GET', 'POST'])
@login_required(roles=['yonetici'])
def ders_ekle():
    if request.method == 'POST':
        ad = request.form.get('ad')
        ogretmen_id = request.form.get('ogretmen_id')
        
        yeni_ders = Ders(ad=ad, ogretmen_id=ogretmen_id)
        db.session.add(yeni_ders)
        db.session.commit()
        
        flash('Ders başarıyla eklendi', 'success')
        return redirect(url_for('dersler'))
    
    ogretmenler = Kullanici.query.filter_by(rol='ogretmen').all()
    return render_template('ders_ekle.html', ogretmenler=ogretmenler)

@app.route('/ders/duzenle/<int:id>', methods=['GET', 'POST'])
@login_required(roles=['yonetici'])
def ders_duzenle(id):
    ders = Ders.query.get_or_404(id)
    
    if request.method == 'POST':
        ders.ad = request.form.get('ad')
        ders.ogretmen_id = request.form.get('ogretmen_id')
        
        db.session.commit()
        flash('Ders bilgileri güncellendi', 'success')
        return redirect(url_for('dersler'))
    
    ogretmenler = Kullanici.query.filter_by(rol='ogretmen').all()
    return render_template('ders_duzenle.html', ders=ders, ogretmenler=ogretmenler)

@app.route('/ders/sil/<int:id>')
@login_required(roles=['yonetici'])
def ders_sil(id):
    ders = Ders.query.get_or_404(id)
    
    # İlişkili notları sil
    Not.query.filter_by(ders_id=id).delete()
    
    # Dersi sil
    db.session.delete(ders)
    db.session.commit()
    
    flash('Ders kaydı silindi', 'success')
    return redirect(url_for('dersler'))

# Not İşlemleri
@app.route('/notlar')
@login_required(roles=['yonetici', 'ogretmen', 'ogrenci'])
def notlar():
    if session['rol'] == 'ogrenci':
        ogrenci = Ogrenci.query.filter_by(kullanici_id=session['kullanici_id']).first()
        if ogrenci:
            notlar = Not.query.filter_by(ogrenci_id=ogrenci.id).all()
            return render_template('notlar.html', notlar=notlar, rol=session['rol'])
    else:
        notlar = Not.query.all()
        return render_template('notlar.html', notlar=notlar, rol=session['rol'])
    
    return redirect(url_for('anasayfa'))

@app.route('/not/ekle', methods=['GET', 'POST'])
@login_required(roles=['yonetici', 'ogretmen'])
def not_ekle():
    if request.method == 'POST':
        ogrenci_id = request.form.get('ogrenci_id')
        ders_id = request.form.get('ders_id')
        deger = request.form.get('deger')
        aciklama = request.form.get('aciklama')
        
        yeni_not = Not(
            ogrenci_id=ogrenci_id,
            ders_id=ders_id,
            deger=float(deger),
            aciklama=aciklama
        )
        
        db.session.add(yeni_not)
        db.session.commit()
        
        flash('Not başarıyla eklendi', 'success')
        return redirect(url_for('notlar'))
    
    ogrenciler = Ogrenci.query.all()
    dersler = Ders.query.all()
    return render_template('not_ekle.html', ogrenciler=ogrenciler, dersler=dersler)

@app.route('/not/duzenle/<int:id>', methods=['GET', 'POST'])
@login_required(roles=['yonetici', 'ogretmen'])
def not_duzenle(id):
    not_kaydi = Not.query.get_or_404(id)
    
    if request.method == 'POST':
        not_kaydi.ogrenci_id = request.form.get('ogrenci_id')
        not_kaydi.ders_id = request.form.get('ders_id')
        not_kaydi.deger = float(request.form.get('deger'))
        not_kaydi.aciklama = request.form.get('aciklama')
        
        db.session.commit()
        flash('Not bilgileri güncellendi', 'success')
        return redirect(url_for('notlar'))
    
    ogrenciler = Ogrenci.query.all()
    dersler = Ders.query.all()
    return render_template('not_duzenle.html', not_kaydi=not_kaydi, ogrenciler=ogrenciler, dersler=dersler)

@app.route('/not/sil/<int:id>')
@login_required(roles=['yonetici', 'ogretmen'])
def not_sil(id):
    not_kaydi = Not.query.get_or_404(id)
    db.session.delete(not_kaydi)
    db.session.commit()
    
    flash('Not kaydı silindi', 'success')
    return redirect(url_for('notlar'))

# İstatistikler ve Raporlama
@app.route('/istatistikler')
@login_required(roles=['yonetici', 'ogretmen'])
def istatistikler():
    # Öğrenci bazında not ortalamaları
    ogrenciler = Ogrenci.query.all()
    ogrenci_ortalamalar = []
    
    for ogrenci in ogrenciler:
        notlar = [not_.deger for not_ in ogrenci.notlar]
        if notlar:
            ortalama = sum(notlar) / len(notlar)
            ogrenci_ortalamalar.append({
                'ad': f"{ogrenci.ad} {ogrenci.soyad}",
                'ortalama': round(ortalama, 2)
            })
    
    # Ders bazında not ortalamaları
    dersler = Ders.query.all()
    ders_ortalamalar = []
    
    for ders in dersler:
        notlar = [not_.deger for not_ in ders.notlar]
        if notlar:
            ortalama = sum(notlar) / len(notlar)
            ders_ortalamalar.append({
                'ad': ders.ad,
                'ortalama': round(ortalama, 2)
            })
    
    return render_template('istatistikler.html', 
                           ogrenci_ortalamalar=ogrenci_ortalamalar,
                           ders_ortalamalar=ders_ortalamalar)

# Profil sayfası
@app.route('/profil')
@login_required()
def profil():
    kullanici = Kullanici.query.get(session['kullanici_id'])
    
    if kullanici.rol == 'ogrenci':
        ogrenci = Ogrenci.query.filter_by(kullanici_id=kullanici.id).first()
        return render_template('profil.html', kullanici=kullanici, ogrenci=ogrenci)
    
    return render_template('profil.html', kullanici=kullanici)

# Uygulama başlangıcı
if __name__ == '__main__':
    if not os.path.exists('instance'):
        os.makedirs('instance')
    veritabani_olustur()
    app.run(debug=True, host='0.0.0.0', port=5000)

# ... mevcut kodun sonundaki route'ların hemen altında ekle

from flask import jsonify

@app.route('/api/ogrenciler')
@login_required(roles=['yonetici', 'ogretmen'])
def api_ogrenciler():
    ogrenciler = Ogrenci.query.all()
    data = []
    for o in ogrenciler:
        data.append({
            'id': o.id,
            'ad': o.ad,
            'soyad': o.soyad,
            'yas': o.yas,
            'sinif': o.sinif,
            'telefon': o.telefon,
            'email': o.email,
            'kullanici_id': o.kullanici_id
        })
    return jsonify(data)

@app.route('/api/dersler')
@login_required(roles=['yonetici', 'ogretmen'])
def api_dersler():
    dersler = Ders.query.all()
    data = []
    for d in dersler:
        data.append({
            'id': d.id,
            'ad': d.ad,
            'ogretmen_id': d.ogretmen_id,
            'not_ortalamasi': d.not_ortalamasi
        })
    return jsonify(data)

@app.route('/api/notlar')
@login_required(roles=['yonetici', 'ogretmen', 'ogrenci'])
def api_notlar():
    if session['rol'] == 'ogrenci':
        ogrenci = Ogrenci.query.filter_by(kullanici_id=session['kullanici_id']).first()
        if ogrenci:
            notlar = Not.query.filter_by(ogrenci_id=ogrenci.id).all()
        else:
            notlar = []
    else:
        notlar = Not.query.all()

    data = []
    for n in notlar:
        data.append({
            'id': n.id,
            'ogrenci_id': n.ogrenci_id,
            'ders_id': n.ders_id,
            'deger': n.deger,
            'aciklama': n.aciklama
        })
    return jsonify(data)


# if __name__ == '__main__' bloğu burada devam eder
if __name__ == '__main__':
    if not os.path.exists('instance'):
        os.makedirs('instance')
    veritabani_olustur()
    app.run(debug=True, host='0.0.0.0', port=5000)
