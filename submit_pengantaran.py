import pyodbc

def get_db_connection():
    try:
        cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=diantarin.database.windows.net;'
            'DATABASE=diantarin;'
            'UID=diantarin;'
            'PWD=4nomal1D1antar1n'
        )
        return cnxn
    except pyodbc.Error as e:
        raise Exception(f"Database connection failed: {e}")

class Pengantaran:
    def __init__(self, nomor_faktur, perjalanan_id, shift_ke, jam_pengiriman, jam_kembali,
                 urutan_pengiriman, driver_id, nama_driver, kontak_id, input_latitude,
                 input_longitude, tipe_kendaraan, nomor_polisi_kendaraan, google_map_url,
                 min_jarak_pengiriman, min_durasi_pengiriman, created_by, update_by):
        self.nomor_faktur = nomor_faktur
        self.perjalanan_id = perjalanan_id
        self.shift_ke = shift_ke
        self.jam_pengiriman = jam_pengiriman
        self.jam_kembali = jam_kembali
        self.urutan_pengiriman = urutan_pengiriman
        self.driver_id = driver_id
        self.nama_driver = nama_driver
        self.kontak_id = kontak_id
        self.input_latitude = input_latitude
        self.input_longitude = input_longitude
        self.tipe_kendaraan = tipe_kendaraan
        self.nomor_polisi_kendaraan = nomor_polisi_kendaraan
        self.google_map_url = google_map_url
        self.min_jarak_pengiriman = min_jarak_pengiriman
        self.min_durasi_pengiriman = min_durasi_pengiriman
        self.created_by = created_by
        self.update_by = update_by

    def submit_pengantaran_to_db(self):
        cnxn = None
        cursor = None
        try:
            # Mendapatkan koneksi ke database
            cnxn = get_db_connection()
            cursor = cnxn.cursor()
            
            # Eksekusi query menggunakan stored procedure
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
                self.nomor_faktur,
                str(self.perjalanan_id),
                self.shift_ke,
                self.jam_pengiriman,
                self.jam_kembali,
                self.urutan_pengiriman,
                self.driver_id,
                self.nama_driver,
                str(self.kontak_id),
                self.input_latitude,
                self.input_longitude,
                self.tipe_kendaraan,
                self.nomor_polisi_kendaraan,
                self.google_map_url,
                self.min_jarak_pengiriman,
                self.min_durasi_pengiriman,
                self.created_by,
                self.update_by
            )
            # Commit transaksi
            cnxn.commit()
        
        except pyodbc.DatabaseError as db_error:
            # Jika terjadi error pada database
            raise Exception(f"Database error: {db_error}")
        
        finally:
            # Pastikan cursor dan koneksi ditutup
            if cursor:
                cursor.close()
            if cnxn:
                cnxn.close()
