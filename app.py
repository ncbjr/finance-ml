"""
SISTEMA DE GESTÃO FINANCEIRA - Interface Web
=============================================

Adaptado de interface_web_completa.py para classificação de categorias financeiras.
Combina Machine Learning e LLMs para classificar despesas automaticamente.
"""

from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime
import os

# Importar classificadores LLM
import llm_classifier

# Inicializar Flask app
app = Flask(__name__)

# Variáveis globais para modelo e scalers
modelo = None
scaler_X = None
label_encoder = None
tfidf = None

def carregar_modelo_e_recursos():
    """
    Carrega o modelo Keras e os recursos salvos (scalers, encoder, tfidf)
    """
    try:
        # Carregar modelo Keras
        modelo = load_model('data/saved_models/category_model.h5', compile=False)
        
        # Recompilar o modelo
        modelo.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Carregar recursos para processar dados
        scaler_X = joblib.load('data/saved_models/scaler_X.pkl')
        label_encoder = joblib.load('data/saved_models/label_encoder.pkl')
        tfidf = joblib.load('data/saved_models/tfidf.pkl')
        
        print("✓ Modelo e recursos carregados com sucesso!")
        return modelo, scaler_X, label_encoder, tfidf

    except FileNotFoundError as e:
        print(f"✗ Arquivo não encontrado: {e}")
        print("Certifique-se de executar 'python train_model.py' primeiro!")
        return None, None, None, None
    except Exception as e:
        print(f"✗ Erro ao carregar modelo: {e}")
        return None, None, None, None

def classificar_categoria_ml(descricao, valor, data_despesa=None):
    """
    Classifica a categoria da despesa usando Machine Learning
    
    Parâmetros:
    - descricao: descrição da despesa
    - valor: valor da despesa
    - data_despesa: data da despesa (opcional)
    
    Retorno: {"categoria": "...", "confianca": 0.0-1.0}
    """
    try:
        # Se não tem data, usar data atual
        if data_despesa is None:
            data_despesa = datetime.now()
        else:
            data_despesa = pd.to_datetime(data_despesa)
        
        # Extrair features de texto (TF-IDF)
        text_features = tfidf.transform([descricao]).toarray()
        
        # Features numéricas
        numeric_features = np.array([[valor]])
        
        # Features temporais
        mes = data_despesa.month
        dia_semana = data_despesa.dayofweek
        temporal_features = np.array([[mes, dia_semana]])
        
        # Combinar features
        features = np.hstack([text_features, numeric_features, temporal_features])
        
        # Normalizar features
        features_normalized = scaler_X.transform(features)
        
        # Fazer previsão
        predicao = modelo.predict(features_normalized, verbose=0)
        
        # Pegar categoria com maior probabilidade
        categoria_idx = np.argmax(predicao[0])
        confianca = float(predicao[0][categoria_idx])
        categoria = label_encoder.inverse_transform([categoria_idx])[0]
        
        return {
            "categoria": categoria,
            "confianca": confianca
        }
        
    except Exception as e:
        print(f"Erro na classificação ML: {e}")
        raise e


# Rotas da aplicação
@app.route('/')
def index():
    """
    Exibe a página principal
    """
    return render_template('index.html')

@app.route('/api/classify/ml', methods=['POST'])
def api_classify_ml():
    """
    Classifica usando apenas Machine Learning
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Dados JSON não fornecidos'
            })
        
        descricao = data.get('descricao', '')
        valor = float(data.get('valor', 0))
        data_despesa = data.get('data', None)
        
        if not descricao or valor <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Descrição e valor são obrigatórios'
            })
        
        # Classificar com ML
        resultado = classificar_categoria_ml(descricao, valor, data_despesa)
        
        return jsonify({
            'status': 'success',
            'categoria': resultado['categoria'],
            'confianca': resultado['confianca'],
            'metodo': 'ml'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        })

@app.route('/api/classify/llm', methods=['POST'])
def api_classify_llm():
    """
    Classifica usando apenas LLM
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Dados JSON não fornecidos'
            })
        
        descricao = data.get('descricao', '')
        
        if not descricao:
            return jsonify({
                'status': 'error',
                'message': 'Descrição é obrigatória'
            })
        
        # Classificar com LLM
        resultado = llm_classifier.classificar_com_llm(descricao)
        
        return jsonify({
            'status': 'success',
            'categoria': resultado['categoria'],
            'confianca': resultado['confianca'],
            'metodo': 'llm',
            'provider': resultado['provider']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        })

@app.route('/api/classify/hybrid', methods=['POST'])
def api_classify_hybrid():
    """
    Classifica usando ML + LLM (híbrido)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Dados JSON não fornecidos'
            })
        
        descricao = data.get('descricao', '')
        valor = float(data.get('valor', 0))
        data_despesa = data.get('data', None)
        
        if not descricao or valor <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Descrição e valor são obrigatórios'
            })
        
        # Classificar com ML (se modelo disponível)
        categoria_ml = None
        confianca_ml = 0.0
        
        if modelo is not None:
            try:
                resultado_ml = classificar_categoria_ml(descricao, valor, data_despesa)
                categoria_ml = resultado_ml['categoria']
                confianca_ml = resultado_ml['confianca']
            except:
                pass
        
        # Classificar com LLM e combinar
        resultado = llm_classifier.classificar_hibrido(descricao, categoria_ml, confianca_ml)
        
        return jsonify({
            'status': 'success',
            'categoria': resultado['categoria'],
            'confianca': resultado['confianca'],
            'metodo': 'hybrid',
            'provider': resultado['provider'],
            'detalhes': resultado
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        })

@app.route('/api/expense', methods=['POST'])
def api_add_expense():
    """
    Adiciona uma nova despesa ao CSV
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Dados JSON não fornecidos'
            })
        
        # Extrair dados
        data_despesa = data.get('data', datetime.now().strftime('%Y-%m-%d'))
        descricao = data.get('descricao', '')
        valor = float(data.get('valor', 0))
        categoria = data.get('categoria', 'Outros')
        subcategoria = data.get('subcategoria', '')
        tags = data.get('tags', '')
        
        # Validar
        if not descricao or valor <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Descrição e valor são obrigatórios'
            })
        
        # Ler CSV existente
        df = pd.read_csv('data/expenses.csv')
        
        # Adicionar nova linha
        nova_despesa = pd.DataFrame([{
            'data': data_despesa,
            'descricao': descricao,
            'valor': valor,
            'categoria': categoria,
            'subcategoria': subcategoria,
            'tags': tags
        }])
        
        df = pd.concat([df, nova_despesa], ignore_index=True)
        
        # Salvar
        df.to_csv('data/expenses.csv', index=False)
        
        return jsonify({
            'status': 'success',
            'message': 'Despesa adicionada com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao adicionar despesa: {str(e)}'
        })

@app.route('/api/expenses', methods=['GET'])
def api_get_expenses():
    """
    Lista todas as despesas
    """
    try:
        df = pd.read_csv('data/expenses.csv')
        
        # Converter para JSON
        expenses = df.to_dict('records')
        
        # Estatísticas básicas
        total = float(df['valor'].sum())
        media = float(df['valor'].mean())
        count = len(df)
        
        # Gastos por categoria
        por_categoria = df.groupby('categoria')['valor'].sum().to_dict()
        
        return jsonify({
            'status': 'success',
            'expenses': expenses,
            'stats': {
                'total': total,
                'media': media,
                'count': count,
                'por_categoria': por_categoria
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao listar despesas: {str(e)}'
        })

@app.route('/status')
def status():
    """
    Endpoint para verificar se o modelo está carregado
    """
    if modelo is not None and scaler_X is not None and label_encoder is not None:
        return jsonify({
            'status': 'success',
            'message': 'Modelo ML carregado e pronto para uso',
            'categorias': list(label_encoder.classes_)
        })
    else:
        return jsonify({
            'status': 'warning',
            'message': 'Modelo ML não carregado (apenas LLM disponível)'
        })

def main():
    """Função principal"""
    global modelo, scaler_X, label_encoder, tfidf
    
    print("=== SISTEMA DE GESTÃO FINANCEIRA ===\n")
    
    # Carregar modelo e recursos
    print("Carregando modelo ML e recursos...")
    modelo, scaler_X, label_encoder, tfidf = carregar_modelo_e_recursos()
    
    if modelo is None:
        print("⚠ Modelo ML não disponível, usando apenas LLM")
        print("Execute 'python train_model.py' para treinar o modelo ML\n")
    
    # Iniciar servidor Flask
    print("\n" + "="*50)
    print("SERVIDOR WEB INICIADO")
    print("="*50)
    print("🌐 Acesse: http://localhost:5000")
    print("📊 Status: http://localhost:5000/status")
    print("🔧 APIs disponíveis:")
    print("   - POST /api/classify/ml (Machine Learning)")
    print("   - POST /api/classify/llm (LLM)")
    print("   - POST /api/classify/hybrid (ML + LLM)")
    print("   - POST /api/expense (Adicionar despesa)")
    print("   - GET /api/expenses (Listar despesas)")
    print("\nPressione Ctrl+C para parar o servidor")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()

