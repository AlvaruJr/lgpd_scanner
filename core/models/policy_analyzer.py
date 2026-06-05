import requests
from bs4 import BeautifulSoup

class PolicyAnalyzer:
    """Model responsável por extrair e analisar o texto das Políticas de Privacidade."""
    
    def __init__(self, url_politica):
        self.url_politica = url_politica

    def analisar_texto_politica(self):
        if not self.url_politica:
            return {"erro": "Nenhum link de política fornecido para análise."}
            
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resposta = requests.get(self.url_politica, headers=headers, timeout=10)
            soup = BeautifulSoup(resposta.text, 'html.parser')
            
            # Limpa o HTML removendo scripts e estilos
            for script in soup(["script", "style"]):
                script.decompose()
            texto_limpo = soup.get_text().lower()
            
            # Critérios de avaliação (Palavras-chave LGPD)
            criterios = {
                "Direitos dos Titulares": ["titular", "direitos", "acesso", "retificar", "excluir"],
                "Canal de Contato (DPO/Encarregado)": ["encarregado", "dpo", "contato", "privacidade@", "data protection"],
                "Bases Legais & Finalidade": ["finalidade", "base legal", "consentimento", "legítimo interesse"],
                "Compartilhamento com Terceiros": ["compartilhar", "terceiros", "parceiros", "transferência"]
            }
            
            analise_requisitos = {}
            score_texto = 100
            
            for requisito, palavras in criterios.items():
                encontrado = any(palavra in texto_limpo for palavra in palavras)
                analise_requisitos[requisito] = encontrado
                if not encontrado:
                    score_texto -= 25
                    
            return {
                "score_texto": max(score_texto, 0),
                "requisitos_identificados": analise_requisitos,
                "tamanho_texto_caracteres": len(texto_limpo)
            }
            
        except Exception as e:
            return {"erro": f"Erro ao analisar texto da política: {str(e)}"}