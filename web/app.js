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
    confirmButtonColor: "#0eb0f2", // Brand Blue
    background: "#ffffff",
    customClass: {
      popup: "custom-swal-popup",
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
    confirmButtonColor: "#0eb0f2", // Brand Blue
    cancelButtonColor: "#64748b", // Slate
    reverseButtons: true,
    customClass: {
      popup: "custom-swal-popup",
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
    if (navItems.length === 5) {
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

  // Initialize sidebar state
  initSidebar();
});

// ============================================
// SIDEBAR LOGIC
// ============================================

function toggleSidebar() {
  document.body.classList.toggle("sidebar-collapsed");
  const isCollapsed = document.body.classList.contains("sidebar-collapsed");
  localStorage.setItem("sidebarCollapsed", isCollapsed);

  // Update toggle button icon
  const toggleBtn = document.querySelector(".sidebar-toggle-btn i");
  if (toggleBtn) {
    toggleBtn.className = isCollapsed ? "fas fa-chevron-right" : "fas fa-chevron-left";
  }
}

function initSidebar() {
  const isCollapsed = localStorage.getItem("sidebarCollapsed") === "true";
  if (isCollapsed) {
    document.body.classList.add("sidebar-collapsed");
    // Update toggle button icon
    const toggleBtn = document.querySelector(".sidebar-toggle-btn i");
    if (toggleBtn) {
      toggleBtn.className = "fas fa-chevron-right";
    }
  }
}

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
        Tentang: "about",
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
      about: "Tentang",
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
      about: "Tentang SnapFlux",
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
console.log("  nav('about') - Navigate to about");

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
            <div class="flex items-center justify-between gap-4 w-full">
                <label class="flex items-center gap-3 cursor-pointer flex-1 min-w-0">
                    <input
                        type="checkbox"
                        id="check-${account.id}"
                        class="account-checkbox shrink-0"
                        checked
                        onchange="updateStatistics()"
                    >
                    <div class="account-name truncate font-medium text-gray-700">${account.nama}</div>
                </label>
                
                <div class="flex flex-col items-end shrink-0 gap-2">
                    <div id="status-badge-${account.id}" class="text-xs font-medium px-2 py-1 rounded bg-slate-100 text-slate-500">
                        Menunggu
                    </div>
                    <div id="error-msg-${account.id}" class="text-[11px] text-right hidden"></div>
                </div>
            </div>

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
  // Confirm
  const confirmStart = await showConfirm(
    `<div style="text-align: left; font-size: 0.8rem; color: #334155;"><p style="margin-bottom: 0.5rem;">Anda akan memproses <strong>${selectedAccounts.length} akun</strong> dengan konfigurasi berikut:</p><table style="width: 100%; border-collapse: collapse;"><tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 4px 0; color: #64748b; font-weight: 500;">Mode</td><td style="padding: 4px 0; text-align: right; color: #0f172a; font-weight: 600;">${settings.headless ? '<span style="color: #64748b"><i class="fas fa-ghost"></i> Headless</span>' : '<span style="color: #0eb0f2"><i class="fas fa-desktop"></i> GUI Terlihat</span>'}</td></tr><tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 4px 0; color: #64748b; font-weight: 500;">Filter Tanggal</td><td style="padding: 4px 0; text-align: right; color: #0f172a; font-weight: 600;">${settings.date ? settings.date.split("-").reverse().join("/") : '<span style="color: #94a3b8">Hari Ini</span>'}</td></tr><tr><td style="padding: 4px 0; color: #64748b; font-weight: 500;">Jeda Antar Akun</td><td style="padding: 4px 0; text-align: right; color: #0f172a; font-weight: 600;">${settings.delay} detik</td></tr></table></div>`,
    "Konfirmasi Otomasi",
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
    const statusBadge = document.getElementById(`status-badge-${account.id}`);
    const progressBar = document.getElementById(`progress-${account.id}`);
    const errorMsg = document.getElementById(`error-msg-${account.id}`);

    if (statusBadge) {
      statusBadge.textContent = "Menunggu";
      statusBadge.className = "text-xs font-medium px-2 py-1 rounded bg-slate-100 text-slate-500 shrink-0";
      statusBadge.innerHTML = "Menunggu";
    }
    if (errorMsg) {
      errorMsg.textContent = "";
      errorMsg.className = "text-[11px] text-right hidden";
    }
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

  // Handle custom messages
  if (status.startsWith("done|")) {
    statusText = status.split("|")[1];
    status = "done"; // Normalize status for styling
  } else if (status.startsWith("error|")) {
    statusText = status.split("|")[1];
    status = "error"; // Normalize status for styling
  } else {
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
        statusText = "Selesai";
        break;
      case "error":
        statusText = "Gagal";
        break;
      default:
        statusText = "Menunggu";
    }
  }

  // Update Status Badge & Error Message on Dashboard
  const statusBadge = document.getElementById(`status-badge-${accountId}`);
  const errorMsgDiv = document.getElementById(`error-msg-${accountId}`);

  if (statusBadge) {
    // Reset classes
    statusBadge.className = "text-xs font-medium px-2 py-1 rounded shrink-0";

    if (status === "processing") {
      statusBadge.textContent = "Memproses...";
      statusBadge.classList.add("bg-blue-100", "text-blue-600");
      statusBadge.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Proses';
    } else if (status === "done") {
      statusBadge.textContent = "Berhasil";
      statusBadge.classList.add("bg-green-100", "text-green-600");
      statusBadge.innerHTML = '<i class="fas fa-check mr-1"></i> Berhasil';
    } else if (status === "error") {
      statusBadge.textContent = "Gagal";
      statusBadge.classList.add("bg-red-100", "text-red-600");
      statusBadge.innerHTML = '<i class="fas fa-times mr-1"></i> Gagal';
    } else {
      statusBadge.textContent = "Menunggu";
      statusBadge.classList.add("bg-slate-100", "text-slate-500");
    }
  }

  if (errorMsgDiv) {
    // Reset base classes but keep layout
    errorMsgDiv.className = "text-[11px] text-right";

    if (status === "error") {
      // Only show message if it's not generic "Gagal"
      if (statusText && statusText !== "Gagal" && statusText !== "error") {
        errorMsgDiv.textContent = statusText;
        errorMsgDiv.classList.add("text-red-500");

        // Customize error message based on content
        if (statusText.includes("Login gagal")) {
          errorMsgDiv.innerHTML = 'Login Gagal <i class="fas fa-key ml-1"></i>';
        } else if (statusText.includes("koneksi")) {
          errorMsgDiv.innerHTML = 'Masalah Koneksi <i class="fas fa-wifi ml-1"></i>';
        } else if (statusText.includes("browser")) {
          errorMsgDiv.innerHTML = 'Gagal Browser <i class="fas fa-window-close ml-1"></i>';
        }
      } else {
        errorMsgDiv.classList.add("hidden");
      }

    } else if (status === "done") {
      // Show success details if available (e.g. "Stok: 10...")
      if (statusText.includes("Stok")) {
        errorMsgDiv.innerHTML = statusText;
        errorMsgDiv.classList.add("text-slate-500", "font-mono");
      } else {
        errorMsgDiv.classList.add("hidden");
      }
    } else {
      errorMsgDiv.classList.add("hidden");
    }
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
    logMessage("Memulai export ke CSV...", "info");
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
    console.error("Error downloading CSV:", error);
    logMessage("Gagal export ke CSV", "error");
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
          type: "text/csv",
        });

        if ("showSaveFilePicker" in window) {
          try {
            const handle = await window.showSaveFilePicker({
              suggestedName: result.filename,
              types: [
                {
                  description: "CSV Files",
                  accept: {
                    "text/csv": [".csv"],
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
      updateErrorTracking(metrics.errors, metrics.failed_accounts_detail || []);
    }

    // Update Business Metrics (NEW)
    const totalSalesEl = document.getElementById("metric-total-sales");
    const totalStockEl = document.getElementById("metric-total-stock");

    if (metrics.business_metrics) {
      if (totalSalesEl)
        totalSalesEl.textContent =
          metrics.business_metrics.total_penjualan || 0;
      if (totalStockEl)
        totalStockEl.textContent = metrics.business_metrics.total_stok || 0;
    }
  } catch (error) {
    console.error("Error updating dashboard metrics:", error);
  }
}

function updateErrorTracking(errors, failedAccountsDetail) {
  const errorTracking = document.getElementById("error-tracking");
  const errorList = document.getElementById("error-list");

  if (!errorTracking || !errorList) return;

  // Show error tracking section if there are errors
  const totalErrors = Object.values(errors).reduce((a, b) => a + b, 0);
  if (totalErrors > 0) {
    errorTracking.style.display = "block";

    // Group failed accounts by error type
    const accountsByErrorType = {};
    failedAccountsDetail.forEach((acc) => {
      const errorType = acc.error_type || "unknown";
      if (!accountsByErrorType[errorType]) {
        accountsByErrorType[errorType] = [];
      }
      accountsByErrorType[errorType].push(acc.nama);
    });

    // Build error list with account names
    const errorItems = Object.entries(errors)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5) // Top 5 errors
      .map(
        ([type, count]) => {
          const accountNames = accountsByErrorType[type] || [];
          const accountNamesHtml = accountNames.length > 0
            ? `<div style="margin-top: 0.5rem; padding-left: 1rem; font-size: 0.8rem; color: var(--text-muted);">
                 ${accountNames.map(name => `<div style="padding: 0.25rem 0;">• ${name}</div>`).join("")}
               </div>`
            : "";

          return `
                <div style="padding: 0.75rem; background: #f8fafc; border-radius: 6px; margin-bottom: 0.5rem; border-left: 3px solid var(--error);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: var(--text-main); font-size: 0.875rem; font-weight: 500;">${type.replace(/_/g, " ")}</span>
                        <span style="font-weight: 700; color: var(--error); font-size: 0.95rem;">${count}</span>
                    </div>
                    ${accountNamesHtml}
                </div>
            `;
        },
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
    about: {
      title: "Tentang SnapFlux",
      subtitle: "Informasi tentang aplikasi",
      icon: "fa-info-circle",
      breadcrumb: "Tentang",
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

// ============================================
// MOBILE RESPONSIVE FUNCTIONALITY
// ============================================

// Mobile menu toggle functionality
function initializeMobileMenu() {
  // Create mobile header if it doesn't exist
  const mainWrapper = document.querySelector(".main-wrapper");
  if (mainWrapper && !document.querySelector(".mobile-header")) {
    const mobileHeader = document.createElement("div");
    mobileHeader.className = "mobile-header";
    mobileHeader.innerHTML = `
      <button class="hamburger-menu" id="hamburgerMenu">
        <i class="fas fa-bars"></i>
      </button>
      <div class="mobile-logo">SnapFlux</div>
      <div style="width: 40px;"></div> <!-- Spacer for centering -->
    `;
    mainWrapper.insertBefore(mobileHeader, mainWrapper.firstChild);
  }

  // Create sidebar overlay if it doesn't exist
  if (!document.querySelector(".sidebar-overlay")) {
    const overlay = document.createElement("div");
    overlay.className = "sidebar-overlay";
    overlay.id = "sidebarOverlay";
    document.body.appendChild(overlay);
  }

  // Add event listeners
  const hamburgerMenu = document.getElementById("hamburgerMenu");
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.getElementById("sidebarOverlay");

  if (hamburgerMenu && sidebar && overlay) {
    // Function to close sidebar
    const closeSidebar = () => {
      sidebar.classList.remove("mobile-open");
      overlay.classList.remove("active");
      sidebar.style.transform = "";
      sidebar.style.transition = "";
      overlay.style.opacity = "";
      overlay.style.transition = "";
      const icon = hamburgerMenu.querySelector("i");
      if (icon) {
        icon.className = "fas fa-bars";
      }
      console.log("Sidebar closed");
    };

    // Function to open sidebar
    const openSidebar = () => {
      sidebar.classList.add("mobile-open");
      overlay.classList.add("active");
      const icon = hamburgerMenu.querySelector("i");
      if (icon) {
        icon.className = "fas fa-times";
      }
      console.log("Sidebar opened");
    };

    // Toggle sidebar on hamburger click
    hamburgerMenu.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      console.log("Hamburger clicked");

      if (sidebar.classList.contains("mobile-open")) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    // Close sidebar when overlay is clicked
    overlay.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log("Overlay clicked");
      closeSidebar();
    });

    // Close sidebar when nav item is clicked (mobile)
    const navItems = sidebar.querySelectorAll(".nav-item");
    navItems.forEach((item) => {
      item.addEventListener("click", () => {
        if (window.innerWidth <= 768) {
          console.log("Nav item clicked on mobile");
          setTimeout(closeSidebar, 100); // Small delay for better UX
        }
      });
    });

    // Make closeSidebar available globally for debugging
    window.closeMobileSidebar = closeSidebar;
    window.openMobileSidebar = openSidebar;
  }
}

// Handle window resize
function handleWindowResize() {
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const hamburgerMenu = document.getElementById("hamburgerMenu");

  if (window.innerWidth > 768) {
    // Desktop view - reset mobile classes and inline styles
    if (sidebar) {
      sidebar.classList.remove("mobile-open");
      sidebar.style.transform = "";
      sidebar.style.transition = "";
      sidebar.style.boxShadow = "";
    }
    if (overlay) {
      overlay.classList.remove("active");
      overlay.style.opacity = "";
      overlay.style.transition = "";
    }
    if (hamburgerMenu && hamburgerMenu.querySelector("i")) {
      hamburgerMenu.querySelector("i").className = "fas fa-bars";
    }
  }
}

// Touch gesture support for mobile
function initializeTouchGestures() {
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const hamburgerMenu = document.getElementById("hamburgerMenu");

  // Swipe gesture configuration
  const swipeConfig = {
    threshold: 100, // Minimum distance to trigger close (px)
    edgeThreshold: 50, // Edge detection for opening (px)
    velocityThreshold: 0.3, // Minimum velocity to trigger action
    maxAngle: 30, // Maximum angle from horizontal (degrees)
    closeThreshold: 100, // Distance to close sidebar (px)
    openThreshold: 80, // Distance to open sidebar (px)
  };

  let startX = 0;
  let startY = 0;
  let currentX = 0;
  let currentY = 0;
  let isDragging = false;
  let isSidebarDrag = false;
  let startTime = 0;
  let isScrolling = null;

  // Touch events for swipe gestures on sidebar
  if (sidebar) {
    sidebar.addEventListener(
      "touchstart",
      (e) => {
        if (
          window.innerWidth <= 768 &&
          sidebar.classList.contains("mobile-open")
        ) {
          startX = e.touches[0].clientX;
          startY = e.touches[0].clientY;
          currentX = startX;
          currentY = startY;
          startTime = Date.now();
          isDragging = true;
          isSidebarDrag = true;
          isScrolling = null;

          // Add visual feedback
          sidebar.classList.add("swiping");
          sidebar.style.boxShadow = "0 0 30px rgba(0, 0, 0, 0.3)";
        }
      },
      { passive: true },
    );

    sidebar.addEventListener(
      "touchmove",
      (e) => {
        if (!isDragging || !isSidebarDrag || window.innerWidth > 768) return;

        currentX = e.touches[0].clientX;
        currentY = e.touches[0].clientY;
        const diffX = currentX - startX;
        const diffY = currentY - startY;
        const absDiffX = Math.abs(diffX);
        const absDiffY = Math.abs(diffY);

        // Determine scroll direction on first move
        if (isScrolling === null && absDiffX > 2 && absDiffY > 2) {
          isScrolling = absDiffY > absDiffX;
        }

        // If user is scrolling vertically, don't handle swipe
        if (isScrolling) {
          return;
        }

        // Only process horizontal swipe (not vertical scroll)
        if (absDiffX > absDiffY && absDiffX > 10) {
          // Swipe left to close sidebar
          if (diffX < 0) {
            // Prevent default to stop scrolling
            e.preventDefault();

            // Calculate transform based on swipe distance
            const translateX = Math.max(diffX, -280); // Max 280px (sidebar width)
            sidebar.style.transform = `translateX(${translateX}px)`;
            sidebar.style.transition = "none";

            // Adjust overlay opacity
            const opacity = Math.max(0, 1 + diffX / 280);
            overlay.style.opacity = opacity;
            overlay.style.transition = "none";

            // Visual feedback: adjust shadow based on swipe progress
            const shadowIntensity = Math.max(0, 1 + diffX / 280);
            sidebar.style.boxShadow = `0 0 ${30 * shadowIntensity}px rgba(0, 0, 0, ${0.3 * shadowIntensity})`;

            // Haptic feedback at threshold
            if (Math.abs(diffX) > 100 && Math.abs(diffX) < 105) {
              if (navigator.vibrate) {
                navigator.vibrate(10); // Short vibration
              }
            }
          }
        }
      },
      { passive: false },
    );

    sidebar.addEventListener(
      "touchend",
      (e) => {
        if (!isDragging || !isSidebarDrag) return;

        const diffX = currentX - startX;
        const diffY = currentY - startY;
        const absDiffX = Math.abs(diffX);
        const duration = Date.now() - startTime;
        const velocity = duration > 0 ? absDiffX / duration : 0;

        // Remove swiping class
        sidebar.classList.remove("swiping");

        // Reset transition
        sidebar.style.transition = "transform 0.3s ease, box-shadow 0.3s ease";
        overlay.style.transition = "opacity 0.3s ease";

        // Determine if should close based on distance or velocity
        const shouldClose =
          diffX < -swipeConfig.closeThreshold ||
          (diffX < -30 && velocity > swipeConfig.velocityThreshold);

        // If swiped enough to the left or fast swipe, close sidebar
        if (shouldClose && !isScrolling) {
          // Haptic feedback for close action
          if (navigator.vibrate) {
            navigator.vibrate(20); // Slightly longer vibration for action
          }

          sidebar.classList.remove("mobile-open");
          overlay.classList.remove("active");
          if (hamburgerMenu && hamburgerMenu.querySelector("i")) {
            hamburgerMenu.querySelector("i").className = "fas fa-bars";
          }
          sidebar.style.transform = "";
          overlay.style.opacity = "";
          sidebar.style.boxShadow = "";

          console.log("Sidebar closed via swipe");
        } else {
          // Snap back to open position with haptic feedback
          if (navigator.vibrate) {
            navigator.vibrate(5); // Very short vibration for snap back
          }

          sidebar.style.transform = "translateX(0)";
          overlay.style.opacity = "1";
          sidebar.style.boxShadow = "0 0 30px rgba(0, 0, 0, 0.3)";

          // Reset box shadow after animation
          setTimeout(() => {
            sidebar.style.boxShadow = "";
          }, 300);
        }

        isDragging = false;
        isSidebarDrag = false;
        startX = 0;
        currentX = 0;
        startY = 0;
        currentY = 0;
      },
      { passive: true },
    );
  }

  // Touch events for swipe gestures on document (open sidebar)
  document.addEventListener(
    "touchstart",
    (e) => {
      if (window.innerWidth <= 768 && !sidebar.contains(e.target)) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isDragging = true;
        isSidebarDrag = false;
      }
    },
    { passive: true },
  );

  document.addEventListener(
    "touchmove",
    (e) => {
      if (!isDragging || isSidebarDrag || window.innerWidth > 768) return;

      currentX = e.touches[0].clientX;
      currentY = e.touches[0].clientY;
      const diffX = currentX - startX;
      const diffY = Math.abs(currentY - startY);

      // Only process horizontal swipe from left edge
      if (Math.abs(diffX) > diffY && Math.abs(diffX) > 10) {
        // Swipe right to open sidebar (from left edge)
        if (
          startX < 50 &&
          diffX > 80 &&
          !sidebar.classList.contains("mobile-open")
        ) {
          // Haptic feedback for opening
          if (navigator.vibrate) {
            navigator.vibrate(15);
          }

          sidebar.classList.add("mobile-open");
          overlay.classList.add("active");
          if (hamburgerMenu && hamburgerMenu.querySelector("i")) {
            hamburgerMenu.querySelector("i").className = "fas fa-times";
          }

          console.log("Sidebar opened via swipe");
        }
      }
    },
    { passive: true },
  );

  document.addEventListener(
    "touchend",
    () => {
      if (!isSidebarDrag) {
        isDragging = false;
        startX = 0;
        currentX = 0;
        startY = 0;
        currentY = 0;
      }
    },
    { passive: true },
  );

  // Prevent body scroll when sidebar is open on mobile
  if (sidebar && overlay) {
    const preventBodyScroll = () => {
      if (sidebar.classList.contains("mobile-open")) {
        document.body.style.overflow = "hidden";
        document.body.style.position = "fixed";
        document.body.style.width = "100%";
      } else {
        document.body.style.overflow = "";
        document.body.style.position = "";
        document.body.style.width = "";
      }
    };

    // Create observer to watch sidebar class changes
    const observer = new MutationObserver(preventBodyScroll);
    observer.observe(sidebar, {
      attributes: true,
      attributeFilter: ["class"],
    });

    // Initial check
    preventBodyScroll();
  }

  console.log("Touch gestures initialized with swipe-to-close support");
}

// Optimize form inputs for mobile
function optimizeForMobile() {
  // Add viewport meta tag if it doesn't exist
  if (!document.querySelector('meta[name="viewport"]')) {
    const viewport = document.createElement("meta");
    viewport.name = "viewport";
    viewport.content =
      "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no";
    document.head.appendChild(viewport);
  }

  // Prevent zoom on form inputs for iOS
  const inputs = document.querySelectorAll("input, select, textarea");
  inputs.forEach((input) => {
    if (window.innerWidth <= 768) {
      // Set font-size to prevent zoom on iOS
      if (getComputedStyle(input).fontSize < "16px") {
        input.style.fontSize = "16px";
      }
    }
  });

  // Optimize table display on mobile
  const tables = document.querySelectorAll("table");
  tables.forEach((table) => {
    if (!table.parentElement.classList.contains("table-responsive")) {
      const wrapper = document.createElement("div");
      wrapper.className = "table-responsive";
      wrapper.style.overflowX = "auto";
      wrapper.style.webkitOverflowScrolling = "touch";
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
  });
}

// Initialize all mobile functionality
function initializeMobileResponsive() {
  // Only initialize if we're in a browser environment
  if (typeof window !== "undefined") {
    console.log("=== MOBILE INITIALIZATION START ===");
    console.log("Window width:", window.innerWidth);
    console.log("Is mobile:", DeviceDetection.isMobile());

    // Force mobile menu initialization
    try {
      initializeMobileMenu();
      console.log("✓ Mobile menu initialized");
    } catch (error) {
      console.error("✗ Mobile menu initialization failed:", error);
    }

    // Force touch gestures initialization
    try {
      initializeTouchGestures();
      console.log("✓ Touch gestures initialized");
    } catch (error) {
      console.error("✗ Touch gestures initialization failed:", error);
    }

    // Force mobile optimization
    try {
      optimizeForMobile();
      console.log("✓ Mobile optimization applied");
    } catch (error) {
      console.error("✗ Mobile optimization failed:", error);
    }

    // Add resize listener
    window.addEventListener("resize", handleWindowResize);

    // Handle orientation change
    window.addEventListener("orientationchange", () => {
      setTimeout(() => {
        handleWindowResize();
        optimizeForMobile();
      }, 100);
    });

    // Force check sidebar state on mobile
    if (DeviceDetection.isMobile()) {
      setTimeout(() => {
        const sidebar = document.querySelector(".sidebar");
        const overlay = document.getElementById("sidebarOverlay");
        console.log("Sidebar exists:", !!sidebar);
        console.log("Overlay exists:", !!overlay);
        console.log(
          "Sidebar has mobile-open class:",
          sidebar?.classList.contains("mobile-open"),
        );

        // Ensure sidebar is hidden initially
        if (sidebar && !sidebar.classList.contains("mobile-open")) {
          sidebar.style.transform = "translateX(-100%)";
          sidebar.style.webkitTransform = "translateX(-100%)";
          console.log("✓ Sidebar forced to hidden state");
        }
      }, 500);
    }

    console.log("=== MOBILE INITIALIZATION COMPLETE ===");
  }
}

// ============================================
// VIEWPORT HEIGHT FIX FOR MOBILE BROWSERS
// ============================================

// Fix viewport height issues on mobile browsers
function fixMobileViewportHeight() {
  // Get the actual viewport height
  let vh = window.innerHeight * 0.01;

  // Set the CSS custom property
  document.documentElement.style.setProperty("--vh", `${vh}px`);

  // Update on resize and orientation change
  const updateVH = () => {
    vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty("--vh", `${vh}px`);
  };

  window.addEventListener("resize", updateVH);
  window.addEventListener("orientationchange", () => {
    setTimeout(updateVH, 100); // Delay to get correct viewport after orientation change
  });

  // Also update when virtual keyboard appears/disappears on mobile
  if (DeviceDetection && DeviceDetection.isMobile()) {
    window.addEventListener("focusin", updateVH);
    window.addEventListener("focusout", updateVH);

    // Handle virtual keyboard for input fields
    handleVirtualKeyboard();
  }

  console.log("Mobile viewport height fixed:", vh + "px");
}

// Force update sidebar height for mobile devices
function forceSidebarHeightUpdate() {
  const sidebar = document.querySelector(".sidebar");
  if (!sidebar || !DeviceDetection.isMobile()) return;

  // Get current viewport height
  const viewportHeight = window.innerHeight;

  // Force height update
  sidebar.style.height = viewportHeight + "px";
  sidebar.style.minHeight = viewportHeight + "px";
  sidebar.style.maxHeight = viewportHeight + "px";

  // Also update with CSS custom properties
  const vh = viewportHeight * 0.01;
  document.documentElement.style.setProperty("--vh", `${vh}px`);

  // Apply CSS fallbacks
  sidebar.style.setProperty("height", "100vh", "important");
  sidebar.style.setProperty("height", "100dvh", "important");
  sidebar.style.setProperty(
    "height",
    "calc(var(--vh, 1vh) * 100)",
    "important",
  );

  console.log("Forced sidebar height update:", viewportHeight + "px");
}

// Handle virtual keyboard appearance/disappearance
function handleVirtualKeyboard() {
  let initialViewportHeight = window.innerHeight;

  const adjustSidebarForKeyboard = () => {
    const currentHeight = window.innerHeight;
    const heightDifference = initialViewportHeight - currentHeight;
    const sidebar = document.querySelector(".sidebar");

    if (sidebar) {
      if (heightDifference > 150) {
        // Keyboard is likely open
        sidebar.style.height = currentHeight + "px";
        sidebar.classList.add("keyboard-open");
      } else {
        // Keyboard is likely closed
        sidebar.style.height = "100vh";
        sidebar.style.height = "100dvh";
        sidebar.style.height = "calc(var(--vh, 1vh) * 100)";
        sidebar.classList.remove("keyboard-open");
      }
    }
  };

  // Listen for viewport height changes
  window.addEventListener("resize", adjustSidebarForKeyboard);

  // Listen for input focus/blur events
  document.addEventListener("focusin", (e) => {
    if (e.target.matches("input, textarea, select")) {
      setTimeout(adjustSidebarForKeyboard, 300); // Delay for keyboard animation
    }
  });

  document.addEventListener("focusout", (e) => {
    if (e.target.matches("input, textarea, select")) {
      setTimeout(adjustSidebarForKeyboard, 300); // Delay for keyboard animation
    }
  });

  // Handle orientation change
  window.addEventListener("orientationchange", () => {
    setTimeout(() => {
      initialViewportHeight = window.innerHeight;
      adjustSidebarForKeyboard();
    }, 500);
  });
}

// ============================================
// DEVICE DETECTION AND PERFORMANCE HELPERS
// ============================================

// Device detection utilities
const DeviceDetection = {
  isMobile: () => window.innerWidth <= 768,
  isTablet: () => window.innerWidth > 768 && window.innerWidth <= 1024,
  isDesktop: () => window.innerWidth > 1024,
  isTouchDevice: () => "ontouchstart" in window || navigator.maxTouchPoints > 0,
  isIOS: () => /iPad|iPhone|iPod/.test(navigator.userAgent),
  isAndroid: () => /Android/.test(navigator.userAgent),
  getOrientation: () =>
    window.innerHeight > window.innerWidth ? "portrait" : "landscape",
};

// Performance optimization helpers
const PerformanceOptimizer = {
  // Debounce function for resize events
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Throttle function for scroll events
  throttle: (func, limit) => {
    let inThrottle;
    return function () {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  },

  // Lazy loading for heavy content
  observeElements: (selector, callback, options = {}) => {
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              callback(entry.target);
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.1, ...options },
      );

      document.querySelectorAll(selector).forEach((el) => observer.observe(el));
    } else {
      // Fallback for older browsers
      document.querySelectorAll(selector).forEach(callback);
    }
  },
};

// Enhanced mobile menu with performance optimization
function initializeEnhancedMobileMenu() {
  const debouncedResize = PerformanceOptimizer.debounce(
    handleWindowResize,
    250,
  );

  initializeMobileMenu();

  // Optimized resize handler
  window.removeEventListener("resize", handleWindowResize);
  window.addEventListener("resize", debouncedResize);

  // Force sidebar height update on mobile
  if (DeviceDetection.isMobile()) {
    forceSidebarHeightUpdate();

    // Update on resize and orientation change
    window.addEventListener("resize", forceSidebarHeightUpdate);
    window.addEventListener("orientationchange", () => {
      setTimeout(forceSidebarHeightUpdate, 100);
    });
  }

  // Force sidebar height recalculation on mobile
  if (DeviceDetection.isMobile()) {
    const sidebar = document.querySelector(".sidebar");
    if (sidebar) {
      // Ensure sidebar spans full height
      sidebar.style.height = "100vh";
      sidebar.style.height = "100dvh";
      sidebar.style.height = "calc(var(--vh, 1vh) * 100)";

      // Add touch event listeners for better mobile interaction
      sidebar.addEventListener("touchstart", (e) => {
        e.stopPropagation();
      });

      sidebar.addEventListener("touchmove", (e) => {
        e.stopPropagation();
      });
    }
  }

  // Add visual feedback for touch interactions
  const touchElements = document.querySelectorAll(
    ".btn, .nav-item, .hamburger-menu",
  );
  touchElements.forEach((element) => {
    if (DeviceDetection.isTouchDevice()) {
      element.style.cursor = "pointer";
      element.addEventListener(
        "touchstart",
        function () {
          this.style.opacity = "0.7";
        },
        { passive: true },
      );

      element.addEventListener(
        "touchend",
        function () {
          setTimeout(() => {
            this.style.opacity = "";
          }, 150);
        },
        { passive: true },
      );
    }
  });
}

// Adaptive loading based on device capabilities
function adaptiveContentLoading() {
  // Reduce animations on lower-end devices
  if (DeviceDetection.isMobile() && navigator.hardwareConcurrency <= 2) {
    document.documentElement.style.setProperty("--animation-duration", "0.1s");
    console.log("Reduced animations for low-end device");
  }

  // Optimize images for mobile
  const images = document.querySelectorAll("img");
  images.forEach((img) => {
    if (DeviceDetection.isMobile()) {
      img.loading = "lazy";
      if (img.src.includes(".png") || img.src.includes(".jpg")) {
        // Add WebP support detection if needed
        const canvas = document.createElement("canvas");
        if (canvas.toDataURL("image/webp").indexOf("data:image/webp") === 0) {
          img.style.imageRendering = "optimizeQuality";
        }
      }
    }
  });
}

// Network-aware content loading
function networkAwareLoading() {
  if ("connection" in navigator) {
    const connection = navigator.connection;
    const isSlow =
      connection.effectiveType === "slow-2g" ||
      connection.effectiveType === "2g" ||
      connection.saveData;

    if (isSlow) {
      // Disable heavy animations
      document.documentElement.style.setProperty("--shadow-md", "none");
      document.documentElement.style.setProperty("--shadow-lg", "none");
      console.log("Optimized for slow network");
    }
  }
}

// Initialize when DOM is loaded
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    console.log("=== DOM CONTENT LOADED ===");
    console.log("Starting initialization...");

    try {
      fixMobileViewportHeight();
      console.log("✓ Viewport height fixed");
    } catch (error) {
      console.error("✗ Viewport height fix failed:", error);
    }

    try {
      initializeEnhancedMobileMenu();
      console.log("✓ Enhanced mobile menu initialized");
    } catch (error) {
      console.error("✗ Enhanced mobile menu failed:", error);
    }

    try {
      initializeTouchGestures();
      console.log("✓ Touch gestures initialized");
    } catch (error) {
      console.error("✗ Touch gestures failed:", error);
    }

    try {
      optimizeForMobile();
      console.log("✓ Mobile optimization applied");
    } catch (error) {
      console.error("✗ Mobile optimization failed:", error);
    }

    try {
      adaptiveContentLoading();
      console.log("✓ Adaptive content loading applied");
    } catch (error) {
      console.error("✗ Adaptive content loading failed:", error);
    }

    try {
      networkAwareLoading();
      console.log("✓ Network aware loading applied");
    } catch (error) {
      console.error("✗ Network aware loading failed:", error);
    }

    // Force sidebar height update for mobile
    if (DeviceDetection.isMobile()) {
      setTimeout(() => {
        try {
          forceSidebarHeightUpdate();
          console.log("✓ Sidebar height updated");
        } catch (error) {
          console.error("✗ Sidebar height update failed:", error);
        }
      }, 100);
    }

    // Initialize overflow fixes for mobile
    setTimeout(() => {
      try {
        initializeOverflowFixes();
        console.log("✓ Overflow fixes initialized");
      } catch (error) {
        console.error("✗ Overflow fixes failed:", error);
      }
    }, 200);

    console.log("Enhanced mobile responsive functionality initialized");
    console.log("Device info:", {
      mobile: DeviceDetection.isMobile(),
      tablet: DeviceDetection.isTablet(),
      touch: DeviceDetection.isTouchDevice(),
      orientation: DeviceDetection.getOrientation(),
      screenWidth: window.innerWidth,
      screenHeight: window.innerHeight,
    });

    console.log("=== INITIALIZATION COMPLETE ===");
  });
} else {
  console.log("=== DOM ALREADY LOADED ===");
  console.log("Starting immediate initialization...");

  fixMobileViewportHeight();
  initializeEnhancedMobileMenu();
  initializeTouchGestures();
  optimizeForMobile();
  adaptiveContentLoading();
  networkAwareLoading();

  // Force sidebar height update for mobile
  if (DeviceDetection.isMobile()) {
    setTimeout(forceSidebarHeightUpdate, 100);
  }

  // Initialize overflow fixes for mobile
  setTimeout(() => {
    initializeOverflowFixes();
  }, 200);

  console.log("=== IMMEDIATE INITIALIZATION COMPLETE ===");
}

// ============================================
// OVERFLOW DETECTION AND FIX
// ============================================

// Detect and fix overflowing elements on mobile
function detectAndFixOverflow() {
  if (!DeviceDetection.isMobile()) return;

  // Get all potentially overflowing elements
  const elements = document.querySelectorAll(
    ".card, .stat-card, .btn, p, span, h1, h2, h3, h4, .account-item, .log-message",
  );

  elements.forEach((element) => {
    // Check if element is overflowing
    if (element.scrollWidth > element.clientWidth) {
      // Apply fix
      element.style.wordWrap = "break-word";
      element.style.overflowWrap = "break-word";
      element.style.wordBreak = "break-word";
      element.style.maxWidth = "100%";
      element.style.boxSizing = "border-box";
      element.style.overflow = "hidden";
    }
  });

  // Fix container overflow
  const containers = document.querySelectorAll(".container, .main-wrapper");
  containers.forEach((container) => {
    container.style.overflowX = "hidden";
    container.style.maxWidth = "100vw";
  });

  console.log("Overflow detection and fix applied");
}

// Apply text wrapping to all elements
function applyTextWrapping() {
  if (!DeviceDetection.isMobile()) return;

  const textElements = document.querySelectorAll(
    "p, span, h1, h2, h3, h4, h5, h6, div, label, button, a",
  );

  textElements.forEach((element) => {
    element.style.wordWrap = "break-word";
    element.style.overflowWrap = "break-word";
    element.style.maxWidth = "100%";
    element.style.boxSizing = "border-box";
  });

  console.log("Text wrapping applied to all elements");
}

// Monitor and fix dynamic content
function monitorDynamicContent() {
  if (!DeviceDetection.isMobile()) return;

  // Create observer to watch for DOM changes
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length) {
        setTimeout(() => {
          detectAndFixOverflow();
          applyTextWrapping();
        }, 100);
      }
    });
  });

  // Observe the entire document
  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  console.log("Dynamic content monitoring started");
}

// Initialize all overflow fixes
function initializeOverflowFixes() {
  if (DeviceDetection.isMobile()) {
    // Initial fix
    detectAndFixOverflow();
    applyTextWrapping();

    // Monitor dynamic content
    monitorDynamicContent();

    // Reapply on window resize
    const debouncedFix = PerformanceOptimizer.debounce(() => {
      detectAndFixOverflow();
      applyTextWrapping();
    }, 250);

    window.addEventListener("resize", debouncedFix);
    window.addEventListener("orientationchange", () => {
      setTimeout(() => {
        detectAndFixOverflow();
        applyTextWrapping();
      }, 300);
    });

    console.log("Overflow fixes initialized");
  }
}
