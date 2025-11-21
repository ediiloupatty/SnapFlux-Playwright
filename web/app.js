// ============================================
// SNAPFLUX AUTOMATION - FRONTEND LOGIC
// ============================================

// Global variables
let accounts = [];
let allSelected = false;
let automationRunning = false;
let headlessEnabled = true;
let currentProcessingAccount = null;
let currentAccountIndex = 0;
let totalAccounts = 0;

// ============================================
// MODERN ALERT HELPERS
// ============================================

// Modern alert using SweetAlert2
function showAlert(message, type = "info") {
  const icons = {
    info: "info",
    success: "success",
    error: "error",
    warning: "warning",
  };

  return Swal.fire({
    icon: icons[type] || "info",
    title:
      type === "error"
        ? "Oops..."
        : type === "success"
          ? "Berhasil!"
          : "Informasi",
    text: message,
    confirmButtonText: "OK",
    confirmButtonColor: "#4a70a9",
    background: "#ffffff",
    customClass: {
      popup: "rounded-lg",
      confirmButton: "btn btn-primary",
    },
  });
}

// Modern confirm using SweetAlert2
async function showConfirm(message, title = "Konfirmasi") {
  const result = await Swal.fire({
    title: title,
    html: message.replace(/\n/g, "<br>"),
    icon: "question",
    showCancelButton: true,
    confirmButtonText: "Ya, Lanjutkan",
    cancelButtonText: "Batal",
    confirmButtonColor: "#4a70a9",
    cancelButtonColor: "#6b7280",
    reverseButtons: true,
    customClass: {
      popup: "rounded-lg",
      confirmButton: "btn btn-primary",
      cancelButton: "btn btn-secondary",
    },
  });

  return result.isConfirmed;
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener("DOMContentLoaded", async () => {
  console.log("🚀 Initializing SnapFlux Automation...");

  // Wait a bit to ensure DOM is fully rendered
  await new Promise((resolve) => setTimeout(resolve, 100));

  // Initialize default values first
  initializeDefaults();

  // Make sure all functions are accessible globally
  window.startAutomation = startAutomation;
  window.pauseAutomation = pauseAutomation;
  window.stopAutomation = stopAutomation;
  window.handleFileSelect = handleFileSelect;
  window.toggleSelectAll = toggleSelectAll;
  window.showPage = showPage;
  window.toggleHeadless = toggleHeadless;
  window.downloadExcel = downloadExcel;
  window.openResultsFolder = openResultsFolder;
  window.saveResultsAs = saveResultsAs;
  window.clearLog = clearLog;
  window.showProcessingView = showProcessingView;
  window.hideProcessingView = hideProcessingView;
  window.updateProcessingView = updateProcessingView;
  window.clearExpiredSessions = clearExpiredSessions;
  window.clearAllSessions = clearAllSessions;

  console.log("✅ All functions registered globally");

  // Setup navigation event listeners with retry
  let retryCount = 0;
  const maxRetries = 5;

  const trySetupNavigation = () => {
    const navItems = document.querySelectorAll(".nav-item");
    if (navItems.length === 4) {
      setupNavigation();
      console.log("✅ Navigation setup successful");
    } else if (retryCount < maxRetries) {
      retryCount++;
      console.log(
        `⏳ Retrying navigation setup (${retryCount}/${maxRetries})...`,
      );
      setTimeout(trySetupNavigation, 200);
    } else {
      console.error("❌ Failed to setup navigation after multiple retries");
    }
  };

  trySetupNavigation();

  logMessage("Sistem siap", "info");

  // Start dashboard metrics refresh
  startDashboardRefresh();

  // Start header time update
  updateHeaderTime();
  setInterval(updateHeaderTime, 1000);
});

// Initialize default values
function initializeDefaults() {
  console.log("🔧 Initializing defaults...");

  // Set default date to today
  const today = new Date().toISOString().split("T")[0];
  const dateFilter = document.getElementById("date-filter");
  if (dateFilter) {
    dateFilter.value = today;
    console.log("✅ Date filter set to:", today);
  }

  // Initialize headless toggle visual state
  const headlessToggle = document.getElementById("headless-toggle");
  if (headlessToggle && headlessEnabled) {
    headlessToggle.classList.add("active");
    console.log("✅ Headless toggle initialized");
  }

  console.log("✅ Defaults initialized");
}

// ============================================
// NAVIGATION
// ============================================

function setupNavigation() {
  console.log("🔧 Setting up navigation...");

  // Get all nav items
  const navItems = document.querySelectorAll(".nav-item");
  console.log(`Found ${navItems.length} navigation items`);

  if (navItems.length === 0) {
    console.error("❌ No navigation items found!");
    return;
  }

  navItems.forEach((navItem, index) => {
    console.log(`Setting up nav item ${index}:`, navItem.textContent.trim());

    // Remove any existing onclick attribute to prevent conflicts
    navItem.removeAttribute("onclick");

    // Add multiple event types for better compatibility
    const handleClick = function (e) {
      e.preventDefault();
      e.stopPropagation();

      console.log("🖱️ Nav item clicked:", navItem.textContent.trim());

      // Determine which page to show based on nav item content or data attribute
      const pageMap = {
        Dasbor: "dashboard",
        Otomasi: "automation",
        Hasil: "results",
        Pengaturan: "settings",
      };

      const navText = navItem.textContent.trim();
      const pageName = pageMap[navText];

      if (pageName) {
        console.log(`📍 Navigating to: ${pageName}`);
        showPage(pageName);
      } else {
        console.error("❌ Unknown nav item:", navText);
      }
    };

    // Add both click and mousedown events
    navItem.addEventListener("click", handleClick, true);
    navItem.addEventListener("mousedown", handleClick, true);

    // Add visual feedback
    navItem.style.cursor = "pointer";

    console.log(`✅ Nav item ${index} setup complete`);
  });

  console.log("✅ Navigation setup complete");

  // Test that navigation is working
  console.log("🧪 Testing navigation system...");
  console.log("Try clicking the menu items now!");
}

function showPage(pageName) {
  console.log("=== showPage called ===");
  console.log("Page name:", pageName);

  try {
    // Hide all pages
    const allSections = document.querySelectorAll(".page-section");
    console.log("Found sections:", allSections.length);

    if (allSections.length === 0) {
      console.error("❌ No page sections found!");
      return;
    }

    allSections.forEach((section) => {
      console.log("Hiding section:", section.id);
      section.classList.remove("active");
      section.style.display = "none"; // Force hide
    });

    // Remove active from all nav items
    const allNavItems = document.querySelectorAll(".nav-item");
    console.log("Found nav items:", allNavItems.length);
    allNavItems.forEach((item) => {
      item.classList.remove("active");
    });

    // Show selected page
    const pageElement = document.getElementById(pageName + "-page");
    console.log("Looking for element with ID:", pageName + "-page");
    console.log("Found element:", pageElement);

    if (pageElement) {
      pageElement.classList.add("active");
      pageElement.style.display = "block"; // Force show
      console.log("✅ Activated page:", pageName);
    } else {
      console.error("❌ Page element not found:", pageName + "-page");
      console.log("Available sections:");
      allSections.forEach((s) => console.log("  -", s.id));
      return;
    }

    // Set active nav item
    const navItems = document.querySelectorAll(".nav-item");
    const pageMap = {
      dashboard: "Dasbor",
      automation: "Otomasi",
      results: "Hasil",
      settings: "Pengaturan",
    };

    navItems.forEach((item) => {
      const navText = item.textContent.trim();
      if (navText === pageMap[pageName]) {
        item.classList.add("active");
        console.log("✅ Activated nav item for:", pageName);
      }
    });

    // Update page title in header
    const pageTitles = {
      dashboard: "Dasbor",
      automation: "Kontrol Otomasi",
      results: "Hasil Export",
      settings: "Pengaturan",
    };
    const pageTitleElement = document.getElementById("page-title");
    if (pageTitleElement && pageTitles[pageName]) {
      pageTitleElement.textContent = pageTitles[pageName];
      console.log("✅ Updated page title to:", pageTitles[pageName]);
    }

    // Update header info (icon, subtitle, breadcrumb)
    updateHeaderInfo(pageName);

    // Update debug indicator
    const debugIndicator = document.getElementById("current-page-name");
    if (debugIndicator) {
      debugIndicator.textContent = pageName;
      debugIndicator.style.color = "#fff";
      debugIndicator.style.fontWeight = "bold";
      console.log("✅ Updated debug indicator to:", pageName);
    }

    console.log("=== showPage completed successfully ===");
  } catch (error) {
    console.error("❌ Error in showPage:", error);
  }
}

// ============================================
// TEST & DEBUG FUNCTIONS
// ============================================

// Test function to manually check navigation
window.testNavigation = function () {
  console.log("=== NAVIGATION TEST START ===");

  // Test 1: Check if sections exist
  const sections = document.querySelectorAll(".page-section");
  console.log(`✓ Found ${sections.length} sections:`);
  sections.forEach((s) => console.log(`  - ${s.id}`));

  // Test 2: Check if nav items exist
  const navItems = document.querySelectorAll(".nav-item");
  console.log(`✓ Found ${navItems.length} nav items:`);
  navItems.forEach((n, i) => console.log(`  - ${i}: ${n.textContent.trim()}`));

  // Test 3: Check z-index
  const sidebar = document.querySelector(".sidebar");
  const sidebarZIndex = window.getComputedStyle(sidebar).zIndex;
  console.log(`✓ Sidebar z-index: ${sidebarZIndex}`);

  // Test 4: Check pointer events
  navItems.forEach((item, i) => {
    const style = window.getComputedStyle(item);
    console.log(
      `  Nav item ${i} pointer-events: ${style.pointerEvents}, cursor: ${style.cursor}`,
    );
  });

  // Test 5: Try to navigate
  console.log("\n🔄 Testing navigation to 'automation'...");
  try {
    showPage("automation");
    console.log("✓ Navigation function executed");
  } catch (error) {
    console.error("✗ Navigation failed:", error);
  }

  console.log("=== NAVIGATION TEST END ===");
  console.log("\nTo test manually, run:");
  console.log("  testNavigation()");
  console.log("  showPage('dashboard')");
  console.log("  showPage('automation')");
  console.log("  showPage('results')");
  console.log("  showPage('settings')");
};

// Make showPage easily testable from console
window.nav = function (page) {
  console.log(`🔄 Manual navigation to: ${page}`);
  showPage(page);
};

console.log("💡 Debug commands available:");
console.log("  testNavigation() - Run full navigation test");
console.log("  nav('dashboard') - Navigate to dashboard");
console.log("  nav('automation') - Navigate to automation");
console.log("  nav('results') - Navigate to results");
console.log("  nav('settings') - Navigate to settings");

// ============================================
// EXCEL FILE MANAGEMENT
// ============================================

async function handleFileSelect(input) {
  if (input.files && input.files[0]) {
    const file = input.files[0];
    const fileName = file.name;

    // Update label
    const label = document.getElementById("selected-filename");
    if (label) label.textContent = fileName;

    logMessage(`Membaca file ${fileName}...`, "info");

    // Read file
    const reader = new FileReader();
    reader.onload = async function (e) {
      const base64Data = e.target.result;

      try {
        // Check if function exists
        if (typeof eel.load_accounts_from_data !== "function") {
          showAlert(
            "Update belum diterapkan. Harap TUTUP aplikasi dan jalankan ulang START_GUI.bat",
            "warning",
          );
          input.value = "";
          label.textContent = "Belum ada file";
          return;
        }

        const result = await eel.load_accounts_from_data(
          base64Data,
          fileName,
        )();

        if (result.success) {
          accounts = result.accounts;
          renderAccounts();
          updateStatistics();

          // Update dashboard dengan data realtime
          updateDashboardMetrics();

          logMessage(`${result.message}`, "success");
        } else {
          showAlert(result.message, "error");
          logMessage(`${result.message}`, "error");
          // Reset input
          input.value = "";
          label.textContent = "Belum ada file";
        }
      } catch (error) {
        console.error("Error loading accounts:", error);
        logMessage("Gagal memuat akun dari file", "error");
        showAlert("Terjadi kesalahan saat memuat akun: " + error, "error");
        // Reset input
        input.value = "";
        label.textContent = "Belum ada file";
      }
    };

    reader.onerror = function (error) {
      console.error("Error reading file:", error);
      showAlert("Gagal membaca file", "error");
    };

    reader.readAsDataURL(file);
  }
}

// ============================================
// ACCOUNT RENDERING
// ============================================

function renderAccounts() {
  const container = document.getElementById("accounts-container");

  if (accounts.length === 0) {
    container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-inbox"></i>
                </div>
                <p style="margin: 0">Belum ada akun dimuat</p>
                <p style="font-size: 0.875rem; margin-top: 0.5rem">Load file Excel untuk memulai</p>
            </div>
        `;
    return;
  }

  container.innerHTML = "";

  accounts.forEach((account) => {
    const accountDiv = document.createElement("div");
    accountDiv.id = `account-${account.id}`;
    accountDiv.className = "account-list-item";

    accountDiv.innerHTML = `
            <label class="flex items-center gap-4 cursor-pointer w-full">
                <input
                    type="checkbox"
                    id="check-${account.id}"
                    class="account-checkbox"
                    checked
                    onchange="updateStatistics()"
                >
                <div class="account-info">
                    <div class="account-name">${account.nama}</div>
                </div>
            </label>

            <div class="absolute bottom-0 left-0 w-full h-0.5 bg-gray-100">
                <div id="progress-${account.id}" class="h-full bg-indigo-500 transition-all duration-300" style="width: 0%"></div>
            </div>
        `;

    container.appendChild(accountDiv);
  });
}

function toggleSelectAll() {
  allSelected = !allSelected;

  // Get the button element
  const btn = document.getElementById("select-all-btn");

  // Add visual feedback with animation
  if (btn) {
    // Pulse effect
    btn.style.animation = "pulse 0.3s ease";
    setTimeout(() => {
      btn.style.animation = "";
    }, 300);

    // Update button text and style based on state
    if (allSelected) {
      btn.innerHTML = '<i class="fas fa-times-circle"></i> Batalkan Semua';
      btn.classList.remove("btn-primary");
      btn.classList.add("btn-secondary");
      btn.style.background =
        "linear-gradient(135deg, #6b7280 0%, #4b5563 100%)";
    } else {
      btn.innerHTML = '<i class="fas fa-check-double"></i> Pilih Semua';
      btn.classList.remove("btn-secondary");
      btn.classList.add("btn-primary");
      btn.style.background = "";
    }
  }

  accounts.forEach((account) => {
    const checkbox = document.getElementById(`check-${account.id}`);
    if (checkbox) {
      checkbox.checked = allSelected;
    }
  });
  updateStatistics();
}

// ============================================
// AUTOMATION CONTROL
// ============================================

async function startAutomation() {
  console.log("🚀 startAutomation() called");

  // Validasi
  const selectedAccounts = accounts.filter((acc) => {
    const checkbox = document.getElementById(`check-${acc.id}`);
    return checkbox && checkbox.checked;
  });

  if (selectedAccounts.length === 0) {
    showAlert("Pilih minimal 1 akun untuk diproses!", "warning");
    return;
  }

  // Get settings
  const settings = {
    headless: headlessEnabled,
    date: document.getElementById("date-filter").value || null,
    delay: parseFloat(document.getElementById("delay-input").value) || 2.0,
  };

  // Start real-time dashboard updates
  startDashboardRefresh();

  // Confirm
  const confirmStart = await showConfirm(
    `Mulai otomasi untuk <strong>${selectedAccounts.length} akun</strong>?<br><br>` +
    `<div style="text-align: left; display: inline-block;">` +
    `<strong>Mode:</strong> ${settings.headless ? "Headless (Background)" : "GUI Terlihat"}<br>` +
    `<strong>Tanggal:</strong> ${settings.date || "Tanpa filter"}<br>` +
    `<strong>Delay:</strong> ${settings.delay} detik` +
    `</div>`,
    "Mulai Otomasi?",
  );

  if (!confirmStart) return;

  // Disable controls
  automationRunning = true;
  updateControlButtons();

  // Update status
  document.getElementById("status-text").textContent = "Memproses";
  updateHeaderStatus("processing", "Memproses");
  logMessage("Memulai otomasi...", "info");

  // Reset statistics
  resetAccountStatuses();

  // Show processing view with first account
  totalAccounts = selectedAccounts.length;
  currentAccountIndex = 1;

  // Reset progress
  const processingProgressFill = document.getElementById(
    "processing-progress-fill",
  );
  const processingPercent = document.getElementById("processing-percent");
  if (processingProgressFill) processingProgressFill.style.width = "0%";
  if (processingPercent) processingPercent.textContent = "0%";

  // Get first selected account
  const firstAccount = accounts.find((acc) =>
    selectedAccounts.includes(acc.id),
  );
  if (firstAccount) {
    currentProcessingAccount = firstAccount;
    updateProcessingView(
      firstAccount.nama,
      "",
      1,
      totalAccounts,
      "Mempersiapkan proses...",
      false,
    );
  }

  showProcessingView();

  try {
    const result = await eel.start_automation(selectedAccounts, settings)();

    if (!result.success) {
      showAlert(result.message, "error");
      logMessage(`${result.message}`, "error");
      automationRunning = false;
      updateControlButtons();
      hideProcessingView();
    }
  } catch (error) {
    console.error("Error starting automation:", error);
    logMessage("Gagal memulai otomasi", "error");
    showAlert("Terjadi kesalahan: " + error, "error");
    automationRunning = false;
    updateControlButtons();
    hideProcessingView();
  }
}

async function pauseAutomation() {
  try {
    const result = await eel.pause_automation()();

    if (result.success) {
      const pauseBtn = document.getElementById("pause-btn");
      const pauseBtnProcessing = document.getElementById(
        "pause-btn-processing",
      );

      if (result.paused) {
        if (pauseBtn)
          pauseBtn.innerHTML = '<i class="fas fa-play"></i> Lanjutkan';
        if (pauseBtnProcessing) {
          pauseBtnProcessing.innerHTML =
            '<i class="fas fa-play"></i> Lanjutkan';
          pauseBtnProcessing.classList.remove("btn-secondary");
          pauseBtnProcessing.classList.add("btn-success");
        }
        document.getElementById("status-text").textContent = "Dijeda";
        updateHeaderStatus("paused", "Dijeda");
      } else {
        if (pauseBtn) pauseBtn.innerHTML = '<i class="fas fa-pause"></i> Jeda';
        if (pauseBtnProcessing) {
          pauseBtnProcessing.innerHTML = '<i class="fas fa-pause"></i> Jeda';
          pauseBtnProcessing.classList.remove("btn-success");
          pauseBtnProcessing.classList.add("btn-secondary");
        }
        document.getElementById("status-text").textContent = "Memproses";
        updateHeaderStatus("processing", "Memproses");
      }
    }
  } catch (error) {
    console.error("Error pausing automation:", error);
    showAlert("Terjadi kesalahan saat pause: " + error, "error");
  }
}

async function stopAutomation() {
  const confirm = await showConfirm(
    "Automation yang sedang berjalan akan dihentikan.<br>Data yang sudah diproses akan tetap tersimpan.",
    "Hentikan Automation?",
  );
  if (!confirm) return;

  try {
    const result = await eel.stop_automation()();

    if (result.success) {
      automationRunning = false;
      updateControlButtons();
      document.getElementById("status-text").textContent = "Dihentikan";
      updateHeaderStatus("stopped", "Dihentikan");
      logMessage("Otomasi dihentikan", "warning");
      hideProcessingView();
    }
  } catch (error) {
    console.error("Error stopping automation:", error);
    logMessage("Gagal menghentikan otomasi", "error");
  }
}

function updateControlButtons() {
  const startBtn = document.getElementById("start-btn");
  const pauseBtn = document.getElementById("pause-btn");
  const stopBtn = document.getElementById("stop-btn");

  if (automationRunning) {
    startBtn.disabled = true;
    startBtn.classList.add("opacity-50", "cursor-not-allowed");
    pauseBtn.disabled = false;
    pauseBtn.classList.remove("opacity-50", "cursor-not-allowed");
    stopBtn.disabled = false;
    stopBtn.classList.remove("opacity-50", "cursor-not-allowed");
  } else {
    startBtn.disabled = false;
    startBtn.classList.remove("opacity-50", "cursor-not-allowed");
    pauseBtn.disabled = true;
    pauseBtn.classList.add("opacity-50", "cursor-not-allowed");
    stopBtn.disabled = true;
    stopBtn.classList.add("opacity-50", "cursor-not-allowed");
  }
}

function resetAccountStatuses() {
  accounts.forEach((account) => {
    const statusBadge = document.getElementById(`status-${account.id}`);
    const progressBar = document.getElementById(`progress-${account.id}`);
    const indicator = document.getElementById(`indicator-${account.id}`);

    if (statusBadge) {
      statusBadge.textContent = "Menunggu";
      statusBadge.className = "text-xs font-bold text-muted";
    }
    if (indicator) indicator.className = "account-status-indicator";
    if (progressBar) progressBar.style.width = "0%";
  });
  updateStatistics();
}

// ============================================
// CALLBACKS FROM PYTHON
// ============================================

eel.expose(update_account_status);
function update_account_status(accountId, status, progress) {
  const progressBar = document.getElementById(`progress-${accountId}`);
  const accountRow = document.getElementById(`account-${accountId}`);

  if (progressBar) progressBar.style.width = `${progress}%`;

  // Define status text for processing view
  let statusText;
  switch (status) {
    case "processing":
      statusText = "Sedang login dan mengambil data...";
      break;
    case "login":
      statusText = "Melakukan login ke akun...";
      break;
    case "fetching":
      statusText = "Mengambil data transaksi...";
      break;
    case "saving":
      statusText = "Menyimpan data ke Excel...";
      break;
    case "done":
      statusText = "Akun berhasil diproses!";
      break;
    case "error":
      statusText = "Terjadi kesalahan saat memproses";
      break;
    default:
      statusText = "Menunggu giliran proses...";
  }

  // Update processing view
  const account = accounts.find((acc) => acc.id === accountId);
  if (account) {
    currentProcessingAccount = account;
    const selectedAccounts = accounts.filter((acc) => {
      const cb = document.getElementById(`check-${acc.id}`);
      return cb && cb.checked;
    });
    currentAccountIndex =
      selectedAccounts.findIndex((acc) => acc.id === accountId) + 1;

    updateProcessingView(
      account.nama,
      "",
      currentAccountIndex,
      totalAccounts,
      statusText,
    );
  }

  // Highlight active card
  if (accountRow && status === "processing") {
    document.querySelectorAll(".account-list-item").forEach((c) => {
      c.classList.remove("selected");
      c.classList.remove("processing");
    });
    accountRow.classList.add("selected");
    accountRow.classList.add("processing");

    // Auto-scroll to processing account - smooth scroll into view
    setTimeout(() => {
      accountRow.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
        inline: "nearest",
      });
    }, 100);
  } else if (accountRow && status !== "processing") {
    accountRow.classList.remove("processing");
  }

  updateStatistics();

  // Update dashboard metrics in real-time
  updateDashboardMetrics();
}

eel.expose(update_overall_progress);
function update_overall_progress(current, total, percent) {
  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");
  const progressPercent = document.getElementById("progress-percent");

  // Also update processing view progress
  const processingProgressFill = document.getElementById(
    "processing-progress-fill",
  );
  const processingPercentView = document.getElementById("processing-percent");

  // Update circular progress chart
  const progressCircle = document.getElementById("processing-progress-circle");
  const percentChart = document.getElementById("processing-percent-chart");

  if (progressCircle) {
    const circumference = 2 * Math.PI * 34; // r=34
    const offset = circumference * (1 - percent / 100);
    progressCircle.style.strokeDashoffset = offset;
  }

  if (percentChart) {
    percentChart.textContent = `${Math.round(percent)}%`;
  }

  if (processingProgressFill)
    processingProgressFill.style.width = `${percent}%`;
  if (processingPercentView)
    processingPercentView.textContent = `${Math.round(percent)}%`;
  if (progressBar) progressBar.style.width = `${percent}%`;
  if (progressText) progressText.textContent = `${current}/${total}`;
  if (progressPercent) progressPercent.textContent = `${percent}%`;
}

eel.expose(log_message);
function log_message(message, type = "info") {
  const logContainer = document.getElementById("log-container");
  const now = new Date();
  const timestamp = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}:${String(now.getSeconds()).padStart(2, "0")}`;

  let color, icon, bgColor;
  switch (type) {
    case "success":
      color = "#10b981";
      icon = "✓";
      bgColor = "rgba(16, 185, 129, 0.1)";
      break;
    case "error":
      color = "#ef4444";
      icon = "✗";
      bgColor = "rgba(239, 68, 68, 0.1)";
      break;
    case "warning":
      color = "#f59e0b";
      icon = "⚠";
      bgColor = "rgba(245, 158, 11, 0.1)";
      break;
    default:
      color = "#60a5fa";
      icon = "ℹ";
      bgColor = "transparent";
  }

  const logEntry = document.createElement("div");
  logEntry.style.cssText = `
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0.75rem;
    margin: 0.25rem 0;
    border-radius: 4px;
    background: ${bgColor};
    transition: all 0.2s ease;
    font-size: 0.875rem;
  `;

  logEntry.innerHTML = `
    <span style="color: #6b7280; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; min-width: 60px;">${timestamp}</span>
    <span style="color: ${color}; font-weight: 700; font-size: 1rem;">${icon}</span>
    <span style="color: #d4d4d4; flex: 1; line-height: 1.4;">${message}</span>
  `;

  logEntry.onmouseover = function () {
    this.style.backgroundColor = "rgba(74, 112, 169, 0.12)";
  };
  logEntry.onmouseout = function () {
    this.style.backgroundColor = bgColor;
  };

  logContainer.appendChild(logEntry);
  logContainer.scrollTo({ top: logContainer.scrollHeight, behavior: "smooth" });

  if (logContainer.children.length > 500) {
    logContainer.removeChild(logContainer.firstChild);
  }
}
// Alias for backward compatibility
const logMessage = log_message;

// ============================================
// PROCESSING VIEW FUNCTIONS
// ============================================

function showProcessingView() {
  const processingView = document.getElementById("processing-view");
  if (processingView) {
    processingView.classList.remove("hidden");
    processingView.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

function hideProcessingView() {
  const processingView = document.getElementById("processing-view");
  if (processingView) {
    processingView.classList.add("hidden");
  }
}

function updateProcessingView(
  name,
  username,
  current,
  total,
  statusText = "Memproses...",
  updateProgress = false,
) {
  const nameEl = document.getElementById("processing-name");
  if (nameEl) nameEl.textContent = name || "Memuat...";

  const usernameEl = document.getElementById("processing-username");
  if (usernameEl) usernameEl.textContent = username || "---";

  const currentEl = document.getElementById("processing-current");
  const totalEl = document.getElementById("processing-total");
  if (currentEl) currentEl.textContent = current || 0;
  if (totalEl) totalEl.textContent = total || 0;

  const statusEl = document.getElementById("processing-status");
  if (statusEl) {
    const statusSpan = statusEl.querySelector("span:last-child");
    if (statusSpan) {
      statusSpan.textContent = statusText;
    } else {
      statusEl.textContent = statusText;
    }
  }

  // Always update progress based on current/total
  const progress = total > 0 ? (current / total) * 100 : 0;

  // Update circular progress chart
  const progressCircle = document.getElementById("processing-progress-circle");
  const percentChart = document.getElementById("processing-percent-chart");

  if (progressCircle) {
    const circumference = 2 * Math.PI * 34; // r=34
    const offset = circumference * (1 - progress / 100);
    progressCircle.style.strokeDashoffset = offset;
  }

  if (percentChart) {
    percentChart.textContent = `${Math.round(progress)}%`;
  }

  // Update linear progress bar
  const progressFill = document.getElementById("processing-progress-fill");
  if (progressFill) progressFill.style.width = `${progress}%`;

  if (updateProgress) {
    const progressPercent = document.getElementById("processing-percent");
    if (progressPercent)
      progressPercent.textContent = `${Math.round(progress)}%`;
  }
}

eel.expose(automation_completed);
function automation_completed(successCount, totalCount) {
  automationRunning = false;
  updateControlButtons();
  hideProcessingView();

  const statusText = document.getElementById("status-text");
  if (statusText) statusText.textContent = "Selesai";

  // Update header status
  updateHeaderStatus("completed", "Selesai");

  // Final dashboard update
  updateDashboardMetrics();

  logMessage(
    `🎉 Automation selesai! ${successCount}/${totalCount} akun berhasil`,
    "success",
  );

  try {
    showExportCard(successCount);
  } catch (error) {
    console.error("❌ Error calling showExportCard:", error);
  }

  if ("Notification" in window && Notification.permission === "granted") {
    new Notification("SnapFlux Automation", {
      body: `Automation selesai! ${successCount}/${totalCount} akun berhasil diproses.`,
      icon: "/icon.png",
    });
  }
}

function clearLog() {
  const container = document.getElementById("log-container");
  if (container) {
    container.innerHTML = "";
    eel.clear_results()();
    logMessage("Log dan data hasil dibersihkan", "info");
  }
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

function showExportCard(successCount) {
  showPage("results");
  setTimeout(() => {
    const exportCard = document.getElementById("export-card");
    const exportCount = document.getElementById("export-count");
    if (exportCard && exportCount) {
      exportCount.textContent = successCount;
      exportCard.style.display = "block";
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, 100);
}

async function downloadExcel() {
  try {
    logMessage("Memulai export ke Excel...", "info");
    const result = await eel.export_to_excel()();
    if (result.success) {
      logMessage(`${result.message}`, "success");
      logMessage(`File disimpan: ${result.filepath}`, "info");
      const fileName = result.filepath.split(/[\\\/]/).pop();
      alert(
        `Export berhasil!\n\nFile: ${fileName}\nLokasi: ${result.filepath}`,
      );
    } else {
      logMessage(`${result.message}`, "error");
      alert(`Export gagal: ${result.message}`);
    }
  } catch (error) {
    console.error("Error downloading Excel:", error);
    logMessage("Gagal export ke Excel", "error");
    alert("Error: " + error);
  }
}

async function openResultsFolder() {
  try {
    const result = await eel.open_export_folder()();
    if (result.success) {
      logMessage("Folder results dibuka", "success");
    } else {
      logMessage(`${result.message}`, "error");
      alert(`Gagal membuka folder: ${result.message}`);
    }
  } catch (error) {
    console.error("Error opening folder:", error);
    logMessage("Gagal membuka folder results", "error");
    alert("Error: " + error);
  }
}

async function saveResultsAs() {
  try {
    logMessage("💾 Memulai proses Simpan Sebagai...", "info");
    const result = await eel.save_results_as()();

    if (result.success) {
      if (result.data) {
        const byteCharacters = atob(result.data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {
          type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        });

        if ("showSaveFilePicker" in window) {
          try {
            const handle = await window.showSaveFilePicker({
              suggestedName: result.filename,
              types: [
                {
                  description: "Excel Files",
                  accept: {
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                      [".xlsx"],
                  },
                },
              ],
            });
            const writable = await handle.createWritable();
            await writable.write(blob);
            await writable.close();
            logMessage(`File berhasil disimpan: ${handle.name}`, "success");
            showAlert(
              `File berhasil disimpan sebagai ${handle.name}`,
              "success",
            );
            return;
          } catch (err) {
            if (err.name !== "AbortError") {
              console.error("File picker error:", err);
            } else {
              logMessage("⚠️ Penyimpanan dibatalkan oleh pengguna", "warning");
              return;
            }
          }
        }

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = result.filename;
        document.body.appendChild(a);
        a.click();

        // Tunggu sebentar untuk cleanup
        // Note: Tidak ada alert karena browser sudah punya notifikasi download sendiri
        setTimeout(() => {
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          logMessage(`File berhasil diunduh: ${result.filename}`, "success");
        }, 100);
      } else {
        logMessage(`${result.message}`, "success");
        alert(result.message);
      }
    } else {
      if (result.message === "Cancelled") {
        logMessage("Penyimpanan dibatalkan", "warning");
      } else {
        logMessage(`${result.message}`, "error");
        alert(`Gagal menyimpan: ${result.message}`);
      }
    }
  } catch (error) {
    console.error("Error saving results:", error);
    logMessage("Gagal menyimpan file", "error");
    alert("Error: " + error);
  }
}

// ============================================
// STATISTICS
// ============================================

function updateStatistics() {
  let success = 0,
    error = 0,
    processing = 0,
    waiting = 0;
  accounts.forEach((account) => {
    const statusBadge = document.getElementById(`status-${account.id}`);
    if (statusBadge) {
      if (statusBadge.classList.contains("status-done")) success++;
      else if (statusBadge.classList.contains("status-error")) error++;
      else if (statusBadge.classList.contains("status-processing"))
        processing++;
      else waiting++;
    }
  });

  const successEl = document.getElementById("success-count");
  const errorEl = document.getElementById("failed-count");
  const totalEl = document.getElementById("total-accounts");

  if (successEl) successEl.textContent = success;
  if (errorEl) errorEl.textContent = error;
  if (totalEl) totalEl.textContent = accounts.length;

  // Force dashboard refresh to get latest data
  if (dashboardRefreshInterval === null && (success > 0 || error > 0)) {
    startDashboardRefresh();
  }
}

function updateCircularChart(success, error, processing, waiting) {
  const total = success + error + processing + waiting;
  const totalAccountsEl = document.getElementById("total-accounts");
  if (totalAccountsEl) totalAccountsEl.textContent = total;
  if (total === 0) return;

  const circumference = 2 * Math.PI * 80; // r=80
  let currentOffset = 0;

  // Helper to set arc
  const setArc = (id, count) => {
    const el = document.getElementById(id);
    if (el) {
      const len = circumference * (count / total);
      el.setAttribute("stroke-dasharray", `${len} ${circumference}`);
      el.setAttribute("stroke-dashoffset", currentOffset);
      currentOffset -= len;
    }
  };

  setArc("chart-success", success);
  setArc("chart-error", error);
  setArc("chart-processing", processing);
}

// ============================================
// KEYBOARD SHORTCUTS & MISC
// ============================================

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    if (!automationRunning) startAutomation();
  }
  if ((e.ctrlKey || e.metaKey) && e.key === "p") {
    e.preventDefault();
    if (automationRunning) pauseAutomation();
  }
  if (e.key === "Escape") {
    if (automationRunning) stopAutomation();
  }
});

function toggleHeadless() {
  const toggle = document.getElementById("headless-toggle");
  if (toggle) {
    headlessEnabled = toggle.checked;
    console.log("Headless mode:", headlessEnabled);
  }
}

// Request notification permission
if ("Notification" in window && Notification.permission !== "granted") {
  Notification.requestPermission();
}

// ============================================
// DASHBOARD METRICS & MONITORING
// ============================================

let dashboardRefreshInterval = null;

async function updateDashboardMetrics() {
  try {
    // Get telemetry metrics
    const metrics = await eel.get_telemetry_metrics()();

    // Update main stat cards (Total Akun, Berhasil, Gagal)
    const totalAccountsEl = document.getElementById("total-accounts");
    const successCountEl = document.getElementById("success-count");
    const failedCountEl = document.getElementById("failed-count");

    if (totalAccountsEl) {
      totalAccountsEl.textContent =
        metrics.total_accounts || accounts.length || 0;
    }
    if (successCountEl) {
      successCountEl.textContent = metrics.successful || 0;
    }
    if (failedCountEl) {
      failedCountEl.textContent = metrics.failed || 0;
    }

    // Update performance metrics
    const successRate = document.getElementById("metric-success-rate");
    const avgTime = document.getElementById("metric-avg-time");
    const sessionDuration = document.getElementById("metric-session-duration");
    const throughput = document.getElementById("metric-throughput");

    if (successRate) successRate.textContent = `${metrics.success_rate || 0}%`;
    if (avgTime) avgTime.textContent = `${metrics.avg_processing_time || 0}s`;
    if (sessionDuration)
      sessionDuration.textContent = formatDuration(
        metrics.session_duration || 0,
      );

    // Calculate throughput
    const throughputValue =
      metrics.session_duration > 0
        ? ((metrics.total_accounts / metrics.session_duration) * 60).toFixed(1)
        : 0;
    if (throughput) throughput.textContent = `${throughputValue}/min`;

    // Update error tracking
    if (metrics.errors && Object.keys(metrics.errors).length > 0) {
      updateErrorTracking(metrics.errors);
    }

    // Update Business Metrics (NEW)
    const totalSalesEl = document.getElementById("metric-total-sales");
    const totalStockEl = document.getElementById("metric-total-stock");

    if (metrics.business_metrics) {
      if (totalSalesEl) totalSalesEl.textContent = metrics.business_metrics.total_penjualan || 0;
      if (totalStockEl) totalStockEl.textContent = metrics.business_metrics.total_stok || 0;
    }

  } catch (error) {
    console.error("Error updating dashboard metrics:", error);
  }
}

function updateErrorTracking(errors) {
  const errorTracking = document.getElementById("error-tracking");
  const errorList = document.getElementById("error-list");

  if (!errorTracking || !errorList) return;

  // Show error tracking section if there are errors
  const totalErrors = Object.values(errors).reduce((a, b) => a + b, 0);
  if (totalErrors > 0) {
    errorTracking.style.display = "block";

    // Build error list
    const errorItems = Object.entries(errors)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5) // Top 5 errors
      .map(
        ([type, count]) => `
                <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: #f8fafc; border-radius: 4px;">
                    <span style="color: var(--text-main); font-size: 0.875rem;">${type.replace(/_/g, " ")}</span>
                    <span style="font-weight: 700; color: var(--error);">${count}</span>
                </div>
            `,
      )
      .join("");

    errorList.innerHTML = errorItems;
  } else {
    errorTracking.style.display = "none";
  }
}

function formatDuration(seconds) {
  if (seconds < 60) {
    return `${seconds.toFixed(0)}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}m ${secs}s`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  }
}

function startDashboardRefresh() {
  // Update immediately
  updateDashboardMetrics();

  // Then update every 2 seconds
  dashboardRefreshInterval = setInterval(updateDashboardMetrics, 2000);
}

function stopDashboardRefresh() {
  if (dashboardRefreshInterval) {
    clearInterval(dashboardRefreshInterval);
    dashboardRefreshInterval = null;
  }
}

// ============================================
// HEADER FUNCTIONS
// ============================================

function updateHeaderTime() {
  const timeEl = document.getElementById("header-time");
  if (timeEl) {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");
    timeEl.textContent = `${hours}:${minutes}:${seconds}`;
  }
}

function updateHeaderInfo(pageName) {
  const pageConfig = {
    dashboard: {
      title: "Dasbor",
      subtitle: "Pantau performa otomasi secara realtime",
      icon: "fa-chart-simple",
      breadcrumb: "Dasbor",
    },
    automation: {
      title: "Kontrol Otomasi",
      subtitle: "Kelola dan jalankan proses otomasi",
      icon: "fa-bolt",
      breadcrumb: "Otomasi",
    },
    results: {
      title: "Hasil Export",
      subtitle: "Lihat log aktivitas dan ekspor data",
      icon: "fa-file-lines",
      breadcrumb: "Hasil",
    },
    settings: {
      title: "Pengaturan",
      subtitle: "Konfigurasi preferensi aplikasi",
      icon: "fa-sliders",
      breadcrumb: "Pengaturan",
    },
  };

  const config = pageConfig[pageName];
  if (!config) return;

  // Update title
  const titleEl = document.getElementById("page-title");
  if (titleEl) titleEl.textContent = config.title;

  // Update subtitle
  const subtitleEl = document.getElementById("page-subtitle");
  if (subtitleEl) subtitleEl.textContent = config.subtitle;

  // Update icon
  const iconEl = document.getElementById("page-icon");
  if (iconEl) {
    const iconChild = iconEl.querySelector("i");
    if (iconChild) {
      iconChild.className = `fas ${config.icon}`;
    }
  }

  // Update breadcrumb
  const breadcrumbEl = document.getElementById("breadcrumb-text");
  if (breadcrumbEl) breadcrumbEl.textContent = config.breadcrumb;
}

function updateHeaderStatus(status, text) {
  const statusTextEl = document.getElementById("header-status-text");
  const statusIndicatorEl = document.getElementById("header-status-indicator");
  const statusContainer = statusTextEl?.parentElement;

  if (!statusTextEl || !statusIndicatorEl || !statusContainer) return;

  // Update text
  statusTextEl.textContent = text;

  // Update colors based on status
  const statusStyles = {
    ready: {
      bg: "#f0fdf4",
      border: "#86efac",
      text: "#16a34a",
      indicator: "",
    },
    processing: {
      bg: "#eff6ff",
      border: "#93c5fd",
      text: "#2563eb",
      indicator: "processing",
    },
    paused: {
      bg: "#fef3c7",
      border: "#fcd34d",
      text: "#d97706",
      indicator: "warning",
    },
    stopped: {
      bg: "#fee2e2",
      border: "#fca5a5",
      text: "#dc2626",
      indicator: "error",
    },
    completed: {
      bg: "#f0fdf4",
      border: "#86efac",
      text: "#16a34a",
      indicator: "success",
    },
  };

  const style = statusStyles[status] || statusStyles.ready;

  statusContainer.style.background = style.bg;
  statusContainer.style.borderColor = style.border;
  statusTextEl.style.color = style.text;

  // Update indicator class
  statusIndicatorEl.className = `account-status-indicator ${style.indicator}`;
}

// ============================================
// SESSION MANAGEMENT
// ============================================

async function clearExpiredSessions() {
  try {
    const confirm = await showConfirm(
      "Hapus semua session yang sudah expired?",
      "Clear Expired Sessions",
    );

    if (!confirm) return;

    const result = await eel.clear_expired_sessions()();

    if (result.success) {
      showAlert(result.message, "success");
      logMessage(`${result.message}`, "success");
      updateDashboardMetrics();
    } else {
      showAlert(result.message, "error");
      logMessage(`${result.message}`, "error");
    }
  } catch (error) {
    console.error("Error clearing expired sessions:", error);
    showAlert("Gagal menghapus expired sessions", "error");
  }
}

async function clearAllSessions() {
  try {
    const confirm = await showConfirm(
      "Hapus SEMUA session yang tersimpan?<br><br>⚠️ Semua akun harus login ulang pada run berikutnya.",
      "Clear All Sessions",
    );

    if (!confirm) return;

    const result = await eel.clear_all_sessions()();

    if (result.success) {
      showAlert(result.message, "success");
      logMessage(`${result.message}`, "success");
      updateDashboardMetrics();
    } else {
      showAlert(result.message, "error");
      logMessage(`${result.message}`, "error");
    }
  } catch (error) {
    console.error("Error clearing all sessions:", error);
    showAlert("Gagal menghapus sessions", "error");
  }
}
