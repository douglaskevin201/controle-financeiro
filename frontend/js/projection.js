async function loadProjection() {
    const month = window.currentSelectedMonth;
    const year = window.currentSelectedYear;
    try {
        const projection = await api.get(`/dashboard/projection?month=${month}&year=${year}`);
        renderProjection(projection);
    } catch (err) {
        console.error("Erro ao carregar projeção:", err);
    }
}

function renderProjection(projection) {
    const period = document.getElementById("projection-period");
    const income = document.getElementById("projection-income");
    const bills = document.getElementById("projection-bills");
    const net = document.getElementById("projection-net");
    const balance = document.getElementById("projection-balance");
    const current = document.getElementById("projection-current");
    const plannedIncome = document.getElementById("projection-planned-income");
    const plannedExpense = document.getElementById("projection-planned-expense");
    if (period) period.textContent = `${projection.projection_month}/${projection.projection_year}`;
    if (income) income.textContent = formatBRL(projection.fixed_income_expected);
    if (bills) bills.textContent = formatBRL(projection.recurring_bills_expected);
    if (net) net.textContent = formatBRL(projection.projected_net);
    if (balance) balance.textContent = formatBRL(projection.projected_main_balance);
    if (current) current.textContent = formatBRL(projection.current_main_balance);
    if (plannedIncome) plannedIncome.textContent = formatBRL(projection.planned_income);
    if (plannedExpense) plannedExpense.textContent = formatBRL(projection.planned_expense);
}
