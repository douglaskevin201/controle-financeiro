async function loadFixedIncomes() {
    const month = window.currentSelectedMonth;
    const year = window.currentSelectedYear;
    try {
        const incomes = await api.get(`/fixed-incomes?month=${month}&year=${year}`);
        renderFixedIncomes(incomes);
    } catch (err) {
        console.error("Erro ao carregar rendas fixas:", err);
    }
}

function renderFixedIncomes(incomes) {
    const container = document.getElementById("fixed-incomes-grid");
    const emptyState = document.getElementById("fixed-incomes-empty");
    if (!container) return;
    container.innerHTML = "";
    if (!incomes || incomes.length === 0) {
        emptyState?.classList.remove("hidden");
        return;
    }
    emptyState?.classList.add("hidden");
    incomes.forEach(income => {
        const received = income.is_received_this_month;
        const receipt = income.receipt;
        const card = document.createElement("div");
        card.className = "bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200/90 dark:border-slate-800 shadow-sm";
        card.innerHTML = `
            <div class="flex items-start justify-between gap-3">
                <div>
                    <h3 class="font-bold text-slate-900 dark:text-white">${escapeHtml(income.description)}</h3>
                    <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Recebimento previsto no dia ${income.pay_day}</p>
                </div>
                <span class="text-xs font-semibold ${received ? 'text-emerald-600' : 'text-amber-600'}">${received ? 'Recebido' : 'Previsto'}</span>
            </div>
            <div class="mt-5 text-2xl font-black text-emerald-600 dark:text-emerald-400">${formatBRL(receipt ? receipt.received_amount : income.base_amount)}</div>
            ${receipt && receipt.extra_amount > 0 ? `<p class="text-xs text-slate-500 mt-1">Inclui ${formatBRL(receipt.extra_amount)} em extras</p>` : ''}
            <div class="mt-5 flex gap-2">
                ${received ? `<button onclick="unreceiveFixedIncome(${income.id})" class="flex-1 px-3 py-2 text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-xl">Desfazer</button>` : `<button onclick="receiveFixedIncome(${income.id})" class="flex-1 px-3 py-2 text-xs font-semibold bg-emerald-600 text-white rounded-xl">Confirmar recebimento</button>`}
                <button onclick="deleteFixedIncome(${income.id})" class="px-3 py-2 text-xs font-semibold text-rose-600 bg-rose-50 dark:bg-rose-950/30 rounded-xl" title="Excluir renda fixa">Excluir</button>
            </div>`;
        container.appendChild(card);
    });
}

async function handleCreateFixedIncome(event) {
    event.preventDefault();
    const description = document.getElementById("income-description").value.trim();
    const base_amount = parseFloat(document.getElementById("income-amount").value);
    const pay_day = parseInt(document.getElementById("income-pay-day").value, 10);
    const category = document.getElementById("income-category-id").value;
    if (!description || !Number.isFinite(base_amount) || base_amount <= 0 || !Number.isInteger(pay_day) || pay_day < 1 || pay_day > 31) {
        showToast("Informe descrição, valor e dia válidos.", "error");
        return;
    }
    try {
        await api.post("/fixed-incomes", { description, base_amount, pay_day, category_id: category ? Number(category) : null });
        closeModal("modal-fixed-income");
        document.getElementById("form-fixed-income").reset();
        showToast("Renda fixa cadastrada!");
        loadFixedIncomes();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function receiveFixedIncome(id) {
    window.currentReceivingIncomeId = id;
    document.getElementById("income-extra-amount").value = "0";
    openModal("modal-receive-income");
}

async function handleReceiveFixedIncome(event) {
    event.preventDefault();
    const extra_amount = Number(document.getElementById("income-extra-amount").value.replace(",", "."));
    if (!Number.isFinite(extra_amount) || extra_amount < 0) {
        showToast("Informe um adicional válido.", "error");
        return;
    }
    const month = window.currentSelectedMonth;
    const year = window.currentSelectedYear;
    try {
        await api.post(`/fixed-incomes/${window.currentReceivingIncomeId}/receive?month=${month}&year=${year}`, { extra_amount });
        closeModal("modal-receive-income");
        showToast("Recebimento registrado!");
        loadFixedIncomes();
        loadTransactions();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function unreceiveFixedIncome(id) {
    const month = window.currentSelectedMonth;
    const year = window.currentSelectedYear;
    try {
        await api.post(`/fixed-incomes/${id}/unreceive?month=${month}&year=${year}`, {});
        showToast("Recebimento desfeito.");
        loadFixedIncomes();
        loadTransactions();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function deleteFixedIncome(id) {
    if (!confirm("Excluir esta renda fixa?")) return;
    try {
        await api.delete(`/fixed-incomes/${id}`);
        showToast("Renda fixa removida.");
        loadFixedIncomes();
    } catch (err) {
        showToast(err.message, "error");
    }
}
