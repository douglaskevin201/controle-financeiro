# 💰 Sistema de Controle Financeiro Pessoal

Um aplicativo web moderno, completo e intuitivo para controle e organização financeira pessoal. Construído com **FastAPI**, **SQLAlchemy**, **SQLite**, **TailwindCSS** e **Chart.js**.

---

## 🌟 Principais Funcionalidades

### 1. 📊 Controle Financeiro Básico
- **Receitas e Despesas**: Cadastro simplificado com data, categoria, descrição e valor.
- **Categorização Automática & Personalizada**: Categorias padrão criadas automaticamente (Alimentação, Moradia, Transporte, Lazer, Salário, etc.) com cores e ícones, além de suporte a novas categorias criadas pelo usuário.
- **Visão Geral e Histórico**: Dashboard com saldo atual disponível, total de receitas, total de despesas e evolução mês a mês.

### 2. 📅 Contas Recorrentes & Assinaturas (Compromissos Fixos)
- Cadastro de despesas fixas (Aluguel, Internet, Netflix, Academia) com dia de vencimento.
- **Status em Tempo Real**: Identificação automática de contas pagas e pendentes no mês selecionado.
- **Baixa com 1 Clique**: Marcar conta como paga gera automaticamente uma transação de despesa correspondente e atualiza o saldo.

### 3. 📦 Caixinhas de Reserva (Objetivos Separados)
- Crie múltiplas caixinhas nomeadas (ex: *"Reserva de Emergência"*, *"Viagem de Férias"*, *"Comprar Carro"*).
- **Metas e Progresso**: Defina uma meta opcional e visualize a barra de progresso e porcentagem de alcance.
- **Isolamento de Saldo**: O dinheiro guardado na caixinha sai do saldo disponível do dia a dia e fica protegido.
- **Guardar & Resgatar**: Movimente valores facilmente com histórico detalhado de depósitos e retiradas.

### 4. 📈 Gráficos e Relatórios
- **Gráfico de Rosca**: Distribuição percentual das despesas por categoria.
- **Gráfico de Barras**: Comparativo de entradas vs. saídas ao longo dos 12 meses do ano.

---

## 🛠️ Tecnologias Utilizadas

- **Back-end**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic, Passlib, Bcrypt, Python-JOSE (JWT).
- **Banco de Dados**: SQLite (`finance.db`) - Armazenamento local leve, rápido e sem necessidade de instalar servidores SQL externos.
- **Front-end**: HTML5, TailwindCSS (responsivo para Desktop e Mobile), Vanilla JavaScript modular, Chart.js.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.10 ou superior instalado.

### Passo 1: Criar o ambiente virtual e instalar dependências

No terminal (PowerShell ou Bash), dentro da pasta do projeto:

```powershell
# Criação do ambiente virtual
python -m venv venv

# Ativação do ambiente virtual
# No Windows PowerShell:
.\venv\Scripts\Activate.ps1
# No Linux/Mac:
source venv/bin/activate

# Instalação das dependências
pip install -r backend/requirements.txt
```

### Passo 2: Iniciar a Aplicação

Você pode iniciar o servidor de duas formas:

**Opção 1: Via script facilitador:**
```powershell
python bolso.py
```

**Opção 2: Via Uvicorn diretamente:**
```powershell
uvicorn backend.app.main:app --reload --port 8000
```

### Passo 3: Acessar no Navegador

- **Aplicação Web (Dashboard)**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentação Interativa da API (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Como Executar os Testes Automatizados

Para rodar a suíte de testes de integração:

```powershell
pytest tests/ -v
```

---

## 📂 Estrutura do Projeto

```
teste_google/
├── backend/
│   ├── app/
│   │   ├── main.py                  # Ponto de entrada FastAPI e rotas estáticas
│   │   ├── config.py                # Configurações gerais e JWT
│   │   ├── database.py              # Conexão SQLAlchemy e sessão do SQLite
│   │   ├── models/                  # Tabelas do banco de dados (ORM)
│   │   ├── schemas/                 # Esquemas de validação Pydantic
│   │   ├── routers/                 # Endpoints REST (auth, dashboard, tx, pockets, bills)
│   │   ├── services/                # Regras de negócio e sementes iniciais
│   │   └── utils/                   # Utilitários de segurança (hashing e tokens)
│   └── requirements.txt
├── frontend/
│   ├── index.html                   # Painel principal unificado (SPA)
│   ├── login.html                   # Tela de login e cadastro de usuários
│   ├── css/custom.css               # Estilos complementares
│   └── js/                          # Módulos JS (api, auth, dashboard, transactions, etc.)
├── tests/                           # Testes automatizados com Pytest e SQLite em memória
├── bolso.py                         # Launcher rápido
├── pytest.ini
└── README.md
```

