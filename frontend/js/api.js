const API_BASE = "/api";

const api = {
    getToken() {
        return localStorage.getItem("finance_token");
    },

    setToken(token) {
        localStorage.setItem("finance_token", token);
    },

    setUser(user) {
        localStorage.setItem("finance_user", JSON.stringify(user));
    },

    getUser() {
        const u = localStorage.getItem("finance_user");
        return u ? JSON.parse(u) : null;
    },

    clearAuth() {
        localStorage.removeItem("finance_token");
        localStorage.removeItem("finance_user");
    },

    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {})
        };

        const token = this.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);

            if (response.status === 401) {
                // Se for 401 e não estiver na tela de login, redireciona
                this.clearAuth();
                if (!window.location.pathname.includes("login")) {
                    window.location.href = "/login";
                }
                throw new Error("Sessão expirada. Faça login novamente.");
            }

            if (response.status === 204) {
                return null;
            }

            const data = await response.json();
            if (!response.ok) {
                const message = data.detail || "Ocorreu um erro no servidor.";
                throw new Error(typeof message === "string" ? message : JSON.stringify(message));
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    get(endpoint) {
        return this.request(endpoint, { method: "GET" });
    },

    post(endpoint, body) {
        return this.request(endpoint, {
            method: "POST",
            body: JSON.stringify(body)
        });
    },

    put(endpoint, body) {
        return this.request(endpoint, {
            method: "PUT",
            body: JSON.stringify(body)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: "DELETE" });
    }
};

// Toast notification helper
function showToast(message, type = "success") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "fixed bottom-5 right-5 z-50 flex flex-col gap-2";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    const colors = {
        success: "bg-emerald-600 text-white",
        error: "bg-rose-600 text-white",
        info: "bg-blue-600 text-white"
    };

    toast.className = `px-4 py-3 rounded-lg shadow-lg text-sm font-medium flex items-center gap-2 transform transition-all duration-300 translate-y-2 opacity-0 ${colors[type] || colors.info}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove("translate-y-2", "opacity-0");
    }, 10);

    setTimeout(() => {
        toast.classList.add("opacity-0", "translate-y-2");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Formatador monetário BRL
function formatBRL(value) {
    return Number(value || 0).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });
}

// Formatador de data DD/MM/AAAA
function formatDate(dateString) {
    if (!dateString) return "";
    const parts = dateString.split("-");
    if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    return dateString;
}

