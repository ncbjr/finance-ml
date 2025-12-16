"""
LLM Classifier - Orquestrador de Provedores
============================================
Tenta múltiplos provedores LLM em ordem, com fallback automático.
"""

from dotenv import load_dotenv
load_dotenv()

import llm_fallback

def classificar_com_llm(descricao: str) -> dict:
    """
    Tenta classificar usando vários provedores LLM em ordem.
    Ordem: OpenAI → Anthropic → Gemini → Groq → XAI → Fallback
    """
    
    # Lista de providers para tentar em ordem
    providers = [
        ("OpenAI", "providers.openai"),
        ("Anthropic", "providers.anthropic"),
        ("Gemini", "providers.gemini"),
        ("Groq", "providers.groq"),
        ("XAI", "providers.xai"),
    ]
    
    # Tentar cada provider
    for provider_name, provider_module in providers:
        try:
            # Import dinâmico
            module = __import__(provider_module, fromlist=['classificar_categoria'])
            resultado = module.classificar_categoria(descricao)
            
            # Se funcionou, retornar resultado
            print(f"OK Classificacao bem-sucedida usando {provider_name}")
            return resultado
            
        except Exception as e:
            # Se falhou, tentar próximo
            print(f"ERRO {provider_name} falhou: {str(e)}")
            continue
    
    # Se todos falharam, usar fallback
    print("AVISO: Todos os providers falharam, usando fallback local")
    return llm_fallback.classificar_categoria(descricao)


def classificar_hibrido(descricao: str, categoria_ml: str = None, confianca_ml: float = 0.0) -> dict:
    """
    Classifica usando LLM e combina com resultado do ML (se disponível)
    """
    # Classificar com LLM
    resultado_llm = classificar_com_llm(descricao)
    
    # Se não tem resultado ML, retornar apenas LLM
    if categoria_ml is None:
        return resultado_llm
    
    # Combinar resultados ML e LLM
    # Se ambos concordam, aumentar confiança
    if categoria_ml.lower() == resultado_llm["categoria"].lower():
        return {
            "categoria": resultado_llm["categoria"],
            "confianca": min((confianca_ml + resultado_llm["confianca"]) / 2 + 0.2, 1.0),
            "provider": f"hybrid ({resultado_llm['provider']} + ml)",
            "ml_categoria": categoria_ml,
            "ml_confianca": confianca_ml
        }
    
    # Se discordam, usar o com maior confiança
    if confianca_ml > resultado_llm["confianca"]:
        return {
            "categoria": categoria_ml,
            "confianca": confianca_ml,
            "provider": "ml (discordância com llm)",
            "llm_categoria": resultado_llm["categoria"],
            "llm_confianca": resultado_llm["confianca"]
        }
    else:
        return {
            "categoria": resultado_llm["categoria"],
            "confianca": resultado_llm["confianca"],
            "provider": f"{resultado_llm['provider']} (discordância com ml)",
            "ml_categoria": categoria_ml,
            "ml_confianca": confianca_ml
        }


if __name__ == "__main__":
    # Teste rápido
    print("=== TESTE DE CLASSIFICAÇÃO LLM ===\n")
    
    testes = [
        "Supermercado Carrefour",
        "Uber para trabalho",
        "Consulta médica",
        "Netflix assinatura"
    ]
    
    for descricao in testes:
        print(f"Descrição: {descricao}")
        resultado = classificar_com_llm(descricao)
        print(f"Categoria: {resultado['categoria']}")
        print(f"Confiança: {resultado['confianca']:.2f}")
        print(f"Provider: {resultado['provider']}")
        print()

