import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

class CookieScout:
    """Model responsável pela varredura dinâmica de cookies e identificação de políticas."""
    
    def __init__(self, url):
        self.url = url

    def inspecionar_site(self):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                page.goto(self.url, wait_until="load", timeout=25000)
                
                # Garante uma rolagem para carregar os scripts assíncronos das plataformas
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
                time.sleep(2)
                
                cookies = page.context.cookies()
                html_content = page.content().lower()
                
                url_politica_encontrada = None
                politica_encontrada = False
                termos_chave = ["privacidade", "privacy", "politica-de-privacidade"]
                
                # 🔥 CORREÇÃO CRÍTICA: Trocamos o query_selector_all pelo locator() do Playwright.
                # Os Locators perfuram estruturas de #shadow-root (Web Components do YouTube) automaticamente.
                links_locator = page.locator("a")
                quantidade_links = links_locator.count()
                
                for i in range(quantidade_links):
                    try:
                        link = links_locator.nth(i)
                        href = link.get_attribute("href")
                        texto = link.text_content()
                        texto_limpo = texto.lower().strip() if texto else ""
                        
                        # Verifica se o link textual ou a propriedade destino batem com os termos LGPD
                        if href and any(termo in texto_limpo or termo in href.lower() for termo in termos_chave):
                            politica_encontrada = True
                            url_politica_encontrada = urljoin(self.url, href) if href.startswith("/") else href
                            break
                    except Exception:
                        continue
                
                # STRATEGY FALLBACK: Caso caia em uma tela de consentimento global isolada
                if not politica_encontrada:
                    for termo in termos_chave:
                        busca_direta = page.locator(f"a:has-text('{termo}')").first
                        if busca_direta.count() > 0:
                            href = busca_direta.get_attribute("href")
                            if href:
                                politica_encontrada = True
                                url_politica_encontrada = urljoin(self.url, href) if href.startswith("/") else href
                                break

                # Mapeia scripts de rastreamento capturados no tráfego
                scripts_mapeados = []
                if "google-analytics.com" in html_content or "googletagmanager.com" in html_content or "analytics.google" in html_content:
                    scripts_mapeados.append("www.googletagmanager.com")
                if "connect.facebook.net" in html_content or "facebook.com/tr" in html_content:
                    scripts_mapeados.append("connect.facebook.net (Meta Pixel)")
                if "doubleclick.net" in html_content:
                    scripts_mapeados.append("static.doubleclick.net (Google Ads)")
                
                browser.close()
                
                return {
                    "cookies_encontrados": len(cookies),
                    "scripts_terceiros": scripts_mapeados,
                    "politica_encontrada": politica_encontrada,
                    "url_politica_encontrada": url_politica_encontrada
                }
                
        except Exception as e:
            return {"erro": f"Falha na vistoria automatizada: {str(e)}"}