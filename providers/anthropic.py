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
                    "content": f"Classifique esta despesa em UMA destas 7 categorias: CUSTOS FIXOS, CONFORTO, METAS, PRAZERES, LIBERDADE FINANCEIRA, CONHECIMENTO, ou CATEGORIZAR. Responda APENAS com o nome da categoria em MAIÚSCULAS: {descricao}"
                }
            ]
        )
        
        categoria = message.content[0].text.strip().upper()
        
        # Validar que está nas 7 categorias corretas
        categorias_validas = ['CUSTOS FIXOS', 'CONFORTO', 'METAS', 'PRAZERES', 'LIBERDADE FINANCEIRA', 'CONHECIMENTO', 'CATEGORIZAR']
        if categoria not in categorias_validas:
            categoria = 'CATEGORIZAR'
        
        return {
            "categoria": categoria,
            "confianca": 0.9,
            "provider": "anthropic"
        }
    except Exception as e:
        raise Exception(f"Erro Anthropic: {str(e)}")

