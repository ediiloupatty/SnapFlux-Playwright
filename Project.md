# Project Documentation: SnapFlux-Playwright

Dokumen ini menjelaskan struktur proyek, fungsi-fungsi kode yang digunakan, hubungan antar file, dan alur kerja sistem SnapFlux-Playwright.

## 📂 Struktur Proyek & Penjelasan Kode

Berikut adalah file-file inti yang digunakan dalam sistem ini beserta penjelasan fungsinya.

### 1. `main_gui.py` (Entry Point GUI)
File ini adalah titik awal aplikasi. Menggunakan library `Eel` untuk menghubungkan backend Python dengan frontend HTML/JS.

*   **Fungsi Utama:**
    *   `main()`: Menginisialisasi server Eel, mengecek lokasi Chrome, dan membuka window aplikasi.
    *   `start_automation(accounts, settings)`: Menerima request dari UI untuk memulai proses. Membuat thread baru yang menjalankan `run_automation_background`.
    *   `run_automation_background()`: Wrapper yang membuat instance `ProcessManager` dan menjalankannya. Menghubungkan callback logging UI ke proses background.
    *   `load_accounts_from_supabase()`: Mengambil daftar akun dari database via `SupabaseManager` untuk ditampilkan di UI.
    *   `save_results_as()`: Mengambil hasil dari database dan menyimpannya sebagai file Excel untuk di-download user.

### 2. `modules/core/process_manager.py` (Otak Sistem)
File ini berfungsi sebagai orkestrator yang mengatur alur bisnis logika.

*   **Fungsi Utama:**
    *   `run(accounts, settings)`: Loop utama yang memproses setiap akun satu per satu.
        1. Setup Browser (`PlaywrightBrowserManager`).
        2. Login (`login_direct`).
        3. Ambil Data Stok & Penjualan (`get_stock_value_direct`, `get_tabung_terjual_direct`).
        4. Simpan hasil ke `results` list dan database (`supabase_client`).
    *   `_handle_failure()`: Menangani error per akun (misal timeout, gagal login) agar tidak menghentikan seluruh proses.

### 3. `modules/browser/setup.py` (Pengaturan Browser)
Mengatur konfigurasi Playwright agar berjalan optimal, cepat, dan ringan.

*   **Fungsi Utama:**
    *   `PlaywrightBrowserManager.setup_browser(headless)`:
        *   Menggunakan argumen chromium flags ekstrim untuk performa (block images, disable GPU, disable extensions, dll).
        *   Menyuntikkan script untuk menyembunyikan identitas otomasi (bypassing bot detection).
        *   Return object `Page` yang siap digunakan.

### 4. `modules/browser/login.py` (Logika Login)
Menangani interaksi spesifik pada halaman login merchant.

*   **Fungsi Utama:**
    *   `login_direct(page, username, pin)`:
        *   Mencoba mengisi email/username dengan berbagai kemungkinan *selector* CSS.
        *   Mencoba mengisi PIN.
        *   Klik tombol masuk.
        *   Mendeteksi pesan error "Gagal Masuk Akun" dan melakukan retry otomatis setelah 2 menit jika diperlukan.
    *   `wait_for_dashboard(page)`: Memastikan login berhasil dengan mengecek apakah URL berubah atau elemen dashboard muncul.

### 5. `modules/browser/extractor.py` (Scraping Data)
Berisi logika untuk mengambil data teks dari halaman web. Menggunakan pendekatan "Direct Method" dengan berbagai strategi fallback.

*   **Fungsi Utama:**
    *   `get_stock_value_direct(page)`: Mengambil angka sisa stok tabung. Menggunakan regex untuk mencari pola angka di dekat kata "Stok" dan "Tabung".
    *   `get_tabung_terjual_direct(page)`: Mengambil angka penjualan dari halaman Laporan Penjualan. Menggunakan strategi regex untuk mencari "Total Tabung ... Terjual".
    *   `get_customer_list_direct(page)`: (Opsional) Mengambil detail tabel pembeli jika diperlukan.

### 6. `modules/data/supabase_client.py` (Koneksi Database)
Menangani semua komunikasi dengan database Cloud (Supabase).

*   **Fungsi Utama:**
    *   `fetch_accounts(company_filter)`: Mengambil list akun (`accounts` table) sesuai filter perusahaan user yang login.
    *   `update_account_result()`: Menyimpan hasil scraping (Stok, Terjual, Status) ke tabel `automation_results` secara real-time.
    *   `get_today_summary()`: Menghitung statistik hari ini (Total Sukses, Gagal, Total Penjualan) untuk dashboard.
    *   `get_stock_movement_today()`: Logika kompleks untuk menghitung selisih stok hari ini vs kemarin guna mendeteksi penjualan yang tidak tercatat.

### 7. `modules/data/export.py` (Excel Export)
Logic untuk membuat file output Excel.

*   **Fungsi Utama:**
    *   `export_results_to_excel()`: Menerima list data hasil, dan menulisnya ke file Excel (.xlsx) dengan formatting yang rapi.

---

## 🔗 Hubungan Antar Code (Code-to-Code Relationships)

Alur pemanggilan fungsi antar file berjalan sebagai berikut:

1.  **Frontend ke Backend:**
    Tombol "Start" di Web UI memanggil `eel.start_automation()` di `main_gui.py`.

2.  **Inisialisasi Proses:**
    `main_gui.py` membuat instance `ProcessManager` dan memanggil method `.run()`.

3.  **Loop Proses (di dalam `ProcessManager.run`):**
    *   **Setup:** Memanggil `PlaywrightBrowserManager.setup_browser()` dari `modules/browser/setup.py`.
    *   **Action:** Memanggil `login_direct()` dari `modules/browser/login.py`.
    *   **Extraction:** Jika login sukses, memanggil `get_stock_value_direct()` dan `get_tabung_terjual_direct()` dari `modules/browser/extractor.py`.
    *   **Storage:** Memanggil `supabase_manager.update_account_result()` dari `modules/data/supabase_client.py` untuk simpan ke cloud.

4.  **Feedback:**
    `ProcessManager` menggunakan callback (via `eel`) untuk update progress bar dan status text di UI secara real-time.

---

## ⚙️ Cara Kerja Sistem (Workflow)

1.  **Start:** User memilih akun dan menekan Start.
2.  **Batch Processing:** Sistem memproses akun satu per satu (Serial).
3.  **Worker Cycle (Per Akun):**
    *   Buka Browser (Headless/Hidden).
    *   Buka URL Login.
    *   Input Username & PIN -> Submit.
    *   *Check:* Jika gagal login, catat error, tutup browser, lanjut akun berikutnya.
    *   *Check:* Jika sukses login, navigasi ke Dashboard.
    *   Ambil **Data Stok**.
    *   Klik menu "Laporan Penjualan" -> Ambil **Data Terjual**.
    *   Hitung Status: "Ada Penjualan" jika Terjual > 0, else "Tidak Ada Penjualan".
    *   **Simpan Database:** Upload hasil ke Supabase.
    *   Tutup Browser.
4.  **Monitoring:** Selama proses, hasil langsung muncul di Dashboard Monitoring UI karena data diambil lagi dari Supabase.
5.  **Finish:** Setelah semua akun selesai, user bisa klik "Export Excel" yang akan memanggil `save_results_as()` untuk mengunduh report.

---
*Dokumen ini dibuat otomatis berdasarkan struktur kode SnapFlux-Playwright saat ini.*
