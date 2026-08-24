async function loadRecurringBills() {
    const month = window.currentSelectedMonth;
    const year = window.currentSelectedYear;

    try {
        const bills = await api.get(`/recurring-bills?month=${month}&year=${year}`);
        renderRecurringBills(bills);
    } catch (err) {
        console.error("Erro ao carregar contas recorrentes:", err);
    }
}

function renderRecurringBills(bills) {
    const container = document.getElementById("recurring-bills-grid");
    const emptyState = document.getElementById("recurring-bills-empty");
    if (!container) return;

    container.innerHTML = "";

    if (!bills || bills.length === 0) {
        if (emptyState) emptyState.classList.remove("hidden");
        return;
    }

    if (emptyState) emptyState.classList.add("hidden");

    bills.forEach(bill => {
        const isPaid = bill.is_paid_this_month;
        const card = document.createElement("div");
        card.className = `p-6 rounded-3xl border transition-all ${
            isPaid 
                ? 'bg-slate-50/80 dark:bg-slate-900/40 border-slate-200 dark:border-slate-800' 
                : 'bg-white dark:bg-slate-900 border-slate-200/90 dark:border-slate-800 shadow-sm hover:shadow-md'
        }`;

        const categoryName = bill.category ? bill.category.name : "Conta Fixa";
        const categoryColor = bill.category ? bill.category.color : "#64748B";

        card.innerHTML = `
            <div class="flex items-start justify-between">
                <div class="flex items-center gap-3.5">
                    <div class="w-11 h-11 rounded-2xl flex flex-col items-center justify-center font-bold text-white shadow-md shadow-slate-900/10 shrink-0"
                         style="background-color: ${categoryColor}">
                        <span class="text-[9px] uppercase leading-none font-semibold">Dia</span>
                        <span class="text-base leading-tight">${bill.due_day}</span>
                    </div>
                    <div>
                        <h4 class="font-bold text-slate-900 dark:text-white text-base ${isPaid ? 'line-through text-slate-400 dark:text-slate-500' : ''}">
                            ${bill.description}
                        </h4>
                        <p class="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mt-0.5">
                            <span>Vence dia ${bill.due_day}</span>
                            <span>•</span>
                            <span class="inline-flex items-center gap-1 font-medium" style="color: ${categoryColor}">
                                <span class="w-1.5 h-1.5 rounded-full" style="background-color: ${categoryColor}"></span>
                                ${categoryName}
                            </span>
                        </p>
                    </div>
                </div>

                <div class="text-right shrink-0">
                    <span class="block font-black text-lg text-slate-900 dark:text-white">
                        ${formatBRL(bill.amount)}
                    </span>
                    <span class="inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        isPaid 
                            ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300' 
                            : 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300'
                    }">
                        ${isPaid ? '✓ Pago' : '⏳ Pendente'}
                    </span>
                </div>
            </div>

            <div class="mt-4 pt-3.5 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
                <div>
                    ${isPaid && bill.payment_info ? `
                        <span class="text-xs text-slate-400 dark:text-slate-500">Pago em: ${formatDate(bill.payment_info.paid_at)}</span>
                    ` : `
                        <span class="text-xs text-amber-600 dark:text-amber-400 font-medium">Aguardando pagamento</span>
                    `}
                </div>
                <div class="flex items-center gap-2">
                    ${isPaid ? `
                        <button onclick="unpayRecurringBill(${bill.id})"
                                class="px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition">
                            Desfazer
                        </button>
                    ` : `
                        <button onclick="payRecurringBill(${bill.id})"
                                class="px-3.5 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-sm transition flex items-center gap-1.5">
                            <span>Pagar Conta</span>
                        </button>
                    `}
                    <button onclick="deleteRecurringBill(${bill.id})" title="Excluir Conta Recorrente"
                            class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl transition">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </div>
        `;

        container.appendChild(card);
    });
}

async function handleCreateRecurringBill(e) {
    e.preventDefault();
    const description = document.getElementById("bill-description").value.trim();
    const amount = parseFloat(document.getElementById("bill-amount").value);
    const due_day = parseInt(document.getElementById("bill-due-day").value);
    const category_id = document.getElementById("bill-category-id").value;

    if (!description || isNaN(amount) || amount <= 0 || isNaN(due_day) || due_day < 1 || due_day > 31) {
        showToast("Preencha todos os campos corretamente (dia entre 1 e 31).", "error");
        return;
    }

    try {
        await api.post("/recurring-bills", {
            description,
            amount,
            due_day,
            category_id: category_id ? parseInt(category_id) : null
        });

        showToast("Conta recorrente cadastrada!");
        closeModal("modal-recurring");
        document.getElementById("form-recurring").reset();

        loadRecurringBills();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function payRecurringBill(id) {
    const month = window.currentSelectedMonth;
    const year = window.currentSelectedYear;

    try {
        await api.post(`/recurring-bills/${id}/pay?month=${month}&year=${year}`, {
            create_transaction: true
        });
        showToast("Conta marcada como paga! Despesa registrada.");
        loadRecurringBills();
        loadTransactions();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function unpayRecurringBill(id) {
    const month = window.currentSelectedMonth;
    const year = window.currentSelectedYear;

    try {
        await api.post(`/recurring-bills/${id}/unpay?month=${month}&year=${year}`, {});
        showToast("Pagamento desfeito.");
        loadRecurringBills();
        loadTransactions();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function deleteRecurringBill(id) {
    if (!confirm("Deseja realmente remover esta conta recorrente?")) return;

    try {
        await api.delete(`/recurring-bills/${id}`);
        showToast("Conta recorrente removida.");
        loadRecurringBills();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}
