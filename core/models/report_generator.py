from datetime import datetime

class ReportGenerator:
    """Model responsável por consolidar os dados da auditoria e estruturar o relatório."""
    
    def __init__(self, url_alvo, dados_cookies, dados_politica):
        self.url_alvo = url_alvo
        self.dados_cookies = dados_cookies
        self.dados_politica = dados_politica

    def gerar_dados_relatorio(self):
        # Pega as notas parciais calculadas pelos outros modelos
        score_cookies = self.dados_cookies.get("score_conformidade", 0)
        score_texto = self.dados_politica.get("score_texto", 0) if "erro" not in self.dados_politica else 0
        
        # Calcula a média da nota de conformidade
        score_final = int((score_cookies + score_texto) / 2)
        
        # Define a classificação de risco baseada na pontuação
        if score_final >= 80:
            nivel_risco = "Baixo Risco"
        elif score_final >= 50:
            nivel_risco = "Médio Risco"
        else:
            nivel_risco = "Alto Risco - Crítico"

        # Estrutura o dicionário final com o payload completo do relatório técnico
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
                "requisitos_legais_texto": self.dados_politica.get("requisitos_identificados", {})
            }
        }