import streamlit as st
import pandas as pd

class UIComponents:
    """Classe utilitária com componentes visuais reutilizáveis para a interface."""
    
    @staticmethod
    def exibir_header_relatorio(cabecalho):
        st.markdown("---")
        st.write(f"⏱️ **Data da Vistoria:** {cabecalho['data_auditoria']}")
        st.write(f"🔗 **URL Analisada:** `{cabecalho['url_vistoriada']}`")
        st.markdown("---")

    @staticmethod
    def exibir_alerta_risco(diagnostico):
        score = diagnostico["score_geral"]
        risco = diagnostico["nivel_risco"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Score Geral LGPD", value=f"{score} / 100")
            
        with col2:
            if score >= 80:
                st.success(f"🛡️ Classificação: **{risco}**")
            elif score >= 50:
                st.warning(f"⚠️ Classificação: **{risco}**")
            else:
                st.error(f"🚨 Classificação: **{risco}**")

    @staticmethod
    def renderizar_grafico_requisitos(requisitos):
        if not requisitos:
            st.info("Nenhum dado textual de política para mapear graficamente.")
            return
            
        st.write("### 📊 Mapeamento de Cláusulas Obrigatórias:")
        
        # Converte o dicionário de booleanos em um DataFrame para o Streamlit ler
        dados_df = pd.DataFrame({
            "Cláusula/Requisito": list(requisitos.keys()),
            "Identificado": ["Conforme ✅" if v else "Ausente ❌" for v in requisitos.values()]
        })
        
        st.table(dados_df)