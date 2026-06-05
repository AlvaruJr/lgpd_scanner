from datetime import datetime
from fpdf import FPDF

class ReportGenerator:
    """Model responsável por consolidar os dados e exportar o Relatório Técnico em PDF."""
    
    def __init__(self, url_alvo, dados_cookies, dados_politica):
        self.url_alvo = url_alvo
        self.dados_cookies = dados_cookies
        self.dados_politica = dados_politica

    def gerar_dados_relatorio(self):
        score_cookies = self.dados_cookies.get("score_conformidade", 0)
        score_texto = self.dados_politica.get("score_texto", 0) if "erro" not in self.dados_politica else 0
        score_final = int((score_cookies + score_texto) / 2)
        
        if score_final >= 80:
            nivel_risco = "Baixo Risco"
        elif score_final >= 50:
            nivel_risco = "Medio Risco"
        else:
            nivel_risco = "Alto Risco - Critico"

        return {
            "cabecalho": {
                "sistema": "Scanner de Conformidade LGPD v1.0",
                "data_auditoria": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "url_vistoriada": self.url_alvo
            },
            "diagnostico": {
                "score_geral": score_final,
                "nivel_risco": nivel_risco
            },
            "detalhes_tecnicos": {
                "total_cookies": self.dados_cookies.get("cookies_encontrados", 0),
                "link_politica_encontrado": self.dados_cookies.get("politica_encontrada", False),
                "requisitos_legais_texto": self.dados_politica.get("requisitos_identificados", {}),
                "scripts_terceiros": self.dados_cookies.get("scripts_terceiros", []),
                # 🔥 CORREÇÃO ESSENCIAL: Repassa o parecer obtido pelo PolicyAnalyzer para a View
                "parecer_ia": self.dados_politica.get("parecer_ia", "Analise de conteudo indisponivel.")
            }
        }

    @staticmethod
    def exportar_para_pdf(payload):
        """Desenha o PDF do relatório técnico sem caracteres especiais."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        
        pdf.set_font("Helvetica", "B", size=16)
        pdf.cell(200, 10, txt="RELATORIO TECNICO DE AUDITORIA - LGPD", ln=True, align="C")
        pdf.set_font("Helvetica", size=10)
        pdf.cell(200, 10, txt=f"Gerado por: {payload['cabecalho']['sistema']}", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Helvetica", "B", size=12)
        pdf.cell(200, 8, txt="1. Resumo da Vistoria", ln=True)
        pdf.set_font("Helvetica", size=11)
        pdf.cell(200, 6, txt=f"Data de Execucao: {payload['cabecalho']['data_auditoria']}", ln=True)
        pdf.cell(200, 6, txt=f"URL Analisada: {payload['cabecalho']['url_vistoriada']}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", size=12)
        pdf.cell(200, 8, txt="2. Avaliacao de Conformidade", ln=True)
        pdf.set_font("Helvetica", size=11)
        pdf.cell(200, 6, txt=f"Score Geral Obtido: {payload['diagnostico']['score_geral']} / 100", ln=True)
        pdf.cell(200, 6, txt=f"Grau de Risco Legal: {payload['diagnostico']['nivel_risco']}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", size=12)
        pdf.cell(200, 8, txt="3. Evidencias Coletadas em Rede", ln=True)
        pdf.set_font("Helvetica", size=11)
        pdf.cell(200, 6, txt=f"Cookies disparados no carregamento: {payload['detalhes_tecnicos']['total_cookies']}", ln=True)
        politica_ok = "Identificada" if payload['detalhes_tecnicos']['link_politica_encontrado'] else "Ausente"
        pdf.cell(200, 6, txt=f"Link de Politica de Privacidade: {politica_ok}", ln=True)
        
        scripts = payload['detalhes_tecnicos'].get('scripts_terceiros', [])
        if scripts:
            pdf.cell(200, 6, txt="Scripts e Rastreadores externos mapeados:", ln=True)
            pdf.set_font("Helvetica", "I", size=10)
            for s in scripts:
                s_limpo = s.replace(chr(8212), "-").replace("—", "-")
                pdf.cell(200, 5, txt=f"  * {s_limpo}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", size=12)
        pdf.cell(200, 8, txt="4. Verificacao de Clausulas Obrigatorias", ln=True)
        pdf.set_font("Helvetica", size=11)
        
        requisitos = payload['detalhes_tecnicos']['requisitos_legais_texto']
        if requisitos:
            for req, status in requisitos.items():
                status_txt = "CONFORME" if status else "AUSENTE"
                req_limpo = str(req)
                for char in ["🤖", "📊", "🛡️", "—", "–"]:
                    req_limpo = req_limpo.replace(char, "")
                req_limpo = req_limpo.strip()
                
                pdf.cell(200, 6, txt=f"- {req_limpo}: {status_txt}", ln=True)
        else:
            pdf.cell(200, 6, txt="Nao foi possivel ler as clausulas textuais (Politica Ausente).", ln=True)
            
        return bytes(pdf.output())