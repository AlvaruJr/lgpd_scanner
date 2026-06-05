import streamlit as st
from core.views.components import UIComponents
from core.models.report_generator import ReportGenerator

class DashboardView:
    """View responsável por renderizar a interface do usuário e o painel de exportação na Sidebar."""
    
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
                    relatorio = self.controller.iniciar_vistoria(url_alvo)
                    
                    if "erro" in relatorio:
                        st.error(relatorio["erro"])
                    else:
                        st.success("Vistoria concluída com sucesso!")
                        
                        # --- 📄 GERAÇÃO DO PDF NA SIDEBAR (BARRA LATERAL) ---
                        try:
                            pdf_bytes = ReportGenerator.exportar_para_pdf(relatorio)
                            
                            with st.sidebar:
                                st.header("📄 Exportar Evidências")
                                st.write("O relatório técnico oficial foi gerado com sucesso.")
                                st.download_button(
                                    label="📥 Baixar Relatório PDF",
                                    data=pdf_bytes,
                                    file_name="relatorio_auditoria_lgpd.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                                st.success("Documento pronto!")
                        except Exception as e:
                            st.sidebar.error(f"Erro ao gerar PDF: {str(e)}")
                        
                        # 📊 Renderiza o painel visual na página central
                        UIComponents.exibir_header_relatorio(relatorio["cabecalho"])
                        UIComponents.exibir_alerta_risco(relatorio["diagnostico"])
                        
                        st.write("### 🔍 Detalhes Técnicos Encontrados:")
                        st.write(f"- **Total de cookies identificados:** {relatorio['detalhes_tecnicos']['total_cookies']}")
                        st.write(f"- **Política de Privacidade visível:** {'✅ Sim' if relatorio['detalhes_tecnicos']['link_politica_encontrado'] else '❌ Não'}")
                        
                        scripts = relatorio['detalhes_tecnicos'].get('scripts_terceiros', [])
                        if scripts:
                            st.write("- **Rastreadores e scripts de terceiros identificados:**")
                            for script in scripts:
                                st.caption(f"  • 🛑 {script}")
                        
                        UIComponents.renderizar_grafico_requisitos(relatorio["detalhes_tecnicos"]["requisitos_legais_texto"])
            else:
                st.warning("Por favor, informe uma URL antes de começar.")