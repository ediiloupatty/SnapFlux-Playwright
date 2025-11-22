"""
Data extraction functions untuk mengambil data dari halaman merchant
File ini menangani proses ekstraksi data menggunakan Playwright
"""

import logging
import time
from typing import Dict, List, Optional, Tuple

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Import constants dari local module
try:
    from modules.core.constants import DEFAULT_DELAY
except ImportError:
    try:
        from modules.core.constants import DEFAULT_DELAY
    except ImportError:
        DEFAULT_DELAY = 2.0

logger = logging.getLogger("automation")


def get_stock_value_direct(page: Page) -> Optional[str]:
    """
    ============================================
    FUNGSI GET STOCK VALUE - DIRECT METHOD
    ============================================

    Mengambil nilai stok tabung dari dashboard utama setelah login
    (Bukan dari halaman Atur Produk)

    Args:
        page (Page): Playwright Page object yang sudah di dashboard utama

    Returns:
        str: Nilai stok dalam format string (contoh: "89")
        None: Jika gagal mengambil data
    """
    print("Mengambil data stok dari dashboard utama...")

    try:
        # Tunggu halaman dashboard stabil
        time.sleep(2.0)

        import re

        # Strategi 1: Cari heading "Stok" diikuti angka dan "Tabung" di dashboard
        try:
            # Cari elemen yang tepat mengandung text "Stok"
            stok_elements = page.locator("text=/^Stok$/i").all()

            for stok_elem in stok_elements:
                try:
                    # Ambil parent container
                    parent = stok_elem.locator("..")
                    text_content = parent.text_content()

                    # Cari pattern angka diikuti "Tabung"
                    match = re.search(
                        r"Stok[^\d]*(\d+)\s*Tabung", text_content, re.IGNORECASE
                    )
                    if match:
                        stock_value = match.group(1)
                        print(
                            f"✓ Stok berhasil diambil dari dashboard: {stock_value} tabung"
                        )
                        return stock_value
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"Strategi 1 gagal: {e}")

        # Strategi 2: Cari di seluruh halaman dengan pattern spesifik dashboard
        try:
            page_text = page.text_content("body")

            # Pattern untuk dashboard: "Stok\n89 Tabung" atau "Stok 89 Tabung"
            patterns = [
                r"Stok\s*\n?\s*(\d+)\s*Tabung",
                r"Stok[:\s]*(\d+)\s*Tabung",
            ]

            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    stock_value = match.group(1)
                    print(f"✓ Stok berhasil diambil dari pattern: {stock_value} tabung")
                    return stock_value
        except Exception as e:
            logger.debug(f"Strategi 2 gagal: {e}")

        # Strategi 3: Cari semua elemen dengan "Tabung" dan filter yang relevan dengan stok
        try:
            tabung_elements = page.locator("text=/\\d+\\s*Tabung/i").all()

            for elem in tabung_elements:
                try:
                    # Ambil konteks sekitar elemen
                    parent = elem.locator("..")
                    parent_text = parent.text_content()

                    # Pastikan ini adalah data stok (bukan harga atau yang lain)
                    if (
                        "stok" in parent_text.lower()
                        and "harga" not in parent_text.lower()
                    ):
                        elem_text = elem.text_content()
                        match = re.search(r"(\d+)", elem_text)
                        if match:
                            stock_value = match.group(1)
                            print(f"✓ Stok berhasil diambil: {stock_value} tabung")
                            return stock_value
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"Strategi 3 gagal: {e}")

        print("✗ Gagal mengambil data stok dari dashboard")
        return None

    except Exception as e:
        print(f"✗ Error mengambil stok: {str(e)}")
        logger.error(f"Error get_stock_value_direct: {str(e)}", exc_info=True)
        return None


def get_tabung_terjual_direct(page: Page) -> Optional[int]:
    """
    ============================================
    FUNGSI GET TABUNG TERJUAL - DIRECT METHOD
    ============================================

    Mengambil jumlah tabung terjual dari halaman Laporan Penjualan
    (Langsung dari Data Penjualan, bukan Rekap Penjualan)

    Args:
        page (Page): Playwright Page object yang sudah berada di halaman Laporan Penjualan

    Returns:
        int: Jumlah tabung terjual
        None: Jika gagal mengambil data
    """
    print("Mengambil data tabung terjual dari Laporan Penjualan...")

    # Retry mechanism
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f"   Percobaan ekstraksi ke-{attempt + 1}...")

            # Tunggu halaman stabil
            time.sleep(2.0)

            import re

            # Strategi 1: Cari heading "Total Tabung LPG 3 Kg Terjual"
            # diikuti angka dan "Tabung" di Data Penjualan
            try:
                # Cari text yang tepat
                heading = page.locator("text=/Total Tabung LPG 3 Kg Terjual/i").first
                if heading.count() > 0:
                    try:
                        heading.wait_for(state="visible", timeout=3000)
                        # Ambil parent container yang lebih besar
                        parent = heading.locator("..").locator("..")
                        text_content = parent.text_content()

                        # Cari angka diikuti "Tabung" setelah heading
                        # Pattern: "Total Tabung LPG 3 Kg Terjual\n12 Tabung"
                        match = re.search(
                            r"Total Tabung LPG 3 Kg Terjual[^\d]*(\d+)\s*Tabung",
                            text_content,
                            re.IGNORECASE | re.DOTALL,
                        )
                        if match:
                            tabung_terjual = int(match.group(1))
                            print(
                                f"✓ Tabung terjual berhasil diambil: {tabung_terjual} tabung"
                            )
                            return tabung_terjual
                    except Exception:
                        pass
            except Exception as e:
                logger.debug(f"Strategi 1 gagal: {e}")

            # Strategi 2: Cari di seluruh halaman dengan pattern spesifik
            try:
                page_text = page.text_content("body")

                # Pattern untuk Data Penjualan
                patterns = [
                    r"Total Tabung LPG 3 Kg Terjual\s*\n?\s*(\d+)\s*Tabung",
                    r"Total Tabung LPG 3 Kg Terjual[^\d]*(\d+)\s*Tabung",
                ]

                for pattern in patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                    if match:
                        tabung_terjual = int(match.group(1))
                        print(
                            f"✓ Tabung terjual berhasil diambil: {tabung_terjual} tabung"
                        )
                        return tabung_terjual
            except Exception as e:
                logger.debug(f"Strategi 2 gagal: {e}")

            # Strategi 3: Cari section "Data Penjualan" lalu ambil angka tabung
            try:
                # Cari heading "Data Penjualan"
                data_penjualan = page.locator("text=/Data Penjualan/i").first
                if data_penjualan.count() > 0:
                    try:
                        data_penjualan.wait_for(state="visible", timeout=2000)
                        # Ambil parent section
                        section = data_penjualan.locator("..").locator("..")
                        section_text = section.text_content()

                        # Cari "Total Tabung" dalam section ini
                        match = re.search(
                            r"Total Tabung[^\d]*(\d+)\s*Tabung",
                            section_text,
                            re.IGNORECASE,
                        )
                        if match:
                            tabung_terjual = int(match.group(1))

                            return tabung_terjual
                    except Exception:
                        pass
            except Exception as e:
                logger.debug(f"Strategi 3 gagal: {e}")

            # Strategi 4: Cari elemen yang mengandung "XX Tabung" di context Data Penjualan
            try:
                # Cari semua elemen dengan pattern "XX Tabung"
                tabung_elements = page.locator(r"text=/\d+\s*Tabung/i").all()

                for elem in tabung_elements:
                    try:
                        # Ambil konteks lebih besar
                        parent = elem.locator("..").locator("..")
                        parent_text = parent.text_content()

                        # Pastikan ini adalah Total Tabung Terjual
                        if (
                            "total tabung" in parent_text.lower()
                            and "terjual" in parent_text.lower()
                        ):
                            elem_text = elem.text_content()
                            match = re.search(
                                r"(\d+)\s*Tabung", elem_text, re.IGNORECASE
                            )
                            if match:
                                tabung_terjual = int(match.group(1))
                                print(
                                    f"✓ Tabung terjual berhasil diambil dari elemen: {tabung_terjual} tabung"
                                )
                                return tabung_terjual
                    except Exception:
                        continue
            except Exception as e:
                logger.debug(f"Strategi 4 gagal: {e}")

            print("⚠ Belum berhasil mengambil data, mencoba lagi...")
        except Exception as e:
            print(f"⚠ Error dalam loop ekstraksi: {str(e)}")

    print("✗ Gagal mengambil data tabung terjual setelah semua percobaan")
    return None


def get_customer_list_direct(page: Page, min_tabung: int = 2) -> List[Dict]:
    """
    ============================================
    FUNGSI GET CUSTOMER LIST - DIRECT METHOD
    ============================================

    Mengambil daftar customer dari halaman Rekap Penjualan
    yang membeli >= min_tabung tabung

    Args:
        page (Page): Playwright Page object yang sudah berada di halaman Rekap Penjualan
        min_tabung (int): Minimum jumlah tabung untuk filter (default: 2)

    Returns:
        List[Dict]: List of customer data dengan format:
                   [{'nama': str, 'tabung': int, 'nik': str}, ...]
        []: List kosong jika tidak ada data atau error
    """
    print(f"👥 Mengambil daftar customer dengan >= {min_tabung} tabung...")

    try:
        customers = []

        # Tunggu tabel muncul
        time.sleep(2.0)

        # Coba berbagai selector untuk tabel customer
        table_selectors = [
            "table tbody tr",
            ".mantine-Table-root tbody tr",
            "[class*='table'] tbody tr",
            "div[role='table'] div[role='row']",
        ]

        for selector in table_selectors:
            try:
                rows = page.locator(selector).all()

                if len(rows) == 0:
                    continue

                print(f"Ditemukan {len(rows)} baris data")

                for row in rows:
                    try:
                        # Ambil semua cells dalam row
                        cells = row.locator("td, div[role='cell']").all()

                        if len(cells) < 2:
                            continue

                        # Extract data dari cells
                        # Biasanya format: [Nama, NIK, Jumlah Tabung, ...]
                        row_text = row.text_content()

                        # Extract jumlah tabung (cari angka)
                        import re

                        numbers = re.findall(r"\b(\d+)\b", row_text)

                        if not numbers:
                            continue

                        # Coba identifikasi jumlah tabung (biasanya angka kecil 1-10)
                        tabung_count = None
                        for num_str in numbers:
                            num = int(num_str)
                            if 1 <= num <= 20:  # Range reasonable untuk jumlah tabung
                                tabung_count = num
                                break

                        if not tabung_count or tabung_count < min_tabung:
                            continue

                        # Extract nama (biasanya cell pertama atau kedua)
                        nama = cells[0].text_content().strip() if len(cells) > 0 else ""

                        # Extract NIK (biasanya angka panjang 16 digit)
                        nik = ""
                        for num_str in re.findall(r"\b(\d{16})\b", row_text):
                            nik = num_str
                            break

                        if nama:
                            customer_data = {
                                "nama": nama,
                                "tabung": tabung_count,
                                "nik": nik,
                            }
                            customers.append(customer_data)
                            print(
                                f"  ✓ {nama} - {tabung_count} tabung - NIK: {nik or 'N/A'}"
                            )

                    except Exception as e:
                        continue

                if customers:
                    break  # Jika sudah dapat data, stop

            except Exception:
                continue

        if customers:
            print(
                f"✓ Berhasil mengambil {len(customers)} customer dengan >= {min_tabung} tabung"
            )
        else:
            print("⚠ Tidak ada customer yang memenuhi kriteria")

        return customers

    except Exception as e:
        print(f"✗ Error mengambil customer list: {str(e)}")
        logger.error(f"Error get_customer_list_direct: {str(e)}", exc_info=True)
        return []


def extract_transaction_data(page: Page) -> Dict:
    """
    Extract data transaksi dari halaman detail transaksi

    Args:
        page (Page): Playwright Page object pada halaman detail transaksi

    Returns:
        Dict: Data transaksi dengan keys: tanggal, nama, nik, jumlah_tabung, total_harga
    """
    print("Mengekstrak data transaksi...")

    try:
        transaction_data = {
            "tanggal": "",
            "nama": "",
            "nik": "",
            "jumlah_tabung": 0,
            "total_harga": "",
        }

        # Tunggu halaman stabil
        time.sleep(1.0)

        # Extract dengan mencari label-value pairs
        page_text = page.text_content("body")

        import re

        # Extract NIK (16 digit)
        nik_match = re.search(r"\b(\d{16})\b", page_text)
        if nik_match:
            transaction_data["nik"] = nik_match.group(1)

        # Extract jumlah tabung
        tabung_patterns = [
            r"(\d+)\s*tabung",
            r"jumlah[:\s]+(\d+)",
        ]
        for pattern in tabung_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                transaction_data["jumlah_tabung"] = int(match.group(1))
                break

        # Extract tanggal (format DD/MM/YYYY atau DD-MM-YYYY)
        date_match = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b", page_text)
        if date_match:
            transaction_data["tanggal"] = date_match.group(1)

        # Extract total harga
        price_patterns = [
            r"Rp\s*([\d.,]+)",
            r"total[:\s]+Rp\s*([\d.,]+)",
        ]
        for pattern in price_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                transaction_data["total_harga"] = match.group(1)
                break

        print(f"✓ Data transaksi berhasil diekstrak")
        return transaction_data

    except Exception as e:
        print(f"⚠ Error ekstrak data transaksi: {str(e)}")
        logger.error(f"Error extract_transaction_data: {str(e)}", exc_info=True)
        return {}


def wait_for_data_load(page: Page, timeout: int = 10000) -> bool:
    """
    Menunggu hingga data selesai dimuat di halaman

    Args:
        page (Page): Playwright Page object
        timeout (int): Timeout dalam milliseconds

    Returns:
        bool: True jika data berhasil dimuat, False jika timeout
    """
    try:
        # Tunggu loading spinner hilang
        loading_selectors = [
            ".loading",
            ".spinner",
            "[class*='loading']",
            "[class*='spinner']",
        ]

        for selector in loading_selectors:
            try:
                loading = page.locator(selector).first
                if loading.is_visible(timeout=1000):
                    loading.wait_for(state="hidden", timeout=timeout)
                    print("✓ Loading selesai")
                    return True
            except Exception:
                continue

        # Tunggu content muncul
        time.sleep(1.0)
        return True

    except PlaywrightTimeoutError:
        print("Timeout menunggu data load")
        return False
    except Exception as e:
        print(f"⚠ Error menunggu data load: {str(e)}")
        return False
