import os
import xai_sdk

xai_cliente = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

def classificar_categoria(descricao: str) -> dict:
    """
    Classifica uma despesa usando xAI
    """
    try:
        # Nota: A API do xAI pode ter interface diferente
        # Este é um exemplo genérico que pode precisar de ajuste
        response = xai_cliente.chat(
            messages=[
                {
                    "role": "system",
                    "content": "Classifique despesas em: Alimentação, Transporte, Saúde, Lazer, Educação, Moradia, ou Outros. Responda APENAS com a categoria."
                },
                {
                    "role": "user",
                    "content": f"Classifique: {descricao}"
                }
            ]
        )
        
        categoria = response.strip()
        return {
            "categoria": categoria,
            "confianca": 0.9,
            "provider": "xai"
        }
    except Exception as e:
        raise Exception(f"Erro XAI: {str(e)}")

