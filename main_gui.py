"""
Main GUI entry point untuk SnapFlux Automation menggunakan Eel
File ini menjalankan web-based GUI dengan Python backend
"""

import json

# Import config
try:
    from config import HEADLESS_MODE
except ImportError:
    HEADLESS_MODE = False  # Default fallback
import base64
import io
import logging
import os
import sys
import time
import tkinter as tk
from datetime import datetime
from threading import Event, Thread
from tkinter import filedialog

import eel

# Tambahkan direktori root ke path Python
sys.path.append(os.path.dirname(__file__))

# Import modul automation
from browser_setup import PlaywrightBrowserManager
from data_extractor import get_stock_value_direct, get_tabung_terjual_direct
from excel_handler import save_to_excel_pivot_format
from export_handler import export_results_to_excel
from login_handler import login_direct
from navigation_handler import click_laporan_penjualan_direct, click_date_elements_direct
from telemetry_manager import get_telemetry_manager
from utils import load_accounts_from_excel, setup_logging
from validators import (
    is_valid_email,
    is_valid_phone,
    is_valid_pin,
    validate_username,
)

# Setup logger
logger = logging.getLogger("gui_automation")

# Global variables untuk kontrol automation
automation_thread = None
automation_running = False
automation_paused = False
stop_event = Event()

# Global variables untuk menyimpan hasil
automation_results = []
automation_export_date = None

# Initialize telemetry manager
telemetry_manager = get_telemetry_manager()

# Get correct path for exe and script
if getattr(sys, "frozen", False):
    # Running as compiled exe
    application_path = os.path.dirname(sys.executable)
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Initialize Eel dengan folder web
web_folder = os.path.join(application_path, "web")
eel.init(web_folder)


@eel.expose
def load_accounts_from_data(base64_data, filename):
    """
    Load akun dari data Base64 (file upload dari browser)
    """
    try:
        # Decode base64
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]

        decoded = base64.b64decode(base64_data)
        file_obj = io.BytesIO(decoded)

        # Load accounts using existing utility
        accounts = load_accounts_from_excel(file_obj)

        if not accounts:
            return {
                "success": False,
                "accounts": [],
                "message": "Tidak ada akun valid dalam file",
                "count": 0,
            }

        # Format accounts untuk frontend
        formatted_accounts = []
        for idx, (nama, username, pin) in enumerate(accounts, 1):
            formatted_accounts.append(
                {
                    "id": idx,
                    "nama": nama,
                    "username": username,
                    "pin": pin,
                    "status": "waiting",
                    "progress": 0,
                }
            )

        return {
            "success": True,
            "accounts": formatted_accounts,
            "message": f"Berhasil load {len(accounts)} akun dari {filename}",
            "count": len(accounts),
        }

    except Exception as e:
        logger.error(f"Error loading accounts from data: {str(e)}", exc_info=True)
        return {
            "success": False,
            "accounts": [],
            "message": f"Error: {str(e)}",
            "count": 0,
        }


# Deprecated: load_accounts_from_file (kept for reference if needed, but unused by frontend now)
@eel.expose
def load_accounts_from_file(file_path):
    """
    Load akun dari file Excel

    Args:
        file_path (str): Path ke file Excel

    Returns:
        dict: {
            "success": bool,
            "accounts": list,
            "message": str,
            "count": int
        }
    """
    try:
        # Cari file di folder akun
        akun_dir = os.path.join(os.path.dirname(__file__), "akun")
        full_path = os.path.join(akun_dir, file_path)

        if not os.path.exists(full_path):
            return {
                "success": False,
                "accounts": [],
                "message": f"File tidak ditemukan: {file_path}",
                "count": 0,
            }

        accounts = load_accounts_from_excel(full_path)

        if not accounts:
            return {
                "success": False,
                "accounts": [],
                "message": "Tidak ada akun valid dalam file",
                "count": 0,
            }

        # Format accounts untuk frontend
        formatted_accounts = []
        for idx, (nama, username, pin) in enumerate(accounts, 1):
            formatted_accounts.append(
                {
                    "id": idx,
                    "nama": nama,
                    "username": username,
                    "pin": pin,
                    "status": "waiting",
                    "progress": 0,
                }
            )

        return {
            "success": True,
            "accounts": formatted_accounts,
            "message": f"Berhasil load {len(accounts)} akun",
            "count": len(accounts),
        }

    except Exception as e:
        logger.error(f"Error loading accounts: {str(e)}", exc_info=True)
        return {
            "success": False,
            "accounts": [],
            "message": f"Error: {str(e)}",
            "count": 0,
        }


@eel.expose
def get_available_excel_files():
    """
    Dapatkan list file Excel yang tersedia di folder akun

    Returns:
        dict: {
            "success": bool,
            "files": list,
            "message": str
        }
    """
    try:
        akun_dir = os.path.join(os.path.dirname(__file__), "akun")

        if not os.path.exists(akun_dir):
            return {
                "success": False,
                "files": [],
                "message": "Folder akun tidak ditemukan",
            }

        excel_files = [
            f
            for f in os.listdir(akun_dir)
            if f.endswith((".xlsx", ".xls")) and not f.startswith("~")
        ]

        return {
            "success": True,
            "files": excel_files,
            "message": f"Ditemukan {len(excel_files)} file",
        }

    except Exception as e:
        logger.error(f"Error getting Excel files: {str(e)}", exc_info=True)
        return {"success": False, "files": [], "message": f"Error: {str(e)}"}


@eel.expose
def start_automation(accounts, settings):
    """
    Mulai proses automation

    Args:
        accounts (list): List akun yang akan diproses
        settings (dict): Settings automation {
            "headless": bool,
            "date": str (YYYY-MM-DD atau null),
            "delay": float
        }

    Returns:
        dict: {"success": bool, "message": str}
    """
    global automation_thread, automation_running, stop_event

    try:
        if automation_running:
            return {"success": False, "message": "Automation sedang berjalan"}

        # Reset stop event
        stop_event.clear()
        automation_running = True

        # Parse tanggal jika ada
        selected_date = None
        if settings.get("date"):
            try:
                selected_date = datetime.strptime(settings["date"], "%Y-%m-%d")
            except Exception:
                selected_date = None

        # Jalankan automation di thread terpisah
        automation_thread = Thread(
            target=run_automation_background, args=(accounts, selected_date, settings)
        )
        automation_thread.daemon = True
        automation_thread.start()

        return {"success": True, "message": "Automation dimulai"}

    except Exception as e:
        automation_running = False
        logger.error(f"Error starting automation: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error: {str(e)}"}


@eel.expose
def pause_automation():
    """Pause automation yang sedang berjalan"""
    global automation_paused
    automation_paused = not automation_paused

    status = "paused" if automation_paused else "resumed"
    eel.log_message(f"Automation {status}", "warning")

    return {
        "success": True,
        "paused": automation_paused,
        "message": f"Automation {status}",
    }


@eel.expose
def stop_automation():
    """Stop automation yang sedang berjalan"""
    global automation_running, stop_event

    stop_event.set()
    automation_running = False

    eel.log_message("Automation dihentikan oleh user", "error")

    return {"success": True, "message": "Automation dihentikan"}


def run_automation_background(accounts, selected_date, settings):
    """
    Fungsi background untuk menjalankan automation
    """
    global \
        automation_running, \
        automation_paused, \
        automation_results, \
        automation_export_date

    try:
        # Reset telemetry untuk session baru
        telemetry_manager.reset()

        eel.log_message("Memulai proses automation...", "info")

        headless_mode = settings.get("headless", HEADLESS_MODE)
        delay = settings.get("delay", 2.0)
        # use_session = settings.get("use_session", True) # REMOVED: Always fresh login

        results = []
        # Only reset global results if it's a fresh start (e.g. user cleared logs or explicitly requested reset)
        # For now, we'll append to keep history until cleared manually
        if not automation_results:
            automation_results = []

        automation_export_date = selected_date if selected_date else datetime.now()
        total_accounts = len(accounts)

        for idx, account in enumerate(accounts):
            # Check if stopped
            if stop_event.is_set():
                eel.log_message("Automation dihentikan", "error")
                break

            # Check if paused
            while automation_paused:
                time.sleep(0.5)
                if stop_event.is_set():
                    break

            nama = account["nama"]
            username = account["username"]
            pin = account["pin"]

            # Start telemetry tracking
            telemetry_manager.record_account_start(username)

            # Update overall progress at the start of each account
            progress_percent = int((idx / total_accounts) * 100)
            eel.update_overall_progress(idx, total_accounts, progress_percent)

            # Update status
            eel.update_account_status(account["id"], "processing", 0)
            eel.log_message(f"Memproses: {nama} ({username})", "info")

            browser_manager = None

            try:
                # Setup browser
                eel.update_account_status(account["id"], "processing", 10)
                eel.log_message(f"Setup browser untuk {nama}...", "info")

                telemetry_manager.start_operation("browser_setup", username)
                browser_manager = PlaywrightBrowserManager()
                # Force no session usage
                page = browser_manager.setup_browser(
                    headless=headless_mode,
                    username=None, 
                    use_session=False,
                )
                telemetry_manager.end_operation("browser_setup", username)

                # Tambahkan delay untuk stabilitas di mode GUI
                if not headless_mode:
                    time.sleep(2.0)

                if not page:
                    eel.update_account_status(account["id"], "error", 0)
                    eel.log_message(f"Gagal setup browser untuk {nama}", "error")
                    telemetry_manager.record_account_failure(
                        username, "browser_setup_failed"
                    )
                    continue

                # Login (SELALU LOGIN BARU)
                eel.update_account_status(account["id"], "processing", 30)
                eel.log_message(f"Login untuk {nama}...", "info")

                telemetry_manager.start_operation("login", username)
                success, gagal_info = login_direct(page, username, pin)
                telemetry_manager.end_operation("login", username)

                if not success:
                    eel.update_account_status(account["id"], "error", 0)
                    eel.log_message(f"Login gagal untuk {nama}", "error")
                    telemetry_manager.record_account_failure(
                        username, "login_failed"
                    )
                    browser_manager.close()
                    continue

                eel.log_message(f"Login berhasil untuk {nama}", "success")

                # Ambil stok
                eel.update_account_status(account["id"], "processing", 50)
                eel.log_message(f"Mengambil stok untuk {nama}...", "info")

                telemetry_manager.start_operation("get_stock", username)
                stok_value = get_stock_value_direct(page)
                telemetry_manager.end_operation("get_stock", username)
                if stok_value:
                    eel.log_message(f"Stok {nama}: {stok_value} tabung", "success")
                else:
                    eel.log_message(f"Gagal ambil stok untuk {nama}", "warning")

                # Navigasi ke Laporan Penjualan
                eel.update_account_status(account["id"], "processing", 70)
                eel.log_message(f"Mengambil data penjualan untuk {nama}...", "info")

                tabung_terjual = None
                if click_laporan_penjualan_direct(page):
                    # === FILTER TANGGAL (4 STEPS) ===
                    if selected_date:
                        eel.log_message(f"Menerapkan filter tanggal: {selected_date.strftime('%d/%m/%Y')}", "info")
                        if click_date_elements_direct(page, selected_date):
                            eel.log_message("Filter tanggal berhasil diterapkan", "success")
                        else:
                            eel.log_message("Gagal menerapkan filter tanggal", "warning")
                    # ================================

                    tabung_terjual = get_tabung_terjual_direct(page)
                    if tabung_terjual is not None:
                        eel.log_message(
                            f"Tabung terjual {nama}: {tabung_terjual}", "success"
                        )
                    else:
                        eel.log_message(
                            f"Gagal ambil tabung terjual untuk {nama}",
                            "warning",
                        )
                else:
                    eel.log_message(
                        f"Gagal navigasi ke Laporan Penjualan untuk {nama}",
                        "warning",
                    )

                # Simpan hasil
                eel.update_account_status(account["id"], "processing", 90)

                # Helper untuk konversi aman ke int
                def safe_int(val):
                    try:
                        if val is None: return 0
                        return int(str(val).replace('.', '').replace(',', ''))
                    except:
                        return 0

                stok_int = safe_int(stok_value)
                terjual_int = safe_int(tabung_terjual)

                stok_formatted = f"{stok_int} Tabung"
                tabung_formatted = f"{terjual_int} Tabung"

                status = (
                    "Ada Penjualan"
                    if terjual_int > 0
                    else "Tidak Ada Penjualan"
                )

                result = {
                    "pangkalan_id": username,
                    "nama": nama,
                    "username": username,
                    "stok": stok_formatted,
                    "tabung_terjual": tabung_formatted,
                    "status": status,
                }
                results.append(result)
                automation_results.append(result)  # Save to global for export

                # Simpan ke Excel
                save_date = selected_date if selected_date else datetime.now()
                tanggal_check = save_date.strftime("%Y-%m-%d")

                save_to_excel_pivot_format(
                    pangkalan_id=username,
                    nama_pangkalan=nama,
                    tanggal_check=tanggal_check,
                    stok_awal=stok_formatted,
                    total_inputan=tabung_formatted,
                    status=status,
                    selected_date=save_date,
                )

                # Record success
                telemetry_manager.record_account_success(
                    username,
                    {
                        "stok": stok_formatted,
                        "terjual": tabung_formatted,
                        "status": status,
                    },
                )
                
                # Record business metrics (NEW)
                telemetry_manager.record_business_metrics(stok_int, terjual_int)

                eel.update_account_status(account["id"], "done", 100)
                eel.log_message(
                    f"Selesai: {nama} - Stok: {stok_formatted}, Terjual: {tabung_formatted}",
                    "success",
                )

                eel.update_overall_progress(idx + 1, total_accounts, progress_percent)

            except Exception as e:
                eel.update_account_status(account["id"], "error", 0)
                eel.log_message(f"Error untuk {nama}: {str(e)}", "error")
                logger.error(f"Error processing {nama}: {str(e)}", exc_info=True)
                telemetry_manager.record_account_failure(username, "exception", str(e))

            finally:
                # Delay sejenak sebelum menutup browser agar user bisa melihat hasil akhir
                if not headless_mode:
                    time.sleep(1.0)

                if browser_manager:
                    browser_manager.close()

                # Delay antar akun
                if idx < total_accounts - 1 and not stop_event.is_set():
                    eel.log_message(f"Delay {delay} detik...", "info")
                    time.sleep(delay)

        # Selesai
        eel.log_message(
            f"Automation selesai! Total: {len(results)} akun berhasil diproses",
            "success",
        )
        eel.automation_completed(len(results), total_accounts)

    except Exception as e:
        eel.log_message(f"Error automation: {str(e)}", "error")
        logger.error(f"Error in automation: {str(e)}", exc_info=True)

    finally:
        automation_running = False
        automation_paused = False


@eel.expose
def export_to_excel():
    """
    Export hasil automation ke Excel

    Returns:
        dict: {"success": bool, "filepath": str, "message": str}
    """
    global automation_results, automation_export_date

    try:
        if not automation_results:
            return {
                "success": False,
                "filepath": "",
                "message": "Tidak ada data untuk di-export",
            }

        # Export ke Excel
        export_date = (
            automation_export_date if automation_export_date else datetime.now()
        )
        filepath = export_results_to_excel(automation_results, export_date)

        # Get absolute path
        abs_path = os.path.abspath(filepath)

        return {
            "success": True,
            "filepath": abs_path,
            "message": f"Berhasil export {len(automation_results)} data ke Excel",
        }

    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}", exc_info=True)
        return {"success": False, "filepath": "", "message": f"Error: {str(e)}"}


@eel.expose
def save_results_as():
    """
    Simpan hasil automation dengan mengembalikan base64 string
    agar browser bisa menangani dialog save/download.
    Menghindari masalah threading dengan Tkinter.
    """
    global automation_results, automation_export_date

    try:
        if not automation_results:
            return {"success": False, "message": "Tidak ada data untuk disimpan"}

        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SnapFlux_Export_{timestamp}.xlsx"

        # Use a temp directory
        temp_dir = os.path.join(os.path.dirname(__file__), "temp_export")
        os.makedirs(temp_dir, exist_ok=True)
        temp_filepath = os.path.join(temp_dir, filename)

        # Export ke temp file
        export_date = (
            automation_export_date if automation_export_date else datetime.now()
        )

        saved_path = export_results_to_excel(
            automation_results, export_date, custom_filepath=temp_filepath
        )

        # Read file and convert to base64
        with open(saved_path, "rb") as f:
            file_content = f.read()

        base64_content = base64.b64encode(file_content).decode("utf-8")

        # Clean up temp file
        try:
            os.remove(saved_path)
        except:
            pass

        return {
            "success": True,
            "data": base64_content,
            "filename": filename,
            "message": "File siap disimpan",
        }

    except Exception as e:
        logger.error(f"Error saving results as: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error: {str(e)}"}


@eel.expose
def open_export_folder():
    """
    Buka folder results di file explorer

    Returns:
        dict: {"success": bool, "message": str}
    """
    try:
        results_dir = os.path.join(os.path.dirname(__file__), "results")

        if not os.path.exists(results_dir):
            os.makedirs(results_dir, exist_ok=True)

        # Open folder based on OS
        import platform
        import subprocess

        system = platform.system()
        if system == "Windows":
            os.startfile(results_dir)
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", results_dir])
        else:  # Linux
            subprocess.Popen(["xdg-open", results_dir])

        return {"success": True, "message": "Folder dibuka"}

    except Exception as e:
        logger.error(f"Error opening folder: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error: {str(e)}"}


@eel.expose
def get_export_ready_status():
    """
    Cek apakah ada data yang siap di-export

    Returns:
        dict: {"ready": bool, "count": int}
    """
    global automation_results

    return {"ready": len(automation_results) > 0, "count": len(automation_results)}


@eel.expose
def get_automation_status():
    """Get status automation saat ini"""
    return {"running": automation_running, "paused": automation_paused}


@eel.expose
def get_telemetry_metrics():
    """
    Get real-time telemetry metrics untuk dashboard

    Returns:
        dict: Real-time metrics
    """
    try:
        return telemetry_manager.get_real_time_metrics()
    except Exception as e:
        logger.error(f"Error getting telemetry metrics: {str(e)}")
        return {
            "session_id": "",
            "session_duration": 0,
            "total_accounts": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "success_rate": 0,
            "failure_rate": 0,
            "avg_processing_time": 0,
            "errors": {},
            "timestamp": datetime.now().isoformat(),
        }


@eel.expose
def get_dashboard_data():
    """
    Get comprehensive dashboard data

    Returns:
        dict: Dashboard data dengan overview, counters, rates, performance
    """
    try:
        return telemetry_manager.get_dashboard_data()
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return {
            "overview": {},
            "counters": {},
            "rates": {},
            "performance": {},
            "errors": {},
        }


@eel.expose
def get_session_stats():
    """
    Get session stats (Dummy implementation as session manager is removed)
    """
    return {"stats": {"total": 0, "valid": 0, "expired": 0}, "sessions": []}


@eel.expose
def clear_all_sessions():
    """
    Clear all saved sessions (Dummy implementation)
    """
    return {
        "success": True,
        "count": 0,
        "message": "Session manager dinonaktifkan",
    }
@eel.expose
def save_telemetry_report():
    """
    Save session telemetry report

    Returns:
        dict: {"success": bool, "filepath": str, "message": str}
    """
    try:
        filepath = telemetry_manager.save_session_report()
        return {
            "success": True,
            "filepath": filepath,
            "message": "Report berhasil disimpan",
        }
    except Exception as e:
        logger.error(f"Error saving telemetry report: {str(e)}")
        return {"success": False, "filepath": "", "message": f"Error: {str(e)}"}


@eel.expose
def clear_results():
    """Clear stored automation results"""
    global automation_results
    automation_results = []
    return {"success": True, "message": "Data hasil dibersihkan"}


def main():
    """Main function untuk menjalankan GUI"""
    try:
        # Setup logging
        setup_logging()

        # Check folder struktur
        web_dir = os.path.join(os.path.dirname(__file__), "web")
        if not os.path.exists(web_dir):
            print("✗ Folder 'web' tidak ditemukan!")
            print(
                "   Pastikan folder web/ dengan file HTML/CSS/JS ada di direktori yang sama"
            )
            return

        print("=" * 60)
        print("SNAPFLUX AUTOMATION - GUI VERSION")
        print("=" * 60)
        print("Starting web server...")
        print("Web directory:", web_dir)
        print("=" * 60)

        # Try different ports if one is already in use
        ports_to_try = [8080, 8081, 8082, 8083, 8084]
        started = False

        for port in ports_to_try:
            try:
                print(f"Trying port {port}...")
                # Start Eel dengan Chrome App mode
                eel.start(
                    "index.html",
                    size=(1400, 900),
                    port=port,
                    mode="chrome-app",  # Buka sebagai Chrome app (standalone window)
                    host="localhost",
                    block=True,
                )
                started = True
                break
            except OSError as ose:
                if "10048" in str(ose) or "address already in use" in str(ose).lower():
                    print(f"⚠ Port {port} sudah digunakan, mencoba port lain...")
                    continue
                else:
                    raise
            except EnvironmentError:
                # Jika Chrome tidak tersedia, coba browser default
                print("⚠ Chrome tidak ditemukan, menggunakan browser default...")
                try:
                    eel.start(
                        "index.html",
                        size=(1400, 900),
                        port=port,
                        mode=None,  # Browser default
                        host="localhost",
                        block=True,
                    )
                    started = True
                    break
                except OSError as ose:
                    if (
                        "10048" in str(ose)
                        or "address already in use" in str(ose).lower()
                    ):
                        print(f"⚠ Port {port} sudah digunakan, mencoba port lain...")
                        continue
                    else:
                        raise

        if not started:
            print(
                "✗ Tidak dapat menemukan port yang tersedia. Semua port sudah digunakan."
            )
            print("       Silakan tutup aplikasi lain yang menggunakan port 8080-8084.")

    except Exception as e:
        print(f"✗ Error starting GUI: {str(e)}")
        logger.error(f"Error starting GUI: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
