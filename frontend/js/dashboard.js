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
    const isDark = document.documentElement.classList.contains("dark");

    // 1. Saldo Principal
    const elMainBalance = document.getElementById("dash-main-balance");
    const elMainStatus = document.getElementById("dash-main-status");
    if (elMainBalance) {
        elMainBalance.textContent = formatBRL(summary.main_balance);
        if (summary.main_balance > 0) {
            elMainBalance.className = "text-2xl sm:text-3xl font-black text-slate-900 dark:text-white mt-1";
            if (elMainStatus) elMainStatus.innerHTML = `<span class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full">● Saldo Positivo</span>`;
        } else if (summary.main_balance < 0) {
            elMainBalance.className = "text-2xl sm:text-3xl font-black text-rose-600 dark:text-rose-400 mt-1";
            if (elMainStatus) elMainStatus.innerHTML = `<span class="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 px-2 py-0.5 rounded-full">● Saldo Negativo</span>`;
        } else {
            elMainBalance.className = "text-2xl sm:text-3xl font-black text-slate-800 dark:text-slate-200 mt-1";
            if (elMainStatus) elMainStatus.innerHTML = `<span class="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">✨ Pronto para começar</span>`;
        }
    }

    // 2. Total em Caixinhas
    const elPocketsTotal = document.getElementById("dash-pockets-total");
    const elPocketsStatus = document.getElementById("dash-pockets-status");
    if (elPocketsTotal) {
        elPocketsTotal.textContent = formatBRL(summary.total_in_pockets);
        if (elPocketsStatus) {
            if (summary.total_in_pockets > 0) {
                elPocketsStatus.innerHTML = `<span class="inline-flex items-center gap-1 text-[11px] font-semibold text-teal-600 dark:text-teal-400 bg-teal-50 dark:bg-teal-950/40 px-2 py-0.5 rounded-full">📦 Reservas protegidas</span>`;
            } else {
                elPocketsStatus.innerHTML = `<span class="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">🎯 Nenhuma meta ativa</span>`;
            }
        }
    }

    // 3. Patrimônio Total (Saldo + Caixinhas)
    const elTotalWealth = document.getElementById("dash-total-wealth");
    const elWealthStatus = document.getElementById("dash-wealth-status");
    if (elTotalWealth) {
        elTotalWealth.textContent = formatBRL(summary.total_wealth);
        if (elWealthStatus) {
            if (summary.total_wealth > 0) {
                elWealthStatus.innerHTML = `<span class="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 px-2 py-0.5 rounded-full">🏛️ Total acumulado</span>`;
            } else {
                elWealthStatus.innerHTML = `<span class="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">📊 Saldo + Caixinhas</span>`;
            }
        }
    }

    // 4. Receitas do Mês
    const elMonthlyIncome = document.getElementById("dash-monthly-income");
    const elIncomeStatus = document.getElementById("dash-income-status");
    if (elMonthlyIncome) {
        elMonthlyIncome.textContent = formatBRL(summary.monthly_income);
        if (elIncomeStatus) {
            elIncomeStatus.textContent = summary.monthly_income > 0 ? "Entradas registradas" : "Nenhuma entrada este mês";
        }
    }

    // 5. Despesas do Mês
    const elMonthlyExpense = document.getElementById("dash-monthly-expense");
    const elExpenseStatus = document.getElementById("dash-expense-status");
    if (elMonthlyExpense) {
        elMonthlyExpense.textContent = formatBRL(summary.monthly_expense);
        if (elExpenseStatus) {
            elExpenseStatus.textContent = summary.monthly_expense > 0 ? "Gastos registrados" : "Nenhum gasto este mês";
        }
    }

    // 6. Saldo Líquido do Mês
    const elMonthlyNet = document.getElementById("dash-monthly-net");
    const elNetStatus = document.getElementById("dash-net-status");
    if (elMonthlyNet) {
        elMonthlyNet.textContent = formatBRL(summary.monthly_net);
        elMonthlyNet.className = `text-xl font-bold ${summary.monthly_net >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`;
        if (elNetStatus) {
            elNetStatus.textContent = summary.monthly_net >= 0 ? "Balanço positivo" : "Despesas superam receitas";
        }
    }

    // 7. Contas Fixas Pendentes
    const elPendingBills = document.getElementById("dash-pending-bills");
    const elPendingCount = document.getElementById("dash-pending-count");
    if (elPendingBills) {
        elPendingBills.textContent = formatBRL(summary.recurring_bills_pending);
    }
    if (elPendingCount) {
        elPendingCount.textContent = summary.pending_bills_count > 0 
            ? `${summary.pending_bills_count} conta(s) pendente(s)` 
            : "Tudo pago neste mês! 🎉";
    }
}

function renderCategoryChart(categories) {
    const ctx = document.getElementById("chart-categories");
    if (!ctx) return;

    const isDark = document.documentElement.classList.contains("dark");

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
                borderWidth: isDark ? 2 : 2,
                borderColor: isDark ? '#0f172a' : '#ffffff',
                hoverOffset: 6
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
                        color: isDark ? '#94A3B8' : '#475569',
                        font: { size: 11, family: 'Inter' },
                        padding: 12
                    }
                },
                tooltip: {
                    backgroundColor: isDark ? '#1e293b' : '#0f172a',
                    titleColor: '#ffffff',
                    bodyColor: '#e2e8f0',
                    padding: 10,
                    cornerRadius: 8,
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
            cutout: '70%'
        }
    });
}

function renderMonthlyEvolutionChart(evolutionData) {
    const canvas = document.getElementById("chart-monthly");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const isDark = document.documentElement.classList.contains("dark");

    if (monthlyChartInstance) {
        monthlyChartInstance.destroy();
    }

    if (!evolutionData || evolutionData.length === 0) return;

    const labels = evolutionData.map(d => d.month_name);
    const incomes = evolutionData.map(d => d.income);
    const expenses = evolutionData.map(d => d.expense);

    // Calcula escala inteligente do eixo Y para nunca ficar travado em R$0–R$1 quando vazio
    const maxVal = Math.max(...incomes, ...expenses, 0);
    const suggestedMax = maxVal === 0 ? 1000 : maxVal * 1.2;

    // Gradientes visuais modernos para as barras
    const incomeGradient = ctx.createLinearGradient(0, 0, 0, 300);
    incomeGradient.addColorStop(0, '#10B981');
    incomeGradient.addColorStop(1, '#059669');

    const expenseGradient = ctx.createLinearGradient(0, 0, 0, 300);
    expenseGradient.addColorStop(0, '#F43F5E');
    expenseGradient.addColorStop(1, '#E11D48');

    monthlyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Receitas',
                    data: incomes,
                    backgroundColor: incomeGradient,
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.7,
                    categoryPercentage: 0.6
                },
                {
                    label: 'Despesas',
                    data: expenses,
                    backgroundColor: expenseGradient,
                    borderRadius: 6,
                    borderSkipped: false,
                    barPercentage: 0.7,
                    categoryPercentage: 0.6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMax: suggestedMax,
                    ticks: {
                        color: isDark ? '#94A3B8' : '#64748B',
                        font: { size: 11, family: 'Inter' },
                        callback: (value) => formatBRL(value)
                    },
                    grid: {
                        color: isDark ? 'rgba(255, 255, 255, 0.06)' : '#f1f5f9'
                    },
                    border: {
                        display: false
                    }
                },
                x: {
                    ticks: {
                        color: isDark ? '#94A3B8' : '#64748B',
                        font: { size: 11, family: 'Inter' }
                    },
                    grid: { display: false },
                    border: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: {
                        boxWidth: 12,
                        boxHeight: 12,
                        borderRadius: 3,
                        useBorderRadius: true,
                        color: isDark ? '#94A3B8' : '#475569',
                        font: { size: 12, family: 'Inter', weight: '500' },
                        padding: 16
                    }
                },
                tooltip: {
                    backgroundColor: isDark ? '#1e293b' : '#0f172a',
                    titleColor: '#ffffff',
                    bodyColor: '#e2e8f0',
                    padding: 10,
                    cornerRadius: 8,
                    callbacks: {
                        label: (c) => ` ${c.dataset.label}: ${formatBRL(c.raw)}`
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
            <div class="p-4 bg-amber-500/10 border border-amber-500/30 dark:border-amber-500/20 rounded-2xl flex items-center justify-between text-amber-900 dark:text-amber-300 text-sm">
                <div class="flex items-center gap-3.5">
                    <div class="w-9 h-9 rounded-xl bg-amber-500/20 flex items-center justify-center font-bold text-amber-600 dark:text-amber-400 shrink-0">
                        ⚠️
                    </div>
                    <div>
                        <span class="font-bold">Atenção para as contas fixas do mês:</span>
                        <span class="block text-xs text-amber-800/80 dark:text-amber-300/80 mt-0.5">
                            Você tem <strong>${summary.pending_bills_count} conta(s)</strong> pendente(s) totalizando <strong>${formatBRL(summary.recurring_bills_pending)}</strong>.
                        </span>
                    </div>
                </div>
                <button onclick="switchTab('recurring')" class="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-semibold text-xs shadow-sm transition shrink-0">
                    Ver Contas
                </button>
            </div>
        `;
        alertBox.classList.remove("hidden");
    } else {
        alertBox.classList.add("hidden");
    }
}
