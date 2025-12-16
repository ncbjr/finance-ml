import os
import xai_sdk


xai_cliente = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

def test():

    return True