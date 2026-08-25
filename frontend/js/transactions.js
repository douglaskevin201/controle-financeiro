let cachedCategories = [];

async function loadCategories() {
    try {
        cachedCategories = await api.get("/categories");
        populateCategorySelects();
    } catch (err) {
        console.error("Erro ao carregar categorias:", err);
    }
}

function populateCategorySelects() {
    const selects = [
        document.getElementById("tx-category-id"),
        document.getElementById("tx-filter-category"),
        document.getElementById("bill-category-id"),
        document.getElementById("income-category-id")
    ];

    selects.forEach(select => {
        if (!select) return;
        const currentVal = select.value;
        const isFilter = select.id.includes("filter");
        
        select.innerHTML = isFilter ? '<option value="">Todas as Categorias</option>' : '<option value="">Sem Categoria</option>';

        cachedCategories.forEach(cat => {
            if (select.id === "income-category-id" && cat.type !== "income") return;
            const opt = document.createElement("option");
            opt.value = cat.id;
            opt.textContent = `${cat.type === 'income' ? '🟢' : '🔴'} ${cat.name}`;
            select.appendChild(opt);
        });

        if (currentVal) select.value = currentVal;
    });
}

async function loadTransactions() {
    const month = window.currentSelectedMonth;
    const year = window.currentSelectedYear;
    const typeFilter = document.getElementById("tx-filter-type")?.value || "";
    const catFilter = document.getElementById("tx-filter-category")?.value || "";
    const searchFilter = document.getElementById("tx-filter-search")?.value || "";

    let endpoint = `/transactions?month=${month}&year=${year}`;
    if (typeFilter) endpoint += `&type=${typeFilter}`;
    if (catFilter) endpoint += `&category_id=${catFilter}`;
    if (searchFilter) endpoint += `&search=${encodeURIComponent(searchFilter)}`;

    try {
        const transactions = await api.get(endpoint);
        renderTransactionsTable(transactions);
    } catch (err) {
        console.error("Erro ao carregar transações:", err);
    }
}

function renderTransactionsTable(transactions) {
    const tbody = document.getElementById("transactions-tbody");
    const emptyState = document.getElementById("transactions-empty");
    if (!tbody) return;

    tbody.innerHTML = "";

    if (!transactions || transactions.length === 0) {
        if (emptyState) emptyState.classList.remove("hidden");
        return;
    }

    if (emptyState) emptyState.classList.add("hidden");

    transactions.forEach(tx => {
        const isIncome = tx.type === "income";
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors border-b border-slate-100 dark:border-slate-800/80 text-sm";

        const categoryName = tx.category ? tx.category.name : "Geral";
        const categoryColor = tx.category ? tx.category.color : "#94a3b8";

        tr.innerHTML = `
            <td class="py-3.5 px-4 text-slate-500 dark:text-slate-400 font-medium whitespace-nowrap">
                ${formatDate(tx.transaction_date)}
            </td>
            <td class="py-3.5 px-4 text-slate-900 dark:text-slate-100 font-medium">
                ${escapeHtml(tx.description)}
            </td>
            <td class="py-3.5 px-4">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold"
                      style="background-color: ${categoryColor}20; color: ${categoryColor};">
                    <span class="w-1.5 h-1.5 rounded-full" style="background-color: ${categoryColor}"></span>
                    ${escapeHtml(categoryName)}
                </span>
            </td>
            <td class="py-3.5 px-4 font-bold text-right whitespace-nowrap ${isIncome ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">
                ${isIncome ? '+' : '-'} ${formatBRL(tx.amount)}
            </td>
            <td class="py-3.5 px-4 text-right">
                <button onclick="deleteTransaction(${tx.id})" title="Excluir Transação"
                        class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/50 rounded-lg transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function handleCreateTransaction(e) {
    e.preventDefault();
    const type = document.getElementById("tx-type").value;
    const description = document.getElementById("tx-description").value.trim();
    const amount = parseFloat(document.getElementById("tx-amount").value);
    const category_id = document.getElementById("tx-category-id").value;
    const transaction_date = document.getElementById("tx-date").value;
    const is_planned = document.getElementById("tx-is-planned")?.checked || false;

    if (!description || isNaN(amount) || amount <= 0) {
        showToast("Preencha a descrição e um valor válido.", "error");
        return;
    }

    try {
        await api.post("/transactions", {
            type,
            description,
            amount,
            category_id: category_id ? parseInt(category_id) : null,
            transaction_date: transaction_date || null,
            is_planned
        });

        showToast("Transação adicionada com sucesso!");
        closeModal("modal-transaction");
        document.getElementById("form-transaction").reset();
        document.getElementById("tx-date").valueAsDate = new Date();

        // Recarrega os dados
        loadTransactions();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function deleteTransaction(id) {
    if (!confirm("Deseja realmente excluir esta transação?")) return;

    try {
        await api.delete(`/transactions/${id}`);
        showToast("Transação excluída com sucesso.");
        loadTransactions();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}
