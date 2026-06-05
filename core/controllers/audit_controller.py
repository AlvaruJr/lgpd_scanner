from core.models.cookie_scout import CookieScout
from core.models.policy_analyzer import PolicyAnalyzer
from core.models.report_generator import ReportGenerator

class AuditController:
    """Controller que coordena o fluxo avançado de auditoria entre Models e Views."""
    
    def __init__(self):
        pass

    def iniciar_vistoria(self, url):
        # Validação inicial da URL
        if not url or not url.startswith("http"):
            return {"erro": "URL inválida. Certifique-se de incluir http:// ou https://"}
            
        # 1. Executa a varredura dinâmica com Playwright
        scout = CookieScout(url)
        dados_cookies = scout.inspecionar_site()
        
        # Se o dicionário vier vazio, nulo ou contiver erro, interrompe antes de calcular os scores
        if not dados_cookies or "erro" in dados_cookies:
            return dados_cookies if dados_cookies else {"erro": "Falha desconhecida na varredura."}
            
        # Regra de negócio avançada para o Score Técnico
        score_tec = 100
        
        # Pegando valores de forma segura com .get() para evitar KeyError se a chave não existir
        cookies_encontrados = dados_cookies.get("cookies_encontrados", 0)
        scripts_terceiros = dados_cookies.get("scripts_terceiros", [])
        politica_encontrada = dados_cookies.get("politica_encontrada", False)
        
        # Penaliza baseado na quantidade de cookies ativos sem consentimento
        if cookies_encontrados > 0:
            score_tec -= min(cookies_encontrados * 2, 20)
            
        # Penaliza fortemente se encontrar scripts de rastreamento de terceiros (ex: Meta Pixel)
        if len(scripts_terceiros) > 0:
            score_tec -= 20
            
        # Penaliza se não encontrar link visível de política
        if not politica_encontrada:
            score_tec -= 40
            
        dados_cookies["score_conformidade"] = max(score_tec, 0)
        
        # 2. Executa a análise textual da política de privacidade (Se ela existir)
        url_politica = url if politica_encontrada else None
        analyzer = PolicyAnalyzer(url_politica)
        dados_politica = analyzer.analisar_texto_politica()
        
        # 3. Consolida os dados e gera o payload final estruturado do relatório técnico
        report_engine = ReportGenerator(url, dados_cookies, dados_politica)
        relatorio_final = report_engine.gerar_dados_relatorio()
        
        # Injeta de forma segura a lista de scripts encontrados nos detalhes técnicos da View
        if "detalhes_tecnicos" in relatorio_final:
            relatorio_final["detalhes_tecnicos"]["scripts_terceiros"] = scripts_terceiros
        else:
            # Fallback de segurança se o gerador de relatórios falhar na estrutura
            relatorio_final["detalhes_tecnicos"] = {"scripts_terceiros": scripts_terceiros}
            
        return relatorio_final