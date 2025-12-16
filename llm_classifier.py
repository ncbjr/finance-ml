"""
LLM Classifier - Orquestrador de Provedores
============================================
Tenta múltiplos provedores LLM em ordem, com fallback automático.
"""

from dotenv import load_dotenv
load_dotenv()

import llm_fallback

def classificar_com_llm(descricao: str, threshold_confianca: float = 0.7) -> dict:
    """
    Tenta classificar CATEGORIA usando LLM local primeiro, depois IA externa se necessário.
    Estratégia: Fallback (local) → IA Externa (se confiança baixa)
    Retorna categoria + subcategoria
    """
    import os
    
    # 1. Tentar LLM local (fallback) PRIMEIRO
    resultado_fallback = llm_fallback.classificar_categoria(descricao)
    resultado_subcategoria_fallback = llm_fallback.classificar_subcategoria(
        descricao, resultado_fallback.get('categoria')
    )
    
    # 2. Se confiança do fallback é alta, retornar
    if resultado_fallback['confianca'] >= threshold_confianca:
        print(f"OK Classificação bem-sucedida usando LLM local (confiança: {resultado_fallback['confianca']:.2f})")
        return {
            **resultado_fallback,
            'subcategoria': resultado_subcategoria_fallback.get('subcategoria', ''),
            'confianca_subcategoria': resultado_subcategoria_fallback.get('confianca', 0.0)
        }
    
    # 3. Se confiança baixa, tentar IA externa
    print(f"AVISO: Confiança do LLM local baixa ({resultado_fallback['confianca']:.2f}), tentando IA externa...")
    
    providers = [
        ("OpenAI", "providers.openai"),
        ("Anthropic", "providers.anthropic"),
        ("Gemini", "providers.gemini"),
        ("Groq", "providers.groq"),
        ("XAI", "providers.xai"),
    ]
    
    melhor_resultado = resultado_fallback
    melhor_subcategoria = resultado_subcategoria_fallback
    melhor_confianca = resultado_fallback['confianca']
    
    # Tentar cada provider externo
    for provider_name, provider_module in providers:
        try:
            # Import dinâmico
            module = __import__(provider_module, fromlist=['classificar_categoria'])
            resultado_categoria = module.classificar_categoria(descricao)
            
            # Se IA externa tem confiança melhor que fallback, usar
            if resultado_categoria['confianca'] > melhor_confianca:
                melhor_resultado = resultado_categoria
                melhor_confianca = resultado_categoria['confianca']
                
                # Tentar classificar subcategoria também (se provider suportar)
                resultado_subcategoria = None
                try:
                    if hasattr(module, 'classificar_subcategoria'):
                        resultado_subcategoria = module.classificar_subcategoria(
                            descricao, resultado_categoria.get('categoria')
                        )
                except:
                    pass
                
                # Se não tem subcategoria do provider, usar fallback
                if not resultado_subcategoria:
                    resultado_subcategoria = llm_fallback.classificar_subcategoria(
                        descricao, resultado_categoria.get('categoria')
                    )
                
                melhor_subcategoria = resultado_subcategoria
                print(f"OK Classificação melhorada usando {provider_name} (confiança: {melhor_confianca:.2f})")
                break  # Usar o primeiro que melhorar
            
        except Exception as e:
            # Se falhou, tentar próximo
            print(f"ERRO {provider_name} falhou: {str(e)}")
            continue
    
    # 4. Retornar melhor resultado (fallback ou IA externa)
    return {
        **melhor_resultado,
        'subcategoria': melhor_subcategoria.get('subcategoria', ''),
        'confianca_subcategoria': melhor_subcategoria.get('confianca', 0.0)
    }


def classificar_hibrido(descricao: str, categoria_ml: str = None, confianca_ml: float = 0.0, 
                       subcategoria_ml: str = None, confianca_subcategoria_ml: float = 0.0) -> dict:
    """
    Classifica usando LLM e combina com resultado do ML (se disponível)
    Retorna categoria + subcategoria
    """
    # Classificar com LLM
    resultado_llm = classificar_com_llm(descricao)
    
    # Se não tem resultado ML, retornar apenas LLM
    if categoria_ml is None:
        return resultado_llm
    
    # Combinar resultados ML e LLM para CATEGORIA
    categoria_final = resultado_llm["categoria"]
    confianca_categoria_final = resultado_llm["confianca"]
    
    # Se ambos concordam, aumentar confiança
    if categoria_ml.lower() == resultado_llm["categoria"].lower():
        confianca_categoria_final = min((confianca_ml + resultado_llm["confianca"]) / 2 + 0.2, 1.0)
        provider_categoria = f"hybrid ({resultado_llm['provider']} + ml)"
    # Se discordam, usar o com maior confiança
    elif confianca_ml > resultado_llm["confianca"]:
        categoria_final = categoria_ml
        confianca_categoria_final = confianca_ml
        provider_categoria = "ml (discordância com llm)"
    else:
        provider_categoria = f"{resultado_llm['provider']} (discordância com ml)"
    
    # Para SUBCATEGORIA, usar ML se disponível, senão LLM
    subcategoria_final = subcategoria_ml if subcategoria_ml else resultado_llm.get('subcategoria', '')
    confianca_subcategoria_final = confianca_subcategoria_ml if subcategoria_ml else resultado_llm.get('confianca_subcategoria', 0.0)
    
    return {
        "categoria": categoria_final,
        "confianca": confianca_categoria_final,
        "subcategoria": subcategoria_final,
        "confianca_subcategoria": confianca_subcategoria_final,
        "provider": provider_categoria,
        "ml_categoria": categoria_ml,
        "ml_confianca": confianca_ml,
        "ml_subcategoria": subcategoria_ml,
        "ml_confianca_subcategoria": confianca_subcategoria_ml,
        "llm_categoria": resultado_llm.get("categoria"),
        "llm_confianca": resultado_llm.get("confianca"),
        "llm_subcategoria": resultado_llm.get("subcategoria", ""),
        "llm_confianca_subcategoria": resultado_llm.get("confianca_subcategoria", 0.0)
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

