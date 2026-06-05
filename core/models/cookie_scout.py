import requests
from bs4 import BeautifulSoup

class CookieScout:
    """Model responsável por inspecionar os elementos técnicos da página web."""
    
    def __init__(self, url):
        self.url = url

    def inspecionar_site(self):
        try:
            # Simula uma requisição HTTP simples
            headers = {'User-Agent': 'Mozilla/5.0'}
            resposta = requests.get(self.url, headers=headers, timeout=10)
            
            # Resultado inicial estruturado
            dados_auditoria = {
                "status_code": resposta.status_code,
                "cookies_encontrados": len(resposta.cookies),
                "politica_encontrada": False
            }
            
            # Varredura simples no HTML em busca de links de privacidade
            soup = BeautifulSoup(resposta.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href_minimo = link['href'].lower()
                if 'privacidade' in href_minimo or 'privacy' in href_minimo:
                    dados_auditoria["politica_encontrada"] = True
                    break
                    
            return dados_auditoria
            
        except Exception as e:
            return {"erro": f"Falha ao conectar: {str(e)}"}
        