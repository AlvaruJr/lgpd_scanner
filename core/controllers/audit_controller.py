from core.models.cookie_scout import CookieScout
from core.models.policy_analyzer import PolicyAnalyzer
from core.models.report_generator import ReportGenerator

class AuditController:
    """Controller que coordena o fluxo de auditoria entre os Models e as Views."""
    
    def __init__(self):
        pass

    def iniciar_vistoria(self, url):
        if not url.startswith("http"):
            return {"erro": "URL inválida. Certifique-se de incluir http:// ou https://"}
            
        # 1. Executa a varredura técnica de cookies e links
        scout = CookieScout(url)
        dados_cookies = scout.inspecionar_site()
        if "erro" in dados_cookies:
            return dados_cookies
            
        # Regra de negócio do Score Técnico
        score_tec = 100
        if dados_cookies["cookies_encontrados"] > 0:
            score_tec -= 30
        if not dados_cookies["politica_encontrada"]:
            score_tec -= 40
        dados_cookies["score_conformidade"] = max(score_tec, 0)
        
        # 2. Executa a análise textual da política de privacidade (Se link for encontrado)
        # Para fins de teste/protótipo, se o site não tiver política, simulamos a varredura na própria home ou passamos vazio
        url_politica = url if dados_cookies["politica_encontrada"] else None
        analyzer = PolicyAnalyzer(url_politica)
        dados_politica = analyzer.analisar_texto_politica()
        
        # 3. Consolida e gera a estrutura do relatório técnico
        report_engine = ReportGenerator(url, dados_cookies, dados_politica)
        relatorio_final = report_engine.gerar_dados_relatorio()
        
        return relatorio_final