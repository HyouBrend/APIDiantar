
# Ini adalah pernyataan impor yang mengimpor 'app' dari modul 'ProjectJarak'.
from ProjectJarak import app

# Ini adalah pernyataan kondisional yang memeriksa apakah skrip ini sedang dijalankan sebagai skrip utama.
if __name__ == '__main__':
    # Jika skrip ini adalah skrip utama, maka 'app' (yang diimpor dari 'ProjectJarak') akan dijalankan.
    # 'app' di sini biasanya merujuk ke instance aplikasi Flask.
    # 'host' dan 'port' adalah argumen opsional yang menentukan di mana server akan berjalan.
    app.run(host='0.0.0.0', port=5002)