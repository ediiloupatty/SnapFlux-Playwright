# SnapFlux Automation (Playwright Version)

Automated web scraping and data extraction tool for SnapFlux merchant platform using **Playwright**.
This is a streamlined version of the original SnapFlux Automation, optimized for performance and reliability, specifically focusing on stock monitoring.

## 📋 Description
SnapFlux-Playwright is an automated application for the `subsiditepatlpg.mypertamina.id` merchant platform. It automates login and stock data extraction using Microsoft Playwright, offering superior speed and stability compared to legacy Selenium implementations.

## 🚀 Key Features

### Core Functionality
*   **⚡ High-Performance Automation**: Built on Playwright for faster execution and better stability.
*   **🔐 Automated Login**: Secure and reliable login process to the merchant portal.
*   **📊 Check Stock (Cek Stok)**:
    *   Real-time retrieval of stock data from the dashboard.
    *   Accurate sales tracking.
    *   Automatic status detection (e.g., Sales Available vs. No Sales).
*   **📈 Excel Export**: Automatically exports results to Excel format for easy reporting.
*   **🖥️ Modern GUI**: User-friendly interface built with Eel (HTML/JS).

> **Note**: This version is strictly focused on **Stock Monitoring**. Features such as "Cancel Input" and "Catat Penjualan" from the Selenium v2.0 version are **not included** in this build.

## 🛠️ Technical Stack
*   **Language**: Python 3.8+
*   **Automation Engine**: Playwright
*   **Data Processing**: Pandas, OpenPyxl
*   **Interface**: Eel (HTML/JS/CSS)
*   **Platform**: Windows

## 🚀 Quick Start

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/ediiloupatty/SnapFlux-Playwright.git
cd SnapFlux-Playwright
pip install -r requirements.txt
```

Install Playwright browsers:
```bash
playwright install chromium
```

### 2. Configuration
1.  **Account Setup**: 
    *   Prepare your `akun/akun.xlsx` file.
    *   Ensure it contains the necessary columns: `Username`, `PIN`, etc.
2.  **Environment**: 
    *   Configure any necessary environment variables if required (though the GUI handles most settings).

### 3. Running the Application
To start the GUI version (Recommended):
```bash
python main_gui.py
```
*Or use the `START_GUI.bat` file if available.*

To run the CLI version:
```bash
python main.py
```

## 📂 Project Structure
```
SnapFlux-Playwright/
├── akun/               # Account data and templates
├── modules/            # Core logic (Browser, Network, etc.)
├── web/                # GUI Assets (HTML, CSS, JS)
├── results/            # Exported Excel files
├── logs/               # Application logs
├── main_gui.py         # GUI Entry point
└── main.py             # CLI Entry point
```

## ⚠️ Disclaimer
This tool is for educational and legitimate business purposes only. Users are responsible for complying with the terms of service of the target platform and applicable laws.
