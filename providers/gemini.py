import os
import google.generativeai as gemini 

gemini.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def classificar_categoria(descricao: str) -> dict:
    """
    Classifica uma despesa usando Google Gemini
    """
    try:
        model = gemini.GenerativeModel('gemini-pro')
        prompt = f"Classifique esta despesa em UMA destas 7 categorias: CUSTOS FIXOS, CONFORTO, METAS, PRAZERES, LIBERDADE FINANCEIRA, CONHECIMENTO, ou CATEGORIZAR. Responda APENAS com o nome da categoria em MAIÚSCULAS: {descricao}"
        
        response = model.generate_content(prompt)
        categoria = response.text.strip().upper()
        
        # Validar que está nas 7 categorias corretas
        categorias_validas = ['CUSTOS FIXOS', 'CONFORTO', 'METAS', 'PRAZERES', 'LIBERDADE FINANCEIRA', 'CONHECIMENTO', 'CATEGORIZAR']
        if categoria not in categorias_validas:
            categoria = 'CATEGORIZAR'
        
        return {
            "categoria": categoria,
            "confianca": 0.9,
            "provider": "gemini"
        }
    except Exception as e:
        raise Exception(f"Erro Gemini: {str(e)}")

