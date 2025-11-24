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
from modules.core.process_manager import ProcessManager
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

    # Callbacks untuk CLI
    def on_log(message, level):
        prefix = "✓" if level == "success" else "✗" if level == "error" else "⚠" if level == "warning" else "ℹ"
        # Filter some verbose logs if needed, or just print all
        if level in ["success", "error", "warning"] or "Memproses" in message:
            print(f"{prefix} {message}")
            
    def on_progress(current, total, percent):
        # Simple progress indicator
        pass

    def on_account_status(account_id, status, progress):
        pass
        
    def on_result(result):
        # Print result immediately
        print(f"   Stok: {result['stok']}")
        print(f"   Terjual: {result['tabung_terjual']}")
        print(f"   Status: {result['status']}")

    # Setup Manager
    callbacks = {
        "on_log": on_log,
        "on_progress": on_progress,
        "on_account_status": on_account_status,
        "on_result": on_result
    }
    
    manager = ProcessManager(callbacks)
    
    # Settings
    settings = {
        "headless": headless_mode,
        "date_obj": selected_date,
        "delay": 2.0
    }
    
    # Run
    start_time = time.time()
    results = manager.run(accounts, settings)
    total_waktu = time.time() - start_time
    
    # Summary
    print(f"\n{'=' * 60}")
    print("REKAP PROSES CEK STOK (PLAYWRIGHT)")
    print(f"{'=' * 60}")
    print(f"Total Akun: {len(accounts)}")
    print(f"Berhasil: {len(results)}")
    print(f"Total Waktu: {total_waktu:.2f} detik")
    print(f"{'=' * 60}")


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
