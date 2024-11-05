import pyodbc
from flask import Flask, jsonify, request
from flask_cors import CORS
from uuid import UUID, uuid4
from dotenv import load_dotenv
import traceback
from distance import get_path, get_distance_and_duration
from submit_pengantaran import Pengantaran
from datetime import datetime


app = Flask(__name__)
CORS(app)

# Directly assign the database connection details
server = 'diantarin.database.windows.net'
database = 'diantarin'
username = 'diantarin'
password = '4nomal1D1antar1n'
driver = 'ODBC Driver 17 for SQL Server'

# Function to get a database connection
def get_db_connection():
    try:
        # Use the curly braces {} around the driver name as required by pyodbc
        connection_string = f'DRIVER={{{driver}}};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
        app.logger.info(f"Connecting to the database: {database} on server: {server}")
        return pyodbc.connect(connection_string)
    except pyodbc.DatabaseError as db_error:
        app.logger.error(f"Database error: {db_error}")
        app.logger.error(f"Stack trace: {traceback.format_exc()}")
        return jsonify({"error": "Internal Server Error", "details": str(db_error)}), 500


@app.route('/')
def index():
    return "Koneksi berhasil!"

class Kontak:
    def __init__(self, KontakID, DisplayName, Type, lokasi, latitude, longitude):
        self.KontakID = KontakID
        self.DisplayName = DisplayName
        self.Type = Type
        self.lokasi = lokasi
        self.latitude = latitude
        self.longitude = longitude
        self.nomor_faktur = ""
        self.urutan_pengiriman = 0
    
    def to_dict(self):
        return {
            "KontakID": self.KontakID,
            "DisplayName": self.DisplayName,
            "type": self.Type,
            "lokasi": self.lokasi,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
        
class Karyawan:
    def __init__(self, KaryawanID, Nama, Posisi, NoHP):
        self.KaryawanID = KaryawanID
        self.Nama = Nama
        self.Posisi = Posisi
        self.NoHP = NoHP

class SubmitPerjalanan:
    def __init__(self, KaryawanID, Nama, Posisi, NoHP):
        self.KaryawanID = KaryawanID
        self.Nama = Nama
        self.Posisi = Posisi
        self.NoHP = NoHP
        self.Kontaks = []
    
    def add_kontak(self, kontak):
        self.Kontaks.append(kontak)  # Fungsi untuk menambahkan objek Kontak ke dalam list Kontaks

class HistoryPengantaranFilter:
    def __init__(self, nama_driver, created_by, status, timeline):
        self.nama_driver = nama_driver
        self.created_by = created_by
        self.status = status
        self.timeline = timeline

class ReturnCekGoogle:
    def __init__(self, min_distance, min_duration, google_maps_url, list_kontaks):
        self.min_distance = min_distance
        self.min_duration = min_duration
        self.list_kontaks = list_kontaks
        self.google_maps_url = google_maps_url
    
    def to_dict(self):
        # Assuming ReturnSubmitPerjalanan has attributes like min_distance, total_distance, etc.
        # Convert all necessary attributes to a dictionary
        return {
            "min_distance": self.min_distance,
            "min_duration": self.min_duration,
            "google_maps_url": self.google_maps_url,
            "kontaks": self.list_kontaks  # Assuming Kontak objects can also be serialized to dict
        }

class SubmitPengantaran:
    def __init__(self, shift_ke, jam_pengiriman, jam_kembali, driver_id, nama_driver,
                 tipe_kendaraan, nomor_polisi_kendaraan, google_maps_url, min_jarak_pengiriman, 
                 min_durasi_pengiriman, created_by):
        self.shift_ke = shift_ke
        self.jam_pengiriman = jam_pengiriman
        self.jam_kembali = jam_kembali
        self.driver_id = driver_id
        self.nama_driver = nama_driver
        self.tipe_kendaraan = tipe_kendaraan
        self.nomor_polisi_kendaraan = nomor_polisi_kendaraan
        self.google_maps_url = google_maps_url
        self.min_jarak_pengiriman = min_jarak_pengiriman
        self.min_durasi_pengiriman = min_durasi_pengiriman
        self.created_by = created_by
        self.Kontaks = []
    
    def add_kontak(self, kontak):
        self.Kontaks.append(kontak) 
        
class HistoryPengantaran:
    def __init__(self, perjalanan_id, shift_ke, jam_pengiriman, jam_kembali, 
                 nama_driver, tipe_kendaraan, nomor_polisi_kendaraan, 
                 min_jarak_pengiriman, min_durasi_pengiriman, created_by, 
                 created_at, status):
        self.perjalanan_id = perjalanan_id
        self.shift_ke = shift_ke
        self.jam_pengiriman = jam_pengiriman
        self.jam_kembali = jam_kembali
        self.nama_driver = nama_driver
        self.tipe_kendaraan = tipe_kendaraan
        self.nomor_polisi_kendaraan = nomor_polisi_kendaraan
        self.min_jarak_pengiriman = min_jarak_pengiriman
        self.min_durasi_pengiriman = min_durasi_pengiriman
        self.created_by = created_by
        self.created_at = created_at
        self.status = status


def _build_response(data, page, page_size, total_items):
    """Membangun respons dengan pagination dan navigasi halaman."""
    total_pages = (total_items + page_size - 1) // page_size  # Hitung total halaman

    return {
        "data": data,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        }
    }
    

class DetailPengantaran:
    def __init__(self, PengantaranID, NomorFaktur, PerjalananID, ShiftKe, JamPengiriman, JamKembali, UrutanPengiriman,
                 DriverID, NamaDriver, KontakID, Input_latitude, Input_longitude, TipeKendaraan, NomorPolisiKendaraan, 
                 GoogleMapsURL, MinJarakPengiriman, MinDurasiPengiriman, CreatedBy, CreatedDate, UpdateBy, UpdateDate,
                 DisplayName, lokasi, Posisi, NoHP, Status):
        self.pengantaran_id = PengantaranID
        self.nomor_faktur = NomorFaktur
        self.perjalanan_id = PerjalananID
        self.shift_ke = ShiftKe
        self.jam_pengiriman = JamPengiriman
        self.jam_kembali = JamKembali
        self.urutan_pengiriman = UrutanPengiriman
        self.driver_id = DriverID
        self.nama_driver = NamaDriver
        self.KontakID = KontakID
        self.Input_latitude = Input_latitude
        self.Input_longitude = Input_longitude
        self.tipe_kendaraan = TipeKendaraan
        self.nomor_polisi_kendaraan = NomorPolisiKendaraan
        self.GoogleMapsURL = GoogleMapsURL
        self.min_jarak_pengiriman = MinJarakPengiriman
        self.min_durasi_pengiriman = MinDurasiPengiriman
        self.created_by = CreatedBy
        self.created_date = CreatedDate
        self.update_by = UpdateBy
        self.update_at = UpdateDate
        self.display_name = DisplayName
        self.lokasi = lokasi
        self.posisi = Posisi
        self.no_hp = NoHP
        self.status = Status

class UpdateDetailPengantaran:
    def __init__(self, pengantaran_id, perjalanan_id, nomor_faktur, update_by):
        self.pengantaran_id = pengantaran_id
        self.perjalanan_id = perjalanan_id
        self.nomor_faktur = nomor_faktur
        self.update_by = update_by

class UpdateDetailPerjalanan:
    def __init__(self, perjalanan_id, shift_ke, jam_pengiriman, jam_kembali,
                 update_by, status):
        self.perjalanan_id = perjalanan_id
        self.shift_ke = shift_ke
        self.jam_pengiriman = jam_pengiriman
        self.jam_kembali = jam_kembali
        self.update_by = update_by
        self.status = status

@app.route('/update_detail_perjalanan', methods=['POST'])
def update_detail_perjalanan():
    cnxn = None
    cursor = None
    try:
        data = request.json

        # Membuat objek UpdateDetailPerjalanan dari data yang diterima
        update_detail_perjalanan = UpdateDetailPerjalanan(
            data['perjalanan_id'], data['shift_ke'], data['jam_pengiriman'],
            data['jam_kembali'], data['update_by'], data['status']
        )

        # Mendapatkan koneksi database
        cnxn = get_db_connection()
        cursor = cnxn.cursor()

        # Eksekusi Stored Procedure untuk memperbarui detail perjalanan
        cursor.execute('''
            EXEC UpdateDetailPerjalanan
                @PerjalananID = ?,
                @ShiftKe = ?,
                @JamPengiriman = ?,
                @JamKembali = ?,
                @UpdateBy = ?,
                @Status = ?
            ''',
            update_detail_perjalanan.perjalanan_id,
            update_detail_perjalanan.shift_ke,
            update_detail_perjalanan.jam_pengiriman,
            update_detail_perjalanan.jam_kembali,
            update_detail_perjalanan.update_by,
            update_detail_perjalanan.status
        )

        # Commit transaksi setelah eksekusi
        cnxn.commit()

        return jsonify({"message": "Update Detail Perjalanan Berhasil!"})

    except pyodbc.Error as e:
        # Tangkap dan parsing error yang terjadi
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Tutup cursor dan koneksi setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()


@app.route('/update_detail_pengantaran', methods=['POST'])
def update_detail_pengantaran():
    cnxn = None
    cursor = None
    try:
        data = request.json

        # Membuat objek UpdateDetailPengantaran dari data yang diterima
        update_detail_pengantaran = UpdateDetailPengantaran(
            data['pengantaran_id'], data['perjalanan_id'], 
            data['nomor_faktur'], data['update_by']
        )

        # Mendapatkan koneksi database
        cnxn = get_db_connection()
        cursor = cnxn.cursor()

        # Eksekusi Stored Procedure untuk memperbarui detail pengantaran
        cursor.execute('''
            EXEC UpdateDetailPengantaran
                @PengantaranID = ?,
                @PerjalananID = ?,
                @NomorFaktur = ?,
                @UpdateBy = ?
            ''',
            update_detail_pengantaran.pengantaran_id,
            update_detail_pengantaran.perjalanan_id,
            update_detail_pengantaran.nomor_faktur,
            update_detail_pengantaran.update_by
        )

        # Commit transaksi setelah eksekusi
        cnxn.commit()

        return jsonify({"message": "Update Detail Pengantaran Berhasil!"})

    except pyodbc.Error as e:
        # Tangkap dan parsing error yang terjadi
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Tutup cursor dan koneksi setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()

@app.route('/detail_pengantaran/<perjalanan_id>', methods=['GET'])
def detail_pengantaran(perjalanan_id):
    cnxn = None
    cursor = None
    try:
        # Mendapatkan koneksi database melalui fungsi get_db_connection
        cnxn = get_db_connection()
        if cnxn is None:
            return jsonify({"message": "Database connection error"}), 500

        cursor = cnxn.cursor()

        # Menjalankan query SQL atau stored procedure
        cursor.execute('''
            EXEC DetailPengantaran
                @PerjalananID = ?
            ''',
            perjalanan_id
        )
        rows = cursor.fetchall()

        # Memproses hasil query dan mengembalikan dalam format JSON
        if not rows:
            return jsonify({"message": "No data found", "data": []}), 404

        list_detail_pengantaran = []
        for row in rows:
            detail_pengantaran = DetailPengantaran(*row)
            list_detail_pengantaran.append(detail_pengantaran.__dict__)

        return jsonify({"message": "Success", "data": list_detail_pengantaran})

    except pyodbc.Error as e:
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Tutup cursor dan koneksi setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()
            
@app.route('/history_pengantaran', methods=['POST'])
def history_pengantaran():
    cnxn = get_db_connection()
    if not cnxn:
        return jsonify({"message": "Database connection error"}), 500
    cursor = cnxn.cursor()
    try:
        # Ambil parameter dari request JSON
        data = request.json
        nama_driver = data.get('nama_driver', '')
        created_by = data.get('created_by', '')
        status = data.get('status', '')
        timeline = data.get('timeline', '')  # Ambil parameter timeline
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        page = max(int(request.args.get('page', 1)), 1)
        page_size = max(int(request.args.get('page_size', 10)), 1)

        # Parsing tanggal jika diberikan
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Eksekusi SP untuk mendapatkan seluruh data (tanpa pagination)
        cursor.execute('''
            EXEC [dbo].[HistoryPengantaran] 
                @CreatedBy = ?, 
                @NamaDriver = ?, 
                @Status = ?, 
                @Timeline = ?,  
                @StartDate = ?, 
                @EndDate = ?, 
                @PageNumber = ?, 
                @PageSize = ?
        ''', created_by, nama_driver, status, timeline, start_date, end_date,1, 1000000)
        
        all_rows = cursor.fetchall()  # Ambil semua data terlebih dahulu
        total_items = len(all_rows)  # Hitung total items

        # Hitung total pages
        total_pages = (total_items + page_size - 1) // page_size

        # Ambil data untuk halaman saat ini
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        page_rows = all_rows[start_index:end_index]  # Ambil data sesuai halaman

        if not page_rows:
            return jsonify({
                "message": "No data found", 
                "data": []
            }), 404

        # Ambil nama kolom dan hapus TotalJarakKeseluruhan
        columns = [column[0] for column in cursor.description]
        columns = [col for col in columns if col != 'TotalJarakKeseluruhan']

        # Simpan total jarak keseluruhan jika ada driver yang dipilih
        total_jarak = None
        if nama_driver and page_rows:
            # Ambil semua kolom untuk mendapatkan TotalJarakKeseluruhan
            all_columns = [column[0] for column in cursor.description]
            temp_dict = dict(zip(all_columns, page_rows[0]))
            total_jarak = temp_dict.get('TotalJarakKeseluruhan')

        # Buat list_history tanpa TotalJarakKeseluruhan
        list_history = []
        for row in page_rows:
            row_dict = dict(zip(columns, [r for i, r in enumerate(row) if cursor.description[i][0] != 'TotalJarakKeseluruhan']))
            list_history.append(row_dict)

        # Buat response
        response = {
            "data": list_history
        }

        # Tambahkan total jarak keseluruhan di atas pagination jika driver dipilih
        if nama_driver and total_jarak is not None:
            response["total_jarak_keseluruhan"] = total_jarak

        # Tambahkan pagination
        response["pagination"] = {
            "current_page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }
        
        return jsonify(response), 200

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        cnxn.close()
        
@app.route('/submit_pengantaran', methods=['POST'])
def submit_pengantaran():
    cnxn = None
    cursor = None
    try:
        data = request.json
        _perjalanan_id = uuid4()
        
        cnxn = get_db_connection()
        cursor = cnxn.cursor()

        for kontak in data['kontaks']:
            cursor.execute('''
                EXEC InsertPengantaran
                    @NomorFaktur = ?,
                    @PerjalananID = ?,
                    @ShiftKe = ?,
                    @JamPengirimanstr = ?,
                    @JamKembalistr = ?,
                    @UrutanPengiriman = ?,
                    @DriverID = ?,
                    @NamaDriver = ?,
                    @KontakID = ?,
                    @Input_latitude = ?,
                    @Input_longitude = ?,
                    @TipeKendaraan = ?,
                    @NomorPolisiKendaraan = ?,
                    @google_map_url = ?,
                    @MinJarakPengiriman = ?,
                    @MinDurasiPengiriman = ?,
                    @CreatedBy = ?,
                    @UpdateBy = ?
            ''',
            kontak['nomor_faktur'], 
            str(_perjalanan_id), 
            data['shift_ke'], 
            data['jam_pengiriman'], 
            data['jam_kembali'], 
            kontak['urutan_pengiriman'], 
            data['driver_id'], 
            data['nama_driver'], 
            kontak['KontakID'], 
            kontak['latitude'], 
            kontak['longitude'], 
            data['tipe_kendaraan'], 
            data['nomor_polisi_kendaraan'], 
            data['google_maps_url'], 
            data['min_distance'], 
            data['min_duration'], 
            data['created_by'], 
            data['created_by'])

        # Commit transaksi setelah eksekusi query selesai
        cnxn.commit()

        return jsonify({"message": "Insert Berhasil!"})

    except pyodbc.Error as e:
        # Tangkap dan parsing error database yang terjadi
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    except Exception as e:
        # Tangkap dan parsing error umum yang terjadi
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Tutup cursor dan koneksi setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()

@app.route('/cek_google', methods=['POST'])
def submit_perjalanan():
    cnxn = None
    cursor = None
    try:
        # Ambil data dari body request
        data = request.json

        # Buat koneksi ke database
        cnxn = get_db_connection()
        cursor = cnxn.cursor()

        # Inisiasi perjalanan
        submit_perjalanan = SubmitPerjalanan(data['KaryawanID'], data['Nama'], data['Posisi'], data['NoHP'])
        
        # Proses kontak
        for kontak in data['Kontaks']:
            _kontak = Kontak(kontak['KontakID'], kontak['DisplayName'], kontak['Type'], kontak['lokasi'], kontak['latitude'], kontak['longitude'])
            submit_perjalanan.add_kontak(_kontak)
        
        # Memisahkan pelanggan yang memiliki dan tidak memiliki latitude/longitude
        valid_customers = [kontak for kontak in submit_perjalanan.Kontaks if kontak.latitude and kontak.longitude]
        invalid_customers = [kontak for kontak in submit_perjalanan.Kontaks if not (kontak.latitude and kontak.longitude)]

        # Mengumpulkan poin hanya untuk pelanggan dengan lokasi valid
        points = [f"{kontak.latitude},{kontak.longitude}" for kontak in valid_customers]

        # Hitung rute hanya untuk pelanggan dengan lokasi valid
        efficient_path, min_distance, min_duration = get_path(points)

        # Urutkan berdasarkan rute yang efisien untuk pelanggan dengan lokasi valid
        sorted_kontaks = []
        for point in efficient_path:
            for kontak in valid_customers:
                latitude_str, longitude_str = point.split(',')
                if (kontak.latitude, kontak.longitude) == (latitude_str, longitude_str):
                    sorted_kontaks.append(kontak.__dict__)

        # Tambahkan pelanggan tanpa lokasi di akhir urutan pengiriman
        for kontak in invalid_customers:
            sorted_kontaks.append(kontak.__dict__)

        # Tambahkan urutan pengiriman
        for index, kontak in enumerate(sorted_kontaks, start=1):
            kontak['urutan_pengiriman'] = index

        # Generate Google Maps URL untuk pelanggan yang valid
        if points:
            maps = "/".join(efficient_path)
            google_maps_url = f"https://www.google.com/maps/dir/{maps.replace(' ', '')}"
        else:
            google_maps_url = "No valid locations for route generation."

        # Hasil akhir
        result = ReturnCekGoogle(min_distance, min_duration, google_maps_url, sorted_kontaks)
        return jsonify({"message": "Welcome to the Flask API", "data": result.to_dict()})

    except Exception as e:
        # Tangkap dan parsing error yang terjadi
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Tutup cursor dan koneksi setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()


@app.route('/list_pelanggan', methods=['GET'])
def get_list_pelanggan():
    cnxn = None
    cursor = None
    try:
        # Mendapatkan koneksi database
        cnxn = get_db_connection()
        if cnxn is None:
            return jsonify({"message": "Database connection error"}), 500

        cursor = cnxn.cursor()

        # Menjalankan query SQL
        cursor.execute("""
            SELECT [KontakID], [DisplayName], [Type], [lokasi], [latitude], [longitude]
            FROM [dbo].[Kontak]
            WHERE latitude IS NOT NULL
        """)
        rows = cursor.fetchall()

        # Parsing hasil query ke dalam format JSON
        kontaks = []
        for row in rows:
            kontak = Kontak(*row)
            kontaks.append(kontak.__dict__)

        return jsonify({"message": "Success", "data": kontaks})

    except pyodbc.DatabaseError as db_error:
        app.logger.error(f"Database error: {db_error}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        return jsonify({"message": "Database error occurred"}), 500

    except Exception as e:
        app.logger.error(f"General error: {e}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        return jsonify({"message": "An error occurred"}), 500

    finally:
        # Pastikan cursor dan koneksi ditutup setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()

@app.route('/get_pelanggan/<pelanggan>', methods=['GET'])
def get_pelanggan(pelanggan):
    cnxn = None
    cursor = None
    try:
        # Mendapatkan koneksi database
        cnxn = get_db_connection()
        if cnxn is None:
            return jsonify({"message": "Database connection error"}), 500

        cursor = cnxn.cursor()

        # Menjalankan query SQL menggunakan parameterized query
        cursor.execute("""
            SELECT [KontakID], [DisplayName], [Type], [lokasi], [latitude], [longitude]
            FROM [dbo].[Kontak]
            WHERE DisplayName LIKE ?
        """, ('%' + pelanggan + '%',))
        
        rows = cursor.fetchall()

        # Parsing hasil query ke dalam format JSON
        kontaks = []
        for row in rows:
            kontak = Kontak(*row)
            kontaks.append(kontak.__dict__)

        return jsonify({"message": "Success", "data": kontaks})

    except pyodbc.DatabaseError as db_error:
        app.logger.error(f"Database error: {db_error}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        return jsonify({"message": "Database error occurred"}), 500

    except Exception as e:
        app.logger.error(f"General error: {e}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        return jsonify({"message": "An error occurred"}), 500

    finally:
        # Pastikan cursor dan koneksi ditutup setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()
            
@app.route('/get_pelanggan/<pelanggan>', methods=['GET'])
def get_pelanggan_by_name(pelanggan):  # Mengganti nama function
    cnxn = None
    cursor = None
    try:
        # Mendapatkan koneksi database
        cnxn = get_db_connection()
        if cnxn is None:
            return jsonify({"message": "Database connection error"}), 500

        cursor = cnxn.cursor()

        # Menjalankan query SQL menggunakan parameterized query
        cursor.execute("""
            SELECT [KontakID], [DisplayName], [Type], [lokasi], [latitude], [longitude]
            FROM [dbo].[Kontak]
            WHERE DisplayName LIKE ?
        """, ('%' + pelanggan + '%',))
        
        rows = cursor.fetchall()

        # Parsing hasil query ke dalam format JSON
        kontaks = []
        for row in rows:
            kontak = Kontak(*row)
            kontaks.append(kontak.__dict__)

        return jsonify({"message": "Success", "data": kontaks})

    except pyodbc.DatabaseError as db_error:
        app.logger.error(f"Database error: {db_error}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        return jsonify({"message": "Database error occurred"}), 500

    except Exception as e:
        app.logger.error(f"General error: {e}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        return jsonify({"message": "An error occurred"}), 500

    finally:
        # Pastikan cursor dan koneksi ditutup setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()

@app.route('/list_driver', methods=['GET'])
def get_list_supir():
    cnxn = None
    cursor = None
    try:
        # Mendapatkan koneksi database dari fungsi get_db_connection
        cnxn = get_db_connection()
        cursor = cnxn.cursor()

        # Menjalankan query SQL
        cursor.execute("""
            SELECT [KaryawanID], [Nama], [Posisi], [NoHP]
            FROM [dbo].[Karyawan]
            WHERE Posisi = 'supir'
        """)
        rows = cursor.fetchall()

        # Parsing hasil query ke dalam format JSON
        karyawans = []
        for row in rows:
            karyawan = {
                "KaryawanID": row.KaryawanID,
                "Nama": row.Nama,
                "Posisi": row.Posisi,
                "NoHP": row.NoHP
            }
            karyawans.append(karyawan)

        # Mengembalikan hasil dalam format JSON
        return jsonify({"message": "Success", "data": karyawans})

    except pyodbc.DatabaseError as db_error:
        # Log the error in detail
        app.logger.error(f"Database error: {db_error}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        error_message = {"error": str(db_error)}
        return jsonify({"message": "Database error occurred", "error": error_message}), 500

    except Exception as e:
        # Menangani error umum lainnya
        app.logger.error(f"General error: {e}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        error_message = {"error": str(e)}
        return jsonify({"message": "An error occurred", "error": error_message}), 500

    finally:
        # Pastikan cursor ditutup jika ada
        if cursor:
            cursor.close()
        # Pastikan koneksi ditutup setelah selesai atau jika terjadi error
        if cnxn:
            cnxn.close()

@app.route('/get_driver/<nama>', methods=['GET'])
def get_supir(nama):
    cnxn = None
    cursor = None
    try:
        # Mendapatkan koneksi database
        cnxn = get_db_connection()
        cursor = cnxn.cursor()

        # Menjalankan query SQL menggunakan parameterized query untuk menghindari SQL Injection
        cursor.execute("""
            SELECT [KaryawanID], [Nama], [Posisi], [NoHP]
            FROM [dbo].[Karyawan]
            WHERE Posisi = 'supir' AND Nama LIKE ?
        """, ('%' + nama + '%',))
        
        rows = cursor.fetchall()

        # Parsing hasil query ke dalam format JSON
        karyawans = []
        for row in rows:
            karyawan = {
                "KaryawanID": row.KaryawanID,
                "Nama": row.Nama,
                "Posisi": row.Posisi,
                "NoHP": row.NoHP
            }
            karyawans.append(karyawan)

        # Mengembalikan hasil dalam format JSON
        return jsonify({"message": "Success", "data": karyawans})

    except pyodbc.DatabaseError as db_error:
        # Jika ada error pada database, log detail error
        app.logger.error(f"Database error: {db_error}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        error_message = {"error": str(db_error)}
        return jsonify({"message": "Database error occurred", "error": error_message}), 500

    except Exception as e:
        # Menangani error umum lainnya
        app.logger.error(f"General error: {e}")
        app.logger.error("Stack trace: " + traceback.format_exc())
        error_message = {"error": str(e)}
        return jsonify({"message": "An error occurred", "error": error_message}), 500

    finally:
        # Pastikan cursor ditutup
        if cursor:
            cursor.close()
        # Pastikan koneksi ditutup setelah selesai
        if cnxn:
            cnxn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
