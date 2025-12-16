"""
Processador de CSV em Lote
===========================
Processa um CSV completo e classifica todas as transações usando ML + LLM
"""

import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime
import os
import llm_classifier

# Variáveis globais
modelo = None
scaler_X = None
label_encoder = None
tfidf = None

def carregar_modelo():
    """Carrega modelo ML se disponível"""
    global modelo, scaler_X, label_encoder, tfidf
    
    try:
        modelo = load_model('data/saved_models/category_model.h5', compile=False)
        modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        scaler_X = joblib.load('data/saved_models/scaler_X.pkl')
        label_encoder = joblib.load('data/saved_models/label_encoder.pkl')
        tfidf = joblib.load('data/saved_models/tfidf.pkl')
        return True
    except:
        return False

def classificar_ml(descricao, valor, data_despesa=None):
    """Classifica usando ML"""
    if modelo is None:
        return None
    
    try:
        if data_despesa is None:
            data_despesa = datetime.now()
        else:
            data_despesa = pd.to_datetime(data_despesa)
        
        text_features = tfidf.transform([descricao]).toarray()
        numeric_features = np.array([[valor]])
        mes = data_despesa.month
        dia_semana = data_despesa.dayofweek
        temporal_features = np.array([[mes, dia_semana]])
        
        features = np.hstack([text_features, numeric_features, temporal_features])
        features_normalized = scaler_X.transform(features)
        
        predicao = modelo.predict(features_normalized, verbose=0)
        categoria_idx = np.argmax(predicao[0])
        confianca = float(predicao[0][categoria_idx])
        categoria = label_encoder.inverse_transform([categoria_idx])[0]
        
        return {
            "categoria": categoria,
            "confianca": confianca
        }
    except:
        return None

def processar_csv(input_file, output_file):
    """
    Processa CSV completo e adiciona colunas de classificação
    """
    print(f"Processando {input_file}...")
    
    # Carregar modelo
    ml_disponivel = carregar_modelo()
    if ml_disponivel:
        print("Modelo ML carregado!")
    else:
        print("Modelo ML não disponível, usando apenas LLM")
    
    # Ler CSV
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except:
        df = pd.read_csv(input_file, encoding='latin-1')
    
    print(f"Total de linhas: {len(df)}")
    
    # Detectar colunas (flexível)
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
    
    if not col_descricao:
        raise ValueError("Coluna de descrição não encontrada!")
    if not col_valor:
        raise ValueError("Coluna de valor não encontrada!")
    
    print(f"Colunas detectadas: descrição={col_descricao}, valor={col_valor}, data={col_data}")
    
    # Processar cada linha
    resultados_ml = []
    resultados_llm = []
    resultados_openai = []
    confianca_ml = []
    confianca_llm = []
    confianca_openai = []
    
    for idx, row in df.iterrows():
        descricao = str(row[col_descricao]) if pd.notna(row[col_descricao]) else ""
        valor = float(row[col_valor]) if pd.notna(row[col_valor]) else 0.0
        data = row[col_data] if col_data and pd.notna(row[col_data]) else None
        
        if not descricao or valor <= 0:
            resultados_ml.append("")
            resultados_llm.append("")
            resultados_openai.append("")
            confianca_ml.append(0.0)
            confianca_llm.append(0.0)
            confianca_openai.append(0.0)
            continue
        
        # Classificar com ML
        resultado_ml = classificar_ml(descricao, valor, data)
        if resultado_ml:
            resultados_ml.append(resultado_ml['categoria'])
            confianca_ml.append(resultado_ml['confianca'])
        else:
            resultados_ml.append("")
            confianca_ml.append(0.0)
        
        # Classificar com LLM (todos os providers)
        try:
            resultado_llm = llm_classifier.classificar_com_llm(descricao)
            resultados_llm.append(resultado_llm['categoria'])
            confianca_llm.append(resultado_llm['confianca'])
            
            # Tentar especificamente OpenAI
            try:
                from providers import openai as openai_provider
                resultado_openai = openai_provider.classificar_categoria(descricao)
                resultados_openai.append(resultado_openai['categoria'])
                confianca_openai.append(resultado_openai['confianca'])
            except:
                resultados_openai.append(resultado_llm['categoria'])
                confianca_openai.append(resultado_llm['confianca'])
        except:
            resultados_llm.append("")
            confianca_llm.append(0.0)
            resultados_openai.append("")
            confianca_openai.append(0.0)
        
        if (idx + 1) % 10 == 0:
            print(f"Processadas {idx + 1}/{len(df)} linhas...")
    
    # Adicionar colunas ao DataFrame
    df['Categoria_ML'] = resultados_ml
    df['Confianca_ML'] = [f"{c*100:.1f}%" for c in confianca_ml]
    df['Categoria_LLM'] = resultados_llm
    df['Confianca_LLM'] = [f"{c*100:.1f}%" for c in confianca_llm]
    df['Categoria_OpenAI'] = resultados_openai
    df['Confianca_OpenAI'] = [f"{c*100:.1f}%" for c in confianca_openai]
    
    # Salvar resultado
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nProcessamento concluído!")
    print(f"Arquivo salvo: {output_file}")
    print(f"Total processado: {len(df)} transações")
    
    return df

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python processar_csv.py <arquivo_entrada.csv> [arquivo_saida.csv]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.csv', '_processado.csv')
    
    processar_csv(input_file, output_file)

