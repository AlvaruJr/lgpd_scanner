import streamlit as st
import subprocess
import sys

# Configuração da página do Streamlit (obrigatoriamente o primeiro comando)
st.set_page_config(page_title="Scanner LGPD", page_icon="🛡️", layout="centered")

# --- 🛡️ VALIDADOR DE EXTENSÕES E DEPENDÊNCIAS ---
try:
    # Tenta carregar os módulos centrais do projeto
    from core.controllers.audit_controller import AuditController
    from core.views.dashboard import DashboardView
    extensoes_prontas = True
except ModuleNotFoundError as e:
    extensoes_prontas = False
    modulo_faltante = getattr(e, 'name', str(e))

def main():
    global extensoes_prontas
    
    # Se alguma extensão falhar, força a instalação automática em segundo plano
    if not extensoes_prontas:
        st.warning(f"⚠️ O módulo **'{modulo_faltante}'** não foi localizado no ambiente.")
        
        with st.spinner("📦 Forçando a instalação das dependências do TCC automaticamente..."):
            try:
                # Dispara o pip install usando o caminho exato do executável Python ativo
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                
                # Se a extensão que quebrou foi o playwright, já puxa o gatilho dos navegadores internos
                if "playwright" in modulo_faltante.lower():
                    subprocess.check_call([sys.executable, "-m", "playwright", "install"])
                
                st.success("✅ Todas as dependências e extensões foram instaladas com sucesso!")
                
                # Altera a flag e força o Streamlit a recarregar o arquivo do zero
                extensoes_prontas = True
                st.info("Reiniciando a aplicação, aguarde...")
                st.rerun()
                
            except Exception as erro_instalacao:
                st.error("❌ **Falha Crítica na Instalação Automática**")
                st.write(f"Ocorreu um erro ao tentar rodar o instalador: `{str(erro_instalacao)}`")
                st.info("Por favor, execute manualmente no terminal: `pip install -r requirements.txt`")
                return # Interrompe o fluxo para não estourar a tela vermelha original

    # --- FLUXO NORMAL DO SISTEMA ---
    # Inicializa o Controller
    controller = AuditController()
    
    # Inicializa a View passando o seu respectivo Controller
    interface = DashboardView(controller)
    
    # Renderiza o sistema
    interface.renderizar()

if __name__ == "__main__":
    main()