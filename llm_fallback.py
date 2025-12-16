"""
Fallback LLM - Classificação baseada em palavras-chave
======================================================
Funciona sem necessidade de chaves API.
"""

# Dicionário de palavras-chave para cada categoria
KEYWORDS_MAP = {
    "Alimentação": [
        "supermercado", "mercado", "padaria", "açougue", "feira", "hortifruti",
        "restaurante", "lanchonete", "pizzaria", "delivery", "ifood", "uber eats",
        "comida", "almoço", "jantar", "café", "lanche", "pizza", "hamburguer",
        "carrefour", "extra", "pão de açúcar", "dia"
    ],
    "Transporte": [
        "uber", "99", "taxi", "gasolina", "combustível", "posto", "shell", "petrobras",
        "estacionamento", "parking", "pedágio", "ônibus", "metrô", "trem",
        "carro", "moto", "mecânico", "manutenção", "lavagem", "seguro"
    ],
    "Saúde": [
        "médico", "consulta", "hospital", "clínica", "farmácia", "drogaria",
        "remédio", "medicamento", "exame", "laboratório", "dentista", "fisioterapia",
        "psicólogo", "terapia", "academia", "ginástica", "ortopedista", "oftalmologista",
        "drogasil", "pacheco", "são paulo", "vitamina", "suplemento"
    ],
    "Lazer": [
        "cinema", "teatro", "show", "evento", "parque", "diversão", "bar",
        "balada", "festa", "netflix", "spotify", "amazon prime", "disney",
        "streaming", "assinatura", "hbo", "youtube", "entretenimento", "jogo"
    ],
    "Educação": [
        "curso", "aula", "faculdade", "universidade", "escola", "livro",
        "material", "papelaria", "caderno", "caneta", "apostila", "udemy",
        "coursera", "workshop", "treinamento", "estudo", "amazon", "livraria"
    ],
    "Moradia": [
        "aluguel", "condomínio", "iptu", "luz", "energia", "água", "internet",
        "wifi", "conta", "cemig", "copasa", "taxa", "seguro residencial",
        "manutenção", "reparo", "construção"
    ]
}

def classificar_categoria(descricao: str) -> dict:
    """
    Classifica baseado em palavras-chave
    """
    descricao_lower = descricao.lower()
    
    # Contador de matches por categoria
    matches = {}
    
    for categoria, keywords in KEYWORDS_MAP.items():
        count = sum(1 for keyword in keywords if keyword in descricao_lower)
        if count > 0:
            matches[categoria] = count
    
    # Se encontrou matches, retorna a categoria com mais matches
    if matches:
        categoria = max(matches, key=matches.get)
        # Confiança baseada no número de matches (normalizada)
        confianca = min(matches[categoria] * 0.3, 1.0)
        return {
            "categoria": categoria,
            "confianca": confianca,
            "provider": "fallback"
        }
    
    # Se não encontrou nenhuma palavra-chave, retorna "Outros"
    return {
        "categoria": "Outros",
        "confianca": 0.5,
        "provider": "fallback"
    }

