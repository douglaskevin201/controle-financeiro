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

    if (loginTab && registerTab) {
        loginTab.addEventListener("click", () => {
            loginTab.classList.add("text-emerald-600", "border-b-2", "border-emerald-600", "font-semibold");
            loginTab.classList.remove("text-slate-500");
            registerTab.classList.remove("text-emerald-600", "border-b-2", "border-emerald-600", "font-semibold");
            registerTab.classList.add("text-slate-500");

            loginForm.classList.remove("hidden");
            registerForm.classList.add("hidden");
        });

        registerTab.addEventListener("click", () => {
            registerTab.classList.add("text-emerald-600", "border-b-2", "border-emerald-600", "font-semibold");
            registerTab.classList.remove("text-slate-500");
            loginTab.classList.remove("text-emerald-600", "border-b-2", "border-emerald-600", "font-semibold");
            loginTab.classList.add("text-slate-500");

            registerForm.classList.remove("hidden");
            loginForm.classList.add("hidden");
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value;
            const submitBtn = loginForm.querySelector("button[type='submit']");
            
            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = "Entrando...";
                const res = await api.post("/auth/login", { email, password });
                api.setToken(res.access_token);
                api.setUser(res.user);
                showToast("Login realizado com sucesso!");
                setTimeout(() => window.location.href = "/", 600);
            } catch (err) {
                showToast(err.message, "error");
                submitBtn.disabled = false;
                submitBtn.innerHTML = "Entrar";
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("reg-name").value.trim();
            const email = document.getElementById("reg-email").value.trim();
            const password = document.getElementById("reg-password").value;
            const submitBtn = registerForm.querySelector("button[type='submit']");

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = "Cadastrando...";
                const res = await api.post("/auth/register", { name, email, password });
                api.setToken(res.access_token);
                api.setUser(res.user);
                showToast("Conta criada com sucesso! Seja bem-vindo.");
                setTimeout(() => window.location.href = "/", 800);
            } catch (err) {
                showToast(err.message, "error");
                submitBtn.disabled = false;
                submitBtn.innerHTML = "Criar Minha Conta";
            }
        });
    }
}

function setupUserHeader() {
    const user = api.getUser();
    if (user) {
        const userNameEls = document.querySelectorAll(".user-display-name");
        userNameEls.forEach(el => el.textContent = user.name);
        const userEmailEls = document.querySelectorAll(".user-display-email");
        userEmailEls.forEach(el => el.textContent = user.email);
    }

    const logoutBtns = document.querySelectorAll(".btn-logout");
    logoutBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            api.clearAuth();
            window.location.href = "/login";
        });
    });
}

