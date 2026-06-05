from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class CookieScout:
    """Model avançado responsável por inspecionar cookies e requisições usando Playwright."""
    
    def __init__(self, url):
        self.url = url

    def inspecionar_site(self):
        try:
            dados_auditoria = {
                "status_code": 200,
                "cookies_encontrados": 0,
                "lista_cookies": [],
                "scripts_terceiros": [],
                "politica_encontrada": False
            }
            
            # Inicializa o navegador automatizado em segundo plano (headless=True)
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Lista para interceptar todas as requisições de rede (scripts externos)
                urls_capturadas = []
                page.on("request", lambda request: urls_capturadas.append(request.url))
                
                # Navega até o site e espera até que a rede fique ociosa (scripts carregados)
                resposta = page.goto(self.url, wait_until="networkidle", timeout=15000)
                if resposta:
                    dados_auditoria["status_code"] = resposta.status
                
                # 1. Captura TODOS os cookies reais (inclusive os gerados por JavaScript)
                cookies = page.context.cookies()
                dados_auditoria["cookies_encontrados"] = len(cookies)
                dados_auditoria["lista_cookies"] = [c['name'] for c in cookies]
                
                # 2. Filtra requisições de terceiros conhecidas por rastreamento
                rastreadores_comuns = ['analytics', 'pixel', 'facebook', 'doubleclick', 'hotjar', 'tagmanager']
                for url_req in urls_capturadas:
                    if any(r in url_req.lower() for r in list(set(rastreadores_comuns))):
                        # Guarda apenas o domínio ou nome do rastreador para o relatório
                        dados_auditoria["scripts_terceiros"].append(url_req.split('/')[2])
                
                # Remove duplicados da lista de scripts
                dados_auditoria["scripts_terceiros"] = list(set(dados_auditoria["scripts_terceiros"]))
                
                # 3. Busca o link da política de privacidade no HTML renderizado
                html_conteudo = page.content()
                soup = BeautifulSoup(html_conteudo, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href_minimo = link['href'].lower()
                    if 'privacidade' in href_minimo or 'privacy' in href_minimo:
                        dados_auditoria["politica_encontrada"] = True
                        break
                
                browser.close()
                
            return dados_auditoria
            
        except Exception as e:
            return {"erro": f"Falha na vistoria automatizada: {str(e)}"}