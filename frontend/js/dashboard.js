let categoryChartInstance = null;
let monthlyChartInstance = null;

async function loadDashboardData() {
    const month = window.currentSelectedMonth;
    const year = window.currentSelectedYear;

    try {
        const [summary, charts] = await Promise.all([
            api.get(`/dashboard/summary?month=${month}&year=${year}`),
            api.get(`/dashboard/charts?month=${month}&year=${year}`)
        ]);

        renderSummaryCards(summary);
        renderCategoryChart(charts.expenses_by_category);
        renderMonthlyEvolutionChart(charts.monthly_evolution);
        renderDashboardQuickAlerts(summary);
    } catch (err) {
        console.error("Erro ao carregar dashboard:", err);
    }
}

function renderSummaryCards(summary) {
    // 1. Saldo Principal
    const elMainBalance = document.getElementById("dash-main-balance");
    if (elMainBalance) {
        elMainBalance.textContent = formatBRL(summary.main_balance);
        elMainBalance.className = `text-2xl font-bold ${summary.main_balance >= 0 ? 'text-slate-900' : 'text-rose-600'}`;
    }

    // 2. Total em Caixinhas
    const elPocketsTotal = document.getElementById("dash-pockets-total");
    if (elPocketsTotal) {
        elPocketsTotal.textContent = formatBRL(summary.total_in_pockets);
    }

    // 3. Patrimônio Total (Saldo + Caixinhas)
    const elTotalWealth = document.getElementById("dash-total-wealth");
    if (elTotalWealth) {
        elTotalWealth.textContent = formatBRL(summary.total_wealth);
    }

    // 4. Receitas do Mês
    const elMonthlyIncome = document.getElementById("dash-monthly-income");
    if (elMonthlyIncome) {
        elMonthlyIncome.textContent = formatBRL(summary.monthly_income);
    }

    // 5. Despesas do Mês
    const elMonthlyExpense = document.getElementById("dash-monthly-expense");
    if (elMonthlyExpense) {
        elMonthlyExpense.textContent = formatBRL(summary.monthly_expense);
    }

    // 6. Saldo Líquido do Mês
    const elMonthlyNet = document.getElementById("dash-monthly-net");
    if (elMonthlyNet) {
        elMonthlyNet.textContent = formatBRL(summary.monthly_net);
        elMonthlyNet.className = `text-lg font-bold ${summary.monthly_net >= 0 ? 'text-emerald-600' : 'text-rose-600'}`;
    }

    // 7. Contas Fixas Pendentes
    const elPendingBills = document.getElementById("dash-pending-bills");
    if (elPendingBills) {
        elPendingBills.textContent = formatBRL(summary.recurring_bills_pending);
    }
    const elPendingCount = document.getElementById("dash-pending-count");
    if (elPendingCount) {
        elPendingCount.textContent = `${summary.pending_bills_count} conta(s) pendente(s)`;
    }
}

function renderCategoryChart(categories) {
    const ctx = document.getElementById("chart-categories");
    if (!ctx) return;

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    const emptyContainer = document.getElementById("chart-categories-empty");
    if (!categories || categories.length === 0) {
        ctx.classList.add("hidden");
        if (emptyContainer) emptyContainer.classList.remove("hidden");
        return;
    }

    ctx.classList.remove("hidden");
    if (emptyContainer) emptyContainer.classList.add("hidden");

    const labels = categories.map(c => c.category_name);
    const data = categories.map(c => c.total);
    const colors = categories.map(c => c.color);

    categoryChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const perc = ((val / total) * 100).toFixed(1);
                            return ` ${context.label}: ${formatBRL(val)} (${perc}%)`;
                        }
                    }
                }
            },
            cutout: '68%'
        }
    });
}

function renderMonthlyEvolutionChart(evolutionData) {
    const ctx = document.getElementById("chart-monthly");
    if (!ctx) return;

    if (monthlyChartInstance) {
        monthlyChartInstance.destroy();
    }

    if (!evolutionData || evolutionData.length === 0) return;

    const labels = evolutionData.map(d => d.month_name);
    const incomes = evolutionData.map(d => d.income);
    const expenses = evolutionData.map(d => d.expense);

    monthlyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Receitas',
                    data: incomes,
                    backgroundColor: '#10B981',
                    borderRadius: 6
                },
                {
                    label: 'Despesas',
                    data: expenses,
                    backgroundColor: '#EF4444',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => 'R$ ' + value
                    },
                    grid: {
                        color: '#f1f5f9'
                    }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: { boxWidth: 12 }
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.dataset.label}: ${formatBRL(ctx.raw)}`
                    }
                }
            }
        }
    });
}

function renderDashboardQuickAlerts(summary) {
    const alertBox = document.getElementById("dash-quick-alerts");
    if (!alertBox) return;

    if (summary.pending_bills_count > 0) {
        alertBox.innerHTML = `
            <div class="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between text-amber-800 text-sm">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center font-bold text-amber-600">!</div>
                    <div>
                        <span class="font-semibold">Atenção para as contas fixas do mês:</span>
                        <span>Você ainda tem <strong>${summary.pending_bills_count} conta(s)</strong> pendente(s) totalizando <strong>${formatBRL(summary.recurring_bills_pending)}</strong>.</span>
                    </div>
                </div>
                <button onclick="switchTab('recurring')" class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-medium text-xs transition">
                    Ver Contas
                </button>
            </div>
        `;
        alertBox.classList.remove("hidden");
    } else {
        alertBox.classList.add("hidden");
    }
}

