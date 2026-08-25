// Estado Global
const today = new Date();
window.currentSelectedMonth = today.getMonth() + 1;
window.currentSelectedYear = today.getFullYear();
window.currentActiveTab = "projection";

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initDateFilters();
    initEventListeners();
    initTabNavigation();
    initMobileSidebar();
    initTypeSelectHighlight();

    // Carregamento inicial de dados
    loadCategories();
    loadDashboardData();
    loadTransactions();
    loadRecurringBills();
    loadPockets();
    loadFixedIncomes();
    loadProjection();
});

// ==========================================
// TEMA DARK / LIGHT MODE
// ==========================================
function initTheme() {
    const savedTheme = localStorage.getItem("finance_theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    
    if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
        document.documentElement.classList.add("dark");
        updateThemeToggleIcons(true);
    } else {
        document.documentElement.classList.remove("dark");
        updateThemeToggleIcons(false);
    }

    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", toggleTheme);
    }
}

function toggleTheme() {
    const isDark = document.documentElement.classList.toggle("dark");
    localStorage.setItem("finance_theme", isDark ? "dark" : "light");
    updateThemeToggleIcons(isDark);

    // Atualiza os gráficos do Dashboard para refletir as cores do tema
    if (window.currentActiveTab === "dashboard") {
        loadDashboardData();
    }
}

function updateThemeToggleIcons(isDark) {
    const sunIcon = document.getElementById("theme-icon-sun");
    const moonIcon = document.getElementById("theme-icon-moon");
    if (sunIcon && moonIcon) {
        if (isDark) {
            sunIcon.classList.remove("hidden");
            moonIcon.classList.add("hidden");
        } else {
            sunIcon.classList.add("hidden");
            moonIcon.classList.remove("hidden");
        }
    }
}

// ==========================================
// NAVEGAÇÃO MOBILE (SIDEBAR DRAWER)
// ==========================================
function initMobileSidebar() {
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const sidebar = document.getElementById("app-sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");

    if (mobileMenuBtn && sidebar && backdrop) {
        mobileMenuBtn.addEventListener("click", () => {
            sidebar.classList.remove("-translate-x-full");
            backdrop.classList.remove("hidden");
        });

        backdrop.addEventListener("click", closeMobileSidebar);
    }
}

function closeMobileSidebar() {
    const sidebar = document.getElementById("app-sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (sidebar) sidebar.classList.add("-translate-x-full");
    if (backdrop) backdrop.classList.add("hidden");
}

// ==========================================
// FILTROS DE DATA
// ==========================================
function initDateFilters() {
    const monthSelect = document.getElementById("global-month-select");
    const yearSelect = document.getElementById("global-year-select");

    if (monthSelect) {
        monthSelect.value = window.currentSelectedMonth;
        monthSelect.addEventListener("change", (e) => {
            window.currentSelectedMonth = parseInt(e.target.value);
            onGlobalDateChanged();
        });
    }

    if (yearSelect) {
        yearSelect.value = window.currentSelectedYear;
        yearSelect.addEventListener("change", (e) => {
            window.currentSelectedYear = parseInt(e.target.value);
            onGlobalDateChanged();
        });
    }

    // Define data padrão nos inputs de data para hoje
    const txDateInput = document.getElementById("tx-date");
    if (txDateInput) {
        txDateInput.value = today.toISOString().split('T')[0];
    }
}

function onGlobalDateChanged() {
    loadDashboardData();
    loadTransactions();
    loadRecurringBills();
    loadFixedIncomes();
    loadProjection();
}

// ==========================================
// NAVEGAÇÃO ENTRE ABAS COM INDICADOR LATERAL
// ==========================================
function initTabNavigation() {
    const tabs = ["projection", "dashboard", "transactions", "recurring", "pockets", "fixed-incomes"];
    
    tabs.forEach(tabId => {
        const btn = document.getElementById(`nav-tab-${tabId}`);
        if (btn) {
            btn.addEventListener("click", () => {
                switchTab(tabId);
                closeMobileSidebar();
            });
        }
    });
}

function switchTab(tabId) {
    window.currentActiveTab = tabId;
    const tabs = ["projection", "dashboard", "transactions", "recurring", "pockets", "fixed-incomes"];

    tabs.forEach(t => {
        const btn = document.getElementById(`nav-tab-${t}`);
        const view = document.getElementById(`view-${t}`);

        if (t === tabId) {
            if (btn) {
                // Item ativo com indicador lateral colorido e fundo destacado
                btn.className = "w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-semibold text-sm bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 border-l-4 border-emerald-600 dark:border-emerald-400 shadow-sm transition";
            }
            if (view) view.classList.remove("hidden");
        } else {
            if (btn) {
                // Item inativo
                btn.className = "w-full flex items-center gap-3.5 px-4 py-3 rounded-xl font-medium text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100/70 dark:hover:bg-slate-800/60 border-l-4 border-transparent transition";
            }
            if (view) view.classList.add("hidden");
        }
    });

    // Ações de refresh específicas por aba
    if (tabId === "dashboard") loadDashboardData();
    if (tabId === "transactions") loadTransactions();
    if (tabId === "recurring") loadRecurringBills();
    if (tabId === "pockets") loadPockets();
    if (tabId === "fixed-incomes") loadFixedIncomes();
    if (tabId === "projection") loadProjection();
}

// ==========================================
// DESTAQUE VISUAL NO SELECT DE TIPO (DESPESA / RECEITA)
// ==========================================
function initTypeSelectHighlight() {
    const txTypeSelect = document.getElementById("tx-type");
    if (!txTypeSelect) return;

    function applyHighlight() {
        if (txTypeSelect.value === "expense") {
            txTypeSelect.className = "w-full pl-10 pr-4 py-2.5 bg-rose-50/70 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800/60 text-rose-800 dark:text-rose-300 font-semibold rounded-xl text-sm focus:ring-2 focus:ring-rose-500 transition-colors";
        } else {
            txTypeSelect.className = "w-full pl-10 pr-4 py-2.5 bg-emerald-50/70 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/60 text-emerald-800 dark:text-emerald-300 font-semibold rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 transition-colors";
        }
    }

    txTypeSelect.addEventListener("change", applyHighlight);
    applyHighlight();
}

function initEventListeners() {
    // Formulários
    const formTx = document.getElementById("form-transaction");
    if (formTx) formTx.addEventListener("submit", handleCreateTransaction);

    const formBill = document.getElementById("form-recurring");
    if (formBill) formBill.addEventListener("submit", handleCreateRecurringBill);

    const formPocket = document.getElementById("form-pocket");
    if (formPocket) formPocket.addEventListener("submit", handleCreatePocket);

    const formTransfer = document.getElementById("form-pocket-transfer");
    if (formTransfer) formTransfer.addEventListener("submit", handlePocketTransfer);

    const formCategory = document.getElementById("form-category");
    if (formCategory) formCategory.addEventListener("submit", handleCreateCategory);

    const formFixedIncome = document.getElementById("form-fixed-income");
    if (formFixedIncome) formFixedIncome.addEventListener("submit", handleCreateFixedIncome);

    const formReceiveIncome = document.getElementById("form-receive-income");
    if (formReceiveIncome) formReceiveIncome.addEventListener("submit", handleReceiveFixedIncome);

    // Filtros de transações em tempo real
    const filterType = document.getElementById("tx-filter-type");
    if (filterType) filterType.addEventListener("change", loadTransactions);

    const filterCategory = document.getElementById("tx-filter-category");
    if (filterCategory) filterCategory.addEventListener("change", loadTransactions);

    const filterSearch = document.getElementById("tx-filter-search");
    if (filterSearch) {
        let debounceTimer;
        filterSearch.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(loadTransactions, 300);
        });
    }
}

// Modal helper functions com animação
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("hidden");
        document.body.classList.add("overflow-hidden");
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("hidden");
        document.body.classList.remove("overflow-hidden");
    }
}

// Criar nova categoria customizada
async function handleCreateCategory(e) {
    e.preventDefault();
    const name = document.getElementById("cat-name").value.trim();
    const type = document.getElementById("cat-type").value;
    const color = document.getElementById("cat-color").value;

    if (!name) {
        showToast("Digite o nome da categoria.", "error");
        return;
    }

    try {
        await api.post("/categories", { name, type, color });
        showToast("Categoria criada com sucesso!");
        closeModal("modal-category");
        document.getElementById("form-category").reset();
        await loadCategories();
    } catch (err) {
        showToast(err.message, "error");
    }
}
