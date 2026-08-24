import os
import sys
import subprocess
import webbrowser
import time
import threading

# Garante suporte a UTF-8 no terminal do Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def ensure_environment():
    """Garante que o script execute usando o interpretador do ambiente virtual (venv)"""
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Caminho do executável do venv
    if sys.platform == "win32":
        venv_python = os.path.join(workspace_dir, "venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(workspace_dir, "venv", "bin", "python")

    # Se já estamos rodando no venv, segue em frente
    if sys.executable.lower() == venv_python.lower():
        return

    # Se o venv existe mas o script foi chamado pelo python global (ex: 'python bolso.py')
    if os.path.exists(venv_python):
        print(f"[+] Redirecionando execucao para o ambiente virtual ({venv_python})...\n")
        try:
            sys.exit(subprocess.call([venv_python] + sys.argv))
        except Exception as e:
            print(f"[-] Erro ao alternar para o venv: {e}")

    # Se o venv não existe, cria e instala dependências automaticamente
    else:
        print("[+] Criando ambiente virtual e instalando dependencias...")
        subprocess.check_call([sys.executable, "-m", "venv", os.path.join(workspace_dir, "venv")])
        
        pip_exe = os.path.join(workspace_dir, "venv", "Scripts", "pip.exe") if sys.platform == "win32" else os.path.join(workspace_dir, "venv", "bin", "pip")
        req_file = os.path.join(workspace_dir, "backend", "requirements.txt")
        
        subprocess.check_call([pip_exe, "install", "-r", req_file])
        print("[+] Ambiente configurado com sucesso! Iniciando...\n")
        sys.exit(subprocess.call([venv_python] + sys.argv))

def open_browser_delayed(url):
    time.sleep(1.5)
    try:
        webbrowser.open(url)
    except Exception:
        pass

def main():
    ensure_environment()

    import uvicorn

    url = "http://127.0.0.1:8000"
    swagger_url = "http://127.0.0.1:8000/docs"

    print("=" * 65)
    print(" >>> SISTEMA DE CONTROLE FINANCEIRO PESSOAL INICIADO! <<<")
    print("=" * 65)
    print(f" [*] Aplicacao Web: {url}")
    print(f" [*] Documentacao Swagger da API: {swagger_url}")
    print("=" * 65)
    print(" [*] Abrindo o navegador automaticamente em instantes...")
    print(" [*] Pressione Ctrl+C para encerrar o servidor.")
    print("=" * 65)

    # Abre o navegador em uma thread separada
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    # Inicia o servidor uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
