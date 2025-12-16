"""
INTERFACE WEB COMPLETA - PREVISÃO DE PREÇOS DE CASAS
====================================================

Este é um exemplo completo da interface web implementada.
Use este arquivo para testar a funcionalidade antes da prova.
"""

from flask import Flask, render_template, request, jsonify
import numpy as np
import joblib
from tensorflow.keras.models import load_model
import os

# Inicializar Flask app
app = Flask(__name__)

# Variáveis globais para modelo e scalers
modelo = None
scaler_X = None
scaler_y = None

def carregar_modelo_e_scalers():
    """
    Carrega o modelo Keras e os scalers salvos
    """
    try:
        # Carregar modelo Keras com esse compile=False é para evitar problemas de compatibilidade (gambiarra funcional kkk)
        modelo = load_model('CAMINHO DO MODELO', compile=False)
        
        # Recompilar o modelo com as configurações corretas
        from tensorflow.keras.optimizers import Adam
        modelo.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mean_squared_error',
            metrics=['mean_absolute_error']
        )
        
        # Carregar scalers para normalizar e desnormalizar os dados
        scaler_X = joblib.load('saved_model/scaler_X.pkl')
        scaler_y = joblib.load('saved_model/scaler_y.pkl')
        
        print("✓ Modelo e scalers carregados com sucesso!")
        return modelo, scaler_X, scaler_y

        #tratamento de erro para arquivo não encontrado
    except FileNotFoundError as e:
        print(f"✗ Arquivo não encontrado: {e}")
        print("Certifique-se de executar 'train_model.py' primeiro!")
        return None, None, None
    except Exception as e:
        print(f"✗ Erro ao carregar modelo: {e}")
        return None, None, None

def fazer_previsao(area, quartos, banheiros, idade):
    """
    Aqui a gente Faz a previsão do preço da casa
    
    Parâmetros:
    - area, quartos, banheiros, idade: características da casa
    
    o Retorno é: preço previsto (valor real não normalizado, apenas uma estimativa)
    """
    try:
        #Array numpy com as features [area, quartos, banheiros, idade]
        features = np.array([[area, quartos, banheiros, idade]])
        
        # Normalizar as features usando scaler_X
        features_normalized = scaler_X.transform(features)
        
        # Fazer previsão com o modelo, verbose=0 para não mostrar o progresso
        previsao_normalized = modelo.predict(features_normalized, verbose=0)
        
        # Desnormalizar o resultado usando scaler_y
        preco_previsto = scaler_y.inverse_transform(previsao_normalized)
        
        # Retornar o preço previsto (valor a estimado)
        return float(preco_previsto[0][0])
        
        #tratamento de erro para erro na previsão
    except Exception as e:
        print(f"Erro na previsão: {e}")
        raise e


#daqui pra baixo é configuração da interface web 
@app.route('/')
def index():
    """
    Exibe o formulário principal
    """
    return render_template('index.html')

@app.route('/prever', methods=['POST'])
def prever():
    """
    Processa a previsão via POST (formulário HTML)
    """
    try:
        # Obter dados do formulário
        area = float(request.form.get('area'))
        quartos = int(request.form.get('bedrooms'))
        banheiros = int(request.form.get('bathrooms'))
        idade = int(request.form.get('age'))
        
        # Validar dados de entrada
        if area <= 0 or quartos <= 0 or banheiros <= 0 or idade < 0:
            return jsonify({
                'status': 'error',
                'message': 'Valores devem ser positivos (idade pode ser 0)'
            })
        
        # Fazer previsão
        preco_previsto = fazer_previsao(area, quartos, banheiros, idade)
        
        return jsonify({
            'status': 'success',
            'preco_previsto': preco_previsto,
            'dados': {
                'area': area,
                'quartos': quartos,
                'banheiros': banheiros,
                'idade': idade
            }
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': 'Dados de entrada inválidos. Use apenas números.'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        })

@app.route('/api/prever', methods=['POST'])
def api_prever():
    """
    API JSON para previsão
    """
    try:
        # Obter dados JSON
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Dados JSON não fornecidos'
            })
        
        # Extrair e validar dados
        area = float(data.get('area', 0))
        quartos = int(data.get('bedrooms', 0))
        banheiros = int(data.get('bathrooms', 0))
        idade = int(data.get('age', 0))
        
        # Validar dados de entrada
        if area <= 0 or quartos <= 0 or banheiros <= 0 or idade < 0:
            return jsonify({
                'status': 'error',
                'message': 'Valores devem ser positivos (idade pode ser 0)'
            })
        
        # Fazer previsão
        preco_previsto = fazer_previsao(area, quartos, banheiros, idade)
        
        return jsonify({
            'status': 'success',
            'preco_previsto': preco_previsto
        })
        
    except (ValueError, TypeError) as e:
        return jsonify({
            'status': 'error',
            'message': 'Dados de entrada inválidos. Verifique o formato JSON.'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        })

@app.route('/status')
def status():
    """
    Endpoint para verificar se o modelo está carregado
    """
    if modelo is not None and scaler_X is not None and scaler_y is not None:
        return jsonify({
            'status': 'success',
            'message': 'Modelo carregado e pronto para uso'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Modelo não carregado'
        })

def main():
    """Função principal"""
    global modelo, scaler_X, scaler_y
    
    print("=== INTERFACE WEB DE PREVISÃO DE PREÇOS ===\n")
    
    # Carregar modelo e scalers
    print("Carregando modelo e scalers...")
    modelo, scaler_X, scaler_y = carregar_modelo_e_scalers()
    
    if modelo is None:
        print("✗ Não foi possível carregar o modelo!")
        print("Certifique-se de executar 'train_model.py' primeiro.")
        return
    
    # Iniciar servidor Flask
    print("\n" + "="*50)
    print("SERVIDOR WEB INICIADO")
    print("="*50)
    print("🌐 Acesse: http://localhost:5000")
    print("📊 Status: http://localhost:5000/status")
    print("🔧 API: http://localhost:5000/api/prever")
    print("\nPressione Ctrl+C para parar o servidor")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
