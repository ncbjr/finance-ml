import os
import google.generativeai as gemini 

gemini.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def test():
    return True