import pyodbc
from flask import Flask, jsonify, request
from flask_cors import CORS
from uuid import UUID, uuid4
import traceback
from distance import get_path, get_distance_and_duration
from submit_pengantaran import Pengantaran
from datetime import datetime
from math import ceil


app = Flask(__name__)
CORS(app)

server = 'database.windows.net'
database = 'database'
username = 'username'
password = 'password'
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

class DeliveryOrder:
    def __init__(self, id, product_code, product_name, opening_balance, qty_in, qty_out,
                 closing_balance, delivery_order, total_seharusnya, delivery_date,
                 updated_at, updated_by, created_at, created_by):
        self.id = id
        self.product_code = product_code
        self.product_name = product_name
        self.opening_balance = opening_balance
        self.qty_in = qty_in
        self.qty_out = qty_out
        self.closing_balance = closing_balance
        self.delivery_order = delivery_order
        self.total_seharusnya = total_seharusnya
        self.delivery_date = delivery_date
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.created_at = created_at
        self.created_by = created_by  # New field for created_by

    def to_dict(self):
        return {
            "id": self.id,
            "product_code": self.product_code,
            "product_name": self.product_name,
            "opening_balance": self.opening_balance,
            "qty_in": self.qty_in,
            "qty_out": self.qty_out,
            "closing_balance": self.closing_balance,
            "delivery_order": self.delivery_order,
            "total_seharusnya": self.total_seharusnya,
            "delivery_date": self.delivery_date,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
            "created_at": self.created_at,
            "created_by": self.created_by  # Include created_by in dictionary output
        }


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

@app.route('/add_delivery_order', methods=['POST'])
def add_delivery_order():
    data_list = request.json  # Expecting a list of data dictionaries

    if not isinstance(data_list, list):
        return jsonify({"error": "Request body must be a list of delivery order items."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for data in data_list:
            product_code = data.get('product_code')
            product_name = data.get('product_name')
            delivery_order = data.get('delivery_order')
            delivery_date = data.get('delivery_date')
            created_by = data.get('created_by')  # New field for created_by

            # Check for required fields in each item
            if not all([product_code, product_name, delivery_order, delivery_date, created_by]):
                return jsonify({"error": f"Missing fields in item with product_code {product_code}"}), 400

            # Check if the product_code and delivery_date already exist
            cursor.execute("""
                SELECT id FROM DeliveryOrder WHERE product_code = ? AND delivery_date = ?
            """, (product_code, delivery_date))
            existing_entry = cursor.fetchone()

            if existing_entry:
                # If exists, update the delivery_order
                cursor.execute("""
                    UPDATE DeliveryOrder
                    SET delivery_order = ?, updated_at = ?, updated_by = ?
                    WHERE product_code = ? AND delivery_date = ?
                """, (delivery_order, datetime.now(), created_by, product_code, delivery_date))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO DeliveryOrder (product_code, product_name, delivery_order, delivery_date, created_at, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (product_code, product_name, delivery_order, delivery_date, datetime.now(), created_by))

        conn.commit()
        return jsonify({"message": "Delivery orders added/updated successfully."}), 200

    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/get_delivery_order', methods=['GET'])
def get_delivery_order():
    cnxn = None
    cursor = None
    try:
        # Get page and page_size from query parameters, defaulting to 1 and 10
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        # Get start_date and end_date from query parameters for date range filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Database connection
        cnxn = get_db_connection()
        if cnxn is None:
            return jsonify({"message": "Database connection error"}), 500

        cursor = cnxn.cursor()

        # Get total count of items with date filtering
        count_query = "SELECT COUNT(*) FROM dbo.DeliveryOrder WHERE 1=1"
        params = []

        if start_date:
            count_query += " AND created_at >= ?"
            params.append(start_date)
        if end_date:
            count_query += " AND created_at <= ?"
            params.append(end_date)

        cursor.execute(count_query, *params)
        total_items = cursor.fetchone()[0]
        
        # Calculate total pages
        total_pages = ceil(total_items / page_size)

        # Query with pagination and date filtering, ordered by created_at descending
        offset = (page - 1) * page_size
        data_query = """
            SELECT 
                id, product_code, product_name, opening_balance, qty_in, qty_out,
                closing_balance, delivery_order, total_seharusnya, delivery_date,
                updated_at, updated_by, created_at, created_by
            FROM dbo.DeliveryOrder
            WHERE 1=1
        """

        if start_date:
            data_query += " AND created_at >= ?"
        if end_date:
            data_query += " AND created_at <= ?"

        data_query += " ORDER BY created_at DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, page_size])
        
        cursor.execute(data_query, *params)
        rows = cursor.fetchall()

        # Convert rows to list of dictionaries
        delivery_orders = [
            DeliveryOrder(
                id=row.id,
                product_code=row.product_code,
                product_name=row.product_name,
                opening_balance=row.opening_balance,
                qty_in=row.qty_in,
                qty_out=row.qty_out,
                closing_balance=row.closing_balance,
                delivery_order=row.delivery_order,
                total_seharusnya=row.total_seharusnya,
                delivery_date=row.delivery_date,
                updated_at=row.updated_at,
                updated_by=row.updated_by,
                created_at=row.created_at,
                created_by=row.created_by
            ).to_dict() for row in rows
        ]

        return jsonify({
            "data": delivery_orders,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            },
            "message": "Success"
        })

    except pyodbc.Error as e:
        # Handle and log error
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()


@app.route('/detail_delivery_order/<int:id>', methods=['GET'])
def get_delivery_order_by_id(id):
    cnxn = None
    cursor = None
    try:
        # Establish database connection
        cnxn = get_db_connection()
        if cnxn is None:
            return jsonify({"message": "Database connection error"}), 500

        cursor = cnxn.cursor()

        # Fetch delivery order by ID
        cursor.execute("""
            SELECT 
                id, product_code, product_name, opening_balance, qty_in, qty_out,
                closing_balance, delivery_order, total_seharusnya, delivery_date,
                updated_at, updated_by, created_at, created_by
            FROM dbo.DeliveryOrder
            WHERE id = ?
        """, id)
        
        row = cursor.fetchone()

        # If no record is found, return a 404 error
        if row is None:
            return jsonify({"message": "DeliveryOrder not found"}), 404

        # Convert result to dictionary
        order = DeliveryOrder(
            id=row.id,
            product_code=row.product_code,
            product_name=row.product_name,
            opening_balance=row.opening_balance,
            qty_in=row.qty_in,
            qty_out=row.qty_out,
            closing_balance=row.closing_balance,
            delivery_order=row.delivery_order,
            total_seharusnya=row.total_seharusnya,
            delivery_date=row.delivery_date,
            updated_at=row.updated_at,
            updated_by=row.updated_by,
            created_at=row.created_at,
            created_by=row.created_by  # Include created_by in response
        )

        return jsonify({
            "data": order.to_dict(),
            "message": "Success"
        })

    except pyodbc.Error as e:
        # Handle and log error
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()

@app.route('/delete_detail_delivery_order/<int:id>', methods=['DELETE'])
def delete_delivery_order_by_id(id):
    cnxn = None
    cursor = None
    try:
        # Establish database connection
        cnxn = get_db_connection()
        if cnxn is None:
            return jsonify({"message": "Database connection error"}), 500

        cursor = cnxn.cursor()

        # Delete delivery order by ID
        cursor.execute("""
            DELETE FROM dbo.DeliveryOrder
            WHERE id = ?
        """, id)
        
        # Commit the changes
        cnxn.commit()

        # Check if the order was deleted
        if cursor.rowcount == 0:
            return jsonify({"message": "DeliveryOrder not found"}), 404

        return jsonify({
            "message": "Delivery order deleted successfully"
        }), 200

    except pyodbc.Error as e:
        # Handle and log error
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()

@app.route('/edit_delivery_order/<int:id>', methods=['POST'])
def edit_delivery_order(id):
    cnxn = None
    cursor = None
    try:
        # Establish database connection
        cnxn = get_db_connection()
        if cnxn is None:
            return jsonify({"message": "Database connection error"}), 500

        cursor = cnxn.cursor()

        # Get data from the request body
        data = request.get_json()

        # Extract and validate values from the request data
        product_name = data.get('productName')
        delivery_order = data.get('deliveryOrder')
        updated_by = data.get('updatedBy') 
        delivery_date = data.get('deliveryDate')  # New field for delivery date in full ISO format
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check required fields
        if not product_name or not delivery_order or not updated_by:
            return jsonify({"message": "Missing required fields"}), 400

        # Validate and parse delivery_date in ISO format (yyyy-MM-ddTHH:mm:ss.sss)
        if delivery_date:
            try:
                parsed_date = datetime.strptime(delivery_date, '%Y-%m-%dT%H:%M:%S.%f')
                delivery_date = parsed_date.strftime('%Y-%m-%d')  # Store as 'yyyy-MM-dd'
            except ValueError:
                return jsonify({"message": "Invalid delivery date format. Use yyyy-MM-ddTHH:mm:ss.sss"}), 400
        else:
            delivery_date = None  # If no delivery date is provided, set it to None

        # Update the delivery order in the database
        if delivery_date:
            cursor.execute("""
                UPDATE dbo.DeliveryOrder
                SET product_name = ?, 
                    delivery_order = ?, 
                    updated_by = ?, 
                    updated_at = ?,
                    delivery_date = ?
                WHERE id = ?
            """, (product_name, delivery_order, updated_by, updated_at, delivery_date, id))
        else:
            cursor.execute("""
                UPDATE dbo.DeliveryOrder
                SET product_name = ?, 
                    delivery_order = ?, 
                    updated_by = ?, 
                    updated_at = ?
                WHERE id = ?
            """, (product_name, delivery_order, updated_by, updated_at, id))

        # Commit the transaction
        cnxn.commit()

        # Check if any rows were updated
        if cursor.rowcount == 0:
            return jsonify({"message": "Delivery order not found"}), 404

        return jsonify({"message": "Delivery order updated successfully"}), 200

    except pyodbc.Error as e:
        # Handle and log error
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Ensure resources are closed
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()

@app.route('/list_produk', methods=['GET'])
def get_products():
    cnxn = None
    cursor = None
    try:
        # Mendapatkan koneksi database
        cnxn = get_db_connection()
        if cnxn is None:
            return jsonify({"message": "Database connection error"}), 500

        cursor = cnxn.cursor()

        # Query data tanpa pagination
        cursor.execute("""
            SELECT 
                Name, ProductCode, Description, Stock, Unit, 
                BuyPrice, DefaultBuyAccountCode, DefaultBuyTaxName, 
                SellPrice, DefaultSellAccountCode, DefaultSellTaxName, 
                MinimumStock, ProductCategory
            FROM 
                dbo.Produk
        """)
        
        rows = cursor.fetchall()

        # Parsing hasil query ke dalam format JSON
        products = []
        for row in rows:
            product = {
                "Name": row.Name,
                "ProductCode": row.ProductCode,
                "Description": row.Description,
                "Stock": row.Stock,
                "Unit": row.Unit,
                "BuyPrice": row.BuyPrice,
                "DefaultBuyAccountCode": row.DefaultBuyAccountCode,
                "DefaultBuyTaxName": row.DefaultBuyTaxName,
                "SellPrice": row.SellPrice,
                "DefaultSellAccountCode": row.DefaultSellAccountCode,
                "DefaultSellTaxName": row.DefaultSellTaxName,
                "MinimumStock": row.MinimumStock,
                "ProductCategory": row.ProductCategory
            }
            products.append(product)

        return jsonify({
            "data": products,
            "message": "Success"
        })

    except pyodbc.Error as e:
        # Tangkap error database
        error_message = str(e)
        error_traceback = traceback.format_exc()
        return jsonify({"error": error_message, "traceback": error_traceback}), 500

    finally:
        # Tutup cursor dan koneksi setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()

@app.route('/get_produk/<nama>', methods=['GET'])
def get_produk(nama):
    cnxn = None
    cursor = None
    try:
        # Mendapatkan koneksi database
        cnxn = get_db_connection()
        cursor = cnxn.cursor()

        # Menjalankan query SQL menggunakan parameterized query untuk menghindari SQL Injection
        cursor.execute("""
            SELECT 
                Name, ProductCode, Description, Stock, Unit, 
                BuyPrice, DefaultBuyAccountCode, DefaultBuyTaxName, 
                SellPrice, DefaultSellAccountCode, DefaultSellTaxName, 
                MinimumStock, ProductCategory
            FROM 
                dbo.Produk
            WHERE 
                Name LIKE ?
        """, ('%' + nama + '%',))
        
        rows = cursor.fetchall()

        # Parsing hasil query ke dalam format JSON
        products = []
        for row in rows:
            product = {
                "Name": row.Name,
                "ProductCode": row.ProductCode,
                "Description": row.Description,
                "Stock": row.Stock,
                "Unit": row.Unit,
                "BuyPrice": row.BuyPrice,
                "DefaultBuyAccountCode": row.DefaultBuyAccountCode,
                "DefaultBuyTaxName": row.DefaultBuyTaxName,
                "SellPrice": row.SellPrice,
                "DefaultSellAccountCode": row.DefaultSellAccountCode,
                "DefaultSellTaxName": row.DefaultSellTaxName,
                "MinimumStock": row.MinimumStock,
                "ProductCategory": row.ProductCategory
            }
            products.append(product)

        # Mengembalikan hasil dalam format JSON
        return jsonify({"message": "Success", "data": products})

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
        # Pastikan cursor dan koneksi ditutup setelah selesai
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
