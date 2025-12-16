import os
import openai

openai_Cliente = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classificar_categoria(descricao: str) -> dict:
    """
    Classifica uma despesa usando OpenAI
    """
    try:
        response = openai_Cliente.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente financeiro. Classifique despesas em categorias: Alimentação, Transporte, Saúde, Lazer, Educação, Moradia, ou Outros. Responda APENAS com o nome da categoria, nada mais."
                },
                {
                    "role": "user",
                    "content": f"Classifique esta despesa: {descricao}"
                }
            ],
            temperature=0.3,
            max_tokens=20
        )
        
        categoria = response.choices[0].message.content.strip()
        return {
            "categoria": categoria,
            "confianca": 0.9,
            "provider": "openai"
        }
    except Exception as e:
        raise Exception(f"Erro OpenAI: {str(e)}")

