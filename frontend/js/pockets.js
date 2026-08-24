let currentActivePocketId = null;

async function loadPockets() {
    try {
        const pockets = await api.get("/pockets");
        renderPockets(pockets);
    } catch (err) {
        console.error("Erro ao carregar caixinhas:", err);
    }
}

function renderPockets(pockets) {
    const container = document.getElementById("pockets-grid");
    const emptyState = document.getElementById("pockets-empty");
    if (!container) return;

    container.innerHTML = "";

    if (!pockets || pockets.length === 0) {
        if (emptyState) emptyState.classList.remove("hidden");
        return;
    }

    if (emptyState) emptyState.classList.add("hidden");

    pockets.forEach(pocket => {
        const card = document.createElement("div");
        card.className = "bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between";

        const hasGoal = pocket.target_amount && pocket.target_amount > 0;
        const progress = pocket.progress_percentage || 0;
        const color = pocket.color || "#10B981";

        card.innerHTML = `
            <div>
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 rounded-2xl flex items-center justify-center text-white text-xl font-bold shadow-sm"
                             style="background-color: ${color}">
                            📦
                        </div>
                        <div>
                            <h3 class="font-bold text-slate-900 text-lg">${pocket.name}</h3>
                            <span class="text-xs text-slate-400">Criada em ${formatDate(pocket.created_at.split('T')[0])}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-1">
                        <button onclick="viewPocketHistory(${pocket.id}, '${pocket.name}')" title="Ver Histórico da Caixinha"
                                class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </button>
                        <button onclick="deletePocket(${pocket.id})" title="Excluir Caixinha"
                                class="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </div>
                </div>

                <div class="mb-4">
                    <span class="text-xs text-slate-500 font-medium">Saldo Guardado</span>
                    <div class="text-2xl font-black text-slate-900 mt-0.5">
                        ${formatBRL(pocket.current_amount)}
                    </div>
                    ${hasGoal ? `
                        <div class="text-xs text-slate-500 mt-0.5">
                            Meta: <strong class="text-slate-700">${formatBRL(pocket.target_amount)}</strong>
                        </div>
                    ` : `
                        <div class="text-xs text-slate-400 mt-0.5">Sem meta definida</div>
                    `}
                </div>

                ${hasGoal ? `
                    <div class="mb-6">
                        <div class="flex items-center justify-between text-xs font-semibold mb-1.5">
                            <span class="text-slate-600">Progresso</span>
                            <span style="color: ${color}">${progress}%</span>
                        </div>
                        <div class="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                            <div class="h-2.5 rounded-full transition-all duration-500"
                                 style="width: ${progress}%; background-color: ${color}"></div>
                        </div>
                    </div>
                ` : '<div class="mb-6"></div>'}
            </div>

            <!-- Botões de Ação Rápida -->
            <div class="grid grid-cols-2 gap-2 pt-4 border-t border-slate-100">
                <button onclick="openTransferModal(${pocket.id}, '${pocket.name}', 'deposit')"
                        class="w-full py-2 px-3 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-semibold rounded-xl text-xs flex items-center justify-center gap-1.5 transition">
                    <span>+ Guardar</span>
                </button>
                <button onclick="openTransferModal(${pocket.id}, '${pocket.name}', 'withdraw')"
                        class="w-full py-2 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs flex items-center justify-center gap-1.5 transition">
                    <span>- Resgatar</span>
                </button>
            </div>
        `;

        container.appendChild(card);
    });
}

async function handleCreatePocket(e) {
    e.preventDefault();
    const name = document.getElementById("pocket-name").value.trim();
    const target_amount_val = document.getElementById("pocket-target").value;
    const initial_deposit_val = document.getElementById("pocket-initial").value;
    const color = document.getElementById("pocket-color").value;

    const target_amount = target_amount_val ? parseFloat(target_amount_val) : null;
    const initial_deposit = initial_deposit_val ? parseFloat(initial_deposit_val) : 0;

    if (!name) {
        showToast("Dê um nome para a caixinha.", "error");
        return;
    }

    try {
        await api.post("/pockets", {
            name,
            target_amount,
            initial_deposit,
            color
        });

        showToast("Caixinha criada com sucesso!");
        closeModal("modal-pocket");
        document.getElementById("form-pocket").reset();

        loadPockets();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}

function openTransferModal(pocketId, pocketName, defaultType = "deposit") {
    currentActivePocketId = pocketId;
    document.getElementById("transfer-pocket-name").textContent = pocketName;
    document.getElementById("transfer-type").value = defaultType;
    document.getElementById("transfer-amount").value = "";
    document.getElementById("transfer-desc").value = "";
    openModal("modal-pocket-transfer");
}

async function handlePocketTransfer(e) {
    e.preventDefault();
    if (!currentActivePocketId) return;

    const type = document.getElementById("transfer-type").value;
    const amount = parseFloat(document.getElementById("transfer-amount").value);
    const description = document.getElementById("transfer-desc").value.trim();

    if (isNaN(amount) || amount <= 0) {
        showToast("Informe um valor válido maior que zero.", "error");
        return;
    }

    try {
        await api.post(`/pockets/${currentActivePocketId}/transfer`, {
            type,
            amount,
            description: description || null
        });

        showToast(type === "deposit" ? "Dinheiro guardado na caixinha!" : "Resgate realizado com sucesso!");
        closeModal("modal-pocket-transfer");

        loadPockets();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function viewPocketHistory(pocketId, pocketName) {
    document.getElementById("history-pocket-name").textContent = pocketName;
    const tbody = document.getElementById("pocket-history-tbody");
    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-6 text-slate-400">Carregando...</td></tr>';
    openModal("modal-pocket-history");

    try {
        const txs = await api.get(`/pockets/${pocketId}/transactions`);
        tbody.innerHTML = "";

        if (!txs || txs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-6 text-slate-400">Nenhuma movimentação registrada nesta caixinha.</td></tr>';
            return;
        }

        txs.forEach(tx => {
            const isDeposit = tx.type === "deposit";
            const tr = document.createElement("tr");
            tr.className = "border-b border-slate-100 text-sm";
            tr.innerHTML = `
                <td class="py-2.5 px-3 text-slate-500 whitespace-nowrap">${formatDate(tx.transaction_date)}</td>
                <td class="py-2.5 px-3 font-medium text-slate-800">${tx.description || (isDeposit ? 'Depósito' : 'Resgate')}</td>
                <td class="py-2.5 px-3">
                    <span class="px-2 py-0.5 rounded text-xs font-semibold ${isDeposit ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'}">
                        ${isDeposit ? 'Guardado' : 'Resgatado'}
                    </span>
                </td>
                <td class="py-2.5 px-3 text-right font-bold ${isDeposit ? 'text-emerald-600' : 'text-slate-700'}">
                    ${isDeposit ? '+' : '-'} ${formatBRL(tx.amount)}
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function deletePocket(id) {
    if (!confirm("Tem certeza que deseja excluir esta caixinha? Todas as movimentações dela serão excluídas.")) return;

    try {
        await api.delete(`/pockets/${id}`);
        showToast("Caixinha excluída com sucesso.");
        loadPockets();
        loadDashboardData();
    } catch (err) {
        showToast(err.message, "error");
    }
}

