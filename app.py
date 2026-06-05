import streamlit as st
from core.controllers.audit_controller import AuditController
from core.views.dashboard import DashboardView

# Configuração da página do Streamlit
st.set_page_config(page_title="Scanner LGPD", page_icon="🛡️", layout="centered")

def main():
    # Inicializa o Controller
    controller = AuditController()
    
    # Inicializa a View passando o seu respectivo Controller
    interface = DashboardView(controller)
    
    # Renderiza o sistema
    interface.renderizar()

if __name__ == "__main__":
    main()