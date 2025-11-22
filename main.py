"""
Main entry point untuk automation script SnapFlux menggunakan Playwright
Script ini mengotomatisasi pengambilan data transaksi dari platform merchant Pertamina
"""

import logging
import os
import sys
import time
from datetime import datetime

# Tambahkan direktori root ke path Python
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Import modul Playwright
from modules.browser.setup import PlaywrightBrowserManager
from modules.browser.extractor import get_stock_value_direct, get_tabung_terjual_direct

# Import utility dari PlayWRight local modules
from modules.data.excel import save_to_excel_pivot_format
from modules.browser.login import login_direct
from modules.browser.navigation import click_laporan_penjualan_direct, click_date_elements_direct
from modules.core.utils import (
    get_date_input,
    load_accounts_from_excel,
    print_account_stats,
    setup_logging,
)
from modules.core.validators import (
    is_valid_email,
    is_valid_phone,
    is_valid_pin,
    validate_username,
)

# Import enhanced configuration (backward compatible)
try:
    from modules.core.config import is_headless_mode as config_is_headless

    USE_ENHANCED_CONFIG = True
except ImportError:
    USE_ENHANCED_CONFIG = False

    def config_is_headless():
        return True


# Setup logger untuk tracking error
logger = logging.getLogger("automation")


def run_cek_stok_playwright(accounts, selected_date, headless_mode=None):
    """
    ============================================
    FUNGSI UTAMA: CEK STOK - PLAYWRIGHT VERSION
    ============================================

    Fungsi ini menjalankan fitur cek stok menggunakan Playwright yang meliputi:
    1. Login otomatis ke setiap akun merchant
    2. Navigasi ke halaman Atur Produk untuk cek stok
    3. Navigasi ke halaman Laporan Penjualan > Rekap Penjualan
    4. Mengambil data tabung terjual
    5. Menyimpan hasil ke Excel dengan format pivot

    Args:
        accounts (list): List akun merchant (nama, username, pin)
        selected_date (datetime): Tanggal yang dipilih user untuk filter
        headless_mode (bool): True untuk headless, False untuk GUI, None untuk auto-detect

    Returns:
        None: Menampilkan hasil dan menyimpan ke Excel
    """
    print(f"\nMemulai proses Cek Stok dengan Playwright...")
    if selected_date:
        print(f"Tanggal: {selected_date.strftime('%d %B %Y')}")
    else:
        print(f"Mode: TANPA filter tanggal spesifik")

    # Determine headless mode
    if headless_mode is None:
        # Check headless mode configuration
        if USE_ENHANCED_CONFIG:
            headless_mode = config_is_headless()
        else:
            headless_mode = True  # Default fallback

    if headless_mode:
        print("Browser akan berjalan dalam mode headless (tidak terlihat)")
    else:
        print("Browser akan berjalan dengan GUI visible (terlihat)")

    # Inisialisasi tracking
    total_start = time.time()
    results = []
    rekap = {
        "sukses": [],
        "gagal_login": [],
        "gagal_navigasi": [],
        "gagal_waktu": [],
        "gagal_masuk_akun": [],
        "gagal_masuk_akun_count": 0,
    }

    # Loop pemrosesan setiap akun
    for account_index, (nama, username, pin) in enumerate(accounts):
        print(f"\n{'=' * 60}")
        print(f"Memproses akun: {username} ({nama})")
        print(f"Progress: {account_index + 1}/{len(accounts)}")
        print(f"{'=' * 60}")

        akun_start = time.time()
        browser_manager = None
        page = None

        try:
            # Setup browser Playwright
            print("Inisialisasi Playwright Browser...")
            browser_manager = PlaywrightBrowserManager()
            page = browser_manager.setup_browser(headless=headless_mode)

            if not page:
                print("✗ Gagal setup browser Playwright")
                rekap["gagal_navigasi"].append(username)
                continue

            # Login ke akun merchant
            success, gagal_info = login_direct(page, username, pin)

            # Track gagal masuk akun
            if gagal_info.get("gagal_masuk_akun", False):
                rekap["gagal_masuk_akun"].append(username)
                rekap["gagal_masuk_akun_count"] += gagal_info.get("count", 0)

            if not success:
                print(f"✗ Login gagal untuk {username}")
                rekap["gagal_login"].append(username)
                browser_manager.close()
                continue

            print("✓ Login berhasil!")

            # === TAHAP 1: AMBIL STOK DARI DASHBOARD ===
            print("\n=== TAHAP 1: AMBIL STOK DARI DASHBOARD ===")
            stok_value = None

            # Ambil stok langsung dari dashboard (tidak perlu navigasi ke Atur Produk)
            stok_value = get_stock_value_direct(page)
            if stok_value:
                print(f"✓ Stok berhasil diambil dari dashboard: {stok_value} tabung")
            else:
                print("⚠ Gagal mengambil stok dari dashboard")

            # === TAHAP 2: NAVIGASI KE LAPORAN PENJUALAN & AMBIL TABUNG TERJUAL ===
            print("\n=== TAHAP 2: AMBIL DATA PENJUALAN ===")
            tabung_terjual = None

            # Navigasi ke Laporan Penjualan
            if click_laporan_penjualan_direct(page):
                print("✓ Berhasil masuk ke Laporan Penjualan")

                # === FILTER TANGGAL (4 STEPS) ===
                if selected_date:
                    print(f"📅 Menerapkan filter tanggal: {selected_date.strftime('%d/%m/%Y')}")
                    if click_date_elements_direct(page, selected_date):
                        print("✓ Filter tanggal berhasil diterapkan")
                    else:
                        print("⚠ Gagal menerapkan filter tanggal")
                # ================================

                # Ambil data tabung terjual langsung dari Data Penjualan
                # (tidak perlu klik Rekap Penjualan)
                tabung_terjual = get_tabung_terjual_direct(page)
                if tabung_terjual is not None:
                    print(f"✓ Tabung terjual berhasil diambil: {tabung_terjual} tabung")
                else:
                    print("⚠ Gagal mengambil tabung terjual")
            else:
                print("✗ Gagal navigasi ke Laporan Penjualan")

            # === SELESAI - TIDAK ADA PROSES LAIN ===

            # Simpan hasil dengan format yang sama seperti Selenium
            akun_waktu = time.time() - akun_start

            stok_formatted = f"{stok_value} Tabung" if stok_value else "0 Tabung"
            tabung_formatted = (
                f"{tabung_terjual} Tabung" if tabung_terjual is not None else "0 Tabung"
            )

            # Tentukan status penjualan
            if tabung_terjual and tabung_terjual > 0:
                status = "Ada Penjualan"
            else:
                status = "Tidak Ada Penjualan"

            result = {
                "pangkalan_id": username,  # Gunakan username sebagai ID
                "nama": nama,
                "username": username,
                "stok": stok_formatted,
                "tabung_terjual": tabung_formatted,
                "status": status,
                "waktu": akun_waktu,
            }
            results.append(result)
            rekap["sukses"].append(username)

            print(f"\n✓ Selesai memproses {username}")
            print(f"   Stok: {stok_formatted}")
            print(f"   Terjual: {tabung_formatted}")
            print(f"   ✓ Status: {status}")
            print(f"Waktu: {akun_waktu:.2f} detik")

        except Exception as e:
            print(f"✗ Error memproses {username}: {str(e)}")
            logger.error(f"Error memproses {username}: {str(e)}", exc_info=True)
            rekap["gagal_navigasi"].append(username)

        finally:
            # Cleanup browser
            if browser_manager:
                browser_manager.close()

            # Delay antar akun untuk anti-rate limiting
            if account_index < len(accounts) - 1:
                delay = 2.0
                print(f"Delay {delay} detik sebelum akun berikutnya...")
                time.sleep(delay)

    # === SIMPAN HASIL KE EXCEL ===
    print(f"\n{'=' * 60}")
    print("Menyimpan hasil ke Excel...")
    print(f"{'=' * 60}")

    if results:
        try:
            # Gunakan tanggal hari ini jika selected_date adalah None
            save_date = selected_date if selected_date else datetime.now()

            # Format tanggal untuk Excel
            tanggal_check = save_date.strftime("%Y-%m-%d")

            # Simpan setiap result ke Excel dengan format Selenium
            for result in results:
                try:
                    save_to_excel_pivot_format(
                        pangkalan_id=result["pangkalan_id"],
                        nama_pangkalan=result["nama"],
                        tanggal_check=tanggal_check,
                        stok_awal=result["stok"],
                        total_inputan=result["tabung_terjual"],
                        status=result["status"],
                        selected_date=save_date,
                    )
                    print(
                        f"  ✓ Saved: {result['nama']} - {result['stok']} / {result['tabung_terjual']}"
                    )
                except Exception as e:
                    print(f"  ✗ Error saving {result['nama']}: {str(e)}")

            print("\n✓ Semua data berhasil disimpan ke Excel!")
        except Exception as e:
            print(f"✗ Error menyimpan ke Excel: {str(e)}")
            logger.error(f"Error saving to Excel: {str(e)}", exc_info=True)

    # === TAMPILKAN REKAP ===
    total_waktu = time.time() - total_start
    print(f"\n{'=' * 60}")
    print("REKAP PROSES CEK STOK (PLAYWRIGHT)")
    print(f"{'=' * 60}")
    print(f"✓ Sukses: {len(rekap['sukses'])} akun")
    print(f"✗ Gagal Login: {len(rekap['gagal_login'])} akun")
    print(f"✗ Gagal Navigasi: {len(rekap['gagal_navigasi'])} akun")
    print(f"⚠ Gagal Masuk Akun: {rekap['gagal_masuk_akun_count']} kali")
    print(f"Total Waktu: {total_waktu:.2f} detik")
    print(f"{'=' * 60}")

    # Tampilkan detail hasil
    if results:
        print(f"\nDETAIL HASIL:")
        for result in results:
            print(
                f"  • {result['nama']} ({result['username']}): "
                f"Stok={result['stok']}, "
                f"Terjual={result['tabung_terjual']}, "
                f"Status={result['status']}, "
                f"Waktu={result['waktu']:.2f}s"
            )


def main():
    """
    Fungsi main untuk menjalankan automation Playwright
    """
    print("=" * 60)
    print("SNAPFLUX AUTOMATION - PLAYWRIGHT VERSION")
    print("=" * 60)

    # Setup logging
    try:
        setup_logging()
    except Exception:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    # Load accounts
    try:
        # Cari file akun di folder akun/
        akun_dir = os.path.join(os.path.dirname(__file__), "akun")

        # Cek apakah folder akun ada
        if not os.path.exists(akun_dir):
            print("✗ Folder 'akun' tidak ditemukan!")
            print(f"   Path: {os.path.abspath(akun_dir)}")
            print("\nCara membuat folder dan file akun:")
            print("   1. Buat folder 'akun' di root project")
            print("   2. Buat file Excel dengan kolom: Nama, Username, Password")
            print("   3. Isi data merchant Anda")
            return

        # Cari semua file Excel di folder akun
        try:
            excel_files = [
                f
                for f in os.listdir(akun_dir)
                if f.endswith((".xlsx", ".xls")) and not f.startswith("~")
            ]
        except Exception as e:
            print(f"✗ Error membaca folder akun: {e}")
            return

        if not excel_files:
            print("✗ Tidak ada file Excel ditemukan di folder akun/")
            print(f"   Path: {os.path.abspath(akun_dir)}")
            print("\nCara membuat file akun:")
            print("   1. Buat file Excel di folder 'akun'")
            print("   2. Tambahkan kolom: Nama, Username, Password")
            print("   3. Isi data merchant Anda")
            print("\n   Contoh:")
            print("   | Nama          | Username            | Password |")
            print("   | Pangkalan A   | merchant@email.com  | 123456   |")
            return

        # Gunakan file pertama yang ditemukan
        akun_file = os.path.join(akun_dir, excel_files[0])
        print(f"Membaca file: {excel_files[0]}")
        print(f"   Path: {os.path.abspath(akun_file)}")
        print()

        accounts = load_accounts_from_excel(akun_file)
        if not accounts:
            print("✗ Tidak ada akun valid ditemukan di file")
            print("\nPastikan file Excel memiliki:")
            print("   - Kolom: Nama, Username, Password")
            print("   - Data valid di setiap baris")
            print("   - Username berupa email atau nomor HP")
            print("   - Password berupa angka (PIN)")
            return

        print(f"✓ Berhasil load {len(accounts)} akun")
        try:
            print_account_stats(accounts)
        except Exception:
            print(f"   Total: {len(accounts)} akun")
    except FileNotFoundError as e:
        print(f"✗ File tidak ditemukan: {e}")
        print(f"   Path: {os.path.abspath(akun_dir)}")
        return
    except Exception as e:
        print(f"✗ Error loading accounts: {str(e)}")
        print(f"   Pastikan file Excel memiliki kolom: Nama, Username, Password")
        logger.error(f"Error loading accounts: {str(e)}", exc_info=True)
        return

    # Menu pilihan
    print()
    print("=" * 60)
    print("MENU UTAMA - PLAYWRIGHT VERSION")
    print("=" * 60)
    print("1. Cek Stok (Playwright)")
    print("2. Keluar")
    print("=" * 60)
    print()

    try:
        choice = input("Pilih menu (1-2): ").strip()

        if choice == "1":
            # Ask headless mode preference
            print()
            print("=" * 60)
            print("PILIH MODE BROWSER")
            print("=" * 60)
            print("1. Headless Mode (Browser tidak terlihat - Lebih Cepat)")
            print("2. GUI Mode (Browser terlihat - Untuk Debugging)")
            print("=" * 60)
            print()

            headless_choice = input("Pilih mode browser (1-2, default=1): ").strip()

            if headless_choice == "2":
                headless_mode = False
                print("✓ Mode: GUI Visible (Browser akan terlihat)")
            else:
                headless_mode = True
                print("✓ Mode: Headless (Browser tidak terlihat)")

            # Get tanggal
            try:
                selected_date = get_date_input()
            except EOFError:
                print("\n⚠ Input dibatalkan, menggunakan tanggal hari ini...")
                selected_date = datetime.now()
            except KeyboardInterrupt:
                print("\n⚠ Input dibatalkan oleh user")
                return
            except Exception as e:
                print(f"⚠ Error getting date input: {e}")
                print("Menggunakan tanggal hari ini...")
                selected_date = datetime.now()

            # Allow None for skipping date filter
            if selected_date is None:
                print("✓ Melanjutkan tanpa filter tanggal")
            else:
                print(f"✓ Menggunakan tanggal: {selected_date.strftime('%d/%m/%Y')}")

            print()

            # Jalankan cek stok dengan Playwright
            run_cek_stok_playwright(
                accounts, selected_date, headless_mode=headless_mode
            )

        elif choice == "2":
            print("Terima kasih!")
            return

        else:
            print("✗ Pilihan tidak valid")
            return

    except EOFError:
        print("\n\n⚠ Input error - Program dihentikan")
    except KeyboardInterrupt:
        print("\n\n⚠ Program dihentikan oleh user")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        logger.error(f"Error in main: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
