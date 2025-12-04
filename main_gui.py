"""
Main GUI entry point untuk SnapFlux Automation menggunakan Eel
File ini menjalankan web-based GUI dengan Python backend
"""

import json

# Import config
try:
    from modules.core.config import HEADLESS_MODE
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
import eel.browsers

# Tambahkan direktori root ke path Python
if getattr(sys, "frozen", False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(__file__))

# Import modul automation
from modules.browser.extractor import get_stock_value_direct, get_tabung_terjual_direct
from modules.browser.login import login_direct
from modules.browser.navigation import (
    click_date_elements_direct,
    click_laporan_penjualan_direct,
)
from modules.browser.setup import PlaywrightBrowserManager
from modules.core.network import check_before_step, is_online, wait_for_internet
from modules.core.process_manager import ProcessManager
from modules.core.telemetry import get_telemetry_manager
from modules.core.utils import setup_logging
from modules.data.excel import save_to_excel_pivot_format
from modules.data.export import export_results_to_excel
from modules.data.supabase_client import SupabaseManager

# Setup logger
logger = logging.getLogger("gui_automation")

# Global variables untuk kontrol automation
automation_thread = None
process_manager_instance = None
supabase_manager = None


# Global variables untuk menyimpan hasil
automation_results = []
automation_export_date = None

# Initialize telemetry manager
telemetry_manager = get_telemetry_manager()

# Get correct path for resources and data
# Get correct path for resources and data
if getattr(sys, "frozen", False):
    # Running as compiled exe
    if hasattr(sys, "_MEIPASS"):
        # Mode --onefile (Files are in temp directory)
        BASE_DIR = sys._MEIPASS
    else:
        # Mode --onedir (Files are next to the executable)
        BASE_DIR = os.path.dirname(sys.executable)

    DATA_DIR = os.path.dirname(sys.executable)

    # Set Chrome Binary Path for bundled browser
    bundled_chrome = os.path.join(BASE_DIR, "chrome", "Chromium", "bin", "chrome.exe")
    if os.path.exists(bundled_chrome):
        os.environ["CHROME_BINARY_PATH"] = bundled_chrome
        # Force Eel to use our bundled Chrome
        import eel.browsers

        eel.browsers.set_path("chrome", bundled_chrome)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = BASE_DIR

# Initialize Eel dengan folder web
web_folder = os.path.join(BASE_DIR, "web")
eel.init(web_folder)


@eel.expose
def login(username, password):
    """
    Login user
    """
    global supabase_manager

    try:
        if not supabase_manager:
            supabase_manager = SupabaseManager()

        result = supabase_manager.login_user(username, password)
        return result

    except Exception as e:
        logger.error(f"Error logging in: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error: {str(e)}"}


@eel.expose
def load_accounts_from_supabase(company_access=None):
    """
    Load akun dari Supabase Database
    """
    global supabase_manager

    try:
        logger.info(
            f"[DEBUG GUI] load_accounts_from_supabase called with company_access={company_access}, type={type(company_access)}"
        )

        if not supabase_manager:
            supabase_manager = SupabaseManager()

        logger.info(
            f"[DEBUG GUI] Calling fetch_accounts with company_filter={company_access}"
        )
        accounts = supabase_manager.fetch_accounts(company_filter=company_access)
        logger.info(f"[DEBUG GUI] fetch_accounts returned {len(accounts)} accounts")

        if not accounts:
            return {
                "success": False,
                "accounts": [],
                "message": "Tidak ada akun ditemukan di database atau koneksi gagal",
                "count": 0,
            }

        return {
            "success": True,
            "accounts": accounts,
            "message": f"Berhasil load {len(accounts)} akun dari Database",
            "count": len(accounts),
        }

    except Exception as e:
        logger.error(f"Error loading accounts from Supabase: {str(e)}", exc_info=True)
        return {
            "success": False,
            "accounts": [],
            "message": f"Error: {str(e)}",
            "count": 0,
        }


@eel.expose
def get_dashboard_live_stats(company_access=None):
    """
    Get live dashboard statistics from Supabase (today's summary)
    """
    global supabase_manager

    try:
        logger.info(
            f"[DEBUG GUI] get_dashboard_live_stats called with company_access={company_access}"
        )

        if not supabase_manager:
            supabase_manager = SupabaseManager()

        stats = supabase_manager.get_today_summary(company_filter=company_access)
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting live stats: {str(e)}", exc_info=True)
        return {
            "success": False,
            "stats": {
                "total": 0,
                "success": 0,
                "failed": 0,
                "total_sales": 0,
                "total_stock": 0,
            },
        }


@eel.expose
def get_stock_movement_stats(company_access=None):
    """
    Get stock movement statistics (sales and restocks detected from stock changes)
    """
    global supabase_manager

    try:
        if not supabase_manager:
            supabase_manager = SupabaseManager()

        movement = supabase_manager.get_stock_movement_today(
            company_filter=company_access
        )
        return {"success": True, "movement": movement}
    except Exception as e:
        logger.error(f"Error getting stock movement: {str(e)}", exc_info=True)
        return {
            "success": False,
            "movement": {
                "total_sales_yesterday": 0,
                "reported_sales_yesterday": 0,
                "unreported_sales": 0,
            },
        }


@eel.expose
def load_unprocessed_accounts_only(company_access=None):
    """
    Load only accounts that haven't been processed today (Smart Resume)
    """
    global supabase_manager

    try:
        logger.info(
            f"[DEBUG GUI] load_unprocessed_accounts_only called with company_access={company_access}, type={type(company_access)}"
        )

        if not supabase_manager:
            supabase_manager = SupabaseManager()

        accounts = supabase_manager.get_unprocessed_accounts_today(
            company_filter=company_access
        )
        logger.info(
            f"[DEBUG GUI] get_unprocessed_accounts_today returned {len(accounts)} accounts"
        )

        if not accounts:
            return {
                "success": False,
                "accounts": [],
                "message": "Semua akun sudah dicek hari ini atau tidak ada akun",
                "count": 0,
            }

        return {
            "success": True,
            "accounts": accounts,
            "message": f"Berhasil load {len(accounts)} akun yang belum dicek hari ini",
            "count": len(accounts),
        }

    except Exception as e:
        logger.error(f"Error loading unprocessed accounts: {str(e)}", exc_info=True)
        return {
            "success": False,
            "accounts": [],
            "message": f"Error: {str(e)}",
            "count": 0,
        }


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
    global automation_thread, process_manager_instance

    try:
        if (
            process_manager_instance
            and process_manager_instance.stop_requested == False
            and automation_thread
            and automation_thread.is_alive()
        ):
            return {"success": False, "message": "Automation sedang berjalan"}

        # Parse tanggal jika ada
        selected_date = None
        if settings.get("date"):
            try:
                selected_date = datetime.strptime(settings["date"], "%Y-%m-%d")
            except Exception:
                selected_date = None

        # Pass date object to settings for manager
        settings["date_obj"] = selected_date

        # Jalankan automation di thread terpisah
        automation_thread = Thread(
            target=run_automation_background, args=(accounts, settings)
        )
        automation_thread.daemon = True
        automation_thread.start()

        return {"success": True, "message": "Automation dimulai"}

    except Exception as e:
        logger.error(f"Error starting automation: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error: {str(e)}"}


@eel.expose
def pause_automation():
    """Pause automation yang sedang berjalan"""
    global process_manager_instance

    if not process_manager_instance:
        return {"success": False, "message": "Automation tidak berjalan"}

    if process_manager_instance.pause_requested:
        process_manager_instance.resume()
        status = "resumed"
    else:
        process_manager_instance.pause()
        status = "paused"

    return {
        "success": True,
        "paused": process_manager_instance.pause_requested,
        "message": f"Automation {status}",
    }


@eel.expose
def stop_automation():
    """Stop automation yang sedang berjalan"""
    global process_manager_instance

    if process_manager_instance:
        process_manager_instance.stop()
        eel.log_message("Automation dihentikan oleh user", "error")

    return {"success": True, "message": "Automation dihentikan"}


def run_automation_background(accounts, settings):
    """
    Fungsi background untuk menjalankan automation menggunakan ProcessManager
    """
    global process_manager_instance, automation_results, automation_export_date

    try:
        # Define callbacks
        callbacks = {
            "on_log": eel.log_message,
            "on_progress": eel.update_overall_progress,
            "on_account_status": eel.update_account_status,
            "on_result": lambda res: None,  # We handle results in bulk at the end or via global list
        }

        # Initialize Manager
        process_manager_instance = ProcessManager(
            callbacks, supabase_client=supabase_manager
        )

        # Prepare global results
        if not automation_results:
            automation_results = []

        automation_export_date = (
            settings.get("date_obj") if settings.get("date_obj") else datetime.now()
        )

        # Run Process
        results = process_manager_instance.run(accounts, settings)

        # Update global results
        automation_results.extend(results)

        # Completion event
        eel.automation_completed(len(results), len(accounts))

    except Exception as e:
        eel.log_message(f"Error automation: {str(e)}", "error")
        logger.error(f"Error in automation: {str(e)}", exc_info=True)

    finally:
        process_manager_instance = None


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
        filename = f"SnapFlux_Daily_{timestamp}.xlsx"

        # Use a temp directory
        temp_dir = os.path.join(DATA_DIR, "temp_export")
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
        results_dir = os.path.join(DATA_DIR, "results")

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
    global process_manager_instance
    running = process_manager_instance is not None
    paused = process_manager_instance.pause_requested if running else False
    return {"running": running, "paused": paused}


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


@eel.expose
def get_monitoring_results(company_access=None, limit=100, date_filter=None):
    """
    Get monitoring results (automation history) from database with company filter

    Args:
        company_access (int): Company ID to filter results
        limit (int): Maximum number of results to return
        date_filter (str): Date filter in YYYY-MM-DD format (optional)

    Returns:
        dict: {"success": bool, "results": list, "count": int, "message": str}
    """
    global supabase_manager

    try:
        logger.info(
            f"[DEBUG GUI] get_monitoring_results called with company_access={company_access}, limit={limit}, date_filter={date_filter}"
        )

        if not supabase_manager:
            supabase_manager = SupabaseManager()

        results = supabase_manager.get_automation_results(
            company_filter=company_access, limit=limit, date_filter=date_filter
        )
        logger.info(
            f"[DEBUG GUI] get_automation_results returned {len(results)} results"
        )

        return {
            "success": True,
            "results": results,
            "count": len(results),
            "message": f"Berhasil load {len(results)} hasil monitoring",
        }

    except Exception as e:
        logger.error(f"Error getting monitoring results: {str(e)}", exc_info=True)
        return {
            "success": False,
            "results": [],
            "count": 0,
            "message": f"Error: {str(e)}",
        }


@eel.expose
def add_new_account(data):
    """
    Add new account to database

    Args:
        data (dict): Account data {nama, username, pin, pangkalan_id, company_id}

    Returns:
        dict: {"success": bool, "message": str}
    """
    global supabase_manager

    try:
        logger.info(
            f"[DEBUG GUI] add_new_account called with data: {data.get('nama')}, company_id: {data.get('company_id')}"
        )

        if not supabase_manager:
            supabase_manager = SupabaseManager()

        # Validate required fields
        required_fields = ["nama", "username", "pin", "pangkalan_id", "company_id"]
        for field in required_fields:
            if not data.get(field):
                return {"success": False, "message": f"Field '{field}' wajib diisi!"}

        # Add account
        success = supabase_manager.add_account(data)

        if success:
            logger.info(
                f"[DEBUG GUI] Account {data.get('username')} berhasil ditambahkan"
            )
            return {
                "success": True,
                "message": f"Akun '{data.get('nama')}' berhasil ditambahkan ke database!",
            }
        else:
            logger.warning(f"[DEBUG GUI] Failed to add account {data.get('username')}")
            return {
                "success": False,
                "message": "Gagal menambahkan akun. Username mungkin sudah terdaftar.",
            }

    except Exception as e:
        logger.error(f"Error adding new account: {str(e)}", exc_info=True)
        return {"success": False, "message": f"Error: {str(e)}"}


@eel.expose
def get_stock_summary(company_access=None, date_str=None):
    """
    Get stock summary for a specific date

    Args:
        company_access (int): Company ID to filter
        date_str (str): Date in YYYY-MM-DD format (optional, default today)

    Returns:
        dict: {"success": bool, "data": {total_stock: int, total_sales: int}}
    """
    global supabase_manager

    try:
        if not supabase_manager:
            supabase_manager = SupabaseManager()

        result = supabase_manager.get_stock_summary_by_date(
            company_filter=company_access, date_str=date_str
        )

        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Error getting stock summary: {str(e)}", exc_info=True)
        return {"success": False, "data": {"total_stock": 0, "total_sales": 0}}


def main():
    """Main function untuk menjalankan GUI"""
    try:
        # Setup logging
        setup_logging()

        # Initialize Supabase
        global supabase_manager
        supabase_manager = SupabaseManager()

        # Check folder struktur
        web_dir = os.path.join(BASE_DIR, "web")
        if not os.path.exists(web_dir):
            print("[!] Folder 'web' tidak ditemukan!")
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

        # Check Chrome Path explicitly
        chrome_path = os.environ.get("CHROME_BINARY_PATH")
        print(f"DEBUG: Chrome Path set to: {chrome_path}")

        # Opsi browser untuk Eel
        browser_opts = {
            "mode": "chrome",
            "host": "localhost",
            "block": True,
            "cmdline_args": ["--start-maximized"],
        }

        if chrome_path and os.path.exists(chrome_path):
            print("[v] Menggunakan Bundled Chrome untuk GUI")
            # Force path for 'chrome' mode
            # import eel.browsers removed to avoid UnboundLocalError
            eel.browsers.set_path("chrome", chrome_path)
        else:
            print(
                "[!] Bundled Chrome tidak ditemukan, menggunakan default system browser"
            )
            browser_opts["mode"] = "default"

        for port in ports_to_try:
            try:
                print(f"Trying port {port}...")
                eel.start("login.html", port=port, **browser_opts)
                started = True
                break
            except OSError as ose:
                if "10048" in str(ose) or "address already in use" in str(ose).lower():
                    print(f"[!] Port {port} sudah digunakan, mencoba port lain...")
                    continue
                else:
                    raise
            except EnvironmentError:
                # Jika Chrome tidak tersedia, coba browser default
                print("[!] Chrome tidak ditemukan, menggunakan browser default...")
                try:
                    eel.start(
                        "login.html",
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
                        print(f"[!] Port {port} sudah digunakan, mencoba port lain...")
                        continue
                    else:
                        raise

        if not started:
            print(
                "[x] Tidak dapat menemukan port yang tersedia. Semua port sudah digunakan."
            )
            print("       Silakan tutup aplikasi lain yang menggunakan port 8080-8084.")

    except Exception as e:
        print(f"[x] Error starting GUI: {str(e)}")
        logger.error(f"Error starting GUI: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
