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
                    "content": "Você é um assistente financeiro. Classifique despesas em UMA destas 7 categorias: CUSTOS FIXOS, CONFORTO, METAS, PRAZERES, LIBERDADE FINANCEIRA, CONHECIMENTO, ou CATEGORIZAR. Responda APENAS com o nome da categoria em MAIÚSCULAS."
                },
                {
                    "role": "user",
                    "content": f"Classifique esta despesa: {descricao}"
                }
            ],
            temperature=0.3,
            max_tokens=20
        )
        
        categoria = completion.choices[0].message.content.strip().upper()
        
        # Validar que está nas 7 categorias corretas
        categorias_validas = ['CUSTOS FIXOS', 'CONFORTO', 'METAS', 'PRAZERES', 'LIBERDADE FINANCEIRA', 'CONHECIMENTO', 'CATEGORIZAR']
        if categoria not in categorias_validas:
            categoria = 'CATEGORIZAR'
        
        return {
            "categoria": categoria,
            "confianca": 0.9,
            "provider": "groq"
        }
    except Exception as e:
        raise Exception(f"Erro Groq: {str(e)}")

