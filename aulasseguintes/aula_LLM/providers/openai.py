import os
import openai

openai_Cliente = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def teste():
    response = openai_Cliente.responses.create(
        model="gpt-5-nano",
        reasoning= {
            "effort" : "low"
        },
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Seja Direto e Consiso, use uma unica frase nas respostas."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Qual o Sentido da Vida?"
                    }
                ]
            }
        ]
    )

    return response