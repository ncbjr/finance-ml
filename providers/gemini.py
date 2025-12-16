import os
import google.generativeai as gemini 

gemini.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def classificar_categoria(descricao: str) -> dict:
    """
    Classifica uma despesa usando Google Gemini
    """
    try:
        model = gemini.GenerativeModel('gemini-pro')
        prompt = f"Classifique esta despesa em UMA categoria (Alimentação, Transporte, Saúde, Lazer, Educação, Moradia, ou Outros). Responda APENAS com o nome da categoria: {descricao}"
        
        response = model.generate_content(prompt)
        categoria = response.text.strip()
        
        return {
            "categoria": categoria,
            "confianca": 0.9,
            "provider": "gemini"
        }
    except Exception as e:
        raise Exception(f"Erro Gemini: {str(e)}")

