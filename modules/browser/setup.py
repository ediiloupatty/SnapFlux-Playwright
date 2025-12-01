"""
Setup dan konfigurasi browser Playwright untuk automation
File ini mengatur Playwright Browser dengan optimasi performa maksimal
"""

import logging
import os
import sys

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

# Setup logging untuk tracking error
logger = logging.getLogger("browser_setup")

# Import config module
try:
    from modules.core.config import (
        CHROME_BINARY_PATH,
        DEFAULT_TIMEOUT,
        NAVIGATION_TIMEOUT,
        is_headless_mode,
    )
    from modules.core.config import (
        get_chrome_binary as get_chrome_from_config,
    )
except ImportError:
    # Fallback jika config tidak tersedia
    CHROME_BINARY_PATH = None
    DEFAULT_TIMEOUT = 20000
    NAVIGATION_TIMEOUT = 20000

    def get_chrome_from_config():
        return None

    def is_headless_mode():
        return True


# Konfigurasi path Chrome binary (fallback)
CHROME_BINARY = r"D:\edi\Programing\PlayWRight\chrome\Chromium\bin\chrome.exe"


# Docker environment detection
def is_docker_environment():
    """
    Deteksi apakah aplikasi berjalan di Docker container

    Returns:
        bool: True jika berjalan di Docker, False jika tidak
    """
    docker_indicators = []

    # Cek file .dockerenv (paling reliable)
    if os.path.exists("/.dockerenv"):
        docker_indicators.append(True)

    # Cek environment variable
    if os.environ.get("DOCKER_CONTAINER") == "true":
        docker_indicators.append(True)

    # Cek cgroup (jika ada)
    try:
        if os.path.exists("/proc/1/cgroup"):
            with open("/proc/1/cgroup", "r") as f:
                cgroup_content = f.read()
                if "docker" in cgroup_content or "containerd" in cgroup_content:
                    docker_indicators.append(True)
    except (IOError, PermissionError):
        pass

    return any(docker_indicators)


def get_chrome_binary():
    """
    Get Chrome binary path with priority:
    1. Environment Variable
    2. Config Module
    3. Docker Default
    4. Hardcoded Fallback
    """
    # 1. Environment Variable
    env_chrome = os.environ.get("CHROME_BINARY_PATH")
    if env_chrome and os.path.exists(env_chrome):
        return env_chrome

    # 2. Config Module
    chrome_from_config = get_chrome_from_config()
    if chrome_from_config and os.path.exists(chrome_from_config):
        return chrome_from_config

    # 3. Docker Default
    if is_docker_environment():
        docker_chrome = "/usr/bin/google-chrome"
        if os.path.exists(docker_chrome):
            return docker_chrome
            
    # 4. Hardcoded Fallback
    return CHROME_BINARY


class PlaywrightBrowserManager:
    """
    Manager class untuk mengelola Playwright browser instance
    """

    def __init__(self):
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    def _handle_route(self, route):
        """
        Handler untuk memblokir resource berat agar loading cepat
        """
        try:
            # Block images, fonts, and media
            if route.request.resource_type in ["image", "media", "font"]:
                route.abort()
            else:
                route.continue_()
        except Exception:
            # Jika terjadi error (misal page sudah closed), abaikan
            pass

    def setup_browser(self, headless=None, username=None, use_session=False):
        """
        Setup Playwright Browser dengan konfigurasi optimal untuk performa maksimal

        Args:
            headless (bool): Jika True, browser akan berjalan tanpa GUI untuk performa lebih cepat
                           Jika None, akan menggunakan config default
            username (str): Tidak digunakan lagi (legacy parameter)
            use_session (bool): Tidak digunakan lagi (legacy parameter)

        Returns:
            Page: Object Page Playwright yang sudah dikonfigurasi

        Raises:
            Exception: Jika terjadi error saat setup browser
        """
        # Determine headless mode
        if headless is None:
            headless = is_headless_mode()

        print("Setting up Playwright Browser dengan optimasi performa...")
        print(
            f"   Mode: {'Headless (tidak terlihat)' if headless else 'GUI Visible (terlihat)'}"
        )

        # Informasi environment
        if is_docker_environment():
            print("Detected: Running in Docker container")
        else:
            print("Detected: Running in local environment")

        try:
            # Inisialisasi Playwright
            self.playwright = sync_playwright().start()

            # Argumen untuk browser optimasi performa
            browser_args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-ipc-flooding-protection",
                "--disable-blink-features=AutomationControlled",
                "--disable-background-networking",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-translate",
                "--hide-scrollbars",
                "--mute-audio",
                "--disable-java",
                "--disable-flash",
                "--aggressive-cache-discard",
                "--disable-gpu-sandbox",
                "--disable-software-rasterizer",
                "--disable-gpu-process-crash-limit",
                "--disable-gpu-memory-buffer-video-frames",
                "--disable-gpu-rasterization",
                "--disable-zero-copy",
                "--disable-accelerated-2d-canvas",
                "--disable-accelerated-jpeg-decoding",
                "--disable-accelerated-mjpeg-decode",
                "--disable-accelerated-video-decode",
                "--disable-webgl",
                "--disable-webgl2",
                "--disable-3d-apis",
                "--disable-client-side-phishing-detection",
                "--disable-component-extensions-with-background-pages",
                "--disable-domain-reliability",
                "--disable-features=TranslateUI",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                "--disable-web-resources",
                "--disable-logging",
                "--disable-permissions-api",
                "--memory-pressure-off",
                "--max_old_space_size=1024",
                "--window-size=1366,768",
            ]

            # Tentukan executable path
            chrome_binary_path = get_chrome_binary()
            executable_path = None

            if os.path.exists(chrome_binary_path):
                executable_path = chrome_binary_path
                print(f"✓ Menggunakan Chrome binary: {chrome_binary_path}")
            else:
                print("⚠ Chrome binary tidak ditemukan, menggunakan default Chromium")

            # Launch browser dengan Chromium
            if executable_path:
                self.browser = self.playwright.chromium.launch(
                    headless=headless,
                    args=browser_args,
                    executable_path=executable_path,
                    timeout=30000,  # 30 detik timeout
                )
            else:
                self.browser = self.playwright.chromium.launch(
                    headless=headless, args=browser_args, timeout=30000
                )

            # Buat browser context dengan konfigurasi (Fresh context)
            self.context = self.browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True,
                permissions=[],
            )

            # Set default timeouts (dari config)
            self.context.set_default_timeout(DEFAULT_TIMEOUT)
            self.context.set_default_navigation_timeout(NAVIGATION_TIMEOUT)

            # Buat page baru
            self.page = self.context.new_page()

            # OPTIMIZATION: Block heavy resources (Images, Fonts, Media)
            # DISABLED TEMPORARILY: Menyebabkan gagal login (terdeteksi bot/missing assets)
            # self.page.route("**/*", lambda route: self._handle_route(route))

            # Inject script untuk hide automation
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Override the permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );

                // Chrome runtime
                window.chrome = {
                    runtime: {}
                };

                // Plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // Languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en', 'id-ID']
                });
            """)

            print(
                "✓ Playwright Browser berhasil di-setup dengan optimasi performa maksimal!"
            )
            print("JavaScript enabled untuk interaksi optimal dengan halaman web")

            return self.page

        except Exception as e:
            print(f"✗ Error setup Playwright Browser: {str(e)}")
            logger.error(f"Error setup browser: {str(e)}", exc_info=True)
            self.close()
            return None

    def close(self):
        """
        Menutup browser, context, dan playwright instance
        """
        try:
            if self.page:
                self.page.close()
                self.page = None

            if self.context:
                self.context.close()
                self.context = None

            if self.browser:
                self.browser.close()
                self.browser = None

            if self.playwright:
                self.playwright.stop()
                self.playwright = None

            print("✓ Browser berhasil ditutup")

        except Exception as e:
            print(f"⚠ Warning saat menutup browser: {str(e)}")
            logger.warning(f"Warning saat menutup browser: {str(e)}")


def setup_browser(headless=False):
    """
    Fungsi helper untuk setup browser Playwright dengan mudah
    (Kompatibel dengan interface Selenium setup_driver)

    Args:
        headless (bool): Jika True, browser akan berjalan tanpa GUI

    Returns:
        tuple: (PlaywrightBrowserManager, Page) - Manager dan Page object
    """
    manager = PlaywrightBrowserManager()
    page = manager.setup_browser(headless=headless)

    if page is None:
        return None, None

    return manager, page
