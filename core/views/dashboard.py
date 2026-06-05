import streamlit as st
from core.views.components import UIComponents

class DashboardView:
    """View responsável por renderizar a interface do usuário."""
    
    def __init__(self, controller):
        self.controller = controller

    def renderizar(self):
        st.title("🛡️ Scanner de Conformidade LGPD")
        st.subheader("Ferramenta de Auditoria Automatizada para TCC")
        st.write("Insira a URL de uma aplicação web para iniciar a vistoria técnica.")

        # Campo de entrada de URL
        url_alvo = st.text_input("URL do site/app a ser vistoriado:", placeholder="https://exemplo.com.br")

        if st.button("Iniciar Vistoria Técnica", type="primary"):
            if url_alvo:
                with st.spinner("Realizando varredura dinâmica nos cookies e políticas..."):
                    # Chama o controller para processar o fluxo completo
                    relatorio = self.controller.iniciar_vistoria(url_alvo)
                    
                    if "erro" in relatorio:
                        st.error(relatorio["erro"])
                    else:
                        st.success("Vistoria concluída com sucesso!")
                        
                        # 📊 Usa os componentes visuais para renderizar o cabeçalho e o score
                        UIComponents.exibir_header_relatorio(relatorio["cabecalho"])
                        UIComponents.exibir_alerta_risco(relatorio["diagnostico"])
                        
                        st.write("### 🔍 Detalhes Técnicos Encontrados:")
                        st.write(f"- **Total de cookies identificados:** {relatorio['detalhes_tecnicos']['total_cookies']}")
                        st.write(f"- **Política de Privacidade visível:** {'✅ Sim' if relatorio['detalhes_tecnicos']['link_politica_encontrado'] else '❌ Não'}")
                        
                        # 🔥 NOVO: Mostra os scripts de terceiros capturados pelo Playwright
                        scripts = relatorio['detalhes_tecnicos'].get('scripts_terceiros', [])
                        if scripts:
                            st.write("- **Rastreadores e scripts de terceiros identificados:**")
                            for script in scripts:
                                st.caption(f"  • 🛑 {script}")
                        else:
                            st.write("- **Rastreadores e scripts de terceiros:** ✨ Nenhum rastreador comum identificado.")
                        
                        # Mostra a tabela com os requisitos da LGPD textuais
                        UIComponents.renderizar_grafico_requisitos(relatorio["detalhes_tecnicos"]["requisitos_legais_texto"])
            else:
                st.warning("Por favor, informe uma URL antes de começar.")