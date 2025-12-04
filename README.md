# SnapFlux Automation (Playwright Version)

Automated web scraping and data extraction tool for SnapFlux merchant platform using **Playwright**.
This is a streamlined version of the original SnapFlux Automation, optimized for performance and reliability, specifically focusing on stock monitoring.

## 📋 Description
SnapFlux-Playwright is an automated application for the `subsiditepatlpg.mypertamina.id` merchant platform. It automates login and stock data extraction using Microsoft Playwright, offering superior speed and stability compared to legacy Selenium implementations.

**✨ Multi-Company Support**: The system now includes multi-tenant architecture with company-based data isolation. Each company (e.g., PT Moy Veronika, PT Lorito) has their own accounts and results, ensuring complete data separation and security.

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
*   **🏢 Multi-Company System**: Company-based data isolation with role-based access control.
*   **☁️ Cloud Database**: Supabase integration for real-time data sync and monitoring.
*   **📊 Monitoring Dashboard**: View historical automation results with filtering capabilities.

> **Note**: This version is strictly focused on **Stock Monitoring**. Features such as "Cancel Input" and "Catat Penjualan" from the Selenium v2.0 version are **not included** in this build.

## 🛠️ Technical Stack
*   **Language**: Python 3.8+
*   **Automation Engine**: Playwright
*   **Data Processing**: Pandas, OpenPyxl
*   **Database**: Supabase (PostgreSQL)
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
├── akun/               # Account data and templates (legacy)
├── modules/            # Core logic (Browser, Network, etc.)
│   ├── browser/        # Playwright automation
│   ├── core/           # Business logic & utilities
│   ├── data/           # Database & Excel processing
│   └── auth/           # Authentication modules
├── web/                # GUI Assets (HTML, CSS, JS)
├── results/            # Exported Excel files
├── logs/               # Application logs
├── main_gui.py         # GUI Entry point
└── main.py             # CLI Entry point
```

## 🏢 Multi-Company System

### Database Schema
The system uses Supabase with the following key tables:
- **companies**: Company master data (PT Moy Veronika, PT Lorito, etc.)
- **users**: User accounts with company association and role-based access
- **accounts**: Merchant accounts (pangkalan) assigned to specific companies
- **automation_results**: Automation results linked to accounts

### Company Isolation
- **Login**: Users are authenticated and associated with a specific company
- **Accounts**: Only accounts belonging to the user's company are displayed
- **Results**: Automation results are filtered by company_id
- **Dashboard**: All metrics and statistics are company-specific
- **Monitoring**: Historical data shows only company-related records

### Usage
1. **Login**: Use your company credentials (username/password)
2. **Load Accounts**: Click "Muat dari Database" - only your company's accounts will load
3. **Run Automation**: Process automation for your company's accounts
4. **View Results**: All results are automatically filtered by your company
5. **Monitoring**: View historical data in the "Monitoring" tab with date filtering

## 🔐 Security Features
- Password hashing (SHA256) for user authentication
- Company-based data isolation at database level
- Role-based access control (admin, operator)
- Secure Supabase connection with API keys
- Session management with localStorage

## 📊 Monitoring Features
- **Real-time Dashboard**: Live statistics for today's automation runs
- **Historical Data**: View past automation results with date filtering
- **Stock Movement**: Track yesterday's sales including unreported transactions
- **Success Rate**: Monitor automation performance and error tracking
- **Company-Specific**: All data filtered by user's company

## ⚠️ Disclaimer
This tool is for educational and legitimate business purposes only. Users are responsible for complying with the terms of service of the target platform and applicable laws.
