import os
import anthropic

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTROPIC_API_KEY"))


def teste():

    return True