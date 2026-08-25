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

def test_fixed_income_receipt_is_idempotent_and_supports_extra(client, auth_headers):
    res_income = client.post("/api/fixed-incomes", headers=auth_headers, json={
        "description": "Salário mensal",
        "base_amount": 5000.0,
        "pay_day": 5
    })
    assert res_income.status_code == 201
    income_id = res_income.json()["id"]

    first = client.post(f"/api/fixed-incomes/{income_id}/receive?month=8&year=2026", headers=auth_headers, json={
        "extra_amount": 300.0,
        "paid_date": "2026-08-05"
    })
    assert first.status_code == 200
    assert first.json()["receipt"]["received_amount"] == 5300.0

    second = client.post(f"/api/fixed-incomes/{income_id}/receive?month=8&year=2026", headers=auth_headers, json={
        "extra_amount": 700.0,
        "paid_date": "2026-08-05"
    })
    assert second.status_code == 200
    assert second.json()["receipt"]["received_amount"] == 5700.0

    transactions = client.get("/api/transactions?month=8&year=2026", headers=auth_headers)
    assert transactions.status_code == 200
    assert len(transactions.json()) == 1
    assert transactions.json()[0]["amount"] == 5700.0

    dashboard = client.get("/api/dashboard/summary?month=8&year=2026", headers=auth_headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["fixed_income_expected"] == 5000.0

def test_installments_and_next_month_projection(client, auth_headers):
    bill = client.post("/api/recurring-bills", headers=auth_headers, json={
        "description": "Compra parcelada",
        "amount": 500.0,
        "total_amount": 500.0,
        "installments_total": 2,
        "due_day": 10,
        "start_month": 8,
        "start_year": 2026
    })
    assert bill.status_code == 201
    assert bill.json()["amount"] == 250.0
    assert bill.json()["total_amount"] == 500.0

    next_month = client.get("/api/dashboard/projection?month=8&year=2026", headers=auth_headers)
    assert next_month.status_code == 200
    assert next_month.json()["projection_month"] == 9
    assert next_month.json()["recurring_bills_expected"] == 250.0

    planned = client.post("/api/transactions", headers=auth_headers, json={
        "description": "Compra planejada",
        "amount": 100.0,
        "type": "expense",
        "is_planned": True,
        "transaction_date": "2026-09-15"
    })
    assert planned.status_code == 201
    projection_with_plan = client.get("/api/dashboard/projection?month=8&year=2026", headers=auth_headers)
    assert projection_with_plan.json()["planned_expense"] == 100.0
    assert projection_with_plan.json()["projected_net"] == -350.0

    current = client.get("/api/dashboard/summary?month=8&year=2026", headers=auth_headers)
    assert current.status_code == 200
    assert current.json()["monthly_expense"] == 0.0

    after_installments = client.get("/api/recurring-bills?month=10&year=2026", headers=auth_headers)
    assert after_installments.status_code == 200
    assert after_installments.json() == []

