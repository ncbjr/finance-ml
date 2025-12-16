import os
import openai

openai_Cliente = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classificar_categoria(descricao: str) -> dict:
    """
    Classifica uma despesa usando OpenAI (categoria - 7 classes)
    """
    try:
        response = openai_Cliente.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente financeiro. Classifique despesas em UMA destas 7 categorias: CUSTOS FIXOS, CONFORTO, METAS, PRAZERES, LIBERDADE FINANCEIRA, CONHECIMENTO, ou CATEGORIZAR. Responda APENAS com o nome da categoria em MAIÚSCULAS, nada mais."
                },
                {
                    "role": "user",
                    "content": f"Classifique esta despesa: {descricao}"
                }
            ],
            temperature=0.3,
            max_tokens=30
        )
        
        categoria = response.choices[0].message.content.strip().upper()
        
        # Validar que está nas 7 categorias corretas
        categorias_validas = ['CUSTOS FIXOS', 'CONFORTO', 'METAS', 'PRAZERES', 'LIBERDADE FINANCEIRA', 'CONHECIMENTO', 'CATEGORIZAR']
        if categoria not in categorias_validas:
            categoria = 'CATEGORIZAR'
        
        return {
            "categoria": categoria,
            "confianca": 0.9,
            "provider": "openai"
        }
    except Exception as e:
        raise Exception(f"Erro OpenAI: {str(e)}")

