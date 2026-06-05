from core.models.cookie_scout import CookieScout
from core.models.policy_analyzer import PolicyAnalyzer
from core.models.report_generator import ReportGenerator
from core.models.history_manager import HistoryManager  # 🔥 Novo Import

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
        
        # Se o dicionário vier vazio, nulo ou contiver erro, interrompe o fluxo
        if not dados_cookies or "erro" in dados_cookies:
            return dados_cookies if dados_cookies else {"erro": "Falha desconhecida na varredura."}
            
        # Regra de negócio avançada para o Score Técnico
        score_tec = 100
        
        cookies_encontrados = dados_cookies.get("cookies_encontrados", 0)
        scripts_terceiros = dados_cookies.get("scripts_terceiros", [])
        politica_encontrada = dados_cookies.get("politica_encontrada", False)
        
        # Penalizações baseadas em critérios objectives
        if cookies_encontrados > 0:
            score_tec -= min(cookies_encontrados * 2, 20)
            
        if len(scripts_terceiros) > 0:
            score_tec -= 20
            
        if not politica_encontrada:
            score_tec -= 40
            
        dados_cookies["score_conformidade"] = max(score_tec, 0)
        
        # 2. Executa a análise textual inteligente da política de privacidade (Se ela existir)
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
            relatorio_final["detalhes_tecnicos"] = {"scripts_terceiros": scripts_terceiros}
            
        # 🔥 PERSISTÊNCIA: Grava o relatório gerado com sucesso direto no arquivo JSON local
        HistoryManager.salvar_relatorio(relatorio_final)
            
        return relatorio_final

    def obter_historico_local(self):
        """Busca a lista de relatórios antigos armazenados no disco."""
        return HistoryManager.listar_historico()