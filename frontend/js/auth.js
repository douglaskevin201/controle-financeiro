document.addEventListener("DOMContentLoaded", () => {
    const isLoginPage = window.location.pathname.includes("login");
    const token = api.getToken();

    if (!token && !isLoginPage) {
        window.location.href = "/login";
        return;
    }

    if (token && isLoginPage) {
        window.location.href = "/";
        return;
    }

    if (isLoginPage) {
        setupLoginView();
    } else {
        setupUserHeader();
    }
});

function setupLoginView() {
    const loginTab = document.getElementById("tab-login");
    const registerTab = document.getElementById("tab-register");
    const loginForm = document.getElementById("form-login");
    const registerForm = document.getElementById("form-register");
    const linkToRegister = document.getElementById("link-to-register");
    const linkToLogin = document.getElementById("link-to-login");
    const forgotPasswordBtn = document.getElementById("btn-forgot-password");

    // Funções de alternância de abas
    function activateTab(tab) {
        if (tab === "login") {
            // Estilos do botão de aba ativo
            loginTab.className = "flex-1 py-2.5 text-center text-sm font-semibold rounded-xl transition-all duration-200 bg-white text-slate-900 shadow-sm";
            registerTab.className = "flex-1 py-2.5 text-center text-sm font-medium rounded-xl transition-all duration-200 text-slate-500 hover:text-slate-800";
            
            // Exibição dos formulários
            loginForm.classList.remove("hidden");
            registerForm.classList.add("hidden");
            
            // Foco automático no e-mail de login
            const emailInput = document.getElementById("login-email");
            if (emailInput) emailInput.focus();
        } else {
            // Estilos do botão de aba ativo
            registerTab.className = "flex-1 py-2.5 text-center text-sm font-semibold rounded-xl transition-all duration-200 bg-white text-slate-900 shadow-sm";
            loginTab.className = "flex-1 py-2.5 text-center text-sm font-medium rounded-xl transition-all duration-200 text-slate-500 hover:text-slate-800";
            
            // Exibição dos formulários
            registerForm.classList.remove("hidden");
            loginForm.classList.add("hidden");
            
            // Foco automático no nome de cadastro
            const nameInput = document.getElementById("reg-name");
            if (nameInput) nameInput.focus();
        }
    }

    if (loginTab) loginTab.addEventListener("click", () => activateTab("login"));
    if (registerTab) registerTab.addEventListener("click", () => activateTab("register"));
    if (linkToRegister) linkToRegister.addEventListener("click", () => activateTab("register"));
    if (linkToLogin) linkToLogin.addEventListener("click", () => activateTab("login"));

    // Recuperação de senha (microtexto interativo)
    if (forgotPasswordBtn) {
        forgotPasswordBtn.addEventListener("click", () => {
            showToast("Para redefinir sua senha, solicite suporte ou crie uma nova conta com outro e-mail.", "info");
        });
    }

    // Configuração dos botões de mostrar/ocultar senha (Eye Toggle)
    setupPasswordVisibilityToggles();

    // Envio do formulário de Login
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value;
            const submitBtn = loginForm.querySelector("button[type='submit']");
            
            setButtonLoading(submitBtn, true, "Entrando...");
            
            try {
                const res = await api.post("/auth/login", { email, password });
                api.setToken(res.access_token);
                api.setUser(res.user);
                showToast("Login realizado com sucesso! Bem-vindo de volta.");
                setTimeout(() => window.location.href = "/", 600);
            } catch (err) {
                showToast(err.message, "error");
                setButtonLoading(submitBtn, false, "Entrar");
            }
        });
    }

    // Envio do formulário de Cadastro
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("reg-name").value.trim();
            const email = document.getElementById("reg-email").value.trim();
            const password = document.getElementById("reg-password").value;
            const submitBtn = registerForm.querySelector("button[type='submit']");

            if (password.length < 6) {
                showToast("A senha deve conter no mínimo 6 caracteres.", "error");
                return;
            }

            setButtonLoading(submitBtn, true, "Criando conta...");

            try {
                const res = await api.post("/auth/register", { name, email, password });
                api.setToken(res.access_token);
                api.setUser(res.user);
                showToast("Conta criada com sucesso! Seja bem-vindo.");
                setTimeout(() => window.location.href = "/", 800);
            } catch (err) {
                showToast(err.message, "error");
                setButtonLoading(submitBtn, false, "Criar Minha Conta");
            }
        });
    }
}

// Configura o toggle de visualização de senha
function setupPasswordVisibilityToggles() {
    const toggleBtns = document.querySelectorAll(".toggle-password-btn");
    
    toggleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            const input = document.getElementById(targetId);
            if (!input) return;

            const iconEye = btn.querySelector(".icon-eye");
            const iconEyeOff = btn.querySelector(".icon-eye-off");

            if (input.type === "password") {
                input.type = "text";
                if (iconEye) iconEye.classList.add("hidden");
                if (iconEyeOff) iconEyeOff.classList.remove("hidden");
            } else {
                input.type = "password";
                if (iconEye) iconEye.classList.remove("hidden");
                if (iconEyeOff) iconEyeOff.classList.add("hidden");
            }
        });
    });
}

// Controle de estado de carregamento do botão com spinner
function setButtonLoading(button, isLoading, text) {
    if (!button) return;
    const spinner = button.querySelector(".btn-spinner");
    const textEl = button.querySelector(".btn-text");

    button.disabled = isLoading;

    if (isLoading) {
        if (spinner) spinner.classList.remove("hidden");
        if (textEl) textEl.textContent = text;
    } else {
        if (spinner) spinner.classList.add("hidden");
        if (textEl) textEl.textContent = text;
    }
}

function setupUserHeader() {
    const user = api.getUser();
    if (user) {
        const userNameEls = document.querySelectorAll(".user-display-name");
        userNameEls.forEach(el => el.textContent = user.name);

        const userEmailEls = document.querySelectorAll(".user-display-email");
        userEmailEls.forEach(el => el.textContent = user.email);

        // Iniciais para o avatar
        const initialsEls = document.querySelectorAll(".user-display-initials");
        if (user.name) {
            const parts = user.name.trim().split(/\s+/);
            const initials = parts.length > 1 
                ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() 
                : parts[0].slice(0, 2).toUpperCase();
            initialsEls.forEach(el => el.textContent = initials);
        }
    }

    const logoutBtns = document.querySelectorAll(".btn-logout");
    logoutBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            api.clearAuth();
            window.location.href = "/login";
        });
    });
}
