// Estado Global
const today = new Date();
window.currentSelectedMonth = today.getMonth() + 1;
window.currentSelectedYear = today.getFullYear();
window.currentActiveTab = "dashboard";

document.addEventListener("DOMContentLoaded", () => {
    initDateFilters();
    initEventListeners();
    initTabNavigation();

    // Carregamento inicial de dados
    loadCategories();
    loadDashboardData();
    loadTransactions();
    loadRecurringBills();
    loadPockets();
});

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
}

function initTabNavigation() {
    const tabs = ["dashboard", "transactions", "recurring", "pockets"];
    
    tabs.forEach(tabId => {
        const btn = document.getElementById(`nav-tab-${tabId}`);
        if (btn) {
            btn.addEventListener("click", () => switchTab(tabId));
        }
    });
}

function switchTab(tabId) {
    window.currentActiveTab = tabId;
    const tabs = ["dashboard", "transactions", "recurring", "pockets"];

    tabs.forEach(t => {
        const btn = document.getElementById(`nav-tab-${t}`);
        const view = document.getElementById(`view-${t}`);

        if (t === tabId) {
            if (btn) {
                btn.className = "flex items-center gap-2.5 px-4 py-2.5 rounded-xl font-semibold text-sm bg-emerald-50 text-emerald-700 transition";
            }
            if (view) view.classList.remove("hidden");
        } else {
            if (btn) {
                btn.className = "flex items-center gap-2.5 px-4 py-2.5 rounded-xl font-medium text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition";
            }
            if (view) view.classList.add("hidden");
        }
    });

    // Ações de refresh específicas por aba
    if (tabId === "dashboard") loadDashboardData();
    if (tabId === "transactions") loadTransactions();
    if (tabId === "recurring") loadRecurringBills();
    if (tabId === "pockets") loadPockets();
}

function initEventListeners() {
    // Forms
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

// Modal helper functions
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

