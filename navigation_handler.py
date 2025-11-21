"""
Navigation handling untuk berpindah antar halaman di platform merchant
File ini menangani proses navigasi menggunakan Playwright
"""

import logging
import time
from typing import Optional

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from datetime import datetime

# Import constants dari local module
try:
    from .constants import DEFAULT_DELAY
except ImportError:
    try:
        from constants import DEFAULT_DELAY
    except ImportError:
        DEFAULT_DELAY = 2.0

logger = logging.getLogger("playwright_automation")


def click_laporan_penjualan_direct(page: Page) -> bool:
    """
    ============================================
    FUNGSI KLIK MENU LAPORAN PENJUALAN - DIRECT
    ============================================

    Mencari dan mengklik menu "Laporan Penjualan" di sidebar/menu

    Args:
        page (Page): Playwright Page object

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    print("Mencari dan mengklik menu Laporan Penjualan...")

    try:
        # Tunggu halaman stabil
        time.sleep(2.0)

        # Coba berbagai selector untuk menu Laporan Penjualan
        # Coba selector yang terbukti berhasil untuk menu Laporan Penjualan
        menu_selectors = [
            # Selector utama yang berhasil
            "div:has(img[alt*='sale']):has-text('Laporan Penjualan')",
            # Backup selectors jika yang utama gagal
            "div:has(img[src*='icon-saleReport']):has-text('Laporan Penjualan')",
            "text=Laporan Penjualan",
            "[href*='laporan-penjualan']",
        ]

        for selector in menu_selectors:
            try:
                print(f"   Mencoba selector: {selector}")
                menu_item = page.locator(selector).first

                # Cek apakah elemen ada dengan count
                if menu_item.count() == 0:
                    print(f"   ✗ Elemen tidak ditemukan")
                    continue

                # Scroll ke elemen jika ada
                try:
                    menu_item.scroll_into_view_if_needed()
                    time.sleep(0.5)
                except Exception:
                    pass

                # Tunggu elemen visible dengan wait_for
                try:
                    menu_item.wait_for(state="visible", timeout=3000)
                except Exception:
                    print(f"   ✗ Elemen tidak visible")
                    continue

                print(f"   ✓ Elemen ditemukan, mengklik...")
                menu_item.click(force=True)
                print("✓ Menu Laporan Penjualan berhasil diklik")
                time.sleep(2.0)
                return True
            except Exception as e:
                print(f"   ✗ Selector gagal: {str(e)[:50]}")
                continue

        print("✗ Gagal menemukan menu Laporan Penjualan dengan semua selector")
        return False

    except Exception as e:
        print(f"✗ Error klik Laporan Penjualan: {str(e)}")
        logger.error(f"Error click_laporan_penjualan_direct: {str(e)}", exc_info=True)
        return False


def navigate_to_atur_produk(page: Page) -> bool:
    """
    ============================================
    FUNGSI NAVIGASI KE ATUR PRODUK
    ============================================

    Mencari dan mengklik menu "Atur Produk" untuk cek stok

    Args:
        page (Page): Playwright Page object

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    print("Mencari dan mengklik menu Atur Produk...")

    try:
        # Tunggu halaman stabil
        time.sleep(1.0)

        # Coba berbagai selector untuk menu Atur Produk
        menu_selectors = [
            "text=Atur Produk",
            "a:has-text('Atur Produk')",
            "button:has-text('Atur Produk')",
            "div:has-text('Atur Produk')",
            "[href*='atur-produk']",
            "[href*='atur_produk']",
            "[href*='produk']",
        ]

        for selector in menu_selectors:
            try:
                menu_item = page.locator(selector).first
                if menu_item.count() > 0:
                    try:
                        menu_item.wait_for(state="visible", timeout=2000)
                        menu_item.click()
                        print("✓ Menu Atur Produk berhasil diklik")
                        time.sleep(1.5)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        print("✗ Gagal menemukan menu Atur Produk")
        return False

    except Exception as e:
        print(f"✗ Error navigasi ke Atur Produk: {str(e)}")
        logger.error(f"Error navigate_to_atur_produk: {str(e)}", exc_info=True)
        return False


def click_rekap_penjualan_direct(page: Page) -> bool:
    """
    ============================================
    FUNGSI KLIK REKAP PENJUALAN - DIRECT
    ============================================

    Mencari dan mengklik menu/tab "Rekap Penjualan" di halaman Laporan Penjualan

    Args:
        page (Page): Playwright Page object

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    print("Mencari dan mengklik Rekap Penjualan...")

    try:
        # Tunggu halaman stabil
        time.sleep(1.0)

        # Coba berbagai selector untuk Rekap Penjualan
        rekap_selectors = [
            "text=Rekap Penjualan",
            "a:has-text('Rekap Penjualan')",
            "button:has-text('Rekap Penjualan')",
            "div:has-text('Rekap Penjualan')",
            "[href*='rekap-penjualan']",
            "[href*='rekap_penjualan']",
            "tab:has-text('Rekap Penjualan')",
        ]

        for selector in rekap_selectors:
            try:
                rekap_item = page.locator(selector).first
                if rekap_item.count() > 0:
                    try:
                        rekap_item.wait_for(state="visible", timeout=2000)
                        rekap_item.click()
                        print("✓ Rekap Penjualan berhasil diklik")
                        time.sleep(1.5)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        print("✗ Gagal menemukan Rekap Penjualan")
        return False

    except Exception as e:
        print(f"✗ Error klik Rekap Penjualan: {str(e)}")
        logger.error(f"Error click_rekap_penjualan_direct: {str(e)}", exc_info=True)
        return False


def click_catat_penjualan_direct(page: Page) -> bool:
    """
    ============================================
    FUNGSI KLIK CATAT PENJUALAN - DIRECT
    ============================================

    Mencari dan mengklik menu "Catat Penjualan" untuk input transaksi baru

    Args:
        page (Page): Playwright Page object

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    print("📝 Mencari dan mengklik menu Catat Penjualan...")

    try:
        # Tunggu halaman stabil
        time.sleep(1.0)

        # Coba berbagai selector untuk menu Catat Penjualan
        menu_selectors = [
            "text=Catat Penjualan",
            "a:has-text('Catat Penjualan')",
            "button:has-text('Catat Penjualan')",
            "div:has-text('Catat Penjualan')",
            "[href*='catat-penjualan']",
            "[href*='catat_penjualan']",
        ]

        for selector in menu_selectors:
            try:
                menu_item = page.locator(selector).first
                if menu_item.count() > 0:
                    try:
                        menu_item.wait_for(state="visible", timeout=2000)
                        menu_item.click()
                        print("✓ Menu Catat Penjualan berhasil diklik")
                        time.sleep(1.5)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        print("✗ Gagal menemukan menu Catat Penjualan")
        return False

    except Exception as e:
        print(f"✗ Error klik Catat Penjualan: {str(e)}")
        logger.error(f"Error click_catat_penjualan_direct: {str(e)}", exc_info=True)
        return False


        return False


def get_indo_month(month_int: int) -> tuple:
    """
    Helper untuk mendapatkan nama bulan Indonesia (Full dan Singkat)
    """
    months = {
        1: ("Januari", "Jan"),
        2: ("Februari", "Feb"),
        3: ("Maret", "Mar"),
        4: ("April", "Apr"),
        5: ("Mei", "Mei"),
        6: ("Juni", "Jun"),
        7: ("Juli", "Jul"),
        8: ("Agustus", "Agt"), # Sesuaikan dengan UI: Agt atau Agu
        9: ("September", "Sep"),
        10: ("Oktober", "Okt"),
        11: ("November", "Nov"),
        12: ("Desember", "Des"),
    }
    return months.get(month_int, ("", ""))


def click_date_elements_direct(page: Page, target_date: datetime) -> bool:
    """
    ============================================
    FUNGSI FILTER TANGGAL - DIRECT (4 STEPS)
    ============================================
    
    Alur:
    1. Klik "Atur Rentang Waktu"
    2. Klik Header "Bulan Tahun" (misal: "November 2025") -> Membuka pilihan bulan
    3. Klik Bulan Singkat (misal: "Nov") -> Membuka pilihan tanggal
    4. Klik Tanggal (misal: "20") -> Klik 2x
    """
    print(f"📅 Memilih tanggal: {target_date.strftime('%d/%m/%Y')} (4 Steps)...")

    try:
        # Tunggu halaman stabil
        time.sleep(1.0)

        # === STEP 1: Klik Button "Atur Rentang Waktu" ===
        print("   Step 1: Klik 'Atur Rentang Waktu'...")
        step1_selectors = [
            "button:has-text('Atur Rentang Waktu')",
            "div:has-text('Atur Rentang Waktu')",
            ".date-range-picker", 
        ]
        
        step1_success = False
        for selector in step1_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0 and elem.is_visible():
                    elem.click()
                    step1_success = True
                    time.sleep(1.0)
                    break
            except:
                continue
        
        if not step1_success:
            print("   ⚠ Tidak menemukan tombol 'Atur Rentang Waktu', mencoba lanjut...")

        # Persiapkan data tanggal
        day = target_date.day
        month = target_date.month
        year = target_date.year
        month_full, month_short = get_indo_month(month)
        
        # Format header biasanya "Bulan Tahun" (e.g., "November 2025")
        # Kita cari tombol yang text-nya ADALAH "Bulan Tahun" saat ini
        # Karena default kalender biasanya membuka bulan saat ini/terakhir dipilih
        
        # Note: Kita perlu mencari tombol header yang sedang aktif.
        # Biasanya tombol ini berada di bagian atas kalender.
        
        # === STEP 2: Klik Header "Bulan Tahun" ===
        # Tujuannya untuk membuka view pemilihan bulan (Jan, Feb, Mar...)
        print(f"   Step 2: Klik Header (Mencari tombol dengan tahun '{year}')...")
        
        step2_success = False
        try:
            # Cari tombol yang mengandung teks Tahun (misal 2025) dan Bulan (misal November)
            # Locator ini mencari tombol di dalam struktur kalender yang menampilkan "November 2025"
            # Kita gunakan strategi: cari tombol yang punya text bulan lengkap DAN tahun
            
            # Coba 1: Cari tombol spesifik dengan text "Bulan Tahun" (misal "November 2025")
            # Ini asumsi kalender sedang menampilkan bulan sesuai tanggal hari ini/default
            # Jika user input bulan lain, kita tetap harus klik header yang TAMPIL SAAT INI dulu
            
            # Ambil text dari header kalender yang sedang tampil
            # Biasanya class-nya mantine-Calendar-monthLevelGroup atau sejenisnya
            # Kita cari tombol yang ada di bagian atas popover
            
            # Generic locator untuk header: tombol yang mengandung tahun target
            header_btn = page.locator(f"button:has-text('{year}')").first
            
            if header_btn.count() > 0 and header_btn.is_visible():
                header_text = header_btn.text_content()
                print(f"      -> Menemukan header: '{header_text}'")
                header_btn.click()
                step2_success = True
                time.sleep(1.0) # Tunggu grid bulan muncul
            else:
                print(f"      ⚠ Tidak menemukan tombol header dengan tahun {year}")
                
        except Exception as e:
            print(f"   ⚠ Warning Step 2: {e}")

        # === STEP 3: Klik Bulan Singkat (Jan, Feb, ... Nov, Des) ===
        # Grid bulan seharusnya sudah terbuka sekarang
        print(f"   Step 3: Klik Bulan '{month_short}'...")
        
        step3_success = False
        try:
            # Cari tombol dengan text bulan singkat persis
            # Gunakan text-is atau has-text tapi pastikan itu tombol pilihan bulan
            month_btn = page.locator(f"button:text-is('{month_short}')").first
            
            if month_btn.count() == 0:
                # Coba variasi lain jika Agt/Agu
                if month == 8:
                    alt_aug = "Agu" if month_short == "Agt" else "Agt"
                    month_btn = page.locator(f"button:text-is('{alt_aug}')").first
            
            if month_btn.count() > 0 and month_btn.is_visible():
                month_btn.click()
                step3_success = True
                print(f"      -> Berhasil klik bulan {month_short}")
                time.sleep(1.0) # Tunggu grid tanggal muncul
            else:
                print(f"      ⚠ Tidak menemukan tombol bulan '{month_short}'")
                
        except Exception as e:
            print(f"   ⚠ Warning Step 3: {e}")

        # === STEP 4: Klik Tanggal (Specific Day) - KLIK 2X ===
        print(f"   Step 4: Klik Tanggal '{day}' (2x)...")

        try:
            # Cari tombol tanggal. Hati-hati dengan angka yang sama di bulan sebelumnya/berikutnya.
            # Biasanya tanggal aktif punya class tertentu atau tidak punya class 'outside'/'muted'
            
            # Locator spesifik untuk tanggal di kalender (hindari tanggal dari bulan lain jika mungkin)
            # Menggunakan text exact match untuk angka
            date_btn = page.locator(f"button:text-is('{day}')").first
            
            if date_btn.count() == 0:
                 # Fallback: contains text
                 date_btn = page.locator(f"button:has-text('{day}')").first
            
            if date_btn.count() > 0:
                # Klik pertama
                date_btn.click()
                print(f"      -> Klik pertama tanggal {day}")
                time.sleep(1.0) # Delay diperlama agar tidak dianggap double-click instan
                
                # Klik kedua
                date_btn.click()
                print(f"      -> Klik kedua tanggal {day}")
                
                print(f"   ✓ Berhasil klik tanggal {day} (2x)")
                time.sleep(1.5) # Tunggu efek UI selesai
                return True
            else:
                print(f"   ✗ Gagal menemukan tombol tanggal {day}")
                return False
                
        except Exception as e:
            print(f"   ✗ Error Step 4: {e}")
            return False

    except Exception as e:
        print(f"✗ Error set tanggal (4-step): {str(e)}")
        logger.error(f"Error click_date_elements_direct: {str(e)}", exc_info=True)
        return False


def click_date_elements_rekap_penjualan(page: Page, target_date: datetime) -> bool:
    """
    ============================================
    FUNGSI FILTER TANGGAL REKAP PENJUALAN (4 STEPS)
    ============================================
    
    Implementasi logika 4 langkah untuk halaman Rekap Penjualan
    """
    print(f"📅 Memilih tanggal Rekap: {target_date.strftime('%d/%m/%Y')} (4 Steps)...")

    try:
        time.sleep(1.0)
        
        # === STEP 1: Klik Button "Atur Rentang Waktu" ===
        # Di rekap penjualan mungkin labelnya berbeda atau sama
        print("   Step 1: Klik 'Atur Rentang Waktu'...")
        step1_selectors = [
            "button:has-text('Atur Rentang Waktu')",
            "div:has-text('Atur Rentang Waktu')",
            "input[placeholder*='Pilih tanggal']", # Kadang berupa input
        ]
        
        step1_success = False
        for selector in step1_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0:
                    elem.click()
                    step1_success = True
                    time.sleep(1.0)
                    break
            except:
                continue
                
        if not step1_success:
            print("   ⚠ Tidak menemukan tombol 'Atur Rentang Waktu' di Rekap")

        # Persiapkan data
        day = target_date.day
        month = target_date.month
        year = target_date.year
        month_full, month_short = get_indo_month(month)
        target_month_year = f"{month_full} {year}"

        # === STEP 2: Klik Header "Bulan Tahun" ===
        print(f"   Step 2: Klik Header (Mencari tombol dengan tahun '{year}')...")
        try:
            header_btn = page.locator(f"button:has-text('{year}')").first
            if header_btn.count() > 0:
                print(f"      -> Menemukan header: '{header_btn.text_content()}'")
                header_btn.click()
                time.sleep(1.0)
            else:
                print(f"      ⚠ Tidak menemukan tombol header tahun {year}")
        except Exception:
            pass

        # === STEP 3: Klik Bulan Singkat ===
        print(f"   Step 3: Klik Bulan '{month_short}'...")
        try:
            month_btn = page.locator(f"button:text-is('{month_short}')").first
            
            if month_btn.count() == 0 and month == 8:
                 alt_aug = "Agu" if month_short == "Agt" else "Agt"
                 month_btn = page.locator(f"button:text-is('{alt_aug}')").first

            if month_btn.count() > 0:
                month_btn.click()
                print(f"      -> Berhasil klik bulan {month_short}")
                time.sleep(1.0)
            else:
                print(f"      ⚠ Tidak menemukan tombol bulan '{month_short}'")
        except Exception:
            pass

        # === STEP 4: Klik "Tanggal" (2x) ===
        print(f"   Step 4: Klik Tanggal '{day}' (2x)...")
        try:
            date_btn = page.locator(f"button:text-is('{day}')").first
            if date_btn.count() == 0:
                 date_btn = page.locator(f"button:has-text('{day}')").first
            
            if date_btn.count() > 0:
                date_btn.click()
                print(f"      -> Klik pertama tanggal {day}")
                time.sleep(1.0) # Delay diperlama
                
                date_btn.click()
                print(f"      -> Klik kedua tanggal {day}")
                
                print(f"   ✓ Berhasil klik tanggal {day} (2x)")
                time.sleep(1.5) # Tunggu efek UI
                return True
            else:
                print(f"   ✗ Gagal menemukan tombol tanggal {day}")
                return False
        except Exception as e:
            print(f"   ✗ Error Step 4: {e}")
            return False

    except Exception as e:
        print(f"✗ Error set tanggal rekap (4-step): {str(e)}")
        logger.error(f"Error click_date_elements_rekap_penjualan: {str(e)}", exc_info=True)
        return False


def find_and_click_element_by_text(
    page: Page, text: str, element_type: str = "button"
) -> bool:
    """
    Helper function untuk mencari dan mengklik elemen berdasarkan text

    Args:
        page (Page): Playwright Page object
        text (str): Text yang dicari
        element_type (str): Tipe elemen (button, a, div, etc)

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        selectors = [
            f"{element_type}:has-text('{text}')",
            f"text={text}",
            f"{element_type}:text-is('{text}')",
        ]

        for selector in selectors:
            try:
                element = page.locator(selector).first
                if element.count() > 0:
                    try:
                        element.wait_for(state="visible", timeout=2000)
                        element.click()
                        print(f"✓ Element '{text}' berhasil diklik")
                        time.sleep(1.0)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        return False

    except Exception as e:
        print(f"⚠ Error find and click element: {str(e)}")
        return False


def wait_for_page_load(page: Page, timeout: int = 10000) -> bool:
    """
    Menunggu hingga halaman selesai loading

    Args:
        page (Page): Playwright Page object
        timeout (int): Timeout dalam milliseconds

    Returns:
        bool: True jika berhasil, False jika timeout
    """
    try:
        # Tunggu network idle
        page.wait_for_load_state("networkidle", timeout=timeout)
        print("✓ Halaman selesai loading")
        return True

    except PlaywrightTimeoutError:
        print("Timeout menunggu halaman load")
        return False
    except Exception as e:
        print(f"⚠ Error wait for page load: {str(e)}")
        return False


def scroll_to_element(page: Page, selector: str) -> bool:
    """
    Scroll halaman hingga elemen terlihat

    Args:
        page (Page): Playwright Page object
        selector (str): Selector elemen yang ingin di-scroll

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        element = page.locator(selector).first
        element.scroll_into_view_if_needed()
        print(f"✓ Scroll ke elemen berhasil")
        time.sleep(0.5)
        return True

    except Exception as e:
        print(f"⚠ Error scroll to element: {str(e)}")
        return False


def go_back_to_home(page: Page) -> bool:
    """
    Kembali ke halaman utama/dashboard

    Args:
        page (Page): Playwright Page object

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        print("🏠 Kembali ke halaman utama...")

        # Coba klik menu Home/Dashboard
        home_selectors = [
            "text=Dashboard",
            "text=Home",
            "text=Beranda",
            "a:has-text('Dashboard')",
            "a:has-text('Home')",
            "a:has-text('Beranda')",
            "[href='/']",
            "[href='/dashboard']",
            "[href='/home']",
        ]

        for selector in home_selectors:
            try:
                home_item = page.locator(selector).first
                if home_item.count() > 0:
                    try:
                        home_item.wait_for(state="visible", timeout=2000)
                        home_item.click()
                        print("✓ Berhasil kembali ke halaman utama")
                        time.sleep(1.5)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        # Alternatif: gunakan browser back
        print("⚠ Mencoba browser back...")
        page.go_back()
        time.sleep(1.5)
        return True

    except Exception as e:
        print(f"✗ Error kembali ke home: {str(e)}")
        logger.error(f"Error go_back_to_home: {str(e)}", exc_info=True)
        return False
