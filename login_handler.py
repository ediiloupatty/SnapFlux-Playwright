"""
Login handling dan fungsi authentication untuk platform merchant Pertamina
File ini menangani proses login dan error handling menggunakan Playwright
"""

import logging
import time

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Import constants dari local module
try:
    from .constants import DEFAULT_DELAY, LOGIN_URL
except ImportError:
    try:
        from constants import DEFAULT_DELAY, LOGIN_URL
    except ImportError:
        LOGIN_URL = "https://subsiditepatlpg.mypertamina.id/merchant-login"
        DEFAULT_DELAY = 2.0

logger = logging.getLogger("playwright_automation")


def login_direct(page: Page, username: str, pin: str):
    """
    ============================================
    FUNGSI LOGIN OTOMATIS KE PORTAL MERCHANT
    ============================================

    Fungsi ini melakukan login otomatis ke portal merchant Pertamina dengan Playwright.
    Menggunakan direct selector untuk performa optimal.

    Proses yang dilakukan:
    1. Navigasi ke halaman login
    2. Mencari dan mengisi field email/username
    3. Mencari dan mengisi field PIN/password
    4. Mencari dan mengklik tombol login
    5. Deteksi pesan "Gagal Masuk Akun" jika ada
    6. Return status login

    Args:
        page (Page): Playwright Page object
        username (str): Username berupa email atau nomor HP merchant
        pin (str): PIN untuk authentication ke portal

    Returns:
        tuple: (success, dict) - Status login dan info gagal masuk akun
               Jika login berhasil: (True, {'gagal_masuk_akun': False, 'count': 0})
               Jika login gagal: (False, {'gagal_masuk_akun': False, 'count': 0})
               Jika ada gagal masuk akun: (True/False, {'gagal_masuk_akun': True, 'count': 1})
    """
    print(f"\n🔐 === LOGIN LANGSUNG UNTUK {username} ===")

    try:
        # Navigasi ke halaman login
        print(f"🌐 Navigasi ke {LOGIN_URL}...")
        page.goto(LOGIN_URL, wait_until="domcontentloaded")

        # Tunggu halaman loading - OPTIMIZED DELAY
        time.sleep(1.0)

        # Langsung cari dan isi email
        print("📧 Mencari dan mengisi field email...")
        email_filled = False

        # Coba berbagai selector untuk email field
        email_selectors = [
            'input[type="text"]',
            'input[type="email"]',
            'input[name="email"]',
            'input[name="username"]',
            'input[placeholder*="Email"]',
            'input[placeholder*="email"]',
        ]

        for selector in email_selectors:
            try:
                email_input = page.locator(selector).first
                if email_input.count() > 0:
                    try:
                        email_input.wait_for(state="visible", timeout=2000)
                        email_input.clear()
                        email_input.fill(username)
                        print(f"✅ Email berhasil diisi: {username}")
                        email_filled = True
                        break
                    except Exception:
                        continue
            except Exception:
                continue

        if not email_filled:
            print("❌ Gagal mengisi email")
            return False, {"gagal_masuk_akun": False, "count": 0}

        # Langsung cari dan isi PIN
        print("🔑 Mencari dan mengisi field PIN...")
        pin_filled = False

        # Coba berbagai selector untuk PIN field
        pin_selectors = [
            'input[type="password"]',
            'input[name="password"]',
            'input[name="pin"]',
            'input[placeholder*="PIN"]',
            'input[placeholder*="Password"]',
        ]

        for selector in pin_selectors:
            try:
                pin_input = page.locator(selector).first
                if pin_input.count() > 0:
                    try:
                        pin_input.wait_for(state="visible", timeout=2000)
                        pin_input.clear()
                        pin_input.fill(pin)
                        print(f"✅ PIN berhasil diisi: {pin}")
                        pin_filled = True
                        break
                    except Exception:
                        continue
            except Exception:
                continue

        if not pin_filled:
            print("❌ Gagal mengisi PIN")
            return False, {"gagal_masuk_akun": False, "count": 0}

        # Langsung cari dan klik tombol login
        print("🚀 Mencari dan mengklik tombol login...")
        login_clicked = False

        # Coba berbagai selector untuk tombol login
        login_selectors = [
            'button:has-text("MASUK")',
            'button:has-text("Masuk")',
            'button:has-text("LOGIN")',
            'button:has-text("Login")',
            'button[type="submit"]',
        ]

        for selector in login_selectors:
            try:
                login_button = page.locator(selector).first
                if login_button.count() > 0:
                    try:
                        login_button.wait_for(state="visible", timeout=2000)
                        if login_button.is_enabled():
                            login_button.click()
                            print("✅ Tombol login berhasil diklik")
                            login_clicked = True
                            break
                    except Exception:
                        continue
            except Exception:
                continue

        if not login_clicked:
            print("❌ Gagal mengklik tombol login")
            return False, {"gagal_masuk_akun": False, "count": 0}

        # Tunggu proses login - beri waktu untuk modal muncul
        print("⏳ Menunggu proses login...")
        time.sleep(5.0)

        # === DETEKSI PESAN "GAGAL MASUK AKUN" ===
        gagal_masuk_detected = False

        print("🔍 Memeriksa apakah ada pesan 'Gagal Masuk Akun'...")
        try:
            # Cek apakah ada pesan "Gagal Masuk Akun" dengan berbagai selector
            error_selectors = [
                # Title/Header selectors
                "h5:has-text('Gagal Masuk Akun')",
                "h4:has-text('Gagal Masuk Akun')",
                "h3:has-text('Gagal Masuk Akun')",
                ".mantine-Title-root:has-text('Gagal Masuk Akun')",
                # Text content selectors
                "text=Gagal Masuk Akun",
                "text=Akun anda tidak dapat melakukan login",
                "text=salah PIN 5 kali",
                "text=Login kembali setelah",
                # Modal/Dialog selectors
                "[role='dialog']:has-text('Gagal Masuk Akun')",
                ".modal:has-text('Gagal Masuk Akun')",
                ".dialog:has-text('Gagal Masuk Akun')",
                # Generic container selectors
                "div:has-text('Gagal Masuk Akun')",
                "div:has-text('salah PIN 5 kali')",
                "p:has-text('Akun anda tidak dapat melakukan login')",
            ]

            for selector in error_selectors:
                try:
                    print(f"   Mencoba selector: {selector}")
                    error_element = page.locator(selector).first
                    if error_element.count() > 0:
                        try:
                            error_element.wait_for(state="visible", timeout=2000)
                            gagal_masuk_detected = True
                            print("❌ PESAN 'GAGAL MASUK AKUN' TERDETEKSI!")
                            print("   Akun tidak dapat login karena salah PIN 5 kali")

                            # Coba ambil text lengkap pesan
                            try:
                                full_text = error_element.text_content()
                                if full_text:
                                    print(f"   Pesan lengkap: {full_text[:100]}...")
                            except Exception:
                                pass

                            break
                        except Exception:
                            continue
                except Exception as e:
                    print(f"   ✗ Selector gagal: {str(e)[:50]}")
                    continue

            if not gagal_masuk_detected:
                print("✓ Tidak ada pesan 'Gagal Masuk Akun'")
        except Exception as e:
            print(f"⚠️ Error saat cek pesan error: {str(e)}")

        # === HANDLE GAGAL MASUK AKUN ===
        if gagal_masuk_detected:
            print("🔄 === PROSES RETRY LOGIN SETELAH GAGAL MASUK AKUN ===")
            print("⏳ Menunggu 2 menit (120 detik)...")

            # Tunggu 120 detik
            time.sleep(120)
            print("✅ Tunggu 2 menit selesai!")

            # Langsung klik tombol MASUK lagi tanpa reload
            print("🔄 Mengklik tombol MASUK lagi tanpa refresh halaman...")

            retry_clicked = False
            for selector in login_selectors:
                try:
                    login_button = page.locator(selector).first
                    if login_button.count() > 0:
                        try:
                            login_button.wait_for(state="visible", timeout=2000)
                            if login_button.is_enabled():
                                login_button.click()
                                print("✅ Tombol MASUK berhasil diklik lagi!")
                                retry_clicked = True
                                break
                        except Exception:
                            continue
                except Exception:
                    continue

            if not retry_clicked:
                print("❌ Gagal mengklik tombol MASUK lagi")
                return False, {"gagal_masuk_akun": gagal_masuk_detected, "count": 1}

            # Tunggu proses login kedua
            print("⏳ Menunggu proses login kedua...")
            time.sleep(3.0)

        # Tunggu dan verifikasi dashboard muncul
        print("🔍 Memverifikasi login berhasil...")
        dashboard_loaded = wait_for_dashboard(page, timeout=15000)

        # Cek URL sebagai fallback
        current_url = page.url
        is_not_login_page = "merchant-login" not in current_url

        if dashboard_loaded or is_not_login_page:
            if dashboard_loaded:
                print("✅ Login berhasil!")
            else:
                print("✅ Login berhasil! (URL sudah berubah dari halaman login)")
            return True, {
                "gagal_masuk_akun": gagal_masuk_detected,
                "count": 1 if gagal_masuk_detected else 0,
            }
        else:
            print("❌ Login gagal - masih di halaman login")
            print(f"   Current URL: {current_url}")
            return False, {
                "gagal_masuk_akun": gagal_masuk_detected,
                "count": 1 if gagal_masuk_detected else 0,
            }

    except Exception as e:
        print(f"❌ Error dalam login: {str(e)}")
        logger.error(f"Error dalam login: {str(e)}", exc_info=True)
        return False, {"gagal_masuk_akun": False, "count": 0}


def wait_for_dashboard(page: Page, timeout: int = 10000):
    """
    Menunggu hingga dashboard merchant muncul setelah login

    Args:
        page (Page): Playwright Page object
        timeout (int): Timeout dalam milliseconds (default 10000 = 10 detik)

    Returns:
        bool: True jika dashboard berhasil dimuat, False jika tidak
    """
    try:
        # Tunggu hingga URL berubah dari halaman login
        page.wait_for_url(lambda url: "merchant-login" not in url, timeout=timeout)

        # Verifikasi beberapa elemen dashboard
        dashboard_indicators = [
            "text=Dashboard",
            "text=Laporan Penjualan",
            "text=Atur Produk",
            "text=Catat Penjualan",
            "text=Atur Stok",
            "[class*='dashboard']",
            "[class*='sidebar']",
        ]

        for selector in dashboard_indicators:
            try:
                element = page.locator(selector).first
                if element.count() > 0:
                    try:
                        element.wait_for(state="visible", timeout=2000)
                        print("✅ Dashboard berhasil dimuat")
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        # Jika tidak ada elemen dashboard yang ditemukan tapi URL sudah berubah
        if "merchant-login" not in page.url:
            print("✅ Login berhasil (URL berubah dari halaman login)")
            return True

        print("⚠️ Dashboard tidak terdeteksi tapi masih mencoba melanjutkan")
        return False

    except PlaywrightTimeoutError:
        # Jika timeout tapi URL sudah berubah, anggap berhasil
        if "merchant-login" not in page.url:
            print("✅ Login berhasil (URL sudah bukan halaman login)")
            return True
        print("⏱️ Timeout menunggu dashboard")
        return False
    except Exception as e:
        print(f"⚠️ Error menunggu dashboard: {str(e)}")
        return False


def is_logged_in(page: Page):
    """
    Cek apakah user sudah login dengan memeriksa URL dan elemen dashboard

    Args:
        page (Page): Playwright Page object

    Returns:
        bool: True jika sudah login, False jika belum
    """
    try:
        current_url = page.url

        # Jika masih di halaman login, berarti belum login
        if "merchant-login" in current_url:
            return False

        # Cek apakah ada elemen yang menandakan user sudah login
        dashboard_selectors = [
            "text=Dashboard",
            "text=Laporan Penjualan",
            "text=Atur Produk",
        ]

        for selector in dashboard_selectors:
            try:
                element = page.locator(selector).first
                if element.count() > 0:
                    try:
                        element.wait_for(state="visible", timeout=1000)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        # Jika URL bukan login page dan ada content, assume logged in
        if "merchant-login" not in current_url:
            return True

        return False

    except Exception as e:
        print(f"⚠️ Error cek login status: {str(e)}")
        return False


def logout(page: Page):
    """
    Logout dari akun merchant

    Args:
        page (Page): Playwright Page object

    Returns:
        bool: True jika logout berhasil, False jika gagal
    """
    try:
        print("🚪 Melakukan logout...")

        # Coba cari tombol logout
        logout_selectors = [
            "button:has-text('Logout')",
            "button:has-text('Keluar')",
            "a:has-text('Logout')",
            "a:has-text('Keluar')",
            "[class*='logout']",
        ]

        for selector in logout_selectors:
            try:
                logout_button = page.locator(selector).first
                if logout_button.count() > 0:
                    try:
                        logout_button.wait_for(state="visible", timeout=2000)
                        logout_button.click()
                        print("✅ Tombol logout berhasil diklik")
                        time.sleep(1.0)

                        # Verifikasi logout berhasil
                        if "merchant-login" in page.url:
                            print("✅ Logout berhasil")
                            return True
                        break
                    except Exception:
                        continue
            except Exception:
                continue

        return False

    except Exception as e:
        print(f"⚠️ Error saat logout: {str(e)}")
        return False
