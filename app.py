import uuid
import locale
from datetime import timedelta, datetime
import hashlib
import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, json, jsonify, request, send_file, url_for, render_template
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, create_access_token, decode_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from pymongo import MongoClient
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

import suket_kematian as sk
import suket_penghasilan as sp
import suket_tidak_mampu as stm
import suket_domisili as sd
import suket_pindah_wilayah as spw
import suket_tanggungan as stk
import suket_orang_yang_sama as soys
import gear as gear

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER_1 = 'static/prfl/'
UPLOAD_FOLDER_2 = 'static/gnkk/'
if not os.path.exists(UPLOAD_FOLDER_1):
    os.makedirs(UPLOAD_FOLDER_1)
if not os.path.exists(UPLOAD_FOLDER_2):
    os.makedirs(UPLOAD_FOLDER_2)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

app.config['JWT_SECRET_KEY'] = 'SAMS'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(weeks=260)
app.config['UPLOAD_FOLDER_1'] = UPLOAD_FOLDER_1
app.config['UPLOAD_FOLDER_2'] = UPLOAD_FOLDER_2
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

FCM_SERVER_KEY = "YOUR_FCM_SERVER_KEY"
FCM_URL = "https://fcm.googleapis.com/fcm/send"
TOKENS_FILE = "tokens.json"

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

mail = Mail(app)
jwt = JWTManager(app)
limiter = Limiter(get_remote_address, app=app)

try:
    MONGODB_URI = os.environ.get("MONGODB_URI")
    DB_NAME = os.environ.get("DB_NAME")
    mongo = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=1000)
    db = mongo[DB_NAME]
    mongo.server_info()
    print("Koneksi berhasil ke MongoDB Atlas")
except Exception as e:
    print("ERROR - Tidak dapat terhubung ke MongoDB Atlas:", str(e))

def serialize_mongo_data(data):
    if data:
        data['_id'] = str(data['_id'])
    return data

@app.errorhandler(RequestEntityTooLarge)
def handle_file_size_error(e):
    return jsonify(status= 'error',message = 'Ukuran file maksimal hanya 2MB.')

@app.route("/")
def index():
    return "yeah"

# UNDER CONSTRUCTION ===========================
def generate_short_token():
    while True:
        short_token = str(uuid.uuid4())[:8]
        existing_token = db.tokens.find_one({'short_token': short_token})
        if not existing_token:
            return short_token
        
# Load token dari file (simulasi database)
def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, 'r') as file:
        return json.load(file)

# Simpan token ke file
def save_tokens(tokens):
    with open(TOKENS_FILE, 'w') as file:
        json.dump(tokens, file)

@app.route('/save-token', methods=['POST'])
def save_token():
    data = request.form or request.json
    user_id = data.get('userId')
    token = data.get('token')

    if not user_id or not token:
        return jsonify({'message': 'userId dan token wajib'}), 400

    tokens = load_tokens()
    tokens[user_id] = token
    save_tokens(tokens)

    return jsonify({'message': 'Token disimpan'}), 200

@app.route('/send-notification', methods=['POST'])
def send_notification():
    data = request.json
    user_id = data.get('userId')
    title = data.get('title')
    body = data.get('body')

    tokens = load_tokens()
    token = tokens.get(user_id)

    if not token:
        return jsonify({'message': 'Token tidak ditemukan untuk userId ini'}), 404

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'key={FCM_SERVER_KEY}',
    }

    payload = {
        "to": token,
        "notification": {
            "title": title or "Notifikasi Baru",
            "body": body or "Ada informasi baru",
        },
        "priority": "high"
    }

    response = request.post(FCM_URL, headers=headers, json=payload)

    return jsonify({
        'message': 'Notifikasi dikirim',
        'status': response.status_code,
        'response': response.json()
    })
# UNDER CONSTRUCTION ===========================


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    try:
        user = db.users.find_one({'email': email})
        if not user:
            return jsonify(message='Email tidak terdaftar!', status="gagal")
        
        reset_token = create_access_token(identity={'noKK': user['noKK']}, expires_delta=timedelta(minutes=5))
        short_token = generate_short_token()
        locale.setlocale(locale.LC_TIME, 'id_ID.utf8')
        db.tokens.insert_one({
            'short_token': short_token,
            'full_token': reset_token,
            'akun' : user['noKK'],
            'waktu' : datetime.now().strftime('%d %B %Y, %H:%M'),
            'status': "Belum diubah",
            'lokasi':""
        })
        reset_link = url_for('reset_password', token=short_token, _external=True)
        msg = Message(
            '🔒 Atur Ulang Kata Sandi - Lurahku',
            sender='salman21ti@mahasiswa.pcr.ac.id',
            recipients=[email]
        )
        
        msg.body = f"""
            Halo Warga,

            Kami menerima permintaan untuk mengatur ulang kata sandi akun Anda.  
            Silakan klik tautan di bawah ini untuk melanjutkan proses reset kata sandi:

            {reset_link}

            ⚠️ *Tautan ini hanya berlaku selama 5 menit.* Jika Anda tidak meminta reset kata sandi, abaikan email ini.

            Salam,  
            Tim Dukungan Lurahku
        """

        msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .container {{
                        font-family: Arial, sans-serif;
                        max-width: 600px;
                        margin: auto;
                        padding: 20px;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                    }}
                    .btn {{
                        display: inline-block;
                        padding: 10px 20px;
                        color: #fff;
                        background-color: #007bff;
                        text-decoration: none;
                        border-radius: 5px;
                    }}
                    .footer {{
                        font-size: 12px;
                        color: #666;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>🔒 Atur Ulang Kata Sandi</h2>
                    <p>Halo <strong>Warga!</strong></p>
                    <p>Kami menerima permintaan untuk mengatur ulang kata sandi akun Anda. Klik tombol di bawah ini untuk melanjutkan:</p>
                    <p><a href="{reset_link}" class="btn"><span style="color:#fff">Atur Ulang Kata Sandi<span></a></p>
                    <p><small>Jika tombol tidak berfungsi, Anda juga dapat mengklik tautan berikut:</small></p>
                    <p><a href="{reset_link}">{reset_link}</a></p>
                    <p><strong>⚠️ Tautan ini hanya berlaku selama 5 menit.</strong></p>
                    <hr>
                    <p class="footer">Jika Anda tidak meminta pengaturan ulang kata sandi, abaikan email ini. Hubungi kami jika Anda memerlukan bantuan lebih lanjut.</p>
                    <p class="footer">Salam, <br>Developer Team Lurahku</p>
                </div>
            </body>
            </html>
        """

        mail.send(msg)
        return jsonify(message='Email atur ulang kata sandi telah dikirim!', status="sukses"), 200
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify(message='Terjadi kesalahan, silakan coba lagi.', status="gagal")


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == "POST":
        try:
            token_entry = db.tokens.find_one({'short_token': token})
            if not token_entry:
                return jsonify({'message': 'Token tidak valid atau telah kedaluwarsa'}), 400
            full_token = token_entry['full_token']
            current_user = decode_token(full_token)  
            user_id = current_user['sub']['noKK']  
            new_password = request.json.get('password')
            latlong = request.json.get('latlong')
            if not new_password:
                return jsonify({'message': 'Password tidak boleh kosong!'}), 400

            hashed_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
            db.users.update_one({'noKK': user_id}, {'$set': {'password': hashed_password}})
            db.tokens.update_one({'short_token': token}, {'$set': {'status': "Telah diubah", 'lokasi': latlong}})

            return jsonify({'message': 'Password berhasil direset!'}), 200
        except Exception as e:
            return jsonify({'message': 'Terjadi kesalahan', 'error': str(e)}), 400

    return render_template('reset_password.html', token=token)

@app.route("/login", methods=['POST'])
def login():
    noKK = request.form.get("noKK")
    password = request.form.get("password")
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    user = db.users.find_one({"noKK": noKK})
    uId = user['uId']
    if user['password'] != pw_hash:
        return jsonify(massege="Nomor KK atau password salah", status="gagal"), 401
    else :
        jabatan = user['jabatan']
        access_token = create_access_token(identity={'uId' : uId, 'jabatan' : jabatan})
        return jsonify(access_token=access_token, status="sukses", jabatan=jabatan), 200

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"] 
    db.blacklist.insert_one({"jti": jti})
    return jsonify({"msg": "Logout berhasil"}), 200

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_blacklist = db.blacklist.find_one({"jti": jti})
    return token_in_blacklist is not None

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token ini sudah tidak valid (logged out)."}), 401

#POST
@app.route("/post_users", methods=['POST'])
@limiter.limit("20 per minute")
def post_users():
    last_user = db.users.find_one(sort=[("uId", -1)])
    last_permit = db.permitted.find_one(sort=[("uId", -1)])
    
    new_permit = last_permit['pId'] + 1 if last_permit else 1
    new_uId = last_user['uId'] + 1 if last_user else 1

    email = request.form.get('email')
    noKK = request.form.get('noKK')
    password = request.form.get('password')
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    gambar_kk = ""
    poto_profil = "static/image/default-person.jpg"
    jabatan = request.form.get('jabatan')
    alamat = ""
    noHp = ""
    rt = "-"
    rw = "-"
    checkNoKK = db.users.find_one({'noKK' : noKK})
    checkEamil = db.users.find_one({'email' : email})
    if checkEamil : 
        return jsonify({'status' : 'gagal', 'message' : 'Email telah terdaftar'})
    if checkNoKK : 
        return jsonify({'status' : 'gagal', 'message' : 'Nomor KK telah terdaftar'})
    else :
      data = {
          "uId": new_uId,
          "email": email,
          "noKK": noKK,
          "password": password_hash,
          "gambar_kk": gambar_kk,
          "poto_profil": poto_profil,
          "jabatan": jabatan,
          "alamat": alamat,
          "noHp": noHp,
          "rt": rt,
          "rw": rw
      }
      permit = {
        "pId" : new_permit,
        "uId" : new_uId,
        "status" : "Menunggu"
      }
      db.users.insert_one(data)
      db.permitted.insert_one(permit)
      return jsonify({'status': 'sukses', 'message' : 'Akun berhasil didaftarkan'})

@app.route("/post_rekom", methods=['POST'])
@jwt_required()
def post_rekom():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    last_user = db.rekom.find_one(sort=[("rekomId", -1)])
    if last_user: new_rekomId = last_user['rekomId'] + 1
    else: new_rekomId = 1

    kepala_keluarga = db.warga.find_one({"uId" : uId, "peran" : "Kepala Keluarga"})
    if kepala_keluarga: 
        rw = request.form.get('rw')
        rt = request.form.get('rt')
        newData = {
            "uId" : uId,
            "rt" : rt,
            "rw" : rw,
            "status" : "menunggu",
            "rekomId" : new_rekomId,
        }
        user = db.rekom.find_one({"uId" : uId})
        if user :
            return jsonify(status="perhatian", message="Anda telah melakukan rekomendasi")
        else :
            try: 
                db.rekom.insert_one(newData)
                return jsonify(status="sukses", message="Rekomendasi anda telah terkirim")
            except :
                return jsonify(status="gagal", message="Rekomendasi anda gagal terkirim")
    else:
        return jsonify(status="gagal", message="Anggota keluarga tidak ada yang berperan sebagai Kepala Keluarga")

@app.route("/post_keluarga", methods=['POST'])
@jwt_required()
def post_keluarga():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    last_user = db.warga.find_one(sort=[("wargaId", -1)])
    if last_user: new_wargaId = last_user['wargaId'] + 1
    else: new_wargaId = 1
    nama = request.form.get('nama')
    nik = request.form.get('nik')
    tempat_lahir = request.form.get('tempat_lahir')
    peran = request.form.get('peran')
    jenis_kelamin = request.form.get('jenis_kelamin')
    agama = request.form.get('agama')
    ttl = request.form.get('ttl')
    pendidikan = request.form.get('pendidikan')
    gol_darah = request.form.get('gol_darah')
    pekerjaan = request.form.get('pekerjaan')
    status_perkawinan = request.form.get('status_perkawinan')
    check_user = db.warga.find_one({"nik" : nik})
    data = {
            "nama" : nama,
            "peran" : peran,
            "nik" : nik,
            "tempat_lahir" : tempat_lahir,
            "peran" : peran,
            "jenis_kelamin" : jenis_kelamin,
            "agama" : agama,
            "ttl" : ttl,
            "pendidikan" : pendidikan,
            "gol_darah" : gol_darah,
            "pekerjaan" : pekerjaan,
            "status_perkawinan" : status_perkawinan,
            "jabatan" : "Masyarakat",
            "uId" : uId,
            "wargaId" : new_wargaId,
        }
    if check_user :
        return jsonify(status="perhatian", message="Nomor NIK telah terdaftar")
    else :
        try:
            db.warga.insert_one(data)
            return jsonify(status='sukses', message="Berhasil ditambahkan")
        except:
            print("Gagal:", str(e))
            return jsonify(status='gagal', message="Gagal ditambahkan")

@app.route("/post_suket_kematian", methods=['POST'])
@jwt_required()
def post_suket_kematian():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    nikT = request.form.get('nikT')
    nikP = request.form.get('nikP')
    pelapor = db.warga.find_one({"nik": nikP}, {"_id": 0})

    if uId == pelapor['uId'] :
        kewarganegaraanT = request.form.get('kewarganegaraanT')
        kewarganegaraanT = kewarganegaraanT.upper()
        hubunganP = request.form.get('hubunganP')
        hubunganP = hubunganP.title()
        keteranganP = request.form.get('keteranganP')
        hariHM = request.form.get('hariHM')
        hariHM = hariHM.title()
        tanggalHM = request.form.get('tanggalHM')
        pukulHM = request.form.get('pukulHM')
        bertempatHM = request.form.get('bertempatHM')
        bertempatHM = bertempatHM.title()
        penyebabHM = request.form.get('penyebabHM')
        penyebabHM = penyebabHM.title()

        terlapor = db.warga.find_one({"nik": nikT}, {"_id": 0})
        userTerlapor = db.users.find_one({"uId": terlapor['uId']}, {"_id": 0})
        userPelapor = db.users.find_one({"uId": pelapor['uId']}, {"_id": 0})

        namaTerlapor = terlapor['nama']
        nikTerlapor = terlapor['nik']
        tempat_lahir = terlapor['tempat_lahir'].split(',')[0]
        ttlTerlapor = f"{tempat_lahir}, {terlapor['ttl']}"
        jenis_kelaminTerlapor = terlapor['jenis_kelamin']
        alamatTerlapor = userTerlapor['alamat']
        agamaTerlapor = terlapor['agama']
        statusPerkawinanTerlapor = terlapor['status_perkawinan']
        pekerjaanTerlapor = terlapor['pekerjaan']
        
        namaPelapor = pelapor['nama']
        nikPelapor = pelapor['nik']
        tempat_lahir_pelapor = pelapor['tempat_lahir'].split(',')[0]
        ttlPelapor = f"{tempat_lahir_pelapor}, {pelapor['ttl']}"
        jenis_kelaminPelapor = pelapor['jenis_kelamin']
        alamatPelapor = userPelapor['alamat']
        wargaIdP = pelapor['wargaId']
        rtP = userPelapor['rt']
        rwP = userPelapor['rw']
        noHp = userPelapor['noHp']

        last_surat = db.surat.find_one(sort=[("suratId", -1)])
        if last_surat: suratId = last_surat['suratId'] + 1
        else: suratId = 1  
        last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
        if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
        else: riwayatId = 1  
        # last_suket_kematian = db.surat.count_documents({"jenisSurat": "Surat Keterangan Kematian"})
        # if last_suket_kematian : 
        #     kode_surat = last_suket_kematian + 1
        # else :
        #     kode_surat = 1
        
        jam, menit, detik = gear.get_waktu()
        hari, bulan, tahun = gear.get_tanggal()
        kabisat = gear.get_kabisat(bulan)

        data_terlapor = {
            "Nama": namaTerlapor,
            "NIK": nikTerlapor,
            "Tempat, Tanggal Lahir": ttlTerlapor,
            "Jenis Kelamin": jenis_kelaminTerlapor,
            "Alamat": alamatTerlapor,
            "Agama": agamaTerlapor,
            "Status Perkawinan": statusPerkawinanTerlapor,
            "Pekerjaan": pekerjaanTerlapor,
            "Kewarganegaraan": kewarganegaraanT,
        }
        data_hari_meninggal = {
            "Hari": hariHM,
            "Tanggal": tanggalHM,
            "Pukul": pukulHM,
            "Bertempat di": bertempatHM,
            "Penyebab": penyebabHM,
        }
        data_pelapor = {
            "Nama": namaPelapor,
            "NIK": nikPelapor,
            "Tempat, Tanggal Lahir": ttlPelapor,
            "Jenis Kelamin": jenis_kelaminPelapor,
            "Alamat": f"{alamatPelapor} RT.{rtP} RW.{rwP}",
            "Hubungan dengan almarhum": hubunganP,
        }
        # ======================================================
        isi_surat = {
            "data_terlapor" : data_terlapor,
            "data_hari_meninggal" : data_hari_meninggal,
            "data_pelapor" : data_pelapor,
        }
        # ======================================================
        data_surat = {
            "nama_pelapor": namaPelapor,
            "jenis_surat": "Surat Keterangan Kematian",
            "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
            "keterangan_surat": keteranganP,
            "no_hp" : noHp,
            "status_surat": "Menunggu Persetujuan RT",
            "isi_surat" : isi_surat,
            "kode_surat" : 0,
            "rt" : rtP,
            "rw" : rwP,
            "wargaId" : wargaIdP,
            "suratId": suratId,
        }
        data_riwayat = {
            "riwayatId" : riwayatId,
            "suratId" : suratId,
            "uId" : uId,
            "catatan" : "",
            "status_surat" : "Menunggu Persetujuan RT",
            "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
        }
        try:
            # sk.create_pdf(f"static/file/suket-kematian-{kode_surat}.pdf", kode_surat, f"{gear.hari} {gear.kabisat} {gear.tahun}", gear.romawi, gear.tahun, data_terlapor, data_hari_meninggal, data_pelapor)
            db.surat.insert_one(data_surat)
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Permohonan Surat Kematian telah dikirimkan")
        except Exception as e:
            print("Gagal:", str(e))
            return jsonify(status='gagal', message="Permohonan Surat Kematian gagal dikirimkan")
    else :
        return jsonify(status='gagal', message="Pelapor hanya dapat NIK yang terdaftar di KK")

@app.route("/post_suket_penghasilan", methods=['POST'])
@jwt_required()
def post_suket_penghasilan():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    nikP = request.form.get('nikP')
    pelapor = db.warga.find_one({"nik": nikP}, {"_id": 0})
    if pelapor :
        if uId == pelapor['uId'] :
            penghasilanP = request.form.get('penghasilanP')
            keteranganP = request.form.get('keteranganP')
            userPelapor = db.users.find_one({"uId": pelapor['uId']}, {"_id": 0})
            namaPelapor = pelapor['nama']
            nikPelapor = pelapor['nik']
            agamaPelapor = pelapor['agama']
            tempat_lahir_pelapor = pelapor['tempat_lahir'].split(',')[0]
            ttlPelapor = f"{tempat_lahir_pelapor}, {pelapor['ttl']}"
            jenis_kelaminPelapor = pelapor['jenis_kelamin']
            alamatPelapor = userPelapor['alamat']
            pekerjaanPelapor = pelapor['pekerjaan']
            rtP = userPelapor['rt']
            rwP = userPelapor['rw']
            noHp = userPelapor['noHp']
            wargaIdP = pelapor['wargaId']

            jam, menit, detik = gear.get_waktu()
            hari, bulan, tahun = gear.get_tanggal()
            kabisat = gear.get_kabisat(bulan)

            last_surat = db.surat.find_one(sort=[("suratId", -1)])
            if last_surat: suratId = last_surat['suratId'] + 1
            else: suratId = 1  
            last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
            if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
            else: riwayatId = 1  
            # last_suket_penghasilan = db.surat.count_documents({"jenisSurat": "Surat Keterangan Penghasilan"})
            # if last_suket_penghasilan : 
            #     kode_surat = last_suket_penghasilan + 1
            # else :
            #     kode_surat = 1
            
            data_pelapor = {
                "Nama": namaPelapor,
                "NIK": nikPelapor,
                "Tempat, Tanggal Lahir": ttlPelapor,
                "Jenis Kelamin": jenis_kelaminPelapor,
                "Agama": agamaPelapor,
                "Pekerjaan" : pekerjaanPelapor,
                "Alamat": f"{alamatPelapor} RT.{rtP} RW.{rwP}",
            }
            isi_surat = {
                "data_pelapor": data_pelapor,
                "penghasilanP" : penghasilanP,
            }
            data_surat = {
                "nama_pelapor": namaPelapor,
                "jenis_surat": "Surat Keterangan Penghasilan",
                "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
                "keterangan_surat": keteranganP,
                "no_hp" : noHp,
                "isi_surat" : isi_surat,
                "status_surat": "Menunggu Persetujuan RT",
                "kode_surat" : 0,
                "rt" : rtP,
                "rw" : rwP,
                "wargaId" : wargaIdP,
                "suratId": suratId,
            }
            data_riwayat = {
                "riwayatId" : riwayatId,
                "suratId" : suratId,
                "uId" : uId,
                "catatan" : "",
                "status_surat" : "Menunggu Persetujuan RT",
                "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
            }
            try:
                # sp.create_pdf(f"static/file/suket-penghasilan-{kode_surat}.pdf", kode_surat, f"{gear.hari} {gear.kabisat} {gear.tahun}", gear.romawi, gear.tahun, data_pelapor, rtP, rwP, penghasilanP, keteranganP)
                db.surat.insert_one(data_surat)
                db.riwayat.insert_one(data_riwayat)
                return jsonify(status='sukses', message="Permohonan Surat Penghasilan telah dikirimkan")
            except Exception as e:
                print("Gagal:", str(e))
                return jsonify(status='gagal', message="Permohonan Surat Penghasilan gagal dikirimkan")
        else :
            return jsonify(status='gagal', message="Gunakan NIK yang terdaftar di KK")
    else :
        return jsonify(status='gagal', message="NIK tidak terdaftar")

@app.route("/post_suket_tidak_mampu", methods=['POST'])
@jwt_required()
def post_suket_tidak_mampu():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    nikP = request.form.get('nikP')
    pelapor = db.warga.find_one({"nik": nikP}, {"_id": 0})
    if uId == pelapor['uId']:
        keteranganP = request.form.get('keteranganP')
        userPelapor = db.users.find_one({"uId": pelapor['uId']}, {"_id": 0})
        namaPelapor = pelapor['nama']
        nikPelapor = pelapor['nik']
        agamaPelapor = pelapor['agama']
        tempat_lahir_pelapor = pelapor['tempat_lahir'].split(',')[0]
        ttlPelapor = f"{tempat_lahir_pelapor}, {pelapor['ttl']}"
        jenis_kelaminPelapor = pelapor['jenis_kelamin']
        alamatPelapor = userPelapor['alamat']
        pekerjaanPelapor = pelapor['pekerjaan']
        rtP = userPelapor['rt']
        rwP = userPelapor['rw']
        noHp = userPelapor['noHp']
        wargaIdP = pelapor['wargaId']
        
        last_surat = db.surat.find_one(sort=[("suratId", -1)])
        if last_surat: suratId = last_surat['suratId'] + 1
        else: suratId = 1  
        last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
        if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
        else: riwayatId = 1  
        
        jam, menit, detik = gear.get_waktu()
        hari, bulan, tahun = gear.get_tanggal()
        kabisat = gear.get_kabisat(bulan)

        data_pelapor = {
            "Nama": namaPelapor,
            "NIK": nikPelapor,
            "Tempat, Tanggal Lahir": ttlPelapor,
            "Jenis Kelamin": jenis_kelaminPelapor,
            "Agama": agamaPelapor,
            "Pekerjaan" : pekerjaanPelapor,
            "Alamat": f"{alamatPelapor} RT.{rtP} RW.{rwP}",
        }
        isi_surat = {
            "data_pelapor": data_pelapor,
        }
        data_surat = {
            "nama_pelapor": namaPelapor,
            "jenis_surat": "Surat Keterangan Tidak Mampu",
            "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
            "keterangan_surat": keteranganP,
            "no_hp" : noHp,
            "isi_surat" : isi_surat,
            "status_surat": "Menunggu Persetujuan RT",
            "kode_surat" : 0,
            "rt" : rtP,
            "rw" : rwP,
            "wargaId" : wargaIdP,
            "suratId": suratId,
        }
        data_riwayat = {
            "riwayatId" : riwayatId,
            "suratId" : suratId,
            "uId" : uId,
            "catatan" : "",
            "status_surat" : "Menunggu Persetujuan RT",
            "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
        }
        try:
            db.surat.insert_one(data_surat)
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Permohonan Surat Tidak Mampu telah dikirimkan")
        except Exception as e:
            print("Gagal:", str(e))
            return jsonify(status='gagal', message="Permohonan Surat Tidak Mampu gagal dikirimkan")
    else :
        return jsonify(status='gagal', message="Hanya dapat menggunakan NIK yang terdaftar di KK")

@app.route("/post_suket_gaib", methods=['POST'])
@jwt_required()
def post_suket_gaib():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    nikT = request.form.get('nikT')
    nikP = request.form.get('nikP')
    pelapor = db.warga.find_one({"nik": nikP}, {"_id": 0})
    if uId == pelapor['uId'] :
        wargaNegaraT = request.form.get('wargaNegaraT')
        wargaNegaraT = wargaNegaraT.title()
        wargaNegaraP = request.form.get('wargaNegaraP')
        wargaNegaraP = wargaNegaraP.title()
        hubunganP = request.form.get('hubunganP')
        hubunganP = hubunganP.title()
        keteranganP = request.form.get('keteranganP')
        bulanHilang = request.form.get('bulanHilang')
        bulanHilang = bulanHilang.title()
        tahunHilang = request.form.get('tahunHilang')

        terlapor = db.warga.find_one({"nik": nikT}, {"_id": 0})
        userPelapor = db.users.find_one({"uId": pelapor['uId']}, {"_id": 0})

        namaTerlapor = terlapor['nama']
        nikTerlapor = terlapor['nik']
        tempat_lahir = terlapor['tempat_lahir'].split(',')[0]
        ttlTerlapor = f"{tempat_lahir}, {terlapor['ttl']}"
        agamaTerlapor = terlapor['agama']
        pekerjaanTerlapor = terlapor['pekerjaan']
        
        namaPelapor = pelapor['nama']
        nikPelapor = pelapor['nik']
        tempat_lahir_pelapor = pelapor['tempat_lahir'].split(',')[0]
        ttlPelapor = f"{tempat_lahir_pelapor}, {pelapor['ttl']}"
        agamaP = pelapor['agama']
        pekerjaanP = pelapor['pekerjaan']
        alamatPelapor = userPelapor['alamat']
        wargaIdP = pelapor['wargaId']
        rtP = userPelapor['rt']
        rwP = userPelapor['rw']
        noHp = userPelapor['noHp']

        last_surat = db.surat.find_one(sort=[("suratId", -1)])
        if last_surat: suratId = last_surat['suratId'] + 1
        else: suratId = 1  
        
        last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
        if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
        else: riwayatId = 1  

        jam, menit, detik = gear.get_waktu()
        hari, bulan, tahun = gear.get_tanggal()
        kabisat = gear.get_kabisat(bulan)

        data_terlapor = {
            "Nama": namaTerlapor,
            "NIK": nikTerlapor,
            "Tempat, Tanggal Lahir": ttlTerlapor,
            "Warga Negara": wargaNegaraT,
            "Agama": agamaTerlapor,
            "Pekerjaan": pekerjaanTerlapor,
        }
        data_pelapor = {
            "Nama": namaPelapor,
            "NIK": nikPelapor,
            "Tempat, Tanggal Lahir": ttlPelapor,
            "Warga Negara" : wargaNegaraP,
            "Agama" : agamaP,
            "Pekerjaan" : pekerjaanP,
            "Alamat": f"{alamatPelapor} RT.{rtP} RW.{rwP}",
        }
        # ======================================================
        isi_surat = {
            "data_terlapor" : data_terlapor,
            "data_pelapor" : data_pelapor,
            "bulanHilang" : bulanHilang,
            "tahunHilang" : tahunHilang,
        }
        # ======================================================
        data_surat = {
            "nama_pelapor": namaPelapor,
            "jenis_surat": "Surat Keterangan Gaib",
            "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
            "keterangan_surat": keteranganP,
            "no_hp": noHp,
            "status_surat": "Menunggu Persetujuan RT",
            "isi_surat" : isi_surat,
            "kode_surat" : 0,
            "rt" : rtP,
            "rw" : rwP,
            "wargaId" : wargaIdP,
            "suratId": suratId,
        }
        data_riwayat = {
            "riwayatId" : riwayatId,
            "suratId" : suratId,
            "uId" : uId,
            "catatan" : "",
            "status_surat" : "Menunggu Persetujuan RT",
            "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
        }
        try:
            # sk.create_pdf(f"static/file/suket-kematian-{kode_surat}.pdf", kode_surat, f"{gear.hari} {gear.kabisat} {gear.tahun}", gear.romawi, gear.tahun, data_terlapor, data_hari_meninggal, data_pelapor)
            db.surat.insert_one(data_surat)
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Permohonan Surat Gaib telah dikirimkan")
        except Exception as e:
            print("Gagal:", str(e))
            return jsonify(status='gagal', message="Permohonan Surat Gaib gagal dikirimkan")
    else :
        return jsonify(status='gagal', message="Hanya dapat menggunakan NIK yang terdaftar di KK")

@app.route("/post_suket_orang_yang_sama", methods=['POST'])
@jwt_required()
def post_suket_orang_yang_sama():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    nikP = request.form.get('nikP')
    pelapor = db.warga.find_one({"nik": nikP}, {"_id": 0})
    if uId == pelapor['uId'] :
        dokumenBenar = request.form.get('dokumenBenar')
        nomorDokumenBenar = request.form.get('nomorDokumenBenar')
        dokumenSalah = request.form.get('dokumenSalah')
        nomorDokumenSalah = request.form.get('nomorDokumenSalah')
        dataBenar = request.form.get('dataBenar')
        dataSalah = request.form.get('dataSalah')
        keteranganP = request.form.get('keteranganP')
        userPelapor = db.users.find_one({"uId": pelapor['uId']}, {"_id": 0})

        namaPelapor = pelapor['nama']
        jenisKelaminP = pelapor['jenis_kelamin']
        noHp = userPelapor['noHp']
        rtP = userPelapor['rt']
        rwP = userPelapor['rw']
        wargaIdP = pelapor['wargaId']

        last_surat = db.surat.find_one(sort=[("suratId", -1)])
        if last_surat: suratId = last_surat['suratId'] + 1
        else: suratId = 1  
        last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
        if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
        else: riwayatId = 1 

        jam, menit, detik = gear.get_waktu()
        hari, bulan, tahun = gear.get_tanggal()
        kabisat = gear.get_kabisat(bulan)

        data_pelapor = {
            "Nama": namaPelapor,
            "Jenis Kelamin" : jenisKelaminP,
        }

        # ======================================================
        isi_surat = {
            "data_pelapor" : data_pelapor,
            "dokumenBenar" : dokumenBenar,
            "dokumenSalah" : dokumenSalah,
            "nomorDokumenBenar" : nomorDokumenBenar,
            "nomorDokumenSalah" : nomorDokumenSalah,
            "dataBenar" : dataBenar,
            "dataSalah" : dataSalah,
        }
        # ======================================================

        data_surat = {
            "nama_pelapor": namaPelapor,
            "jenis_surat": "Surat Keterangan Orang Yang Sama",
            "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
            "keterangan_surat": keteranganP,
            "no_hp": noHp,
            "status_surat": "Menunggu Persetujuan RT",
            "isi_surat" : isi_surat,
            "kode_surat" : 0,
            "rt" : rtP,
            "rw" : rwP,
            "wargaId" : wargaIdP,
            "suratId": suratId,
        }
        data_riwayat = {
            "riwayatId" : riwayatId,
            "suratId" : suratId,
            "uId" : uId,
            "catatan" : "",
            "status_surat" : "Menunggu Persetujuan RT",
            "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
        }
        try:
            db.surat.insert_one(data_surat)
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Permohonan Surat Orang Yang Sama telah dikirimkan")
        except Exception as e:
            print("Gagal:", str(e))
            return jsonify(status='gagal', message="Permohonan Surat Orang Yang Sama gagal dikirimkan")
    else :
        return jsonify(status='gagal', message="Hanya dapat menggunakan NIK yang terdaftar pada KK")

@app.route("/post_suket_domisili", methods=['POST'])
@jwt_required()
def post_suket_domisili():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    nikP = request.form.get('nikP')
    pelapor = db.warga.find_one({"nik": nikP}, {"_id": 0})
    if uId == pelapor['uId'] :
        kewarganegaraanP = request.form.get('kewarganegaraanP')
        kewarganegaraanP = kewarganegaraanP.title()
        keteranganP = request.form.get('keteranganP')
        userPelapor = db.users.find_one({"uId": pelapor['uId']}, {"_id": 0})

        namaPelapor = pelapor['nama']
        nikPelapor = pelapor['nik']
        tempat_lahir_pelapor = pelapor['tempat_lahir'].split(',')[0]
        ttlPelapor = f"{tempat_lahir_pelapor}, {pelapor['ttl']}"
        jenisKelaminP = pelapor['jenis_kelamin']
        agamaP = pelapor['agama']
        pekerjaanP = pelapor['pekerjaan']
        alamatPelapor = userPelapor['alamat']
        wargaIdP = pelapor['wargaId']
        rtP = userPelapor['rt']
        rwP = userPelapor['rw']
        noHp = userPelapor['noHp']

        last_surat = db.surat.find_one(sort=[("suratId", -1)])
        if last_surat: suratId = last_surat['suratId'] + 1
        else: suratId = 1  
        last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
        if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
        else: riwayatId = 1  

        jam, menit, detik = gear.get_waktu()
        hari, bulan, tahun = gear.get_tanggal()
        kabisat = gear.get_kabisat(bulan)

        data_pelapor = {
            "Nama": namaPelapor,
            "NIK": nikPelapor,
            "Tempat, Tanggal Lahir": ttlPelapor,
            "Jenis Kelamin" : jenisKelaminP,
            "Kewarganegaraan" : kewarganegaraanP,
            "Agama" : agamaP,
            "Pekerjaan" : pekerjaanP,
            "Alamat": f"{alamatPelapor} RT.{rtP} RW.{rwP}",
        }
        # ======================================================
        isi_surat = {
            "data_pelapor" : data_pelapor,
        }
        # ======================================================
        data_surat = {
            "nama_pelapor": namaPelapor,
            "jenis_surat": "Surat Keterangan Domisili",
            "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
            "keterangan_surat": keteranganP,
            "no_hp": noHp,
            "status_surat": "Menunggu Persetujuan RT",
            "isi_surat" : isi_surat,
            "kode_surat" : 0,
            "rt" : rtP,
            "rw" : rwP,
            "wargaId" : wargaIdP,
            "suratId": suratId,
        }
        data_riwayat = {
            "riwayatId" : riwayatId,
            "suratId" : suratId,
            "uId" : uId,
            "catatan" : "",
            "status_surat" : "Menunggu Persetujuan RT",
            "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
        }
        try:
            # sk.create_pdf(f"static/file/suket-kematian-{kode_surat}.pdf", kode_surat, f"{gear.hari} {gear.kabisat} {gear.tahun}", gear.romawi, gear.tahun, data_terlapor, data_hari_meninggal, data_pelapor)
            db.surat.insert_one(data_surat)
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Permohonan Surat Domisili telah dikirimkan")
        except Exception as e:
            print("Gagal:", str(e))
            return jsonify(status='gagal', message="Permohonan Surat Domisili gagal dikirimkan")
    else :
        return jsonify(status='gagal', message="Hanya dapat menggunakan NIK yang terdaftar pada KK")

@app.route("/post_suket_domisili_perusahaan", methods=['POST'])
@jwt_required()
def post_suket_domisili_perusahaan():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    namaPerusahaan = request.form.get('namaPerusahaan')
    namaYPPerusahaan = request.form.get('namaYPPerusahaan')
    jabatanYP = request.form.get('jabatanYP')
    nikYP = request.form.get('nikYP')
    namaNotaris = request.form.get('namaNotaris')
    noAkta = request.form.get('noAkta')
    tanggalAkta = request.form.get('tanggalAkta')
    namaJalan = request.form.get('namaJalan')
    rt = request.form.get('rt')
    rw = request.form.get('rw')
    noHp = request.form.get('noHp')
    keteranganP = request.form.get('keteranganP')

    pelapor = db.warga.find_one({"nik": nikYP}, {"_id": 0})
    if pelapor : wargaId = pelapor['wargaId']
    else : wargaId = 0

    last_surat = db.surat.find_one(sort=[("suratId", -1)])
    if last_surat: suratId = last_surat['suratId'] + 1
    else: suratId = 1
    last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
    if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
    else: riwayatId = 1  
    
    jam, menit, detik = gear.get_waktu()
    hari, bulan, tahun = gear.get_tanggal()
    kabisat = gear.get_kabisat(bulan)

    data_perusahaan = {
        "Nama Perusahaan": namaPerusahaan,
        "Nama": namaYPPerusahaan,
        "Jabatan": jabatanYP,
        "NIK": nikYP,
    }

    domisili_perusahaan = {
        "Jalan": f"{namaJalan} RT.{rt} RW.{rw}",
        "Kelurahan": "Limbungan",
        "Kecamatan": "Rumbai Timur",
        "Kota": "Pekanbaru",
    }
    # ======================================================
    isi_surat = {
        "data_perusahaan" : data_perusahaan,
        "domisili_perusahaan" : domisili_perusahaan,
        "namaNotaris" : namaNotaris,
        "noAkta" : noAkta,
        "tanggalAkta" : tanggalAkta
    }
    # ======================================================
    data_surat = {
        "nama_pelapor": namaYPPerusahaan,
        "jenis_surat": "Surat Keterangan Domisili Perusahaan",
        "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
        "keterangan_surat": keteranganP,
        "no_hp": noHp,
        "status_surat": "Menunggu Persetujuan RT",
        "isi_surat" : isi_surat,
        "kode_surat" : 0,
        "rt" : rt,
        "rw" : rw,
        "wargaId" : wargaId,
        "suratId": suratId,
    }
    data_riwayat = {
        "riwayatId" : riwayatId,
        "suratId" : suratId,
        "uId" : uId,
        "catatan" : "",
        "status_surat" : "Menunggu Persetujuan RT",
        "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
    }
    try:
        db.surat.insert_one(data_surat)
        db.riwayat.insert_one(data_riwayat)
        return jsonify(status='sukses', message="Permohonan Surat Domisili Perusahaan telah dikirimkan")
    except Exception as e:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Permohonan Surat Domisili Perusahaan gagal dikirimkan")

@app.route("/post_suket_domisili_usaha", methods=['POST'])
@jwt_required()
def post_suket_domisili_usaha():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    namaP = request.form.get('namaP')
    nikP = request.form.get('nikP')
    tempatLahir = request.form.get('tempatLahir')
    tempatLahir = tempatLahir.title()
    tglLahir = request.form.get('tglLahir')
    ttlP = f"{tempatLahir}, {tglLahir}"
    agamaP = request.form.get('agamaP')
    agamaP = agamaP.title()
    pekerjaanP = request.form.get('pekerjaanP')
    alamatP = request.form.get('alamatP')
    jenisUsaha = request.form.get('jenisUsaha')
    rt = request.form.get('rt')
    rw = request.form.get('rw')
    noHp = request.form.get('noHp')
    keteranganP = request.form.get('keteranganP')

    pelapor = db.warga.find_one({"nik": nikP}, {"_id": 0})
    if pelapor : wargaId = pelapor['wargaId']
    else : wargaId = 0

    last_surat = db.surat.find_one(sort=[("suratId", -1)])
    if last_surat: suratId = last_surat['suratId'] + 1
    else: suratId = 1
    last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
    if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
    else: riwayatId = 1  
    
    jam, menit, detik = gear.get_waktu()
    hari, bulan, tahun = gear.get_tanggal()
    kabisat = gear.get_kabisat(bulan)


    data_pelapor = {
        "Nama": namaP,
        "NIK": nikP,
        "Tempat, Tanggal Lahir": ttlP,
        "Agama": agamaP,
        "Pekerjaan": pekerjaanP,
        "Alamat": f"{alamatP} RT.{rt} RW.{rw}"
    }

    alamat_pengajuan = {
        "Alamat": f"{alamatP} RT.{rt} RW.{rw}",
        "Kelurahan": "Limbungan",
        "Kecamatan": "Rumbai Timur",
        "Kota": "Pekanbaru"
    }
    peraturan = {
        "1": "Tidak melakukan penyalahgunaan tempat usaha;",
        "2": "Untuk Memenuhi segala peraturan, hukum dan norma yang berlaku di wilayah Kelurahan Limbungan Kecamatan Rumbai Timur Kota Pekanbaru;",
        "3": "Untuk selalu menjaga kebersihan, keindahan, ketertiban dan keamanan diwilayah /lingkungan tempat usaha yang bersangkutan;",
        "4": "Memenuhi segala kewajiban dan retribusi yang diatur sesuai dengan undang-undang yang berlaku."
    }
    # ======================================================
    isi_surat = {
        "data_pelapor" : data_pelapor,
        "alamat_pengajuan" : alamat_pengajuan,
        "peraturan" : peraturan,
        "jenisUsaha" : jenisUsaha
    }
    # ======================================================
    data_surat = {
        "nama_pelapor": namaP,
        "jenis_surat": "Surat Keterangan Domisili Usaha",
        "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
        "keterangan_surat": keteranganP,
        "no_hp": noHp,
        "status_surat": "Menunggu Persetujuan RT",
        "isi_surat" : isi_surat,
        "kode_surat" : 0,
        "rt" : rt,
        "rw" : rw,
        "wargaId" : wargaId,
        "suratId": suratId,
    }
    data_riwayat = {
        "riwayatId" : riwayatId,
        "suratId" : suratId,
        "uId" : uId,
        "catatan" : "",
        "status_surat" : "Menunggu Persetujuan RT",
        "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
    }
    try:
        db.surat.insert_one(data_surat)
        db.riwayat.insert_one(data_riwayat)
        return jsonify(status='sukses', message="Permohonan Surat Domisili Perusahaan telah dikirimkan")
    except Exception as e:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Permohonan Surat Domisili Perusahaan gagal dikirimkan")

@app.route("/post_suket_tanggungan", methods=['POST'])
@jwt_required()
def post_suket_tanggungan() :
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)

    nikP = request.form.get('nikP')
    pelapor = db.warga.find_one({"nik": nikP}, {"_id": 0})
    if uId == pelapor['uId'] :
        keteranganP = request.form.get('keteranganP')
        tanggungan = json.loads(request.form.get('tanggungan'))
        tanggungan_data = []
        
        for nama in tanggungan:
            orang_tanggungan = db.warga.find_one({
                    "$and": [
                        {"nama": nama},
                        {"uId": uId}
                    ]
                },
                {"_id": 0, "nama": 1, "tempat_lahir": 1, "ttl": 1, "pekerjaan": 1, "peran": 1}
            )
            if orang_tanggungan:
                tanggungan_data.append({
                    "Nama": orang_tanggungan.get("nama"),
                    "Tempat/Tgl Lahir": f'{orang_tanggungan.get("tempat_lahir")} {orang_tanggungan.get("ttl")}',
                    "Pekerjaan": orang_tanggungan.get("pekerjaan"),
                    "Status": orang_tanggungan.get("peran")
                })

        userPelapor = db.users.find_one({"uId": pelapor['uId']}, {"_id": 0})
        
        namaPelapor = pelapor['nama']
        namaP = pelapor['nama']
        tempat_lahir_pelapor = pelapor['tempat_lahir'].split(',')[0]
        ttlPelapor = f"{tempat_lahir_pelapor}, {pelapor['ttl']}"
        jenis_kelaminP = pelapor['jenis_kelamin']
        agamaP = pelapor['agama']
        pekerjaanP = pelapor['pekerjaan']
        alamatPelapor = userPelapor['alamat']
        wargaIdP = pelapor['wargaId']
        rtP = userPelapor['rt']
        rwP = userPelapor['rw']
        noHp = userPelapor['noHp']

        last_surat = db.surat.find_one(sort=[("suratId", -1)])
        if last_surat: suratId = last_surat['suratId'] + 1
        else: suratId = 1
        last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
        if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
        else: riwayatId = 1  
        
        jam, menit, detik = gear.get_waktu()
        hari, bulan, tahun = gear.get_tanggal()
        kabisat = gear.get_kabisat(bulan)
        
        data_pelapor = {
            "Nama": namaP,
            "NIK": nikP,
            "Tempat, Tanggal Lahir": ttlPelapor,
            "Jenis Kelamin": jenis_kelaminP,
            "Agama": agamaP,
            "Pekerjaan": pekerjaanP,
            "Alamat": alamatPelapor,
        }
        # ======================================================
        isi_surat = {
            "data_pelapor" : data_pelapor,
            "tanggungan_data" : tanggungan_data
        }
        # ======================================================
        data_surat = {
            "nama_pelapor": namaPelapor,
            "jenis_surat": "Surat Keterangan Tanggungan Keluarga",
            "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
            "keterangan_surat": keteranganP,
            "no_hp": noHp,
            "status_surat": "Menunggu Persetujuan RT",
            "isi_surat" : isi_surat,
            "kode_surat" : 0,
            "rt" : rtP,
            "rw" : rwP,
            "wargaId" : wargaIdP,
            "suratId": suratId,
        }
        data_riwayat = {
            "riwayatId" : riwayatId,
            "suratId" : suratId,
            "uId" : uId,
            "catatan" : "",
            "status_surat" : "Menunggu Persetujuan RT",
            "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
        }
        try:
            db.surat.insert_one(data_surat)
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Permohonan Surat Tanggungan Keluarga telah dikirimkan")
        except Exception as e:
            print("Gagal:", str(e))
            return jsonify(status='gagal', message="Permohonan Surat Tanggungan Keluarga gagal dikirimkan")
    else :
        return jsonify(status='gagal', message="Hanya dapat menggunakan NIK yang terdaftar di KK")

@app.route("/post_suket_pindah_wilayah", methods=['POST'])
@jwt_required()
def post_suket_pindah_wilayah():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    nikP = request.form.get('nikP')
    pelapor = db.warga.find_one({"nik": nikP}, {"_id": 0})
    if uId == pelapor['uId'] :
        keteranganP = request.form.get('keteranganP')
        nomorSPKTP = request.form.get('nomorSPKTP')
        tglSPKTP = request.form.get('tglSPKTP')

        userPelapor = db.users.find_one({"uId": pelapor['uId']}, {"_id": 0})
        
        namaPelapor = pelapor['nama']
        jenisKelamin = pelapor['jenis_kelamin']
        nikPelapor = pelapor['nik']
        tempat_lahir_pelapor = pelapor['tempat_lahir'].split(',')[0]
        ttlPelapor = f"{tempat_lahir_pelapor}, {pelapor['ttl']}"
        agamaP = pelapor['agama']
        pekerjaanP = pelapor['pekerjaan']
        alamatPelapor = userPelapor['alamat']
        wargaIdP = pelapor['wargaId']
        rtP = userPelapor['rt']
        rwP = userPelapor['rw']
        noHp = userPelapor['noHp']

        last_surat = db.surat.find_one(sort=[("suratId", -1)])
        if last_surat: suratId = last_surat['suratId'] + 1
        else: suratId = 1  
        
        last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
        if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
        else: riwayatId = 1  

        jam, menit, detik = gear.get_waktu()
        hari, bulan, tahun = gear.get_tanggal()
        kabisat = gear.get_kabisat(bulan)

        data_pelapor = {
            "Nama": namaPelapor,
            "Jenis Kelamin" : jenisKelamin,
            "NIK": nikPelapor,
            "Tempat, Tanggal Lahir": ttlPelapor,
            "Agama" : agamaP,
            "Pekerjaan" : pekerjaanP,
            "Alamat": f"{alamatPelapor} RT.{rtP} RW.{rwP}",
        }
        # ======================================================
        isi_surat = {
            "data_pelapor" : data_pelapor,
            "nomorSPKTP" : nomorSPKTP,
            "tglSPKTP" : tglSPKTP,
        }
        # ======================================================
        data_surat = {
            "nama_pelapor": namaPelapor,
            "jenis_surat": "Surat Keterangan Pindah Wilayah",
            "tanggal_pengajuan": f"{hari} {kabisat} {tahun}",
            "keterangan_surat": keteranganP,
            "no_hp": noHp,
            "status_surat": "Menunggu Persetujuan RT",
            "isi_surat" : isi_surat,
            "kode_surat" : 0,
            "rt" : rtP,
            "rw" : rwP,
            "wargaId" : wargaIdP,
            "suratId": suratId,
        }
        data_riwayat = {
            "riwayatId" : riwayatId,
            "suratId" : suratId,
            "uId" : uId,
            "catatan" : "",
            "status_surat" : "Menunggu Persetujuan RT",
            "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
        }
        try:
            # sk.create_pdf(f"static/file/suket-kematian-{kode_surat}.pdf", kode_surat, f"{gear.hari} {gear.kabisat} {gear.tahun}", gear.romawi, gear.tahun, data_terlapor, data_hari_meninggal, data_pelapor)
            db.surat.insert_one(data_surat)
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Permohonan Surat Pindah Wilayah telah dikirimkan")
        except Exception as e:
            print("Gagal:", str(e))
            return jsonify(status='gagal', message="Permohonan Surat Pindah Wilayah gagal dikirimkan")
    else :
        return jsonify(status='gagal', message="Hanya dapat menggunakan NIK yang terdaftar di KK")

#POST

#UPDATE
@app.route("/update_user", methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def update_user():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    data = db.users.find_one({'uId' : uId})
    profil_default = data['poto_profil']
    noKK = request.form.get('noKK')
    email = request.form.get('email')
    alamat = request.form.get('alamat')
    noHp = request.form.get('noHp')
    poto_profil = request.files.get('poto_profil')
    if poto_profil:
        if poto_profil.content_length > app.config['MAX_CONTENT_LENGTH']:
            return jsonify(status='gagal', message='Ukuran file terlalu besar. Maksimal 2MB.'), 200
        now = datetime.now()
        formatted_time = now.strftime("PRFL_%d%m%Y:%H:%M:%S")
        file_extension = poto_profil.filename.split('.')[-1]
        filename = secure_filename(f"{formatted_time}.{file_extension}")
        image_path = os.path.join(app.config['UPLOAD_FOLDER_1'], filename)
        poto_profil.save(image_path)
    else:
        image_path = profil_default
    data = {
        "noKK": noKK,
        "email": email,
        "poto_profil": image_path,  
        "alamat": alamat,
        "noHp": noHp,
    }
    try:
        db.users.update_one({"uId": uId}, {"$set": data})
        return jsonify(status='sukses', message="Profil berhasil diperbaharui"), 200
    except Exception as e:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Gagal memperbaharui profil"), 500

@app.route("/update_user_admin", methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def update_data_user():
    target_uId = request.form.get('uId')
    if not target_uId:
        return jsonify(status='gagal', message='uId user target wajib diisi'), 400
    target_uId = int(target_uId)

    # Ambil data user target
    user_target = db.users.find_one({'uId': target_uId})
    if not user_target:
        return jsonify(status='gagal', message='User tidak ditemukan'), 404

    profil_default = user_target['poto_profil']
    kk_default = user_target['gambar_kk']

    # Ambil semua data input
    noKK = request.form.get('noKK')
    email = request.form.get('email')
    alamat = request.form.get('alamat')
    noHp = request.form.get('noHp')
    jabatan = request.form.get('jabatan')
    rt = request.form.get('rt')
    rw = request.form.get('rw')
    password = request.form.get('password')

    # Proses upload poto_profil
    poto_profil = request.files.get('poto_profil')
    if poto_profil:
        now = datetime.now()
        formatted_time = now.strftime("PRFL_%d%m%Y_%H%M%S")
        file_extension = poto_profil.filename.split('.')[-1]
        filename = secure_filename(f"{formatted_time}.{file_extension}")
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        poto_profil.save(image_path)
    else:
        image_path = profil_default

    # Proses upload gambar_kk
    gambar_kk = request.files.get('gambar_kk')
    if gambar_kk:
        now = datetime.now()
        formatted_time = now.strftime("GNKK_%d%m%Y:%H:%M:%S")
        file_extension = gambar_kk.filename.split('.')[-1]
        kk_filename = secure_filename(f"{formatted_time}.{file_extension}")
        kk_path = os.path.join(app.config['UPLOAD_FOLDER'], kk_filename)
        gambar_kk.save(kk_path)
    else:
        kk_path = kk_default

    # Hash password jika diisi
    if password:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    else:
        hashed_password = user_target['password']

    # Data yang akan diupdate
    data_update = {
        "noKK": noKK,
        "email": email,
        "poto_profil": image_path,
        "gambar_kk": kk_path,
        "alamat": alamat,
        "noHp": noHp,
        "jabatan": jabatan,
        "rt": rt,
        "rw": rw,
        "password": hashed_password,
    }

    try:
        db.users.update_one({"uId": target_uId}, {"$set": data_update})
        return jsonify(status='sukses', message="Data user berhasil diperbaharui"), 200
    except Exception as e:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Gagal memperbaharui data user"), 500

@app.route("/del_surat/<int:suratId>", methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def del_surat(suratId):
    suratId = int(suratId)
    try :
        db.surat.delete_one({"suratId": suratId})
        return jsonify(status='sukses', message = "Surat berhasil dihapus")
    except:
        return jsonify(status='gagal', message = "Surat gagal dihapus")

@app.route('/update_permission', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def update_permission():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    stat = request.form.get('status')
    try:
        db.permitted.update_one({"uId": uId}, {"$set" : {"status" : stat}})
        return jsonify(status='sukses', message="Perizinan berhasil diperbaharui"), 200
    except Exception as e:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Gagal memperbaharui perizinan"), 500

@app.route('/update_user_kk', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def update_user_kk():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    gambarKK = request.files.get('kk_gambar')
    if gambarKK:
        # Check file size manually (if needed)
        if gambarKK.content_length > app.config['MAX_CONTENT_LENGTH']:
            return jsonify(status='gagal', message='Ukuran file terlalu besar. Maksimum 2MB.'), 200
        now = datetime.now()
        formatted_time = now.strftime("GNKK_%d%m%Y:%H:%M:%S")
        file_extension = gambarKK.filename.split('.')[-1]
        filename = secure_filename(f"{formatted_time}.{file_extension}")
        gambar = os.path.join(app.config['UPLOAD_FOLDER_2'], filename)
        gambarKK.save(gambar)
    else:
        return jsonify(status='gagal', message='File kk_gambar tidak ditemukan'), 200
    gambar_kk_update = {'gambar_kk': gambar}
    try:
        db.users.update_one({"uId": uId}, {'$set': gambar_kk_update})
        return jsonify(status='sukses', message="Kartu Keluarga berhasil diupload"), 200
    except Exception as e:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Kartu Keluarga gagal diupload"), 200

@app.route("/update_keluarga/<int:wargaId>", methods=['POST'])
@jwt_required()
def update_keluarga(wargaId):
    wargaId = int(wargaId)
    nama = request.form.get('nama')
    nik = request.form.get('nik')
    tempat_lahir = request.form.get('tempat_lahir')
    peran = request.form.get('peran')
    jenis_kelamin = request.form.get('jenis_kelamin')
    agama = request.form.get('agama')
    status_perkawinan = request.form.get('status_perkawinan')
    ttl = request.form.get('ttl')
    pendidikan = request.form.get('pendidikan')
    gol_darah = request.form.get('gol_darah')
    pekerjaan = request.form.get('pekerjaan')
    check_user = db.warga.find_one({"nik" : nik})
    data = {
            "nama" : nama,
            "peran" : peran,
            "nik" : nik,
            "tempat_lahir" : tempat_lahir,
            "peran" : peran,
            "jenis_kelamin" : jenis_kelamin,
            "agama" : agama,
            "status_perkawinan" : status_perkawinan,
            "ttl" : ttl,
            "pendidikan" : pendidikan,
            "gol_darah" : gol_darah,
            "pekerjaan" : pekerjaan,
        }
    if check_user :
        if check_user['wargaId'] != wargaId:
            print(check_user['wargaId'])
            print(check_user['wargaId'] != wargaId)
            return jsonify(status="perhatian", message="Nomor NIK telah terdaftar")
        else :
            try:
                db.warga.update_one({"wargaId" : wargaId}, {"$set" : data})
                return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
            except:
                print("Gagal:", str(e))
                return jsonify(status='gagal', message="Gagal diperbaharui"), 200 
    else :
        try:
            db.warga.update_one({"wargaId" : wargaId}, {"$set" : data})
            return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
        except:
            print("Gagal:", str(e))
            return jsonify(status='gagal', message="Gagal diperbaharui"), 200 

@app.route("/update_rekom", methods=["POST"])
@jwt_required()
def update_rekom():
    status = request.form.get('status')
    rekomId = request.form.get('rekomId')
    rekomId = int(rekomId)
    data = db.rekom.find_one({"rekomId" : rekomId}, {"_id" : 0})
    uId = data['uId']
    rt = data['rt']
    rw = data['rw']
    uId = int(uId)
    try:
        db.rekom.update_one({"rekomId" : rekomId}, {"$set" : {"status" : status}})
        db.users.update_one({"uId" : uId}, {"$set" : {"rt" : rt, "rw" :rw}})
        return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
    except:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Gagal diperbaharui"), 200 

@app.route("/update_password", methods=["POST"])
@jwt_required()
def update_password():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    password = request.form.get('password')
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    try:
        db.users.update_one({"uId" : uId}, {"$set" : {"password" : password_hash}})
        return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
    except:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Gagal diperbaharui"), 200 

@app.route("/update_jabatan", methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def update_jabatan():
    # Ambil jabatan dari form
    jabatan = request.form.get('jabatan')
    wargaId = request.form.get('wargaId')
    wargaId = int(wargaId)
    
    x = db.warga.find_one({"wargaId": wargaId}, {"_id" : 0})
    user = db.users.find_one({"uId": x['uId']}, {"_id" : 0})
    uId = user['uId']
    
    if not jabatan:
        return jsonify(status='gagal', message="Jabatan tidak boleh kosong"), 400

    try:
        # Update field jabatan saja
        db.warga.update_one({"wargaId": wargaId}, {"$set": {"jabatan": jabatan}})
        db.users.update_one({"uId": uId}, {"$set": {"jabatan": jabatan}})
        return jsonify(status='sukses', message="Jabatan berhasil diperbaharui"), 200
    except Exception as e:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Gagal memperbaharui jabatan"), 500

@app.route("/update_surat_accept", methods=['POST'])
@jwt_required()
def update_surat_accept():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    user = db.users.find_one({'uId' : uId}, {'_id' : 0})
    suratId = request.form.get('suratId')
    suratId = int(suratId)
    
    riw = db.riwayat.find_one({'suratId' : suratId}, {"_id" : 0}, sort=[('waktu', -1)])
    uIdRiwayat = riw['uId']
    
    catatan = request.form.get('catatan')

    jam, menit, detik = gear.get_waktu()
    hari, bulan, tahun = gear.get_tanggal()
    kabisat = gear.get_kabisat(bulan)

    last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
    if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
    else: riwayatId = 1  
    
    try:
        if(user['jabatan'] == "Ketua RT"):
            db.surat.update_one({'suratId' : suratId}, {'$set' : {'status_surat' : 'Menunggu Persetujuan RW'}})
            data_riwayat = {
                "riwayatId" : riwayatId,
                "suratId" : suratId,
                "uId" : uIdRiwayat,
                "catatan" : catatan,
                "status_surat" : "Menunggu Persetujuan RW",
                "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
            }
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
        elif(user['jabatan'] == "Ketua RW"):
            db.surat.update_one({'suratId' : suratId}, {'$set' : {'status_surat' : 'Menunggu Persetujuan Lurah'}})
            data_riwayat = {
                "riwayatId" : riwayatId,
                "suratId" : suratId,
                "uId" : uIdRiwayat,
                "catatan" : catatan,
                "status_surat" : "Menunggu Persetujuan Lurah",
                "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
            }
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
        elif(user['jabatan'] == "Lurah"):
            
            kode_surat = 1
            
            sur = db.surat.find_one({'suratId' : suratId}, {'_id' :0})
            jenSur = sur['jenis_surat']
            isiSur = sur['isi_surat']
            
            data_riwayat = {
                "riwayatId" : riwayatId,
                "suratId" : suratId,
                "uId" : uIdRiwayat,
                "catatan" : catatan,
                "status_surat" : "Surat Disetujui",
                "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
            }
            db.riwayat.insert_one(data_riwayat)
            if jenSur == "Surat Keterangan Tidak Mampu" :
                
                kode_surat = db.surat.count_documents({"jenis_surat": "Surat Keterangan Tidak Mampu", "status_surat": "Surat Disetujui"})
                if kode_surat : 
                    kode_surat = kode_surat + 1
                else :
                    kode_surat = 1
                # kode_surat = int(kode_surat)
                hari, bulan, tahun = gear.get_tanggal()
                kabisat =gear.get_kabisat(bulan)
                romawi = gear.get_romawi(bulan)
                print(jenSur)
                stm.create_pdf(f"static/file/{jenSur}-{kode_surat}.pdf", kode_surat, f"{hari} {kabisat} {tahun}", romawi, tahun, isiSur['data_pelapor'], isiSur['data_pelapor']['Alamat'],sur['rt'], sur['rw'], sur['keterangan_surat'])
                
            elif jenSur == "Surat Keterangan Penghasilan" :
                
                kode_surat = db.surat.count_documents({"jenis_surat": "Surat Keterangan Penghasilan", "status_surat": "Surat Disetujui"})
                if kode_surat : 
                    kode_surat = kode_surat + 1
                else :
                    kode_surat = 1
                # kode_surat = int(kode_surat)
                hari, bulan, tahun = gear.get_tanggal()
                kabisat =gear.get_kabisat(bulan)
                romawi = gear.get_romawi(bulan)
                print(jenSur)
                sp.create_pdf(f"static/file/{jenSur}-{kode_surat}.pdf", kode_surat, f"{hari} {kabisat} {tahun}", romawi, tahun, isiSur['data_pelapor'], sur['rt'], sur['rw'], isiSur['penghasilanP'], sur['keterangan_surat'])
                
            elif jenSur == "Surat Keterangan Kematian" :
                
                kode_surat = db.surat.count_documents({"jenis_surat": "Surat Keterangan Kematian", "status_surat": "Surat Disetujui"})
                if kode_surat : 
                    kode_surat = kode_surat + 1
                else :
                    kode_surat = 1
                # kode_surat = int(kode_surat)
                hari, bulan, tahun = gear.get_tanggal()
                kabisat =gear.get_kabisat(bulan)
                romawi = gear.get_romawi(bulan)
                print(jenSur)
                sk.create_pdf(f"static/file/{jenSur}-{kode_surat}.pdf", kode_surat, f"{hari} {kabisat} {tahun}", romawi, tahun, isiSur['data_terlapor'], isiSur['data_hari_meninggal'], isiSur['data_pelapor'])
                
            elif jenSur == "Surat Keterangan Domisili" :
                
                kode_surat = db.surat.count_documents({"jenis_surat": "Surat Keterangan Domisili", "status_surat": "Surat Disetujui"})
                if kode_surat : 
                    kode_surat = kode_surat + 1
                else :
                    kode_surat = 1
                # kode_surat = int(kode_surat)
                hari, bulan, tahun = gear.get_tanggal()
                kabisat =gear.get_kabisat(bulan)
                romawi = gear.get_romawi(bulan)
                print(jenSur)
                sd.create_pdf(f"static/file/{jenSur}-{kode_surat}.pdf", kode_surat, f"{hari} {kabisat} {tahun}", sur['rt'], sur['rw'], isiSur['data_pelapor']['Alamat'], romawi, tahun, isiSur['data_pelapor'], sur['keterangan_surat'])
                
            elif jenSur == "Surat Keterangan Pindah Wilayah" :
                
                kode_surat = db.surat.count_documents({"jenis_surat": "Surat Keterangan Pindah Wilayah", "status_surat": "Surat Disetujui"})
                if kode_surat : 
                    kode_surat = kode_surat + 1
                else :
                    kode_surat = 1
                # kode_surat = int(kode_surat)
                hari, bulan, tahun = gear.get_tanggal()
                kabisat =gear.get_kabisat(bulan)
                romawi = gear.get_romawi(bulan)
                print(jenSur)
                spw.create_pdf(f"static/file/{jenSur}-{kode_surat}.pdf", kode_surat, f"{hari} {kabisat} {tahun}", romawi, tahun, isiSur['data_pelapor']['Alamat'], sur['rw'], sur['rt'], isiSur['data_pelapor'], isiSur['nomorSPKTP'], isiSur['tglSPKTP'], sur['keterangan_surat'])
                
            elif jenSur == "Surat Keterangan Orang Yang Sama" :
                
                kode_surat = db.surat.count_documents({"jenis_surat": "Surat Keterangan Orang Yang Sama", "status_surat": "Surat Disetujui"})
                if kode_surat : 
                    kode_surat = kode_surat + 1
                else :
                    kode_surat = 1
                # kode_surat = int(kode_surat)
                hari, bulan, tahun = gear.get_tanggal()
                kabisat =gear.get_kabisat(bulan)
                romawi = gear.get_romawi(bulan)
                print(jenSur)
                soys.create_pdf(f"static/file/{jenSur}-{kode_surat}.pdf", kode_surat, f"{hari} {kabisat} {tahun}", romawi, tahun, isiSur['data_pelapor'], isiSur['dataBenar'], isiSur['dataSalah'], isiSur['dokumenBenar'], isiSur['dokumenSalah'], isiSur['nomorDokumenBenar'], isiSur['nomorDokumenSalah'], sur['keterangan_surat'])
                
            elif jenSur == "Surat Keterangan Tanggungan Keluarga" :
                
                kode_surat = db.surat.count_documents({"jenis_surat": "Surat Keterangan Tanggungan Keluarga", "status_surat": "Surat Disetujui"})
                if kode_surat : 
                    kode_surat = kode_surat + 1
                else :
                    kode_surat = 1
                # kode_surat = int(kode_surat)
                hari, bulan, tahun = gear.get_tanggal()
                kabisat =gear.get_kabisat(bulan)
                romawi = gear.get_romawi(bulan)
                print(jenSur)
                
                tanggunganKeluarga = {};
                x = 1;
                for tanggungan in isiSur["tanggungan_data"] :
                    tanggunganKeluarga[f'{x}'] = tanggungan
                    x += 1
                
                print(f"SALMAN ================================================================= {tanggunganKeluarga}")
                stk.create_pdf(f"static/file/{jenSur}-{kode_surat}.pdf", kode_surat, romawi, tahun, f"{hari} {kabisat} {tahun}", sur['tanggal_pengajuan'], isiSur['data_pelapor'], tanggunganKeluarga, sur['keterangan_surat'])
                
            db.surat.update_one({'suratId' : suratId}, {'$set' : {'status_surat' : 'Surat Disetujui', 'kode_surat' : kode_surat}})
            return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
    except:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Gagal diperbaharui"), 200 

@app.route("/update_surat_reject", methods=['POST'])
@jwt_required()
def update_surat_reject():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    user = db.users.find_one({'uId' : uId}, {'_id' : 0})
    
    suratId = request.form.get('suratId')
    suratId = int(suratId)
    riw = db.riwayat.find_one({'suratId' : suratId}, {"_id" : 0}, sort=[('waktu', -1)])
    uIdRiwayat = riw['uId']
    catatan = request.form.get('catatan')

    last_riwayat = db.riwayat.find_one(sort=[("riwayatId", -1)])
    if last_riwayat: riwayatId = last_riwayat['riwayatId'] + 1
    else: riwayatId = 1  

    jam, menit, detik = gear.get_waktu()
    hari, bulan, tahun = gear.get_tanggal()
    kabisat = gear.get_kabisat(bulan)
    
    try:
        if(user['jabatan'] == "Ketua RT"):
            db.surat.update_one({'suratId' : suratId}, {'$set' : {'status_surat' : 'Ditolak RT'}})
            data_riwayat = {
                "riwayatId" : riwayatId,
                "suratId" : suratId,
                "uId" : uIdRiwayat,
                "catatan" : catatan,
                "status_surat" : "Ditolak RT",
                "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
            }
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
        elif(user['jabatan'] == "Ketua RW"):
            db.surat.update_one({'suratId' : suratId}, {'$set' : {'status_surat' : 'Ditolak RW'}})
            data_riwayat = {
                "riwayatId" : riwayatId,
                "suratId" : suratId,
                "uId" : uIdRiwayat,
                "catatan" : catatan,
                "status_surat" : "Ditolak RW",
                "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
            }
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
        elif(user['jabatan'] == "Lurah"):
            db.surat.update_one({'suratId' : suratId}, {'$set' : {'status_surat' : 'Ditolak Lurah'}})
            data_riwayat = {
                "riwayatId" : riwayatId,
                "suratId" : suratId,
                "uId" : uIdRiwayat,
                "catatan" : catatan,
                "status_surat" : "Ditolak Lurah",
                "waktu" : f"{jam}:{menit}:{detik} • {hari} {kabisat} {tahun}"
            }
            db.riwayat.insert_one(data_riwayat)
            return jsonify(status='sukses', message="Berhasil diperbaharui"), 200
    except:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Gagal diperbaharui"), 200 

#UPDATE

#GET
@app.route("/get_users", methods=['GET'])
# @jwt_required()
@limiter.limit("20 per minute")
def get_users():
    data = list(db.users.find({}, {"_id": 0}))
    return jsonify(status= 'sukses', users = data)

@app.route("/get_permission", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_permission():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    data = db.permitted.find_one({"uId" : uId})
    data = serialize_mongo_data(data)
    return jsonify(status= 'sukses', permission = data)

@app.route("/get_user_personal", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_users_personal():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    data = db.users.find_one({"uId" : uId})
    data = serialize_mongo_data(data)
    return jsonify(status= 'sukses', users= data)

@app.route("/get_wilayah", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_wilayah():
    data = list(db.wilayah.find({}, {"_id": 0}))
    return jsonify(status= 'sukses', wilayah = data)

@app.route("/get_warga", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_warga():
    data = list(db.warga.find({}, {"_id": 0}))
    return jsonify(status= 'sukses', warga = data)

@app.route("/get_keluarga", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_keluarga():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    data = list(db.warga.find({'uId' : uId}, {"_id": 0}))
    return jsonify(status= 'sukses', keluarga = data)

@app.route("/get_rekom", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_rekom():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    user = db.users.find_one({"uId" : uId}, {"_id" : 0})
    rt_user = user['rt']
    rw_user = user['rw']
    data = list(db.rekom.find({"rt" : rt_user, "rw" : rw_user}, {"_id": 0}))
    users = []
    msg = ""
    for rekom in data :
        if rekom['status'] == "menunggu":
            x = db.users.find_one({"uId" : rekom['uId']}, {"_id" : 0})
            y = db.warga.find_one({'uId' : rekom['uId'], 'peran': "Kepala Keluarga"})
            if y :
                user_rekom = {
                "poto_profil" : x['poto_profil'],
                "gambar_kk" : x['gambar_kk'],
                "noHp" : x['noHp'],
                "noKK" : x['noKK'],
                "alamat" : x['alamat'],
                "uId" : rekom['uId'],
                "rekomId" : rekom['rekomId'],
                "status" : rekom['status'],
                "rt" : rekom['rt'],
                "rw" : rekom['rw'],
                "nama" : y['nama'],
                "nik" : y['nik'],
                }
                users.append(user_rekom)
            else : 
                msg = "Anggota keluarga tidak memiliki peran Kepala Keluarga"
    return jsonify(status= 'sukses', rekom = users, msg=msg)

@app.route("/get_rekom_personal", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_rekom_personal():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    data = db.rekom.find_one({'uId' : uId}, {"_id": 0})
    if data :
        return jsonify(status= 'sukses', rekom = data)
    else :
        return jsonify(status= 'gagal', rekom = "tidak ada")

@app.route("/get_rt_rw", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_rt_rw():
    ketua = list(db.warga.find({"jabatan" : {"$in": ["Ketua RT", "Ketua RW"]} }, {"_id" : 0}))
    data = []
    for i in ketua :
        user = (db.users.find_one({"uId" : i['uId']}, {'_id' : 0}))
        data.append({
                "nama" : i['nama'],
                "alamat" : user['alamat'],
                "noHp" : user['noHp'],
                "jabatan" : i['jabatan'],
                "rt" : user['rt'],
                "rw" : user['rw'],
                "poto_profil" : user['poto_profil']
        })
    return jsonify(status= 'sukses', rtrw = data)

@app.route("/get_surat", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_surat():
    data = list(db.surat.find({}, {"_id": 0}))
    return jsonify(status= 'sukses', surat = data)

@app.route("/get_riwayat", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_riwayat():
    current_user = get_jwt_identity()
    uId = current_user['uId']
    uId = int(uId)
    data = list(db.riwayat.find({}, {"_id": 0}))
    detail_surat = []
    for x in data:
        if x['uId'] == uId:
            surat = db.surat.find_one({'suratId': x['suratId']}, {"_id": 0})
            if surat:  # Pastikan surat ditemukan
                detail = {
                    "suratId": x['suratId'],
                    "riwayatId": x['riwayatId'],
                    "catatan": x['catatan'],
                    "waktu": x['waktu'],
                    "status_surat": x['status_surat'],
                    "jenis_surat": surat.get('jenis_surat', 'Jenis surat tidak ditemukan'),
                    "tanggal_pengajuan": surat.get('tanggal_pengajuan', 'Tanggal tidak ditemukan'),
                }
                detail_surat.append(detail)
            else:
                print(f"Surat dengan suratId {x['suratId']} tidak ditemukan.")

    return jsonify(status= 'sukses', riwayat = detail_surat)

@app.route("/get_all_riwayat", methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_all_riwayat():
    data = list(db.riwayat.find({}, {"_id": 0}))
    detail_surat = []
    for x in data:
        surat = db.surat.find_one({'suratId': x['suratId']}, {"_id": 0})
        if surat:  # Pastikan surat ditemukan
            detail = {
                "suratId": x['suratId'],
                "riwayatId": x['riwayatId'],
                "catatan": x['catatan'],
                "waktu": x['waktu'],
                "status_surat": x['status_surat'],
                "jenis_surat": surat.get('jenis_surat', 'Jenis surat tidak ditemukan'),
                "tanggal_pengajuan": surat.get('tanggal_pengajuan', 'Tanggal tidak ditemukan'),
            }
            detail_surat.append(detail)
        else:
            print(f"Surat dengan suratId {x['suratId']} tidak ditemukan.")

    return jsonify(status= 'sukses', riwayat = detail_surat)
#GET

#DELETE
@app.route("/del_users/<noKK>", methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def del_users(noKK):
    try:
        db.users.delete_one({"noKK": noKK})
        return jsonify(status= 'sukses', message="Berhasil dihapus")
    except:
        return jsonify(status= 'gagal', message="Gagal dihapus")


@app.route("/del_keluarga/<int:wargaId>", methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def del_keluarga(wargaId):
    wargaId = int(wargaId)
    try :
        db.warga.delete_one({"wargaId": wargaId})
        return jsonify(status='sukses', message = "Keluarga berhasil dihapus")
    except:
        return jsonify(status='gagal', message = "Keluarga gagal dihapus")

@app.route("/del_rekom", methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def del_rekom():
    rekomId = request.form.get('rekomId')
    rekomId = int(rekomId)
    try:
        db.rekom.delete_one({"rekomId": rekomId})
        return jsonify(status='sukses', message = "Berhasil ditolak")
    except:
        return jsonify(status='gagal', message = "Gagal ditolak")
#DELETE


# ---------------------Kode Tambahan---------------------
@app.route('/api/get_pdf/<jenis_surat>/<kode_surat>', methods=['GET'])
@jwt_required()
def get_pdf(jenis_surat, kode_surat):
    try:
        file_path = f"static/file/{jenis_surat}-{kode_surat}.pdf"
        return send_file(file_path, as_attachment=False)
    except FileNotFoundError:
        return jsonify(status='gagal', message="File tidak ditemukan"), 404
    
@app.route("/update_status_surat", methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def update_status_surat():
    # Ambil jabatan dari form
    statusSurat = request.form.get('status_surat')
    suratId = request.form.get('suratId')
    suratId = int(suratId)
    
    x = db.surat.find_one({"suratId": suratId}, {"_id" : 0})
    user = db.surat.find_one({"suratId": x['suratId']}, {"_id" : 0})
    suratId = user['suratId']
    
    if not statusSurat:
        return jsonify(status='gagal', message="Status Surat tidak boleh kosong"), 400

    try:
        # Update field jabatan saja
        # db.warga.update_one({"suratId": suratId}, {"$set": {"jabatan": jabatan}})
        db.surat.update_one({"suratId": suratId}, {"$set": {"status_surat": statusSurat}})
        return jsonify(status='sukses', message="Status surat berhasil diperbaharui"), 200
    except Exception as e:
        print("Gagal:", str(e))
        return jsonify(status='gagal', message="Gagal memperbaharui jabatan"), 500



if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
