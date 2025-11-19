"""
Navigation handling untuk berpindah antar halaman di platform merchant
File ini menangani proses navigasi menggunakan Playwright
"""

import logging
import time
from typing import Optional

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

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
    print("📊 Mencari dan mengklik menu Laporan Penjualan...")

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
                print("✅ Menu Laporan Penjualan berhasil diklik")
                time.sleep(2.0)
                return True
            except Exception as e:
                print(f"   ✗ Selector gagal: {str(e)[:50]}")
                continue

        print("❌ Gagal menemukan menu Laporan Penjualan dengan semua selector")
        return False

    except Exception as e:
        print(f"❌ Error klik Laporan Penjualan: {str(e)}")
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
    print("⚙️ Mencari dan mengklik menu Atur Produk...")

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
                        print("✅ Menu Atur Produk berhasil diklik")
                        time.sleep(1.5)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        print("❌ Gagal menemukan menu Atur Produk")
        return False

    except Exception as e:
        print(f"❌ Error navigasi ke Atur Produk: {str(e)}")
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
    print("📋 Mencari dan mengklik Rekap Penjualan...")

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
                        print("✅ Rekap Penjualan berhasil diklik")
                        time.sleep(1.5)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        print("❌ Gagal menemukan Rekap Penjualan")
        return False

    except Exception as e:
        print(f"❌ Error klik Rekap Penjualan: {str(e)}")
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
                        print("✅ Menu Catat Penjualan berhasil diklik")
                        time.sleep(1.5)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        print("❌ Gagal menemukan menu Catat Penjualan")
        return False

    except Exception as e:
        print(f"❌ Error klik Catat Penjualan: {str(e)}")
        logger.error(f"Error click_catat_penjualan_direct: {str(e)}", exc_info=True)
        return False


def click_date_elements_direct(page: Page, target_date) -> bool:
    """
    ============================================
    FUNGSI FILTER TANGGAL - DIRECT
    ============================================

    Mengklik elemen date picker dan memilih tanggal tertentu

    Args:
        page (Page): Playwright Page object
        target_date (datetime): Tanggal yang ingin dipilih

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    print(f"📅 Memilih tanggal: {target_date.strftime('%d/%m/%Y')}...")

    try:
        # Tunggu halaman stabil
        time.sleep(1.0)

        # Cari date input/picker
        date_selectors = [
            "input[type='date']",
            "input[placeholder*='Tanggal']",
            "input[placeholder*='tanggal']",
            ".date-picker input",
            "[class*='date'] input",
        ]

        date_input = None
        for selector in date_selectors:
            try:
                input_elem = page.locator(selector).first
                if input_elem.count() > 0:
                    try:
                        input_elem.wait_for(state="visible", timeout=2000)
                        date_input = input_elem
                        break
                    except Exception:
                        continue
            except Exception:
                continue

        if not date_input:
            print("❌ Tidak menemukan date input")
            return False

        # Format tanggal sesuai kebutuhan (biasanya YYYY-MM-DD atau DD/MM/YYYY)
        date_string = target_date.strftime("%Y-%m-%d")

        # Isi date input
        date_input.click()
        time.sleep(0.5)
        date_input.fill(date_string)
        print(f"✅ Tanggal berhasil diisi: {date_string}")

        # Tunggu dan klik tombol apply/submit jika ada
        time.sleep(0.5)

        apply_selectors = [
            "button:has-text('Terapkan')",
            "button:has-text('Apply')",
            "button:has-text('Filter')",
            "button[type='submit']",
        ]

        for selector in apply_selectors:
            try:
                apply_btn = page.locator(selector).first
                if apply_btn.count() > 0:
                    try:
                        apply_btn.wait_for(state="visible", timeout=1000)
                        apply_btn.click()
                        print("✅ Tombol apply berhasil diklik")
                        time.sleep(1.5)
                        break
                    except Exception:
                        continue
            except Exception:
                continue

        return True

    except Exception as e:
        print(f"❌ Error set tanggal: {str(e)}")
        logger.error(f"Error click_date_elements_direct: {str(e)}", exc_info=True)
        return False


def click_date_elements_rekap_penjualan(page: Page, target_date) -> bool:
    """
    ============================================
    FUNGSI FILTER TANGGAL REKAP PENJUALAN
    ============================================

    Mengklik elemen date picker di halaman Rekap Penjualan dan memilih tanggal

    Args:
        page (Page): Playwright Page object di halaman Rekap Penjualan
        target_date (datetime): Tanggal yang ingin dipilih

    Returns:
        bool: True jika berhasil, False jika gagal
    """
    print(
        f"📅 Memilih tanggal di Rekap Penjualan: {target_date.strftime('%d/%m/%Y')}..."
    )

    try:
        # Sama seperti click_date_elements_direct
        # tapi dengan selector yang lebih spesifik untuk Rekap Penjualan

        time.sleep(1.0)

        # Cari date range picker (start date dan end date)
        date_range_selectors = [
            "input[placeholder*='Dari']",
            "input[placeholder*='dari']",
            "input[placeholder*='Mulai']",
            "input[placeholder*='mulai']",
            "input[name='startDate']",
            "input[name='start_date']",
        ]

        start_date_input = None
        for selector in date_range_selectors:
            try:
                input_elem = page.locator(selector).first
                if input_elem.count() > 0:
                    try:
                        input_elem.wait_for(state="visible", timeout=2000)
                        start_date_input = input_elem
                        break
                    except Exception:
                        continue
            except Exception:
                continue

        if start_date_input:
            date_string = target_date.strftime("%Y-%m-%d")
            start_date_input.click()
            time.sleep(0.5)
            start_date_input.fill(date_string)
            print(f"✅ Tanggal mulai berhasil diisi: {date_string}")

        # Cari end date jika ada
        end_date_selectors = [
            "input[placeholder*='Sampai']",
            "input[placeholder*='sampai']",
            "input[placeholder*='Hingga']",
            "input[placeholder*='hingga']",
            "input[name='endDate']",
            "input[name='end_date']",
        ]

        end_date_input = None
        for selector in end_date_selectors:
            try:
                input_elem = page.locator(selector).first
                if input_elem.count() > 0:
                    try:
                        input_elem.wait_for(state="visible", timeout=2000)
                        end_date_input = input_elem
                        break
                    except Exception:
                        continue
            except Exception:
                continue

        if end_date_input:
            date_string = target_date.strftime("%Y-%m-%d")
            end_date_input.click()
            time.sleep(0.5)
            end_date_input.fill(date_string)
            print(f"✅ Tanggal akhir berhasil diisi: {date_string}")

        # Klik tombol apply/filter
        time.sleep(0.5)

        apply_selectors = [
            "button:has-text('Terapkan')",
            "button:has-text('Apply')",
            "button:has-text('Filter')",
            "button:has-text('Cari')",
            "button[type='submit']",
        ]

        for selector in apply_selectors:
            try:
                apply_btn = page.locator(selector).first
                if apply_btn.count() > 0:
                    try:
                        apply_btn.wait_for(state="visible", timeout=1000)
                        apply_btn.click()
                        print("✅ Tombol filter berhasil diklik")
                        time.sleep(2.0)
                        break
                    except Exception:
                        continue
            except Exception:
                continue

        return True

    except Exception as e:
        print(f"❌ Error set tanggal rekap: {str(e)}")
        logger.error(
            f"Error click_date_elements_rekap_penjualan: {str(e)}", exc_info=True
        )
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
                        print(f"✅ Element '{text}' berhasil diklik")
                        time.sleep(1.0)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        return False

    except Exception as e:
        print(f"⚠️ Error find and click element: {str(e)}")
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
        print("✅ Halaman selesai loading")
        return True

    except PlaywrightTimeoutError:
        print("⏱️ Timeout menunggu halaman load")
        return False
    except Exception as e:
        print(f"⚠️ Error wait for page load: {str(e)}")
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
        print(f"✅ Scroll ke elemen berhasil")
        time.sleep(0.5)
        return True

    except Exception as e:
        print(f"⚠️ Error scroll to element: {str(e)}")
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
                        print("✅ Berhasil kembali ke halaman utama")
                        time.sleep(1.5)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        # Alternatif: gunakan browser back
        print("⚠️ Mencoba browser back...")
        page.go_back()
        time.sleep(1.5)
        return True

    except Exception as e:
        print(f"❌ Error kembali ke home: {str(e)}")
        logger.error(f"Error go_back_to_home: {str(e)}", exc_info=True)
        return False
