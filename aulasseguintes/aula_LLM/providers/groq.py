import os
import groq

groq_cliente = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

def test():
    return True