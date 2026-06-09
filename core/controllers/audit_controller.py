import os
import logging
import re  # 🔥 Novo Import: Motor de Expressões Regulares para segurança
from urllib.parse import urlparse
from core.models.cookie_scout import CookieScout
from core.models.policy_analyzer import PolicyAnalyzer
from core.models.report_generator import ReportGenerator
from core.models.history_manager import HistoryManager

# --- CONFIGURAÇÃO DO SISTEMA DE LOGS ---
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "auditoria.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

class AuditController:
    """Controller avançado com camadas de Observabilidade e Sanitização de Inputs (Segurança)."""
    
    def __init__(self):
        pass

    def _sanitizar_url(self, url_bruta):
        """Aplica regras estritas de segurança para limpar e validar a URL de entrada."""
        if not url_bruta:
            return None
            
        # 1. Remove espaços em branco nas pontas e quebras de linha/injeções de terminal
        url_limpa = url_bruta.strip().replace("\n", "").replace("\r", "")
        
        # 2. Defesa contra caracteres perigosos comuns em injeção de comandos (XSS/Command Injection)
        # Remove caracteres como ;, |, &, `, <, >, ", '
        url_limpa = re.sub(r'[;\|&`<>"\'\s]', '', url_limpa)
        
        return url_limpa

    def _validar_estrutura_url(self, url):
        """Valida se a string sanitizada possui uma estrutura legítima de URL HTTP/HTTPS."""
        try:
            parsed = urlparse(url)
            # Garante que possui esquema (http ou https) e um netloc (domínio válido)
            if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                return False
                
            # Regex complementar para evitar domínios malformados (ex: http://....)
            dominio_valido = re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', parsed.netloc)
            return bool(dominio_valido)
        except Exception:
            return False

    def iniciar_vistoria(self, url_bruta):
        logging.info(f"=== Solicitação recebida. Input bruto do usuário: '{url_bruta}' ===")
        
        # 🔥 CAMADA DE SEGURANÇA: Sanitização do Input
        url = self._sanitizar_url(url_bruta)
        
        # Verifica se o input restou vazio ou falhou na validação estrutural RFC
        if not url or not self._validar_estrutura_url(url):
            logging.warning(f"🛡️ Bloqueio de Segurança: Input rejeitado por violação estrutural ou tentativa de injeção ('{url_bruta}')")
            return {"erro": "URL inválida ou insegura. Certifique-se de usar o formato correto (ex: https://exemplo.com)."}
            
        if url != url_bruta:
            logging.info(f"🛡️ Higienização aplicada: URL convertida de '{url_bruta}' para '{url}'")

        # 1. Executa a varredura dinâmica com Playwright
        logging.info(f"Iniciando varredura dinâmica segura para: {url}")
        scout = CookieScout(url)
        dados_cookies = scout.inspecionar_site()
        
        if not dados_cookies or "erro" in dados_cookies:
            erro_msg = dados_cookies.get("erro", "Falha desconhecida na varredura.") if dados_cookies else "Retorno nulo do Scout."
            logging.error(f"Falha crítica no Playwright ao inspecionar {url}: {erro_msg}")
            return dados_cookies if dados_cookies else {"erro": "Falha desconhecida na varredura."}
            
        cookies_encontrados = dados_cookies.get("cookies_encontrados", 0)
        scripts_terceiros = dados_cookies.get("scripts_terceiros", [])
        politica_encontrada = dados_cookies.get("politica_encontrada", False)
        url_politica_real = dados_cookies.get("url_politica_encontrada")
        
        logging.info(f"Varredura concluída. Cookies: {cookies_encontrados} | Rastreadores: {len(scripts_terceiros)}")
        
        # Regra de negócio para o Score Técnico
        score_tec = 100
        if cookies_encontrados > 0:
            score_tec -= min(cookies_encontrados * 2, 20)
        if len(scripts_terceiros) > 0:
            score_tec -= 20
        if not politica_encontrada:
            score_tec -= 40
            
        dados_cookies["score_conformidade"] = max(score_tec, 0)
        
        # 2. Executa a análise textual inteligente da política de privacidade
        url_politica_analise = url_politica_real if politica_encontrada else None
        analyzer = PolicyAnalyzer(url_politica_analise)
        dados_politica = analyzer.analisar_texto_politica()
        
        # 3. Consolida os dados e gera o payload final
        report_engine = ReportGenerator(url, dados_cookies, dados_politica)
        relatorio_final = report_engine.gerar_dados_relatorio()
        
        if "detalhes_tecnicos" in relatorio_final:
            relatorio_final["detalhes_tecnicos"]["scripts_terceiros"] = scripts_terceiros
        else:
            relatorio_final["detalhes_tecnicos"] = {"scripts_terceiros": scripts_terceiros}
            
        relatorio_final["diagnostico"]["score_governanca"] = 0
        
        # Persiste o relatório no arquivo JSON local
        HistoryManager.salvar_relatorio(relatorio_final)
        logging.info(f"=== Vistoria concluída com sucesso. Score: {relatorio_final['diagnostico']['score_geral']} ===")
            
        return relatorio_final

    def obter_historico_local(self):
        """Busca a lista de relatórios antigos armazenados no disco."""
        return HistoryManager.listar_historico()