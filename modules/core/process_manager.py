"""
Process Manager Module
======================
Module ini menangani logika inti dari proses bisnis SnapFlux.
Memisahkan logika bisnis dari interface (GUI/CLI).
"""

import time
import logging
from datetime import datetime
from modules.browser.setup import PlaywrightBrowserManager
from modules.browser.login import login_direct
from modules.browser.extractor import get_stock_value_direct, get_tabung_terjual_direct
from modules.browser.navigation import click_laporan_penjualan_direct, click_date_elements_direct
from modules.data.excel import save_to_excel_pivot_format
from modules.core.network import check_before_step
from modules.core.telemetry import get_telemetry_manager
from modules.core.config import HEADLESS_MODE

class ProcessManager:
    """
    Class untuk mengelola proses bisnis (cek stok, penjualan).
    Dapat digunakan oleh GUI maupun CLI.
    """
    
    def __init__(self, callbacks=None, supabase_client=None):
        """
        Inisialisasi ProcessManager
        
        Args:
            callbacks (dict): Dictionary berisi fungsi callback untuk update UI/Log
                - on_log(message, level)
                - on_progress(current, total, percent)
                - on_account_status(account_id, status, progress)
                - on_result(result_data)
            supabase_client: Instance SupabaseManager untuk update database
        """
        self.callbacks = callbacks or {}
        self.supabase_client = supabase_client
        self.stop_requested = False
        self.pause_requested = False
        self.logger = logging.getLogger("process_manager")
        self.telemetry = get_telemetry_manager()
        self.results = []
        
    def _log(self, message, level="info"):
        """Internal helper untuk logging ke callback dan file"""
        if self.callbacks.get("on_log"):
            self.callbacks["on_log"](message, level)
            
        # Log to file based on level
        if level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)

    def _update_status(self, account_id, status, progress):
        """Update status akun di UI"""
        if self.callbacks.get("on_account_status"):
            self.callbacks["on_account_status"](account_id, status, progress)

    def _update_progress(self, current, total, percent):
        """Update progress bar global"""
        if self.callbacks.get("on_progress"):
            self.callbacks["on_progress"](current, total, percent)
            
    def stop(self):
        """Request stop process"""
        self.stop_requested = True
        self._log("Permintaan stop diterima...", "warning")

    def pause(self):
        """Pause process"""
        self.pause_requested = True
        self._log("Proses dipause", "warning")

    def resume(self):
        """Resume process"""
        self.pause_requested = False
        self._log("Proses dilanjutkan", "info")

    def run(self, accounts, settings):
        """
        Jalankan proses untuk list akun
        
        Args:
            accounts (list): List akun [{id, nama, username, pin}, ...]
            settings (dict): Settings {headless, date, delay, ...}
            
        Returns:
            list: List hasil proses
        """
        self.stop_requested = False
        self.results = []
        self.telemetry.reset()
        
        headless_mode = settings.get("headless", HEADLESS_MODE)
        delay = settings.get("delay", 2.0)
        selected_date = settings.get("date_obj") # Expecting datetime object or None
        
        total_accounts = len(accounts)
        self._log(f"Memulai proses untuk {total_accounts} akun...", "info")
        
        for idx, account in enumerate(accounts):
            # Check stop
            if self.stop_requested:
                self._log("Proses dihentikan oleh user", "error")
                break
                
            # Check pause
            while self.pause_requested:
                time.sleep(0.5)
                if self.stop_requested:
                    break
            
            # Extract account info
            # Handle both dictionary (GUI) and tuple/list (CLI) formats
            if isinstance(account, dict):
                account_id = account.get("id", idx)
                nama = account["nama"]
                username = account["username"]
                pin = account["pin"]
                pangkalan_id = account.get("pangkalan_id", username)  # Get Pangkalan_id or fallback to username
            else:
                # Assuming tuple format (nama, username, pin, pangkalan_id) or old format (nama, username, pin)
                account_id = idx
                if len(account) >= 4:
                    nama = account[0]
                    username = account[1]
                    pin = account[2]
                    pangkalan_id = account[3]
                else:
                    nama = account[0]
                    username = account[1]
                    pin = account[2]
                    pangkalan_id = username  # Fallback to username for old format
                
            # Start processing account
            self.telemetry.record_account_start(username)
            progress_percent = int((idx / total_accounts) * 100)
            self._update_progress(idx, total_accounts, progress_percent)
            self._update_status(account_id, "processing", 0)
            self._log(f"Memproses: {nama} ({username})", "info")
            
            browser_manager = None
            
            try:
                # 1. Check Internet
                if not check_before_step("setup browser", username, max_wait=300, log_callback=lambda m, l: self._log(m, l)):
                    self._handle_failure(account_id, username, nama, "connection_timeout", f"Timeout koneksi internet untuk {nama}")
                    continue
                    
                # 2. Setup Browser
                self._update_status(account_id, "processing", 10)
                self._log(f"Setup browser untuk {nama}...", "info")
                
                self.telemetry.start_operation("browser_setup", username)
                browser_manager = PlaywrightBrowserManager()
                page = browser_manager.setup_browser(headless=headless_mode, use_session=False)
                self.telemetry.end_operation("browser_setup", username)
                
                if not headless_mode:
                    time.sleep(2.0)
                    
                if not page:
                    self._handle_failure(account_id, username, nama, "browser_setup_failed", f"Gagal setup browser untuk {nama}")
                    continue
                    
                # 3. Login
                if not check_before_step("login", username, max_wait=300, log_callback=lambda m, l: self._log(m, l)):
                    self._handle_failure(account_id, username, nama, "connection_timeout_login", f"Timeout koneksi sebelum login untuk {nama}")
                    browser_manager.close()
                    continue
                    
                self._update_status(account_id, "processing", 30)
                self._log(f"Login untuk {nama}...", "info")
                
                self.telemetry.start_operation("login", username)
                
                # Retry mechanism for login
                max_retries = 1
                success = False
                gagal_info = {}
                
                for attempt in range(max_retries + 1):
                    if attempt > 0:
                        self._log(f"Login gagal, mencoba ulang proses login untuk {nama}...", "warning")
                        time.sleep(2.0)
                        
                    success, gagal_info = login_direct(page, username, pin)
                    
                    if success:
                        break
                
                self.telemetry.end_operation("login", username)
                
                if not success:
                    self._handle_failure(account_id, username, nama, "login_failed", f"Login gagal untuk {nama}")
                    browser_manager.close()
                    continue
                    
                self._log(f"Login berhasil untuk {nama}", "success")
                
                # 4. Get Data
                if not check_before_step("get data", username, max_wait=300, log_callback=lambda m, l: self._log(m, l)):
                    self._handle_failure(account_id, username, nama, "connection_timeout_data", f"Timeout koneksi sebelum ambil data untuk {nama}")
                    browser_manager.close()
                    continue
                    
                # Ambil Stok
                self._update_status(account_id, "processing", 50)
                self._log(f"Mengambil stok untuk {nama}...", "info")
                
                self.telemetry.start_operation("get_stock", username)
                stok_value = get_stock_value_direct(page)
                self.telemetry.end_operation("get_stock", username)
                
                if stok_value:
                    self._log(f"Stok {nama}: {stok_value} tabung", "success")
                else:
                    self._log(f"Gagal ambil stok untuk {nama}", "warning")
                    
                # Ambil Penjualan
                self._update_status(account_id, "processing", 70)
                self._log(f"Mengambil data penjualan untuk {nama}...", "info")
                
                tabung_terjual = None
                if click_laporan_penjualan_direct(page):
                    if selected_date:
                        self._log(f"Menerapkan filter tanggal: {selected_date.strftime('%d/%m/%Y')}", "info")
                        if click_date_elements_direct(page, selected_date):
                            self._log("Filter tanggal berhasil diterapkan", "success")
                        else:
                            self._log("Gagal menerapkan filter tanggal", "warning")
                            
                    tabung_terjual = get_tabung_terjual_direct(page)
                    if tabung_terjual is not None:
                        self._log(f"Tabung terjual {nama}: {tabung_terjual}", "success")
                    else:
                        self._log(f"Gagal ambil tabung terjual untuk {nama}", "warning")
                else:
                    self._log(f"Gagal navigasi ke Laporan Penjualan untuk {nama}", "warning")
                    
                # 5. Process Result
                self._update_status(account_id, "processing", 90)
                
                stok_int = self._safe_int(stok_value)
                terjual_int = self._safe_int(tabung_terjual)
                
                stok_formatted = f"{stok_int} Tabung"
                tabung_formatted = f"{terjual_int} Tabung"
                status = "Ada Penjualan" if terjual_int > 0 else "Tidak Ada Penjualan"
                
                result = {
                    "pangkalan_id": pangkalan_id,  # Use Pangkalan_id instead of username
                    "nama": nama,
                    "username": username,
                    "stok": stok_formatted,
                    "tabung_terjual": tabung_formatted,
                    "status": status,
                    "waktu": 0 # Bisa ditambahkan perhitungan waktu per akun
                }
                self.results.append(result)
                
                # Save to Excel
                save_date = selected_date if selected_date else datetime.now()
                tanggal_check = save_date.strftime("%Y-%m-%d")
                
                save_to_excel_pivot_format(
                    pangkalan_id=pangkalan_id,  # Use Pangkalan_id instead of username
                    nama_pangkalan=nama,
                    tanggal_check=tanggal_check,
                    stok_awal=stok_formatted,
                    total_inputan=tabung_formatted,
                    status=status,
                    selected_date=save_date,
                )
                
                # Telemetry Success
                self.telemetry.record_account_success(username, {
                    "stok": stok_formatted,
                    "terjual": tabung_formatted,
                    "status": status
                })
                self.telemetry.record_business_metrics(stok_int, terjual_int)
                
                # Update Supabase if client exists
                if self.supabase_client:
                    self._log(f"Updating database untuk {username}...", "info")
                    if self.supabase_client.update_account_result(username, stok_formatted, tabung_formatted, status):
                        self._log("Database updated", "success")
                    else:
                        self._log("Gagal update database", "warning")
                
                # Call callback for result
                if self.callbacks.get("on_result"):
                    self.callbacks["on_result"](result)
                
                self._update_status(account_id, f"done|Stok: {stok_formatted}, Input: {tabung_formatted}", 100)
                self._log(f"Selesai: {nama} - Stok: {stok_formatted}, Terjual: {tabung_formatted}", "success")
                self._update_progress(idx + 1, total_accounts, progress_percent)
                
            except Exception as e:
                self._handle_failure(account_id, username, nama, "exception", f"Error untuk {nama}: {str(e)}")
                self.logger.error(f"Exception processing {nama}: {str(e)}", exc_info=True)
                
            finally:
                if not headless_mode:
                    time.sleep(1.0)
                if browser_manager:
                    browser_manager.close()
                    
                # Delay antar akun
                if idx < total_accounts - 1 and not self.stop_requested:
                    self._log(f"Delay {delay} detik...", "info")
                    time.sleep(delay)
                    
        self._log(f"Proses selesai! Total: {len(self.results)} akun berhasil diproses", "success")
        return self.results

    def _handle_failure(self, account_id, username, nama, error_type, message):
        """Helper untuk handle failure case"""
        self._update_status(account_id, "error", 0)
        self._log(message, "error")
        self.telemetry.record_account_failure(username, error_type, message, nama)

    def _safe_int(self, val):
        """Helper konversi int aman"""
        try:
            if val is None:
                return 0
            return int(str(val).replace(".", "").replace(",", ""))
        except:
            return 0
