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
function showAlert(message, type = 'info') {
  const icons = {
    'info': 'info',
    'success': 'success',
    'error': 'error',
    'warning': 'warning'
  };

  return Swal.fire({
    icon: icons[type] || 'info',
    title: type === 'error' ? 'Oops...' : type === 'success' ? 'Berhasil!' : 'Informasi',
    text: message,
    confirmButtonText: 'OK',
    confirmButtonColor: '#4a70a9',
    background: '#ffffff',
    customClass: {
      popup: 'rounded-lg',
      confirmButton: 'btn btn-primary'
    }
  });
}

// Modern confirm using SweetAlert2
async function showConfirm(message, title = 'Konfirmasi') {
  const result = await Swal.fire({
    title: title,
    html: message.replace(/\n/g, '<br>'),
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Ya, Lanjutkan',
    cancelButtonText: 'Batal',
    confirmButtonColor: '#4a70a9',
    cancelButtonColor: '#6b7280',
    reverseButtons: true,
    customClass: {
      popup: 'rounded-lg',
      confirmButton: 'btn btn-primary',
      cancelButton: 'btn btn-secondary'
    }
  });

  return result.isConfirmed;
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener("DOMContentLoaded", async () => {
  console.log("🚀 Initializing SnapFlux Automation...");

  // Initialize default values first
  initializeDefaults();

  // Load available Excel files
  await loadExcelFiles();

  // Make sure all functions are accessible globally
  window.startAutomation = startAutomation;
  window.pauseAutomation = pauseAutomation;
  window.stopAutomation = stopAutomation;
  window.loadAccounts = loadAccounts;
  window.toggleSelectAll = toggleSelectAll;
  window.showPage = showPage;
  window.toggleHeadless = toggleHeadless;
  window.downloadExcel = downloadExcel;
  window.openResultsFolder = openResultsFolder;
  window.clearLog = clearLog;
  window.showProcessingView = showProcessingView;
  window.hideProcessingView = hideProcessingView;
  window.updateProcessingView = updateProcessingView;

  console.log("✅ All functions registered globally");
  logMessage("✅ Aplikasi siap digunakan", "success");
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

function showPage(pageName) {
  // Hide all pages
  document.querySelectorAll(".page-section").forEach((section) => {
    section.classList.remove("active");
  });

  // Remove active from all nav items
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.remove("active");
  });

  // Show selected page
  const pageElement = document.getElementById(pageName + "-page");
  if (pageElement) {
    pageElement.classList.add("active");
  }

  // Set active nav item - find nav item that calls this page
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach((item) => {
    const onclick = item.getAttribute("onclick");
    if (onclick && onclick.includes(`'${pageName}'`)) {
      item.classList.add("active");
    }
  });

  // Update page title in header
  const pageTitles = {
    dashboard: "Dashboard",
    automation: "Automation Control",
    results: "Export Results",
    settings: "Settings",
  };
  const pageTitleElement = document.getElementById("page-title");
  if (pageTitleElement && pageTitles[pageName]) {
    pageTitleElement.textContent = pageTitles[pageName];
  }
}

// ============================================
// EXCEL FILE MANAGEMENT
// ============================================

async function loadExcelFiles() {
  try {
    const result = await eel.get_available_excel_files()();
    const select = document.getElementById("excel-file-select");

    if (result.success && result.files.length > 0) {
      select.innerHTML = '<option value="">-- Pilih File --</option>';
      result.files.forEach((file) => {
        const option = document.createElement("option");
        option.value = file;
        option.textContent = file;
        select.appendChild(option);
      });
      logMessage(`📂 Ditemukan ${result.files.length} file Excel`, "info");
    } else {
      select.innerHTML = '<option value="">-- Tidak ada file --</option>';
      logMessage("⚠️ Tidak ada file Excel di folder akun/", "warning");
    }
  } catch (error) {
    console.error("Error loading Excel files:", error);
    logMessage("❌ Gagal memuat daftar file Excel", "error");
  }
}

async function loadAccounts() {
  const select = document.getElementById("excel-file-select");
  const fileName = select.value;

  if (!fileName) {
    showAlert("Pilih file Excel terlebih dahulu!", 'warning');
    return;
  }

  logMessage(`📥 Memuat akun dari ${fileName}...`, "info");

  try {
    const result = await eel.load_accounts_from_file(fileName)();

    if (result.success) {
      accounts = result.accounts;
      renderAccounts();
      updateStatistics();

      // Show account info
      document.getElementById("account-info").classList.remove("hidden");
      document.getElementById("account-count").textContent = result.count;

      logMessage(`✅ ${result.message}`, "success");
    } else {
      showAlert(result.message, 'error');
      logMessage(`❌ ${result.message}`, "error");
    }
  } catch (error) {
    console.error("Error loading accounts:", error);
    logMessage("❌ Gagal memuat akun dari file", "error");
    showAlert("Terjadi kesalahan saat memuat akun: " + error, 'error');
  }
}

// ============================================
// ACCOUNT RENDERING
// ============================================

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
    accountDiv.className = "account-list-item"; // Changed class

    accountDiv.innerHTML = `
            <label class="flex items-center gap-3 cursor-pointer w-full">
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
                
                <div class="flex items-center gap-2 ml-auto">
                     <div id="indicator-${account.id}" class="account-status-indicator"></div>
                     <span id="status-${account.id}" class="text-xs font-bold text-muted" style="min-width: 60px; text-align: right;">Menunggu</span>
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
  console.log("Accounts loaded:", accounts.length);
  console.log("Headless enabled:", headlessEnabled);

  // Validasi
  const selectedAccounts = accounts.filter((acc) => {
    const checkbox = document.getElementById(`check-${acc.id}`);
    return checkbox && checkbox.checked;
  });

  console.log("Selected accounts:", selectedAccounts.length);

  if (selectedAccounts.length === 0) {
    console.warn("⚠️ No accounts selected");
    showAlert("Pilih minimal 1 akun untuk diproses!", 'warning');
    return;
  }

  console.log("✅ Validation passed, getting settings...");

  // Get settings
  const settings = {
    headless: headlessEnabled,
    date: document.getElementById("date-filter").value || null,
    delay: parseFloat(document.getElementById("delay-input").value) || 2.0,
  };

  console.log("Settings:", settings);

  // Confirm
  const confirmStart = await showConfirm(
    `Mulai automation untuk <strong>${selectedAccounts.length} akun</strong>?<br><br>` +
    `<div style="text-align: left; display: inline-block;">` +
    `📋 <strong>Mode:</strong> ${settings.headless ? "Headless (Background)" : "GUI Visible"}<br>` +
    `📅 <strong>Tanggal:</strong> ${settings.date || "Tanpa filter"}<br>` +
    `⏱️ <strong>Delay:</strong> ${settings.delay} detik` +
    `</div>`,
    'Mulai Automation?'
  );

  if (!confirmStart) {
    console.log("❌ User cancelled");
    return;
  }

  console.log("✅ User confirmed, starting automation...");

  // Disable controls
  automationRunning = true;
  updateControlButtons();

  // Update status
  document.getElementById("status-text").textContent = "Running...";
  logMessage("🚀 Memulai automation...", "info");

  // Reset statistics
  resetAccountStatuses();

  // Show processing view with first account
  totalAccounts = selectedAccounts.length;
  currentAccountIndex = 1;

  // Reset progress to 0%
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
      firstAccount.username,
      1,
      totalAccounts,
      "⏳ Mempersiapkan proses...",
      false, // Don't update progress, let backend handle it
    );
  }

  showProcessingView();

  try {
    const result = await eel.start_automation(selectedAccounts, settings)();

    if (!result.success) {
      showAlert(result.message, 'error');
      logMessage(`❌ ${result.message}`, "error");
      automationRunning = false;
      updateControlButtons();
      hideProcessingView();
    }
  } catch (error) {
    console.error("Error starting automation:", error);
    logMessage("❌ Gagal memulai automation", "error");
    showAlert("Terjadi kesalahan: " + error, 'error');
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
        // Update sidebar button
        if (pauseBtn) {
          pauseBtn.innerHTML = '<i class="fas fa-play"></i> Resume';
        }
        // Update processing view button
        if (pauseBtnProcessing) {
          pauseBtnProcessing.innerHTML = '<i class="fas fa-play"></i> Resume';
          pauseBtnProcessing.classList.remove("btn-secondary");
          pauseBtnProcessing.classList.add("btn-success");
        }
        document.getElementById("status-text").textContent = "Paused";
      } else {
        // Update sidebar button
        if (pauseBtn) {
          pauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
        }
        // Update processing view button
        if (pauseBtnProcessing) {
          pauseBtnProcessing.innerHTML = '<i class="fas fa-pause"></i> Pause';
          pauseBtnProcessing.classList.remove("btn-success");
          pauseBtnProcessing.classList.add("btn-secondary");
        }
        document.getElementById("status-text").textContent = "Running...";
      }
    }
  } catch (error) {
    console.error("Error pausing automation:", error);
    showAlert("Terjadi kesalahan saat pause: " + error, 'error');
  }
}

async function stopAutomation() {
  const confirm = await showConfirm(
    "Automation yang sedang berjalan akan dihentikan.<br>Data yang sudah diproses akan tetap tersimpan.",
    "Hentikan Automation?"
  );
  if (!confirm) return;

  try {
    const result = await eel.stop_automation()();

    if (result.success) {
      automationRunning = false;
      updateControlButtons();
      document.getElementById("status-text").textContent = "Stopped";
      logMessage("⏹️ Automation dihentikan", "warning");

      // Hide processing view and show list view again
      hideProcessingView();
    }
  } catch (error) {
    console.error("Error stopping automation:", error);
    logMessage("❌ Gagal stop automation", "error");
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

    if (indicator) {
      indicator.className = "account-status-indicator";
    }

    if (progressBar) {
      progressBar.style.width = "0%";
    }
  });

  updateStatistics();
}

// ============================================
// CALLBACKS FROM PYTHON
// ============================================

eel.expose(update_account_status);
function update_account_status(accountId, status, progress) {
  console.log(
    `🔄 update_account_status called: Account ${accountId}, Status: ${status}, Progress: ${progress}%`,
  );

  const statusBadge = document.getElementById(`status-${accountId}`);
  const progressBar = document.getElementById(`progress-${accountId}`);
  const indicator = document.getElementById(`indicator-${accountId}`);
  const accountRow = document.getElementById(`account-${accountId}`);

  if (progressBar) {
    progressBar.style.width = `${progress}%`;
  }

  if (statusBadge && indicator) {
    let text, colorClass, statusText, indicatorClass;

    // Reset classes
    indicator.className = "account-status-indicator";

    switch (status) {
      case "processing":
        text = "Proses";
        colorClass = "text-indigo-500";
        indicatorClass = "processing";
        statusText = "🔄 Sedang login dan mengambil data...";
        break;
      case "login":
        text = "Login";
        colorClass = "text-indigo-500";
        indicatorClass = "processing";
        statusText = "🔐 Melakukan login ke akun...";
        break;
      case "fetching":
        text = "Fetching";
        colorClass = "text-indigo-500";
        indicatorClass = "processing";
        statusText = "📊 Mengambil data transaksi...";
        break;
      case "saving":
        text = "Saving";
        colorClass = "text-indigo-500";
        indicatorClass = "processing";
        statusText = "💾 Menyimpan data ke Excel...";
        break;
      case "done":
        text = "Selesai";
        colorClass = "text-green-500";
        indicatorClass = "done";
        statusText = "✅ Akun berhasil diproses!";
        break;
      case "error":
        text = "Gagal";
        colorClass = "text-red-500";
        indicatorClass = "error";
        statusText = "❌ Terjadi kesalahan saat memproses";
        break;
      default:
        text = "Menunggu";
        colorClass = "text-muted";
        indicatorClass = "";
        statusText = "⏳ Menunggu giliran proses...";
    }

    statusBadge.textContent = text;
    statusBadge.className = `text-xs font-bold ${colorClass}`;
    if (indicatorClass) indicator.classList.add(indicatorClass);

    // Update processing view for any status change
    const account = accounts.find((acc) => acc.id === accountId);
    if (account) {
      currentProcessingAccount = account;

      // Calculate correct index based on selected accounts
      const selectedAccounts = accounts.filter((acc) => {
        const cb = document.getElementById(`check-${acc.id}`);
        return cb && cb.checked;
      });
      currentAccountIndex =
        selectedAccounts.findIndex((acc) => acc.id === accountId) + 1;

      console.log(
        `📝 Updating processing view: ${account.name} (${currentAccountIndex}/${totalAccounts})`,
      );

      updateProcessingView(
        account.nama,
        account.username,
        currentAccountIndex,
        totalAccounts,
        statusText,
      );
    }
  }

  // Scroll to current account
  if (accountRow && status === "processing") {
    accountRow.scrollIntoView({ behavior: "smooth", block: "center" });
    // Highlight active card
    document.querySelectorAll('.account-card').forEach(c => c.classList.remove('selected'));
    accountRow.classList.add('selected');
  }

  updateStatistics();
}

eel.expose(update_overall_progress);
function update_overall_progress(current, total, percent) {
  console.log(
    `📊 update_overall_progress called: ${current}/${total} = ${percent}%`,
  );

  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");
  const progressPercent = document.getElementById("progress-percent");

  // Also update processing view progress
  const processingProgressFill = document.getElementById(
    "processing-progress-fill",
  );
  const processingPercent = document.getElementById("processing-percent");

  if (processingProgressFill) {
    processingProgressFill.style.width = `${percent}%`;
    console.log(`✅ Processing progress bar updated to ${percent}%`);
  }

  if (processingPercent) {
    processingPercent.textContent = `${Math.round(percent)}%`;
    console.log(
      `✅ Processing percent text updated to ${Math.round(percent)}%`,
    );
  }

  if (progressBar) {
    progressBar.style.width = `${percent}%`;
  }

  if (progressText) {
    progressText.textContent = `${current}/${total}`;
  }

  if (progressPercent) {
    progressPercent.textContent = `${percent}%`;
  }
}

eel.expose(log_message);
function logMessage(message, type = "info") {
  const logContainer = document.getElementById("log-container");
  const timestamp = new Date().toLocaleTimeString("id-ID");

  let color, icon, emoji;
  switch (type) {
    case "success":
      color = "#10b981";
      icon = "✓";
      emoji = "✅";
      break;
    case "error":
      color = "#ef4444";
      icon = "✗";
      emoji = "❌";
      break;
    case "warning":
      color = "#f59e0b";
      icon = "⚠";
      emoji = "⚠️";
      break;
    default:
      color = "#60a5fa";
      icon = "ℹ";
      emoji = "ℹ️";
  }

  const logEntry = document.createElement("p");
  logEntry.style.margin = "0.4rem 0";
  logEntry.style.paddingLeft = "0.5rem";
  logEntry.style.borderLeft = "2px solid transparent";
  logEntry.style.transition = "border-color 0.2s ease";

  logEntry.innerHTML = `<span style="color: #6b7280; font-weight: 500;">[${timestamp}]</span> <span style="color: ${color}; font-weight: 700; margin: 0 0.5rem;">${icon}</span> <span style="color: #e5e7eb;">${message}</span>`;

  logEntry.onmouseover = function () {
    this.style.borderLeftColor = "#4A70A9";
    this.style.backgroundColor = "rgba(74, 112, 169, 0.08)";
  };

  logEntry.onmouseout = function () {
    this.style.borderLeftColor = "transparent";
    this.style.backgroundColor = "transparent";
  };

  logContainer.appendChild(logEntry);

  // Auto scroll to bottom with smooth behavior
  logContainer.scrollTo({
    top: logContainer.scrollHeight,
    behavior: "smooth",
  });

  // Limit log entries to prevent memory issues
  if (logContainer.children.length > 500) {
    logContainer.removeChild(logContainer.firstChild);
  }
}

// ============================================
// PROCESSING VIEW FUNCTIONS
// ============================================

function showProcessingView() {
  const processingView = document.getElementById("processing-view");
  const accountsListView = document.getElementById("accounts-list-view");

  if (processingView && accountsListView) {
    processingView.classList.add("active");
    accountsListView.style.display = "none";
    console.log("✅ Processing view shown");
  }
}

function hideProcessingView() {
  const processingView = document.getElementById("processing-view");
  const accountsListView = document.getElementById("accounts-list-view");

  if (processingView && accountsListView) {
    processingView.classList.remove("active");
    accountsListView.style.display = "block";
    console.log("✅ Processing view hidden");
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
  // Update name
  const nameEl = document.getElementById("processing-name");
  if (nameEl) nameEl.textContent = name || "Memuat...";

  // Update username
  const usernameEl = document.getElementById("processing-username");
  if (usernameEl) usernameEl.textContent = username || "---";

  // Update counter
  const currentEl = document.getElementById("processing-current");
  const totalEl = document.getElementById("processing-total");
  if (currentEl) currentEl.textContent = current || 0;
  if (totalEl) totalEl.textContent = total || 0;

  // Update status text
  const statusEl = document.getElementById("processing-status");
  if (statusEl) {
    statusEl.innerHTML = `<span class="processing-spinner"></span><span style="margin-left: 0.5rem">${statusText}</span>`;
  }

  // Only update progress bar if explicitly requested (initial load)
  // Otherwise, let update_overall_progress handle it
  if (updateProgress) {
    const progress = total > 0 ? (current / total) * 100 : 0;
    const progressFill = document.getElementById("processing-progress-fill");
    const progressPercent = document.getElementById("processing-percent");

    if (progressFill) progressFill.style.width = `${progress}%`;
    if (progressPercent)
      progressPercent.textContent = `${Math.round(progress)}%`;
  }

  console.log(
    `📊 Processing: ${name} (${current}/${total}) - Status: ${statusText}`,
  );
}

eel.expose(automation_completed);
function automation_completed(successCount, totalCount) {
  console.log("=".repeat(60));
  console.log("🎉 automation_completed CALLED");
  console.log("   Success Count:", successCount);
  console.log("   Total Count:", totalCount);
  console.log("=".repeat(60));

  automationRunning = false;
  updateControlButtons();

  // Hide processing view and show list view again
  hideProcessingView();

  const statusText = document.getElementById("status-text");
  if (statusText) {
    statusText.textContent = "Completed";
    console.log("✅ Status text updated to 'Completed'");
  } else {
    console.error("❌ status-text element not found!");
  }

  logMessage(
    `🎉 Automation selesai! ${successCount}/${totalCount} akun berhasil`,
    "success",
  );

  // Show export card
  console.log("📊 About to call showExportCard with count:", successCount);
  try {
    showExportCard(successCount);
    console.log("✅ showExportCard called successfully");
  } catch (error) {
    console.error("❌ Error calling showExportCard:", error);
  }

  // Show notification
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification("SnapFlux Automation", {
      body: `Automation selesai! ${successCount}/${totalCount} akun berhasil diproses.`,
      icon: "/icon.png",
    });
    console.log("✅ Browser notification sent");
  }

  // Play sound (optional)
  try {
    const audio = new Audio(
      "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTUIGmi77eifTRALUKXh8LhjHAU7k9n0yHMpBSh+zPLaizsKFGS56+uoVRQKRp/f8L5sIQUsgs/y2Ik1CBlou+3pn00QC1Cl4fC4YxwFO5PZ9MhzKQUofsz03Ys7ChRkuevrqFUUCkef4PC/bSIFLILP8tmJNQgaaLvt6Z9NEAtQpeHwuGMcBTuT2fTIcykFKH7M9N2LOwoUZLnr66hVFApHn+Dwv20iBSyCz/LZiTUIGmi77emfTRALUKXh8LhjHAU7k9n0yHMpBSh+zPTdizwoVZPnr66hVE",
    );
    audio.play();
  } catch (e) {
    // Ignore audio errors
  }

  console.log("=".repeat(60));
  console.log("🎉 automation_completed FINISHED");
  console.log("=".repeat(60));
}

function clearLog() {
  const logContainer = document.getElementById("log-container");
  logContainer.innerHTML =
    '<p class="text-gray-500 text-sm"><span class="text-green-400">[INFO]</span> Log dibersihkan</p>';
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

function showExportCard(successCount) {
  console.log("📊 showExportCard called with count:", successCount);

  // Force switch to results page first
  showPage("results");
  console.log("✅ Switched to results page");

  // Then show the export card with a small delay to ensure page is rendered
  setTimeout(() => {
    const exportCard = document.getElementById("export-card");
    const exportCount = document.getElementById("export-count");

    console.log("Export card element:", exportCard);
    console.log("Export count element:", exportCount);

    if (exportCard && exportCount) {
      exportCount.textContent = successCount;
      exportCard.style.display = "block";

      // Force re-render
      exportCard.offsetHeight; // Trigger reflow

      console.log("✅ Export card displayed");
      console.log("   Card display style:", exportCard.style.display);
      console.log("   Card is visible:", exportCard.offsetHeight > 0);

      // Smooth scroll to top
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      console.error("❌ Export card or count element not found!");
      console.error(
        "   Available IDs on page:",
        Array.from(document.querySelectorAll("[id]"))
          .map((el) => el.id)
          .join(", "),
      );
    }
  }, 100);
}

async function downloadExcel() {
  try {
    logMessage("📥 Memulai export ke Excel...", "info");

    const result = await eel.export_to_excel()();

    if (result.success) {
      logMessage(`✅ ${result.message}`, "success");
      logMessage(`📂 File disimpan: ${result.filepath}`, "info");

      // Show success notification
      const fileName = result.filepath.split(/[\\\/]/).pop();
      alert(
        `Export berhasil!\n\nFile: ${fileName}\nLokasi: ${result.filepath}`,
      );
    } else {
      logMessage(`❌ ${result.message}`, "error");
      alert(`Export gagal: ${result.message}`);
    }
  } catch (error) {
    console.error("Error downloading Excel:", error);
    logMessage("❌ Gagal export ke Excel", "error");
    alert("Error: " + error);
  }
}

async function openResultsFolder() {
  try {
    const result = await eel.open_export_folder()();

    if (result.success) {
      logMessage("📁 Folder results dibuka", "success");
    } else {
      logMessage(`❌ ${result.message}`, "error");
      alert(`Gagal membuka folder: ${result.message}`);
    }
  } catch (error) {
    console.error("Error opening folder:", error);
    logMessage("❌ Gagal membuka folder results", "error");
    alert("Error: " + error);
  }
}

// ============================================
// STATISTICS
// ============================================

function updateStatistics() {
  let success = 0;
  let error = 0;
  let processing = 0;
  let waiting = 0;

  accounts.forEach((account) => {
    const statusBadge = document.getElementById(`status-${account.id}`);
    if (statusBadge) {
      if (statusBadge.classList.contains("status-done")) {
        success++;
      } else if (statusBadge.classList.contains("status-error")) {
        error++;
      } else if (statusBadge.classList.contains("status-processing")) {
        processing++;
      } else {
        waiting++;
      }
    }
  });

  const successEl = document.getElementById("success-count");
  const errorEl = document.getElementById("failed-count");
  const totalEl = document.getElementById("total-accounts");

  if (successEl) successEl.textContent = success;
  if (errorEl) errorEl.textContent = error;
  if (totalEl) totalEl.textContent = accounts.length;

  // Update circular chart (Safeguarded)
  // updateCircularChart(success, error, processing, waiting);
}

// Update circular progress chart
function updateCircularChart(success, error, processing, waiting) {
  const total = success + error + processing + waiting;
  const totalAccountsEl = document.getElementById("total-accounts");
  if (totalAccountsEl) {
    totalAccountsEl.textContent = total;
  }

  if (total === 0) return;

  const circumference = 2 * Math.PI * 80; // r=80
  let currentOffset = 0;

  // Success arc
  const successPercent = success / total;
  const successLength = circumference * successPercent;
  const chartSuccess = document.getElementById("chart-success");
  if (chartSuccess) {
    chartSuccess.setAttribute(
      "stroke-dasharray",
      `${successLength} ${circumference}`,
    );
    chartSuccess.setAttribute("stroke-dashoffset", currentOffset);
  }
  currentOffset -= successLength;

  // Error arc
  const errorPercent = error / total;
  const errorLength = circumference * errorPercent;
  const chartError = document.getElementById("chart-error");
  if (chartError) {
    chartError.setAttribute(
      "stroke-dasharray",
      `${errorLength} ${circumference}`,
    );
    chartError.setAttribute("stroke-dashoffset", currentOffset);
  }
  currentOffset -= errorLength;

  // Processing arc
  const processingPercent = processing / total;
  const processingLength = circumference * processingPercent;
  const chartProcessing = document.getElementById("chart-processing");
  if (chartProcessing) {
    chartProcessing.setAttribute(
      "stroke-dasharray",
      `${processingLength} ${circumference}`,
    );
    chartProcessing.setAttribute("stroke-dashoffset", currentOffset);
  }
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

document.addEventListener("keydown", (e) => {
  // Ctrl/Cmd + Enter = Start
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    if (!automationRunning) {
      startAutomation();
    }
  }

  // Ctrl/Cmd + P = Pause
  if ((e.ctrlKey || e.metaKey) && e.key === "p") {
    e.preventDefault();
    if (automationRunning) {
      pauseAutomation();
    }
  }

  // Escape = Stop
  if (e.key === "Escape") {
    if (automationRunning) {
      stopAutomation();
    }
  }

  // Ctrl/Cmd + L = Clear log
  if ((e.ctrlKey || e.metaKey) && e.key === "l") {
    e.preventDefault();
    clearLog();
  }
});

// ============================================
// REQUEST NOTIFICATION PERMISSION
// ============================================

if ("Notification" in window && Notification.permission === "default") {
  Notification.requestPermission();
}

// ============================================
// CHECK EXPORT STATUS ON LOAD
// ============================================

async function checkExportStatus() {
  try {
    console.log("🔍 Checking export status...");
    const result = await eel.get_export_ready_status()();
    console.log("Export status result:", result);

    if (result.ready && result.count > 0) {
      console.log(`✅ Export ready with ${result.count} results`);
      showExportCard(result.count);
    } else {
      console.log("⏳ No export ready yet");
    }
  } catch (error) {
    console.error("Error checking export status:", error);
  }
}

// Check export status setelah load
setTimeout(checkExportStatus, 1000);

// ============================================
// TOGGLE FUNCTIONS
// ============================================

function toggleHeadless() {
  const toggle = document.getElementById("headless-toggle");
  if (toggle) {
    headlessEnabled = toggle.checked;
    console.log("Headless mode:", headlessEnabled);
  }
}

// Export function globally for testing
window.showExportCard = showExportCard;
window.testExportCard = function () {
  console.log("🧪 Testing export card...");
  showExportCard(5);
};

// Debug helper functions
window.debugInfo = function () {
  console.log("=".repeat(60));
  console.log("🔍 DEBUG INFO");
  console.log("=".repeat(60));
  console.log("Accounts loaded:", accounts.length);
  console.log("Automation running:", automationRunning);
  console.log("Headless enabled:", headlessEnabled);
  console.log(
    "Current page:",
    document.querySelector(".page-section.active")?.id,
  );
  console.log("Export card exists:", !!document.getElementById("export-card"));
  console.log(
    "Export card visible:",
    document.getElementById("export-card")?.style.display,
  );
  console.log(
    "Export count:",
    document.getElementById("export-count")?.textContent,
  );
  console.log("=".repeat(60));
};

window.forceShowExportCard = function () {
  console.log("🔧 Force showing export card...");
  const card = document.getElementById("export-card");
  if (card) {
    card.style.display = "block";
    showPage("results");
    console.log("✅ Export card forced to show");
  } else {
    console.error("❌ Export card not found!");
  }
};

console.log("✅ SnapFlux Automation script loaded!");
console.log("💡 Debug commands:");
console.log("   - testExportCard() : Test export card");
console.log("   - debugInfo() : Show debug information");
console.log("   - forceShowExportCard() : Force show export card");
