"""
SISTEMA DE GESTÃO FINANCEIRA - Interface Web
=============================================

Adaptado de interface_web_completa.py para classificação de categorias financeiras.
Combina Machine Learning e LLMs para classificar despesas automaticamente.
"""

from flask import Flask, render_template, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime
import os
import uuid
import json
import threading
import queue
import subprocess
import shutil

# Importar classificadores LLM
import llm_classifier

# Inicializar Flask app
app = Flask(__name__)

# Variáveis globais para modelos de categoria e subcategoria
modelo_categoria = None
scaler_X_categoria = None
label_encoder_categoria = None
tfidf_categoria = None

modelo_subcategoria = None
scaler_X_subcategoria = None
label_encoder_subcategoria = None
tfidf_subcategoria = None
categoria_encoder_subcategoria = None
categoria_onehot_subcategoria = None
tags_encoder_subcategoria = None
tags_onehot_subcategoria = None

def carregar_modelo_e_recursos():
    """
    Carrega ambos os modelos (categoria e subcategoria) e seus recursos
    """
    global modelo_categoria, scaler_X_categoria, label_encoder_categoria, tfidf_categoria
    global modelo_subcategoria, scaler_X_subcategoria, label_encoder_subcategoria, tfidf_subcategoria
    global categoria_encoder_subcategoria, categoria_onehot_subcategoria
    global tags_encoder_subcategoria, tags_onehot_subcategoria
    
    # Carregar modelo de CATEGORIA
    try:
        modelo_categoria = load_model('data/saved_models/category_model.h5', compile=False)
        modelo_categoria.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        scaler_X_categoria = joblib.load('data/saved_models/category_scaler_X.pkl')
        label_encoder_categoria = joblib.load('data/saved_models/category_label_encoder.pkl')
        tfidf_categoria = joblib.load('data/saved_models/category_tfidf.pkl')
        print("✓ Modelo de CATEGORIA carregado com sucesso!")
    except Exception as e:
        print(f"⚠ Modelo de categoria não disponível: {e}")
        modelo_categoria = None
    
    # Carregar modelo de SUBCATEGORIA
    try:
        modelo_subcategoria = load_model('data/saved_models/subcategoria_model.h5', compile=False)
        modelo_subcategoria.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        scaler_X_subcategoria = joblib.load('data/saved_models/subcategoria_scaler_X.pkl')
        label_encoder_subcategoria = joblib.load('data/saved_models/subcategoria_label_encoder.pkl')
        tfidf_subcategoria = joblib.load('data/saved_models/subcategoria_tfidf.pkl')
        categoria_encoder_subcategoria = joblib.load('data/saved_models/subcategoria_categoria_encoder.pkl')
        categoria_onehot_subcategoria = joblib.load('data/saved_models/subcategoria_categoria_onehot.pkl')
        # Carregar recursos de tags (pode não existir em modelos antigos)
        try:
            tags_encoder_subcategoria = joblib.load('data/saved_models/subcategoria_tags_encoder.pkl')
            tags_onehot_subcategoria = joblib.load('data/saved_models/subcategoria_tags_onehot.pkl')
        except:
            tags_encoder_subcategoria = None
            tags_onehot_subcategoria = None
            print("⚠ Recursos de tags não encontrados (modelo antigo?)")
        print("✓ Modelo de SUBCATEGORIA carregado com sucesso!")
    except Exception as e:
        print(f"⚠ Modelo de subcategoria não disponível: {e}")
        modelo_subcategoria = None
    
    return modelo_categoria, modelo_subcategoria

def classificar_categoria_ml(descricao, valor, data_despesa=None):
    """
    Classifica a CATEGORIA (7 classes) da despesa usando Machine Learning
    
    Parâmetros:
    - descricao: descrição da despesa
    - valor: valor da despesa
    - data_despesa: data da despesa (opcional)
    
    Retorno: {"categoria": "...", "confianca": 0.0-1.0}
    """
    global modelo_categoria, scaler_X_categoria, label_encoder_categoria, tfidf_categoria
    
    if modelo_categoria is None:
        return None
    
    try:
        # Se não tem data, usar data atual
        if data_despesa is None:
            data_despesa = datetime.now()
        else:
            data_despesa = pd.to_datetime(data_despesa)
        
        # Extrair features de texto (TF-IDF) - ÚNICA FEATURE
        text_features = tfidf_categoria.transform([descricao]).toarray()
        
        # Usar apenas descrição
        features = text_features
        
        # Normalizar features
        features_normalized = scaler_X_categoria.transform(features)
        
        # Fazer previsão
        predicao = modelo_categoria.predict(features_normalized, verbose=0)
        
        # Pegar categoria com maior probabilidade
        categoria_idx = np.argmax(predicao[0])
        confianca = float(predicao[0][categoria_idx])
        categoria = label_encoder_categoria.inverse_transform([categoria_idx])[0]
        
        return {
            "categoria": categoria,
            "confianca": confianca
        }
        
    except Exception as e:
        print(f"Erro na classificação ML de categoria: {e}")
        return None

def classificar_subcategoria_ml(descricao, valor, data_despesa=None, categoria=None, tags=''):
    """
    Classifica a SUBCATEGORIA da despesa usando Machine Learning
    Usa categoria e tags como features adicionais!
    
    Parâmetros:
    - descricao: descrição da despesa
    - valor: valor da despesa
    - data_despesa: data da despesa (opcional, não usado mais)
    - categoria: categoria já classificada (obrigatória para melhor precisão)
    - tags: tags da despesa (opcional)
    
    Retorno: {"subcategoria": "...", "confianca": 0.0-1.0}
    """
    global modelo_subcategoria, scaler_X_subcategoria, label_encoder_subcategoria, tfidf_subcategoria
    global categoria_encoder_subcategoria, categoria_onehot_subcategoria
    global tags_encoder_subcategoria, tags_onehot_subcategoria
    
    if modelo_subcategoria is None:
        return None
    
    try:
        # Se não tem categoria, tentar classificar primeiro
        if categoria is None:
            resultado_cat = classificar_categoria_ml(descricao, valor, data_despesa)
            if resultado_cat:
                categoria = resultado_cat['categoria']
            else:
                categoria = 'CATEGORIZAR'  # Default
        
        # Extrair features de texto (TF-IDF)
        text_features = tfidf_subcategoria.transform([descricao]).toarray()
        
        # Features numéricas
        numeric_features = np.array([[valor]])
        
        # Features de categoria (one-hot)
        try:
            categoria_encoded = categoria_encoder_subcategoria.transform([categoria])[0]
            categoria_features = categoria_onehot_subcategoria.transform(categoria_encoded.reshape(-1, 1))
        except:
            # Se categoria não está no encoder, usar zeros
            categoria_features = np.zeros((1, len(categoria_encoder_subcategoria.classes_)))
        
        # Features de tags (one-hot)
        if tags_encoder_subcategoria is not None and tags_onehot_subcategoria is not None:
            try:
                tags_processed = str(tags).strip() if tags else ''
                tags_encoded = tags_encoder_subcategoria.transform([tags_processed])[0]
                tags_features = tags_onehot_subcategoria.transform(tags_encoded.reshape(-1, 1))
            except:
                # Se tag não está no encoder, usar zeros
                tags_features = np.zeros((1, len(tags_encoder_subcategoria.classes_)))
        else:
            # Modelo antigo sem tags - usar zeros
            tags_features = np.zeros((1, 1))  # Placeholder
        
        # Combinar TODAS as features (sem temporais, com tags)
        features = np.hstack([
            text_features, 
            numeric_features, 
            categoria_features,
            tags_features
        ])
        
        # Normalizar features
        features_normalized = scaler_X_subcategoria.transform(features)
        
        # Fazer previsão
        predicao = modelo_subcategoria.predict(features_normalized, verbose=0)
        
        # Pegar subcategoria com maior probabilidade
        subcategoria_idx = np.argmax(predicao[0])
        confianca = float(predicao[0][subcategoria_idx])
        subcategoria = label_encoder_subcategoria.inverse_transform([subcategoria_idx])[0]
        
        return {
            "subcategoria": subcategoria,
            "confianca": confianca
        }
        
    except Exception as e:
        print(f"Erro na classificação ML de subcategoria: {e}")
        return None


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
        
        # Classificar categoria com ML
        resultado_categoria = classificar_categoria_ml(descricao, valor, data_despesa)
        
        # Classificar subcategoria com ML (usando categoria como feature)
        resultado_subcategoria = None
        if resultado_categoria:
            resultado_subcategoria = classificar_subcategoria_ml(
                descricao, valor, data_despesa, resultado_categoria['categoria'], tags=''
            )
        
        resposta = {
            'status': 'success',
            'metodo': 'ml'
        }
        
        if resultado_categoria:
            resposta['categoria'] = resultado_categoria['categoria']
            resposta['confianca_categoria'] = resultado_categoria['confianca']
        else:
            resposta['categoria'] = None
            resposta['confianca_categoria'] = 0.0
        
        if resultado_subcategoria:
            resposta['subcategoria'] = resultado_subcategoria['subcategoria']
            resposta['confianca_subcategoria'] = resultado_subcategoria['confianca']
        else:
            resposta['subcategoria'] = None
            resposta['confianca_subcategoria'] = 0.0
        
        return jsonify(resposta)
        
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
    Classifica usando ML + LLM (híbrido) - retorna categoria + subcategoria
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
        
        # Classificar CATEGORIA com ML (se modelo disponível)
        categoria_ml = None
        confianca_categoria_ml = 0.0
        
        if modelo_categoria is not None:
            try:
                resultado_ml_cat = classificar_categoria_ml(descricao, valor, data_despesa)
                if resultado_ml_cat:
                    categoria_ml = resultado_ml_cat['categoria']
                    confianca_categoria_ml = resultado_ml_cat['confianca']
            except:
                pass
        
        # Classificar SUBCATEGORIA com ML (usando categoria como feature)
        subcategoria_ml = None
        confianca_subcategoria_ml = 0.0
        
        if modelo_subcategoria is not None and categoria_ml:
            try:
                resultado_ml_sub = classificar_subcategoria_ml(descricao, valor, data_despesa, categoria_ml, tags=data.get('tags', ''))
                if resultado_ml_sub:
                    subcategoria_ml = resultado_ml_sub['subcategoria']
                    confianca_subcategoria_ml = resultado_ml_sub['confianca']
            except:
                pass
        
        # Classificar com LLM e combinar (categoria + subcategoria)
        resultado_llm = llm_classifier.classificar_hibrido(
            descricao, 
            categoria_ml, 
            confianca_categoria_ml,
            subcategoria_ml,
            confianca_subcategoria_ml
        )
        
        # Para subcategoria, usar LLM também (se disponível)
        # Por enquanto, usar apenas ML para subcategoria
        # TODO: Adicionar LLM para subcategoria também
        
        resposta = {
            'status': 'success',
            'categoria': resultado_llm['categoria'],
            'confianca_categoria': resultado_llm['confianca'],
            'subcategoria': resultado_llm.get('subcategoria', subcategoria_ml if subcategoria_ml else ''),
            'confianca_subcategoria': resultado_llm.get('confianca_subcategoria', confianca_subcategoria_ml if subcategoria_ml else 0.0),
            'metodo': 'hybrid',
            'provider': resultado_llm['provider'],
            'detalhes': {
                'ml_categoria': categoria_ml,
                'ml_confianca_categoria': confianca_categoria_ml,
                'ml_subcategoria': subcategoria_ml,
                'ml_confianca_subcategoria': confianca_subcategoria_ml,
                'llm_categoria': resultado_llm.get('llm_categoria'),
                'llm_confianca': resultado_llm.get('llm_confianca'),
                'llm_subcategoria': resultado_llm.get('llm_subcategoria', ''),
                'llm_confianca_subcategoria': resultado_llm.get('llm_confianca_subcategoria', 0.0)
            }
        }
        
        return jsonify(resposta)
        
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
        
        # Adicionar nova linha (ordem correta: data,descricao,valor,tags,subcategoria,categoria)
        nova_despesa = pd.DataFrame([{
            'data': data_despesa,
            'descricao': descricao,
            'valor': valor,
            'tags': tags,
            'subcategoria': subcategoria,
            'categoria': categoria
        }])
        
        df = pd.concat([df, nova_despesa], ignore_index=True)
        
        # Garantir ordem correta das colunas ao salvar
        colunas_ordenadas = ['data', 'descricao', 'valor', 'tags', 'subcategoria', 'categoria']
        df = df[colunas_ordenadas]
        
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

@app.route('/expenses')
def expenses_page():
    """
    Página para visualizar todas as despesas
    """
    return render_template('expenses.html')

@app.route('/api/expenses', methods=['GET'])
def api_get_expenses():
    """
    Lista todas as despesas com paginação, filtros e ordenação
    """
    try:
        # Parâmetros de query
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        search = request.args.get('search', '')
        categoria = request.args.get('categoria', '')
        subcategoria = request.args.get('subcategoria', '')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        valor_min = request.args.get('valor_min', type=float)
        valor_max = request.args.get('valor_max', type=float)
        sort_by = request.args.get('sort_by', 'data')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Carregar dados
        df = pd.read_csv('data/expenses.csv')
        
        # Garantir ordem correta das colunas
        colunas_ordenadas = ['data', 'descricao', 'valor', 'tags', 'subcategoria', 'categoria']
        df = df[colunas_ordenadas]
        
        # Converter data para datetime se necessário
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
        
        # Aplicar filtros
        if search:
            df = df[df['descricao'].str.contains(search, case=False, na=False)]
        if categoria:
            df = df[df['categoria'] == categoria]
        if subcategoria:
            df = df[df['subcategoria'] == subcategoria]
        if data_inicio:
            try:
                data_inicio_dt = pd.to_datetime(data_inicio)
                df = df[df['data'] >= data_inicio_dt]
            except:
                pass
        if data_fim:
            try:
                data_fim_dt = pd.to_datetime(data_fim)
                df = df[df['data'] <= data_fim_dt]
            except:
                pass
        if valor_min is not None:
            df = df[df['valor'] >= valor_min]
        if valor_max is not None:
            df = df[df['valor'] <= valor_max]
        
        # Ordenar
        if sort_by in df.columns:
            ascending = (sort_order == 'asc')
            df = df.sort_values(sort_by, ascending=ascending, na_position='last')
        
        # Converter data de volta para string para JSON
        if 'data' in df.columns:
            df['data'] = df['data'].dt.strftime('%Y-%m-%d').fillna('')
        
        # Paginar
        total = len(df)
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        start = (page - 1) * limit
        end = start + limit
        df_page = df.iloc[start:end] if total > 0 else df
        
        # Converter para JSON
        expenses = df_page.to_dict('records')
        
        # Estatísticas (sobre dados filtrados, não paginados)
        total_valor = float(df['valor'].sum()) if len(df) > 0 else 0.0
        media = float(df['valor'].mean()) if len(df) > 0 else 0.0
        count = len(df)
        
        # Gastos por categoria
        por_categoria = df.groupby('categoria')['valor'].sum().to_dict() if len(df) > 0 else {}
        
        return jsonify({
            'status': 'success',
            'expenses': expenses,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': total_pages
            },
            'stats': {
                'total': total_valor,
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

@app.route('/api/expense/<int:index>', methods=['PUT', 'DELETE'])
def api_manage_expense(index):
    """
    Editar ou excluir despesa por índice
    """
    try:
        df = pd.read_csv('data/expenses.csv')
        
        if index < 0 or index >= len(df):
            return jsonify({
                'status': 'error',
                'message': 'Índice inválido'
            }), 400
        
        if request.method == 'DELETE':
            # Excluir despesa
            df = df.drop(df.index[index]).reset_index(drop=True)
            df.to_csv('data/expenses.csv', index=False)
            
            return jsonify({
                'status': 'success',
                'message': 'Despesa excluída com sucesso'
            })
        
        elif request.method == 'PUT':
            # Editar despesa
            data = request.get_json()
            
            # Atualizar campos
            if 'data' in data:
                df.at[index, 'data'] = data['data']
            if 'descricao' in data:
                df.at[index, 'descricao'] = data['descricao']
            if 'valor' in data:
                df.at[index, 'valor'] = float(data['valor'])
            if 'categoria' in data:
                df.at[index, 'categoria'] = data['categoria']
            if 'subcategoria' in data:
                df.at[index, 'subcategoria'] = data.get('subcategoria', '')
            if 'tags' in data:
                df.at[index, 'tags'] = data.get('tags', '')
            
            # Garantir ordem correta das colunas
            colunas_ordenadas = ['data', 'descricao', 'valor', 'tags', 'subcategoria', 'categoria']
            df = df[colunas_ordenadas]
            
            df.to_csv('data/expenses.csv', index=False)
            
            return jsonify({
                'status': 'success',
                'message': 'Despesa atualizada com sucesso',
                'expense': df.iloc[index].to_dict()
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao gerenciar despesa: {str(e)}'
        }), 500

@app.route('/api/expense/find', methods=['POST'])
def api_find_expense():
    """
    Encontrar índice de uma despesa pelos seus dados
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Dados não fornecidos'
            }), 400
        
        df = pd.read_csv('data/expenses.csv')
        
        # Buscar despesa que corresponde aos dados
        mask = pd.Series([True] * len(df))
        
        if 'data' in data:
            mask = mask & (df['data'] == data['data'])
        if 'descricao' in data:
            mask = mask & (df['descricao'] == data['descricao'])
        if 'valor' in data:
            mask = mask & (df['valor'] == float(data['valor']))
        
        matches = df[mask]
        
        if len(matches) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Despesa não encontrada'
            }), 404
        
        # Retornar o primeiro índice encontrado
        index = matches.index[0]
        
        return jsonify({
            'status': 'success',
            'index': int(index)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao buscar despesa: {str(e)}'
        }), 500

@app.route('/api/expenses/export', methods=['GET'])
def api_export_expenses():
    """
    Exportar despesas filtradas para CSV
    """
    try:
        # Aplicar mesmos filtros da listagem
        search = request.args.get('search', '')
        categoria = request.args.get('categoria', '')
        subcategoria = request.args.get('subcategoria', '')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        valor_min = request.args.get('valor_min', type=float)
        valor_max = request.args.get('valor_max', type=float)
        
        # Carregar e filtrar dados
        df = pd.read_csv('data/expenses.csv')
        
        # Garantir ordem correta das colunas
        colunas_ordenadas = ['data', 'descricao', 'valor', 'tags', 'subcategoria', 'categoria']
        df = df[colunas_ordenadas]
        
        # Converter data para datetime se necessário
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
        
        # Aplicar filtros
        if search:
            df = df[df['descricao'].str.contains(search, case=False, na=False)]
        if categoria:
            df = df[df['categoria'] == categoria]
        if subcategoria:
            df = df[df['subcategoria'] == subcategoria]
        if data_inicio:
            try:
                data_inicio_dt = pd.to_datetime(data_inicio)
                df = df[df['data'] >= data_inicio_dt]
            except:
                pass
        if data_fim:
            try:
                data_fim_dt = pd.to_datetime(data_fim)
                df = df[df['data'] <= data_fim_dt]
            except:
                pass
        if valor_min is not None:
            df = df[df['valor'] >= valor_min]
        if valor_max is not None:
            df = df[df['valor'] <= valor_max]
        
        # Converter data de volta para string
        if 'data' in df.columns:
            df['data'] = df['data'].dt.strftime('%Y-%m-%d').fillna('')
        
        # Gerar arquivo CSV temporário
        filename = f'expenses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        filepath = os.path.join('data', filename)
        df.to_csv(filepath, index=False)
        
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='text/csv')
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao exportar despesas: {str(e)}'
        }), 500

@app.route('/upload')
def upload_page():
    """
    Página para upload de CSV
    """
    return render_template('upload.html')

@app.route('/transactions')
def transactions_page():
    """
    Página para visualizar transações processadas
    """
    return render_template('transactions.html')

@app.route('/api/upload-csv', methods=['POST'])
def api_upload_csv():
    """
    Upload e processamento de CSV em lote
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Nenhum arquivo enviado'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Arquivo não selecionado'
            })
        
        # Salvar arquivo temporário
        os.makedirs('data/uploads', exist_ok=True)
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        input_path = f'data/uploads/{file_id}_{filename}'
        output_path = f'data/uploads/{file_id}_processado_{filename}'
        
        file.save(input_path)
        
        # Processar CSV
        df = pd.read_csv(input_path, encoding='utf-8', on_bad_lines='skip')
        
        # Detectar colunas
        col_descricao = None
        col_valor = None
        col_data = None
        
        for col in df.columns:
            col_upper = col.upper()
            if 'DESCRI' in col_upper or 'DESCRICAO' in col_upper:
                col_descricao = col
            if 'VALOR' in col_upper:
                col_valor = col
            if 'DATA' in col_upper or 'DATE' in col_upper:
                col_data = col
        
        if not col_descricao or not col_valor:
            return jsonify({
                'status': 'error',
                'message': 'Colunas de descrição e valor não encontradas'
            })
        
        # Processar cada linha
        resultados_ml_cat = []
        resultados_ml_sub = []
        resultados_llm = []
        resultados_openai = []
        confianca_ml_cat = []
        confianca_ml_sub = []
        confianca_llm = []
        confianca_openai = []
        
        total = len(df)
        for idx, row in df.iterrows():
            descricao = str(row[col_descricao]) if pd.notna(row[col_descricao]) else ""
            valor = float(row[col_valor]) if pd.notna(row[col_valor]) else 0.0
            data = row[col_data] if col_data and pd.notna(row[col_data]) else None
            
            if not descricao or valor <= 0:
                resultados_ml_cat.append("")
                resultados_ml_sub.append("")
                resultados_llm.append("")
                resultados_openai.append("")
                confianca_ml_cat.append(0.0)
                confianca_ml_sub.append(0.0)
                confianca_llm.append(0.0)
                confianca_openai.append(0.0)
                continue
            
            # ML - Categoria
            resultado_ml_cat = None
            if modelo_categoria is not None:
                try:
                    resultado_ml_cat = classificar_categoria_ml(descricao, valor, data)
                    resultados_ml_cat.append(resultado_ml_cat['categoria'] if resultado_ml_cat else "")
                    confianca_ml_cat.append(resultado_ml_cat['confianca'] if resultado_ml_cat else 0.0)
                except:
                    resultados_ml_cat.append("")
                    confianca_ml_cat.append(0.0)
            else:
                resultados_ml_cat.append("")
                confianca_ml_cat.append(0.0)
            
            # ML - Subcategoria (usando categoria como feature)
            resultado_ml_sub = None
            if modelo_subcategoria is not None and resultado_ml_cat:
                try:
                    resultado_ml_sub = classificar_subcategoria_ml(
                        descricao, valor, data, resultado_ml_cat.get('categoria'), tags=row.get('tags', '')
                    )
                    resultados_ml_sub.append(resultado_ml_sub['subcategoria'] if resultado_ml_sub else "")
                    confianca_ml_sub.append(resultado_ml_sub['confianca'] if resultado_ml_sub else 0.0)
                except:
                    resultados_ml_sub.append("")
                    confianca_ml_sub.append(0.0)
            else:
                resultados_ml_sub.append("")
                confianca_ml_sub.append(0.0)
            
            # LLM (todos)
            try:
                resultado_llm = llm_classifier.classificar_com_llm(descricao)
                resultados_llm.append(resultado_llm.get('categoria', ''))
                confianca_llm.append(resultado_llm.get('confianca', 0.0))
            except:
                resultados_llm.append("")
                confianca_llm.append(0.0)
            
            # OpenAI específico
            try:
                from providers import openai as openai_provider
                resultado_openai = openai_provider.classificar_categoria(descricao)
                resultados_openai.append(resultado_openai.get('categoria', ''))
                confianca_openai.append(resultado_openai.get('confianca', 0.0))
            except:
                resultados_openai.append(resultado_llm.get('categoria', '') if resultado_llm else "")
                confianca_openai.append(resultado_llm.get('confianca', 0.0) if resultado_llm else 0.0)
        
        # Adicionar colunas
        df['Categoria_ML'] = resultados_ml_cat
        df['Confianca_ML'] = [c for c in confianca_ml_cat]
        df['Subcategoria_ML'] = resultados_ml_sub
        df['Confianca_Subcategoria_ML'] = [c for c in confianca_ml_sub]
        df['Categoria_LLM'] = resultados_llm
        df['Confianca_LLM'] = [c for c in confianca_llm]
        df['Categoria_OpenAI'] = resultados_openai
        df['Confianca_OpenAI'] = [c for c in confianca_openai]
        
        # Salvar resultado
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        # Salvar metadados
        metadata = {
            'file_id': file_id,
            'original_filename': filename,
            'processed_filename': f'{file_id}_processado_{filename}',
            'total_rows': total,
            'processed_rows': len([r for r in resultados_ml_cat if r])
        }
        
        with open(f'data/uploads/{file_id}_metadata.json', 'w') as f:
            json.dump(metadata, f)
        
        return jsonify({
            'status': 'success',
            'file_id': file_id,
            'total_rows': total,
            'message': f'{total} transações processadas com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar CSV: {str(e)}'
        })

@app.route('/api/download-csv/<file_id>')
def api_download_csv(file_id):
    """
    Download do CSV processado
    """
    try:
        # Buscar metadados
        with open(f'data/uploads/{file_id}_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        file_path = f"data/uploads/{metadata['processed_filename']}"
        return send_file(file_path, as_attachment=True, download_name=f"processado_{metadata['original_filename']}")
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao baixar arquivo: {str(e)}'
        }), 404

@app.route('/api/transactions/<file_id>')
def api_get_transactions(file_id):
    """
    Retorna transações processadas
    """
    try:
        # Buscar metadados
        with open(f'data/uploads/{file_id}_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        # Ler CSV processado
        df = pd.read_csv(f"data/uploads/{metadata['processed_filename']}")
        
        # Converter para JSON
        transactions = df.to_dict('records')
        
        return jsonify({
            'status': 'success',
            'transactions': transactions,
            'metadata': metadata
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao buscar transações: {str(e)}'
        }), 404

@app.route('/status')
def status():
    """
    Endpoint para verificar se os modelos estão carregados
    """
    status_info = {
        'status': 'success',
        'modelos': {}
    }
    
    if modelo_categoria is not None:
        status_info['modelos']['categoria'] = {
            'carregado': True,
            'categorias': list(label_encoder_categoria.classes_)
        }
    else:
        status_info['modelos']['categoria'] = {'carregado': False}
    
    if modelo_subcategoria is not None:
        status_info['modelos']['subcategoria'] = {
            'carregado': True,
            'total_subcategorias': len(label_encoder_subcategoria.classes_)
        }
    else:
        status_info['modelos']['subcategoria'] = {'carregado': False}
    
    if not status_info['modelos']['categoria']['carregado'] and not status_info['modelos']['subcategoria']['carregado']:
        status_info['status'] = 'warning'
        status_info['message'] = 'Modelos ML não carregados (apenas LLM disponível)'
    else:
        status_info['message'] = 'Modelos ML carregados e prontos para uso'
    
    return jsonify(status_info)

# ============================================
# SISTEMA DE TREINAMENTO DE MODELOS
# ============================================

# Estrutura para gerenciar sessões de treinamento
training_sessions = {}
training_lock = threading.Lock()

def executar_com_output(comando, progress_queue, session_id=None):
    """
    Executa comando e captura output linha por linha
    """
    try:
        process = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            shell=True,
            cwd=os.getcwd()
        )
        
        for line in iter(process.stdout.readline, ''):
            if line:
                progress_queue.put(line.strip())
        
        process.wait()
        return process.returncode
    except Exception as e:
        progress_queue.put(f"ERRO ao executar comando: {str(e)}")
        return 1

def executar_treinamento(session_id, arquivo_csv):
    """
    Executa treinamento de ambos os modelos de forma assíncrona
    """
    session = training_sessions.get(session_id)
    if not session:
        return
    
    try:
        session['progress'].put("=== INICIANDO TREINAMENTO ===")
        session['progress'].put(f"Arquivo: {arquivo_csv}")
        session['progress'].put("")
        
        # Backup do expenses.csv original
        expenses_backup = 'data/expenses_backup.csv'
        if os.path.exists('data/expenses.csv'):
            shutil.copy('data/expenses.csv', expenses_backup)
            session['progress'].put("✓ Backup do expenses.csv criado")
        
        # Copiar arquivo enviado para expenses.csv
        shutil.copy(arquivo_csv, 'data/expenses.csv')
        session['progress'].put("✓ Arquivo de treinamento copiado para data/expenses.csv")
        session['progress'].put("")
        
        # Treinar modelo de CATEGORIA
        session['progress'].put("=" * 50)
        session['progress'].put("TREINANDO MODELO DE CATEGORIAS")
        session['progress'].put("=" * 50)
        
        comando_categoria = "python train_model_categoria.py"
        returncode = executar_com_output(comando_categoria, session['progress'], session_id)
        
        if returncode == 0:
            session['progress'].put("✓ Modelo de CATEGORIAS treinado com sucesso!")
        else:
            session['progress'].put("✗ Erro ao treinar modelo de CATEGORIAS")
            session['status'] = 'error'
            session['error'] = 'Erro ao treinar modelo de categorias'
            return
        
        session['progress'].put("")
        
        # Treinar modelo de SUBCATEGORIA
        session['progress'].put("=" * 50)
        session['progress'].put("TREINANDO MODELO DE SUBCATEGORIAS")
        session['progress'].put("=" * 50)
        
        comando_subcategoria = "python train_model_subcategoria.py"
        returncode = executar_com_output(comando_subcategoria, session['progress'], session_id)
        
        if returncode == 0:
            session['progress'].put("✓ Modelo de SUBCATEGORIAS treinado com sucesso!")
        else:
            session['progress'].put("✗ Erro ao treinar modelo de SUBCATEGORIAS")
            session['status'] = 'error'
            session['error'] = 'Erro ao treinar modelo de subcategorias'
            return
        
        session['progress'].put("")
        session['progress'].put("=" * 50)
        session['progress'].put("✓ TREINAMENTO CONCLUÍDO COM SUCESSO!")
        session['progress'].put("=" * 50)
        session['progress'].put("Os modelos foram salvos em data/saved_models/")
        session['progress'].put("Recarregue a página para usar os novos modelos.")
        
        # Restaurar backup se necessário
        if os.path.exists(expenses_backup):
            # Opcional: manter o arquivo de treinamento ou restaurar backup
            # Por enquanto, mantemos o arquivo de treinamento
            pass
        
        session['status'] = 'completed'
        session['completed_at'] = datetime.now().isoformat()
        
    except Exception as e:
        session['progress'].put(f"ERRO CRÍTICO: {str(e)}")
        session['status'] = 'error'
        session['error'] = str(e)
        
        # Restaurar backup se necessário
        if os.path.exists(expenses_backup):
            shutil.copy(expenses_backup, 'data/expenses.csv')
            session['progress'].put("✓ expenses.csv restaurado do backup")

@app.route('/train')
def train_page():
    """
    Página para treinar modelos
    """
    return render_template('train.html')

@app.route('/api/train/download-template', methods=['GET'])
def download_template():
    """
    Gera e retorna planilha modelo para download
    """
    try:
        # Criar CSV modelo
        template_data = {
            'data': ['2024-12-15', '2024-12-15', '2024-12-15', '2024-12-15', '2024-12-15'],
            'descricao': [
                'Supermercado Extra',
                'Uber para trabalho',
                'Netflix assinatura',
                'Curso de Python',
                'Investimento em ações'
            ],
            'valor': [350.00, 25.50, 45.90, 299.00, 1000.00],
            'tags': [
                'custos fixos',
                'conforto',
                'prazeres',
                'conhecimento',
                'liberdade financeira'
            ],
            'subcategoria': [
                'ALIMENTAÇÃO',
                'TRANSPORTE',
                'STREAMING',
                'EDUCAÇÃO',
                'INVESTIMENTO'
            ],
            'categoria': [
                'CUSTOS FIXOS',
                'CONFORTO',
                'PRAZERES',
                'CONHECIMENTO',
                'LIBERDADE FINANCEIRA'
            ]
        }
        
        df = pd.DataFrame(template_data)
        
        # Garantir ordem correta das colunas
        colunas_ordenadas = ['data', 'descricao', 'valor', 'tags', 'subcategoria', 'categoria']
        df = df[colunas_ordenadas]
        
        # Salvar temporariamente
        template_path = 'data/template.csv'
        os.makedirs('data', exist_ok=True)
        df.to_csv(template_path, index=False)
        
        return send_file(template_path, as_attachment=True, download_name='template_despesas.csv', mimetype='text/csv')
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao gerar template: {str(e)}'
        }), 500

@app.route('/api/train/upload', methods=['POST'])
def train_upload():
    """
    Recebe e valida arquivo CSV para treinamento
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Nenhum arquivo enviado'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Nenhum arquivo selecionado'
            }), 400
        
        # Validar extensão
        if not file.filename.endswith('.csv'):
            return jsonify({
                'status': 'error',
                'message': 'Apenas arquivos CSV são permitidos'
            }), 400
        
        # Validar tamanho (máximo 10MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({
                'status': 'error',
                'message': 'Arquivo muito grande (máximo 10MB)'
            }), 400
        
        # Ler e validar estrutura
        try:
            df = pd.read_csv(file)
            
            # Validar colunas obrigatórias
            colunas_obrigatorias = ['data', 'descricao', 'valor', 'tags', 'subcategoria', 'categoria']
            colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
            
            if colunas_faltando:
                return jsonify({
                    'status': 'error',
                    'message': f'Colunas faltando: {", ".join(colunas_faltando)}'
                }), 400
            
            # Validar que não está vazio
            if len(df) == 0:
                return jsonify({
                    'status': 'error',
                    'message': 'Arquivo está vazio'
                }), 400
            
            # Validar tipos básicos
            try:
                df['valor'] = pd.to_numeric(df['valor'], errors='raise')
            except:
                return jsonify({
                    'status': 'error',
                    'message': 'Coluna "valor" deve conter apenas números'
                }), 400
            
        except pd.errors.EmptyDataError:
            return jsonify({
                'status': 'error',
                'message': 'Arquivo CSV está vazio ou inválido'
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao ler CSV: {str(e)}'
            }), 400
        
        # Salvar arquivo validado
        session_id = str(uuid.uuid4())
        session_dir = f'data/training_sessions/{session_id}'
        os.makedirs(session_dir, exist_ok=True)
        
        arquivo_path = os.path.join(session_dir, 'input.csv')
        file.seek(0)
        file.save(arquivo_path)
        
        # Criar sessão
        with training_lock:
            training_sessions[session_id] = {
                'status': 'pending',
                'progress': queue.Queue(),
                'arquivo': arquivo_path,
                'thread': None,
                'started_at': None,
                'completed_at': None,
                'error': None
            }
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'message': 'Arquivo validado com sucesso',
            'rows': len(df)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar upload: {str(e)}'
        }), 500

@app.route('/api/train/start/<session_id>', methods=['POST'])
def train_start(session_id):
    """
    Inicia treinamento assíncrono
    """
    with training_lock:
        session = training_sessions.get(session_id)
        
        if not session:
            return jsonify({
                'status': 'error',
                'message': 'Sessão não encontrada'
            }), 404
        
        if session['status'] == 'running':
            return jsonify({
                'status': 'error',
                'message': 'Treinamento já está em execução'
            }), 400
        
        if session['status'] == 'completed':
            return jsonify({
                'status': 'error',
                'message': 'Treinamento já foi concluído'
            }), 400
        
        # Iniciar thread de treinamento
        session['status'] = 'running'
        session['started_at'] = datetime.now().isoformat()
        
        thread = threading.Thread(
            target=executar_treinamento,
            args=(session_id, session['arquivo']),
            daemon=True
        )
        thread.start()
        session['thread'] = thread
    
    return jsonify({
        'status': 'success',
        'message': 'Treinamento iniciado',
        'session_id': session_id
    })

@app.route('/api/train/progress/<session_id>')
def train_progress(session_id):
    """
    Stream de progresso usando Server-Sent Events (SSE)
    """
    def generate():
        session = training_sessions.get(session_id)
        
        if not session:
            yield f"data: {json.dumps({'error': 'Sessão não encontrada'})}\n\n"
            return
        
        # Enviar status inicial
        yield f"data: {json.dumps({'status': session['status'], 'line': 'Conectado ao stream de progresso...'})}\n\n"
        
        # Stream de progresso
        while True:
            try:
                # Tentar pegar linha da queue (timeout de 1 segundo)
                try:
                    line = session['progress'].get(timeout=1)
                    yield f"data: {json.dumps({'line': line})}\n\n"
                except queue.Empty:
                    # Se queue vazia, verificar status
                    if session['status'] in ['completed', 'error']:
                        yield f"data: {json.dumps({'status': session['status'], 'completed': True})}\n\n"
                        break
                    # Continuar esperando
                    yield f"data: {json.dumps({'heartbeat': True})}\n\n"
                    continue
                    
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
    
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })

def main():
    """Função principal"""
    global modelo_categoria, modelo_subcategoria
    
    print("=== SISTEMA DE GESTÃO FINANCEIRA ===\n")
    
    # Carregar modelos e recursos
    print("Carregando modelos ML (categoria + subcategoria)...")
    modelo_categoria, modelo_subcategoria = carregar_modelo_e_recursos()
    
    if modelo_categoria is None:
        print("⚠ Modelo de CATEGORIA não disponível")
        print("Execute 'python train_model_categoria.py' para treinar\n")
    
    if modelo_subcategoria is None:
        print("⚠ Modelo de SUBCATEGORIA não disponível")
        print("Execute 'python train_model_subcategoria.py' para treinar\n")
    
    if modelo_categoria is None and modelo_subcategoria is None:
        print("⚠ Usando apenas LLM (sem modelos ML)\n")
    
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

