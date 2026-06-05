import json
import os

class HistoryManager:
    """Model responsável por persistir e recuperar o histórico de auditorias em um arquivo local JSON."""
    FILE_PATH = "data/historico_vistorias.json"

    @classmethod
    def _garantir_diretorio_e_arquivo(cls):
        """Garante a existência da pasta data/ e do arquivo JSON de histórico."""
        os.makedirs(os.path.dirname(cls.FILE_PATH), exist_ok=True)
        if not os.path.exists(cls.FILE_PATH):
            with open(cls.FILE_PATH, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    @classmethod
    def salvar_relatorio(cls, relatorio):
        """Salva um relatório no disco, evitando duplicidade da mesma URL."""
        cls._garantir_diretorio_e_arquivo()
        
        with open(cls.FILE_PATH, "r", encoding="utf-8") as f:
            try:
                historico = json.load(f)
            except json.JSONDecodeError:
                historico = []
        
        url_atual = relatorio["cabecalho"]["url_vistoriada"]
        # Remove registros antigos da mesma URL para não inflar o arquivo
        historico = [r for r in historico if r["cabecalho"]["url_vistoriada"] != url_atual]
        
        # Insere no topo da lista (mais recente primeiro)
        historico.insert(0, relatorio)
        
        with open(cls.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=4)

    @classmethod
    def listar_historico(cls):
        """Retorna a lista completa de relatórios salvos em disco."""
        cls._garantir_diretorio_e_arquivo()
        try:
            with open(cls.FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []