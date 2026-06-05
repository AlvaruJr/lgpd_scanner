import os
import json
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Carrega as variaveis de ambiente de forma segura
load_dotenv()

class PolicyAnalyzer:
    """Model inteligente que usa a API do Google Gemini para auditar a Politica de Privacidade."""
    
    def __init__(self, url_politica):
        self.url_politica = url_politica
        self.api_key = os.getenv("GEMINI_API_KEY")
        
    def analisar_texto_politica(self):
        if not self.url_politica:
            return {
                "score_texto": 0,
                "requisitos_identificados": {
                    "Direitos dos Titulares": False,
                    "Canal de Contato (DPO)": False,
                    "Bases Legais e Finalidade": False,
                    "Compartilhamento com Terceiros": False
                },
                "parecer_ia": "Politica de privacidade nao informada pelo site alvo."
            }
            
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resposta = requests.get(self.url_politica, headers=headers, timeout=10)
            soup = BeautifulSoup(resposta.text, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
            texto_limpo = soup.get_text()
            texto_limpo = texto_limpo[:15000] 

            if not self.api_key:
                raise ValueError("Chave de API GEMINI_API_KEY nao localizada no arquivo .env")

            client = genai.Client(api_key=self.api_key)
            
            prompt = f"""
            Analise a seguinte Politica de Privacidade sob as regras estritas da LGPD brasileira.
            Verifique se o texto menciona de forma clara e juridicamente valida os 4 requisitos abaixo:
            1. Direitos dos Titulares (acesso, exclusao, retificacao).
            2. Canal de Contato do DPO / Encarregado de dados (email ou formulario explicito).
            3. Bases Legais e Finalidade do tratamento dos dados.
            4. Compartilhamento com Terceiros ou parceiros.

            Texto da Politica:
            \"\"\"{texto_limpo}\"\"\"

            Responda OBRIGATORIAMENTE em formato JSON puro, contendo exatamente as chaves de verificacao estruturadas abaixo:
            - "Direitos dos Titulares": true/false
            - "Canal de Contato (DPO)": true/false
            - "Bases Legais e Finalidade": true/false
            - "Compartilhamento com Terceiros": true/false
            - "Resumo_Parecer": "Escreva um resumo curto de ate 3 linhas com uma analise critica sobre a clareza deste texto."
            """

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                ),
            )
            
            analise_ia = json.loads(response.text)
            
            score_texto = 100
            requisitos_legais = {}
            chaves_analise = ["Direitos dos Titulares", "Canal de Contato (DPO)", "Bases Legais e Finalidade", "Compartilhamento com Terceiros"]
            
            for chave in chaves_analise:
                presente = analise_ia.get(chave, False)
                requisitos_legais[chave] = presente
                if not presente:
                    score_texto = max(score_texto - 25, 0)
                    
            # 🔥 RETORNO ALINHADO: Garante a entrega do parecer textual extraido da IA
            return {
                "score_texto": score_texto,
                "requisitos_identificados": requisitos_legais,
                "parecer_ia": analise_ia.get("Resumo_Parecer", "Analise concluida com sucesso pela IA.")
            }
            
        except Exception as e:
            return {
                "score_texto": 0,
                "requisitos_identificados": {
                    "Direitos dos Titulares": False,
                    "Canal de Contato (DPO)": False,
                    "Bases Legais e Finalidade": False,
                    "Compartilhamento com Terceiros": False
                },
                "parecer_ia": f"Erro na analise semantica: {str(e)}"
            }