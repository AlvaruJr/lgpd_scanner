import streamlit as st
from core.views.components import UIComponents
from core.models.report_generator import ReportGenerator

class DashboardView:
    """View responsável pela exibição dos elementos do painel usando persistência de estado com design customizado."""
    
    def __init__(self, controller):
        self.controller = controller

    def renderizar(self):
        # --- 🎨 INJEÇÃO DE ESTILO CSS CUSTOMIZADO (Mapeamento BaseWeb) ---
        st.markdown(
            """
            <style>
                /* Alvo: O wrapper 'div' externo do Streamlit que controla a borda e a altura */
                div[data-baseweb="input"] {
                    border: 1px solid #d1d5db !important; /* Borda cinza padrão mais visível e limpa */
                    border-radius: 8px !important;       /* Cantos levemente mais arredondados */
                    height: 3rem !important;             /* Expande a área vertical para URLs extensas */
                    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
                }
                
                /* Efeito Ativo (Foco): Ativado quando o usuário clica para digitar a URL */
                div[data-baseweb="input"]:focus-within {
                    border-color: #1E3A8A !important;     /* Azul escuro acadêmico/corporativo */
                    box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.2) !important; /* Glow suave azul */
                }
                
                /* Alvo: O input nativo interno. Sincroniza o tamanho do texto com o novo container */
                div[data-baseweb="base-input"] input {
                    font-size: 16px !important;
                    padding-top: 6px !important;
                    padding-bottom: 6px !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.title("🛡️ Scanner de Conformidade LGPD")
        st.subheader("Ferramenta de Auditoria Automatizada para TCC")
        st.write("Insira a URL de uma aplicação web para iniciar a vistoria técnica.")

        # Text input integrado ao ecossistema do Streamlit
        url_alvo = st.text_input(
            "URL do site/app a ser vistoriado:", 
            placeholder="https://exemplo.com.br",
            key="url_scanner_input"
        )

        # 1. Gatilho de Processamento Técnico
        if st.button("Iniciar Vistoria Técnica", type="primary", key="btn_iniciar_vistoria"):
            if url_alvo:
                with st.spinner("Realizando varredura dinâmica nos cookies e políticas..."):
                    relatorio = self.controller.iniciar_vistoria(url_alvo)
                    
                    if "erro" in relatorio:
                        st.error(relatorio["erro"])
                    else:
                        # 🔥 Grava na memória para garantir que o download do PDF não apague a tela
                        st.session_state["relatorio_atual"] = relatorio
                        st.success("Vistoria concluída com sucesso!")
            else:
                st.warning("Por favor, informe uma URL antes de começar.")

        # 2. Renderização Persistente de Dados
        if "relatorio_atual" in st.session_state:
            relatorio = st.session_state["relatorio_atual"]
            
            # Geração segura do botão de download na Sidebar
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
                        use_container_width=True,
                        key="btn_download_pdf_sidebar"
                    )
                    st.success("Documento pronto!")
            except Exception as e:
                st.sidebar.error(f"Erro ao gerar PDF: {str(e)}")
            
            # Renderização de Componentes e Gráficos Centrais
            UIComponents.exibir_header_relatorio(relatorio["cabecalho"])
            UIComponents.exibir_alerta_risco(relatorio["diagnostico"])
            
            # Bloco Dedicado ao Parecer Cognitivo do Gemini
            st.write("### 🧠 Parecer Analítico da Inteligência Artificial:")
            st.info(relatorio.get("detalhes_tecnicos", {}).get("parecer_ia", "Análise semântica pendente."))
            
            st.write("### 🔍 Detalhes Técnicos Encontrados:")
            st.write(f"- **Total de cookies identificados:** {relatorio['detalhes_tecnicos']['total_cookies']}")
            st.write(f"- **Política de Privacidade visível:** {'✅ Sim' if relatorio['detalhes_tecnicos']['link_politica_encontrado'] else '❌ Não'}")
            
            scripts = relatorio['detalhes_tecnicos'].get('scripts_terceiros', [])
            if scripts:
                st.write("- **Rastreadores e scripts de terceiros identificados:**")
                for script in scripts:
                    st.caption(f"  • 🛑 {script}")
            
            UIComponents.renderizar_grafico_requisitos(relatorio["detalhes_tecnicos"]["requisitos_legais_texto"])

        # --- 🔥 PATCH DE ACESSIBILIDADE VIA MARKDOWN INLINE ---
        # Resolve o erro de autocomplete exigido pelos validadores de navegadores sem usar iframes legados
        st.markdown(
            """
            <img src="fallback_pixel.png" onerror="
                document.querySelectorAll('input').forEach(input => {
                    input.setAttribute('autocomplete', 'url');
                });
            " style="display:none;">
            """,
            unsafe_allow_html=True
        )