"""
Fallback LLM - Classificação baseada em palavras-chave
======================================================
Funciona sem necessidade de chaves API.
"""

# Dicionário de palavras-chave para as 7 CATEGORIAS corretas (melhorado)
KEYWORDS_MAP_CATEGORIA = {
    "CUSTOS FIXOS": [
        # Alimentação básica
        "supermercado", "mercado", "padaria", "açougue", "feira", "hortifruti", "atacadão",
        "carrefour", "extra", "pão de açúcar", "dia", "walmart", "big", "assai",
        # Moradia
        "aluguel", "condomínio", "iptu", "luz", "energia", "água", "internet",
        "wifi", "conta", "cemig", "copasa", "sabesp", "enel", "light",
        # Taxas e serviços
        "taxa", "seguro residencial", "seguro", "manutenção", "reparo", "conserto",
        "telefone", "celular", "plano", "mensalidade", "anuidade"
    ],
    "CONFORTO": [
        # Transporte
        "uber", "99", "taxi", "gasolina", "combustível", "posto", "shell", "petrobras",
        "ipiranga", "estacionamento", "parking", "pedágio", "ônibus", "metrô", "trem",
        "carro", "moto", "mecânico", "lavagem", "seguro auto", "seguro veículo",
        # Alimentação fora
        "restaurante", "lanchonete", "cafeteria", "padaria", "confeitaria",
        # Eletrônicos e casa
        "eletrônico", "eletrodoméstico", "móvel", "decoração", "casa", "reforma"
    ],
    "PRAZERES": [
        # Entretenimento
        "cinema", "teatro", "show", "evento", "parque", "diversão", "bar",
        "balada", "festa", "netflix", "spotify", "amazon prime", "disney",
        "streaming", "assinatura", "hbo", "youtube", "entretenimento", "jogo",
        "playstation", "xbox", "nintendo", "steam",
        # Alimentação prazer
        "pizzaria", "delivery", "ifood", "uber eats", "rappi", "comida", "almoço", "jantar",
        "café", "lanche", "pizza", "hamburguer", "sorvete", "chocolate", "doces"
    ],
    "CONHECIMENTO": [
        # Educação
        "curso", "aula", "faculdade", "universidade", "escola", "livro",
        "material", "papelaria", "caderno", "caneta", "apostila", "udemy",
        "coursera", "workshop", "treinamento", "estudo", "amazon", "livraria",
        "kindle", "ebook", "certificação", "diploma", "graduação", "pós"
    ],
    "METAS": [
        # Investimentos e objetivos
        "investimento", "poupança", "reserva", "objetivo", "meta", "plano",
        "fundo", "aplicação", "renda fixa", "ações", "tesouro", "cdb",
        "lci", "lca", "fii", "bolsa", "corretora"
    ],
    "LIBERDADE FINANCEIRA": [
        # Independência financeira
        "investimento", "poupança", "reserva", "objetivo", "meta", "plano",
        "fundo", "aplicação", "renda fixa", "ações", "tesouro", "independência",
        "aposentadoria", "patrimônio", "riqueza", "dividendos", "renda passiva"
    ],
    "CATEGORIZAR": []  # Sem palavras-chave específicas - será usado como default
}

# Dicionário de palavras-chave para SUBCATEGORIAS (mapeamento livre)
KEYWORDS_MAP_SUBCATEGORIA = {
    "ALIMENTAÇÃO": ["supermercado", "mercado", "padaria", "açougue", "feira", "hortifruti"],
    "RESTAURANTE": ["restaurante", "lanchonete", "pizzaria", "delivery", "ifood", "uber eats"],
    "TRANSPORTE": ["uber", "99", "taxi", "gasolina", "combustível", "posto", "ônibus", "metrô"],
    "SAÚDE": ["médico", "consulta", "hospital", "clínica", "farmácia", "drogaria", "exame"],
    "LAZER": ["cinema", "teatro", "show", "evento", "parque", "bar", "balada", "festa"],
    "EDUCAÇÃO": ["curso", "aula", "faculdade", "universidade", "escola", "livro"],
    "MORADIA": ["aluguel", "condomínio", "iptu", "luz", "energia", "água", "internet"],
    "FERRAMENTAS": ["ferramenta", "material", "construção", "reparo", "manutenção"],
    "ROUPAS": ["roupa", "vestuário", "moda", "loja", "shopping"],
    "HABITAÇÃO": ["casa", "apartamento", "imóvel", "reforma", "construção"]
}

def classificar_categoria(descricao: str) -> dict:
    """
    Classifica CATEGORIA (7 classes) baseado em palavras-chave
    """
    descricao_lower = descricao.lower()
    
    # Contador de matches por categoria
    matches = {}
    
    for categoria, keywords in KEYWORDS_MAP_CATEGORIA.items():
        if not keywords:  # Pular CATEGORIZAR (sem keywords)
            continue
        count = sum(1 for keyword in keywords if keyword in descricao_lower)
        if count > 0:
            matches[categoria] = count
    
    # Se encontrou matches, retorna a categoria com mais matches
    if matches:
        categoria = max(matches, key=matches.get)
        max_matches = matches[categoria]
        total_keywords = len(KEYWORDS_MAP_CATEGORIA[categoria])
        
        # Confiança melhorada: baseada em proporção de matches e número absoluto
        # Mais matches = maior confiança, mas também considera a proporção
        confianca_base = min(max_matches * 0.25, 0.8)  # Base: até 0.8 por matches
        confianca_proporcao = min(max_matches / max(total_keywords, 1) * 0.3, 0.2)  # Bônus por proporção
        confianca = min(confianca_base + confianca_proporcao, 0.95)  # Máximo 0.95
        
        # Se tem muitos matches, aumentar confiança
        if max_matches >= 3:
            confianca = min(confianca + 0.1, 0.95)
        
        return {
            "categoria": categoria,
            "confianca": confianca,
            "provider": "fallback"
        }
    
    # Se não encontrou nenhuma palavra-chave, retorna "CATEGORIZAR" com confiança baixa
    return {
        "categoria": "CATEGORIZAR",
        "confianca": 0.3,  # Confiança baixa para desconhecido
        "provider": "fallback"
    }

def classificar_subcategoria(descricao: str, categoria: str = None) -> dict:
    """
    Classifica SUBCATEGORIA baseado em palavras-chave
    Usa categoria como contexto adicional
    """
    descricao_lower = descricao.lower()
    
    # Contador de matches por subcategoria
    matches = {}
    
    for subcategoria, keywords in KEYWORDS_MAP_SUBCATEGORIA.items():
        count = sum(1 for keyword in keywords if keyword in descricao_lower)
        if count > 0:
            matches[subcategoria] = count
    
    # Se encontrou matches, retorna a subcategoria com mais matches
    if matches:
        subcategoria = max(matches, key=matches.get)
        max_matches = matches[subcategoria]
        total_keywords = len(KEYWORDS_MAP_SUBCATEGORIA[subcategoria])
        
        # Confiança melhorada similar à categoria
        confianca_base = min(max_matches * 0.25, 0.8)
        confianca_proporcao = min(max_matches / max(total_keywords, 1) * 0.3, 0.2)
        confianca = min(confianca_base + confianca_proporcao, 0.95)
        
        # Se tem muitos matches, aumentar confiança
        if max_matches >= 2:
            confianca = min(confianca + 0.1, 0.95)
        
        return {
            "subcategoria": subcategoria,
            "confianca": confianca,
            "provider": "fallback"
        }
    
    # Se não encontrou nenhuma palavra-chave, retorna vazio com confiança baixa
    return {
        "subcategoria": "",
        "confianca": 0.2,  # Confiança muito baixa para desconhecido
        "provider": "fallback"
    }

