import os
import groq

groq_cliente = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

def classificar_categoria(descricao: str) -> dict:
    """
    Classifica uma despesa usando Groq
    """
    try:
        completion = groq_cliente.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente financeiro. Classifique despesas em categorias: Alimentação, Transporte, Saúde, Lazer, Educação, Moradia, ou Outros. Responda APENAS com o nome da categoria."
                },
                {
                    "role": "user",
                    "content": f"Classifique esta despesa: {descricao}"
                }
            ],
            temperature=0.3,
            max_tokens=20
        )
        
        categoria = completion.choices[0].message.content.strip()
        return {
            "categoria": categoria,
            "confianca": 0.9,
            "provider": "groq"
        }
    except Exception as e:
        raise Exception(f"Erro Groq: {str(e)}")

