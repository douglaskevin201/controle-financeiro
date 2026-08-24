def test_register_and_login(client):
    # Registro
    res = client.post("/api/auth/register", json={
        "name": "Kevin Silva",
        "email": "kevin@teste.com",
        "password": "senhaSegura123"
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "kevin@teste.com"

    # Login
    res_login = client.post("/api/auth/login", json={
        "email": "kevin@teste.com",
        "password": "senhaSegura123"
    })
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()

    # Verifica se as categorias padrão foram criadas
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    res_cat = client.get("/api/categories", headers=headers)
    assert res_cat.status_code == 200
    assert len(res_cat.json()) >= 10

def test_transactions_flow(client, auth_headers):
    # 1. Adiciona uma receita de Salário (R$ 5000)
    res_inc = client.post("/api/transactions", headers=auth_headers, json={
        "description": "Salário Mensal",
        "amount": 5000.0,
        "type": "income",
        "transaction_date": "2026-08-01"
    })
    assert res_inc.status_code == 201
    inc_data = res_inc.json()
    assert inc_data["amount"] == 5000.0

    # 2. Adiciona uma despesa de Supermercado (R$ 650)
    res_exp = client.post("/api/transactions", headers=auth_headers, json={
        "description": "Supermercado do mês",
        "amount": 650.0,
        "type": "expense",
        "transaction_date": "2026-08-05"
    })
    assert res_exp.status_code == 201

    # 3. Lista as transações
    res_list = client.get("/api/transactions", headers=auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 2

def test_recurring_bills_flow(client, auth_headers):
    # 1. Cria conta fixa de Aluguel (R$ 1500, dia 10)
    res_bill = client.post("/api/recurring-bills", headers=auth_headers, json={
        "description": "Aluguel Apartamento",
        "amount": 1500.0,
        "due_day": 10
    })
    assert res_bill.status_code == 201
    bill_id = res_bill.json()["id"]

    # 2. Lista contas do mês
    res_list = client.get("/api/recurring-bills?month=8&year=2026", headers=auth_headers)
    assert res_list.status_code == 200
    assert res_list.json()[0]["is_paid_this_month"] is False

    # 3. Paga a conta fixa
    res_pay = client.post(f"/api/recurring-bills/{bill_id}/pay?month=8&year=2026", headers=auth_headers, json={
        "create_transaction": True
    })
    assert res_pay.status_code == 200
    assert res_pay.json()["is_paid_this_month"] is True

    # 4. Verifica se gerou a transação correspondente
    res_tx = client.get("/api/transactions?month=8&year=2026", headers=auth_headers)
    txs = res_tx.json()
    assert any("Aluguel" in t["description"] and t["amount"] == 1500.0 for t in txs)

    # 5. Desfaz pagamento
    res_unpay = client.post(f"/api/recurring-bills/{bill_id}/unpay?month=8&year=2026", headers=auth_headers, json={})
    assert res_unpay.status_code == 200
    assert res_unpay.json()["is_paid_this_month"] is False

def test_pockets_flow(client, auth_headers):
    # 1. Cria caixinha "Viagem Japão" com meta de R$ 10.000 e depósito inicial de R$ 1.000
    res_pocket = client.post("/api/pockets", headers=auth_headers, json={
        "name": "Viagem Japão",
        "target_amount": 10000.0,
        "initial_deposit": 1000.0,
        "color": "#3B82F6"
    })
    assert res_pocket.status_code == 201
    p_data = res_pocket.json()
    pocket_id = p_data["id"]
    assert p_data["current_amount"] == 1000.0
    assert p_data["progress_percentage"] == 10.0

    # 2. Deposita mais R$ 1.500 na caixinha
    res_dep = client.post(f"/api/pockets/{pocket_id}/transfer", headers=auth_headers, json={
        "type": "deposit",
        "amount": 1500.0,
        "description": "Economia de Agosto"
    })
    assert res_dep.status_code == 200
    assert res_dep.json()["current_amount"] == 2500.0
    assert res_dep.json()["progress_percentage"] == 25.0

    # 3. Resgata R$ 500 da caixinha
    res_with = client.post(f"/api/pockets/{pocket_id}/transfer", headers=auth_headers, json={
        "type": "withdraw",
        "amount": 500.0,
        "description": "Resgate parcial"
    })
    assert res_with.status_code == 200
    assert res_with.json()["current_amount"] == 2000.0

    # 4. Tenta resgatar mais do que possui (R$ 5.000) -> Deve falhar com 400
    res_fail = client.post(f"/api/pockets/{pocket_id}/transfer", headers=auth_headers, json={
        "type": "withdraw",
        "amount": 5000.0
    })
    assert res_fail.status_code == 400
    assert "insuficiente" in res_fail.json()["detail"].lower()

    # 5. Consulta o histórico da caixinha
    res_hist = client.get(f"/api/pockets/{pocket_id}/transactions", headers=auth_headers)
    assert res_hist.status_code == 200
    assert len(res_hist.json()) == 3  # Depósito inicial + Depósito + Resgate

def test_dashboard_summary_calculation(client, auth_headers):
    # Cenário:
    # Receita: +R$ 10.000
    # Despesa: -R$ 2.000
    # Caixinha: Depósito de R$ 3.000
    # Saldo Principal deve ser: 10.000 - 2.000 - 3.000 = R$ 5.000
    # Total em Caixinhas: R$ 3.000
    # Patrimônio Total: R$ 8.000

    client.post("/api/transactions", headers=auth_headers, json={
        "description": "Salário",
        "amount": 10000.0,
        "type": "income",
        "transaction_date": "2026-08-01"
    })

    client.post("/api/transactions", headers=auth_headers, json={
        "description": "Compras",
        "amount": 2000.0,
        "type": "expense",
        "transaction_date": "2026-08-02"
    })

    client.post("/api/pockets", headers=auth_headers, json={
        "name": "Reserva de Emergência",
        "target_amount": 20000.0,
        "initial_deposit": 3000.0
    })

    # Consulta o dashboard
    res_dash = client.get("/api/dashboard/summary?month=8&year=2026", headers=auth_headers)
    assert res_dash.status_code == 200
    dash = res_dash.json()

    assert dash["main_balance"] == 5000.0
    assert dash["total_in_pockets"] == 3000.0
    assert dash["total_wealth"] == 8000.0
    assert dash["monthly_income"] == 10000.0
    assert dash["monthly_expense"] == 2000.0
    assert dash["monthly_net"] == 8000.0

