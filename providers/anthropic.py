import os
import anthropic

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def classificar_categoria(descricao: str) -> dict:
    """
    Classifica uma despesa usando Anthropic Claude
    """
    try:
        message = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=20,
            messages=[
                {
                    "role": "user",
                    "content": f"Classifique esta despesa em UMA categoria (Alimentação, Transporte, Saúde, Lazer, Educação, Moradia, ou Outros). Responda APENAS com o nome da categoria: {descricao}"
                }
            ]
        )
        
        categoria = message.content[0].text.strip()
        return {
            "categoria": categoria,
            "confianca": 0.9,
            "provider": "anthropic"
        }
    except Exception as e:
        raise Exception(f"Erro Anthropic: {str(e)}")

