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
        # Tunggu halaman dashboard stabil (network idle)
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass
            
        time.sleep(3.0) # Tambahan sleep untuk memastikan rendering selesai

        import re

        # Debug: Print page title and url
        print(f"   URL: {page.url}")
        print(f"   Title: {page.title()}")

        # Strategi 1: Cari heading "Stok" diikuti angka dan "Tabung" di dashboard
        try:
            # Cari elemen yang mengandung text "Stok" (case insensitive)
            stok_elements = page.locator("text=/Stok/i").all()

            for stok_elem in stok_elements:
                try:
                    # Cek text elemen itu sendiri
                    elem_text = stok_elem.text_content()
                    
                    # Jika elemen hanya berisi "Stok", cek parent/sibling
                    # Ambil parent container (coba naik 2 level)
                    parent = stok_elem.locator("..")
                    parent_text = parent.text_content()
                    grandparent = parent.locator("..") 
                    grandparent_text = grandparent.text_content()

                    # Gabungkan text untuk pencarian
                    search_text = f"{elem_text} {parent_text} {grandparent_text}"

                    # Cari pattern angka diikuti "Tabung"
                    # Handle newlines dan spasi berlebih
                    match = re.search(
                        r"Stok.*?(\d+)\s*Tabung", search_text, re.IGNORECASE | re.DOTALL
                    )
                    if match:
                        stock_value = match.group(1)
                        print(
                            f"✓ Stok berhasil diambil dari dashboard (Strategy 1): {stock_value} tabung"
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
            # Ditambahkan variasi pattern
            patterns = [
                r"Stok\s*\n?\s*(\d+)\s*Tabung",
                r"Stok[:\s]*(\d+)\s*Tabung",
                r"Sisa Kuota.*?(\d+)\s*Tabung", # Antisipasi istilah lain
                r"Tersedia.*?(\d+)\s*Tabung",
            ]

            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    stock_value = match.group(1)
                    print(f"✓ Stok berhasil diambil dari pattern (Strategy 2): {stock_value} tabung")
                    return stock_value
        except Exception as e:
            logger.debug(f"Strategi 2 gagal: {e}")

        # Strategi 3: Cari semua elemen dengan "Tabung" dan filter yang relevan dengan stok
        try:
            tabung_elements = page.locator("text=/Tabung/i").all()

            for elem in tabung_elements:
                try:
                    # Ambil konteks sekitar elemen
                    parent = elem.locator("..")
                    parent_text = parent.text_content()
                    
                    # Bersihkan text
                    clean_text = " ".join(parent_text.split()).lower()

                    # Pastikan ini adalah data stok (bukan harga atau yang lain)
                    if "stok" in clean_text and "harga" not in clean_text:
                        match = re.search(r"(\d+)", parent_text)
                        if match:
                            stock_value = match.group(1)
                            print(f"✓ Stok berhasil diambil (Strategy 3): {stock_value} tabung")
                            return stock_value
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"Strategi 3 gagal: {e}")

        print("✗ Gagal mengambil data stok dari dashboard")
        
        # Debugging info: Print snippet body text untuk analisis
        try:
            body_text = page.text_content("body")
            clean_body = " ".join(body_text.split())[:500] # Ambil 500 karakter pertama yang sudah dibersihkan
            print(f"   [DEBUG] Page Content Snippet: {clean_body}...")
        except:
            pass
            
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

def get_customer_list_from_cards(page: Page) -> List[Dict]:
    """
    Mengambil daftar customer (Simplified).
    Hanya scroll sekali ke bawah lalu ambil customer menggunakan selector 'div.mantine-hpmcve'
    """
    print("Mengekstrak daftar customer (Simple Scroll)...")
    customers = []
    
    try:
        # 1. Simple Scroll to Bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3.0) # Tunggu load
        
        # 2. Ambil data dengan selector wrapper spesifik
        # div.mantine-Paper-root ternyata membungkus banyak item
        # div.mantine-hpmcve adalah wrapper per item (Nama + Button)
        
        cards = page.locator("div.mantine-hpmcve").all()
        
        # Jika selector aneh itu tidak ketemu, coba fallback ke yang mengandung text ciri khas
        if not cards:
             print("Selector .mantine-hpmcve tidak ketemu, mencoba fallback...")
             # Cari elemen yang memiliki text 'Jenis Pelanggan' tapi bukan container besar
             # Agak tricky, kita stick ke hpmcve dulu sesuai request user sebelumnya
        
        print(f"Total kartu customer ditemukan: {len(cards)}")
        
        for idx, card in enumerate(cards):
            try:
                text = card.text_content()
                if not text: continue
                
                # Parsing Nama
                # Struktur text biasanya: "RICHARD F LANTU710xxxxxxxxxx0011 Jenis Pelanggan..."
                # Kita coba split berdasarkan NIK (16 digit)
                
                import re
                
                nama = "Unknown"
                nik = ""
                
                # Cari NIK
                nik_match = re.search(r"\b\d{16}\b", text)
                if nik_match:
                    nik = nik_match.group(0)
                    # Nama biasanya ada sebelum NIK
                    # Ambil text sebelum NIK
                    pre_nik = text.split(nik)[0].strip()
                    # Bersihkan jika ada newline
                    lines = [l.strip() for l in pre_nik.split('\n') if l.strip()]
                    if lines:
                        nama = lines[-1] # Ambil yang paling bawah dari blok atas (paling dekat NIK)
                else:
                    # Fallback simple
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    if lines: nama = lines[0]
                
                customers.append({"no": idx+1, "nama": nama, "nik": nik})
            except: 
                continue
                
        if customers:
            first = customers[0]
            last = customers[-1]
            print(f"Customer Pertama : {first['nama']} ({first['nik']})")
            print(f"Customer Terakhir: {last['nama']} ({last['nik']})")
            
        return customers

    except Exception as e:
        print(f"Error list extraction: {e}")
        return []


def click_last_customer_card(page: Page) -> bool:
    """
    Scroll ke paling bawah dan klik customer terakhir.
    Target: div.mantine-hpmcve (Wrapper nama & NIK)
    """
    print("Mencari customer paling bawah untuk diklik (Target: .mantine-hpmcve)...")
    try:
        # 1. Scroll Paling Bawah
        print("Scrolling ke bawah page...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2.0)
        
        # 2. Cari elemen spesifik (mantine-hpmcve)
        # Ini adalah wrapper yang berisi Nama dan NIK
        targets = page.locator("div.mantine-hpmcve").all()
        
        if not targets:
            print("⚠ Tidak ditemukan elemen 'div.mantine-hpmcve'. Mencoba mencari kartu biasa...")
            # Fallback ke paper root jika selector spesifik ini gagal (misal class berubah)
            cards = page.locator("div.mantine-Paper-root").all()
            if cards:
                last_card = cards[-1]
                last_card.scroll_into_view_if_needed()
                last_card.click(force=True)
                print("✓ Fallback Clicked last Paper-root")
                return True
            return False
            
        # Ambil yang terakhir
        last_target = targets[-1]
        
        # Logging text untuk konfirmasi
        print(f"Target klik ditemukan (Text: {last_target.text_content()})")
        
        # Scroll & Click
        last_target.scroll_into_view_if_needed()
        time.sleep(1.0)
        
        # Klik langsung pada wrapper tersebut
        print("Mengklik elemen .mantine-hpmcve terakhir...")
        last_target.click(force=True)
        time.sleep(2.0)
        
        print("✓ Berhasil klik customer terakhir!")
        return True
        
    except Exception as e:
        print(f"Error clicking last customer: {e}")
        return False

def click_first_customer_card(page: Page) -> bool:
    """
    Klik customer pertama di list.
    Target: div.mantine-hpmcve pertama.
    """
    print("Mencari customer PERTAMA untuk diklik...")
    try:
        # Import re for validation if needed
        import re

        # 1. Pastikan di top page
        # page.evaluate("window.scrollTo(0, 0)")
        # time.sleep(1.0)
        
        # 2. Cari elemen spesifik (mantine-hpmcve)
        targets = page.locator("div.mantine-hpmcve").all()
        
        first_target = None
        
        if targets:
            for t in targets:
                txt = t.text_content() or ""
                # Skip elemen sorting header
                if "Mengurutkan" in txt or "Filter" in txt:
                    continue
                
                # Validasi: Pastikan ada NIK (16 digit) agar yakin ini customer
                if re.search(r"\d{16}", txt):
                    first_target = t
                    break
            
            # Fallback: Jika tidak ada yang match NIK, ambil elemen kedua (index 1) 
            # karena index 0 biasanya sort button
            if not first_target and len(targets) > 1:
                first_target = targets[1]
                print("⚠ Mengambil target index 1 sebagai fallback (index 0 dianggap sort)")
        
        if not first_target:
            # Fallback ke paper root
            cards = page.locator("div.mantine-Paper-root").all()
            if cards:
                cards[0].scroll_into_view_if_needed()
                cards[0].click(force=True)
                print("✓ Fallback Clicked first Paper-root")
                return True
            return False
            
        print(f"Target klik ditemukan (Text: {first_target.text_content()})")
        
        first_target.scroll_into_view_if_needed()
        time.sleep(0.5)
        first_target.click(force=True)
        time.sleep(2.0)
        
        print("✓ Berhasil klik customer PERTAMA!")
        return True
        
    except Exception as e:
        print(f"Error clicking first customer: {e}")
        return False

def get_transaction_timestamp(page: Page) -> str:
    """
    Mengambil timestamp detail transaksi dari halaman detail customer.
    User Selector: <div class="mantine-Text-root mantine-1ic1mzf">30 Jan 2026 · 06:17</div>
    """
    print("Mengekstrak timestamp transaksi...")
    try:
        page.wait_for_selector("div.mantine-Text-root", timeout=5000)
        
        # Cari elemen yang text-nya mengandung format tanggal
        # Format: "DD Mon YYYY · HH:MM"
        
        # Cara 1: Selector spesifik user (tapi class hash mungkin ganti)
        # .mantine-1ic1mzf
        
        # Cara 2: Regex search di semua text element (Lebih robust)
        import re
        timestamp_pattern = r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\s*·\s*\d{2}:\d{2}"
        
        elements = page.locator("div.mantine-Text-root").all()
        for el in elements:
            if not el.is_visible(): continue
            text = el.text_content()
            if text and re.search(timestamp_pattern, text):
                clean_time = re.search(timestamp_pattern, text).group(0)
                print(f"✓ Timestamp ditemukan: {clean_time}")
                return clean_time
                
        print("Timestamp tidak ditemukan dengan regex, mencoba ambil semua text...")
        return "Not Found"
        
    except Exception as e:
        print(f"Error getting timestamp: {e}")
        return "Error"
