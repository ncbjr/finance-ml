"""
Sistema de Gestão Financeira - Treinamento do Modelo de SUBCATEGORIAS
=======================================================================

Treina modelo para classificar subcategorias (livre, muitas classes).
Usa categoria como feature adicional para melhorar precisão.
"""

import pandas as pd
import numpy as np
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except:
    MATPLOTLIB_AVAILABLE = False
    print("AVISO: Matplotlib nao disponivel - graficos desabilitados")
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import os
import joblib

def mapear_tags_para_categoria(tags):
    """
    Mapeia tags para categorias (mesma função do train_model_categoria)
    """
    if pd.isna(tags) or tags == '':
        return 'CATEGORIZAR'
    
    tags_lower = str(tags).lower().strip()
    
    if 'custos fixos' in tags_lower:
        return 'CUSTOS FIXOS'
    elif 'conforto' in tags_lower:
        return 'CONFORTO'
    elif 'prazeres' in tags_lower:
        return 'PRAZERES'
    elif 'conhecimento' in tags_lower:
        return 'CONHECIMENTO'
    elif 'metas' in tags_lower:
        return 'METAS'
    elif 'liberdade financeira' in tags_lower:
        return 'LIBERDADE FINANCEIRA'
    elif 'categorizar' in tags_lower:
        return 'CATEGORIZAR'
    else:
        return 'CATEGORIZAR'

def carregar_dados():
    """
    Carrega o arquivo CSV e prepara dados para subcategorias
    """
    df = pd.read_csv('data/expenses.csv')
    
    # Mapear categorias corretamente se necessário
    if 'tags' in df.columns:
        df['categoria_mapeada'] = df['tags'].apply(mapear_tags_para_categoria)
        df['categoria'] = df.apply(
            lambda row: row['categoria_mapeada'] if pd.isna(row.get('categoria', '')) or str(row.get('categoria', '')).strip() == '' 
            else row['categoria'],
            axis=1
        )
        if 'categoria_mapeada' in df.columns:
            df = df.drop(columns=['categoria_mapeada'])
    
    # Filtrar apenas linhas com subcategoria válida
    df = df[df['subcategoria'].notna()]
    df = df[df['subcategoria'].astype(str).str.strip() != '']
    df = df[df['subcategoria'].astype(str).str.strip() != 'DESCONHECIDO']
    
    return df

def preparar_dados(df):
    """
    Prepara os dados para classificação de SUBCATEGORIAS
    Usa categoria como feature adicional!
    """
    print("   Preparando features para subcategorias...")
    
    # Separar Y (subcategoria)
    y = df['subcategoria']
    
    # Encoder para subcategorias
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"   Total de subcategorias únicas: {len(label_encoder.classes_)}")
    print(f"   Primeiras 10: {list(label_encoder.classes_[:10])}")
    
    # Features de texto - TF-IDF da descrição
    tfidf = TfidfVectorizer(max_features=100, stop_words=None)
    text_features = tfidf.fit_transform(df['descricao']).toarray()
    
    # Features numéricas - valor
    numeric_features = df[['valor']].values
    
    # FEATURE ADICIONAL: Categoria (one-hot encoding)
    # Isso ajuda muito na classificação de subcategorias!
    categoria_encoder = LabelEncoder()
    categorias_encoded = categoria_encoder.fit_transform(df['categoria'])
    
    # One-hot encoding de categoria
    from sklearn.preprocessing import OneHotEncoder
    categoria_onehot = OneHotEncoder(sparse_output=False)
    categoria_features = categoria_onehot.fit_transform(categorias_encoded.reshape(-1, 1))
    
    print(f"   Categorias únicas: {len(categoria_encoder.classes_)}")
    print(f"   Features de categoria (one-hot): {categoria_features.shape[1]} dimensões")
    
    # FEATURE ADICIONAL: Tags (one-hot encoding)
    # Processar tags: se vazio/NaN, usar string vazia
    df['tags_processed'] = df['tags'].fillna('').astype(str).str.strip()
    
    # Criar encoder para tags únicas
    tags_encoder = LabelEncoder()
    tags_encoded = tags_encoder.fit_transform(df['tags_processed'])
    
    # One-hot encoding de tags
    tags_onehot = OneHotEncoder(sparse_output=False)
    tags_features = tags_onehot.fit_transform(tags_encoded.reshape(-1, 1))
    
    print(f"   Tags únicas: {len(tags_encoder.classes_)}")
    print(f"   Features de tags (one-hot): {tags_features.shape[1]} dimensões")
    
    # Combinar TODAS as features (sem temporais, com tags)
    X = np.hstack([
        text_features,      # TF-IDF da descrição
        numeric_features,  # Valor
        categoria_features, # Categoria (one-hot)
        tags_features      # Tags (one-hot) - NOVO!
    ])
    
    # Dividir dados de treino e teste
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Normalização
    print("   Normalizando dados X (features)...")
    scaler_X = StandardScaler()
    X_treino_scaled = scaler_X.fit_transform(X_treino)
    X_teste_scaled = scaler_X.transform(X_teste)
    
    # Salvar recursos
    os.makedirs('data/saved_models', exist_ok=True)
    joblib.dump(scaler_X, 'data/saved_models/subcategoria_scaler_X.pkl')
    joblib.dump(label_encoder, 'data/saved_models/subcategoria_label_encoder.pkl')
    joblib.dump(tfidf, 'data/saved_models/subcategoria_tfidf.pkl')
    joblib.dump(categoria_encoder, 'data/saved_models/subcategoria_categoria_encoder.pkl')
    joblib.dump(categoria_onehot, 'data/saved_models/subcategoria_categoria_onehot.pkl')
    joblib.dump(tags_encoder, 'data/saved_models/subcategoria_tags_encoder.pkl')
    joblib.dump(tags_onehot, 'data/saved_models/subcategoria_tags_onehot.pkl')
    
    print(f"   Dados X normalizados: média={X_treino_scaled.mean():.3f}, std={X_treino_scaled.std():.3f}")
    print(f"   Total de features: {X_treino_scaled.shape[1]}")
    
    return X_treino_scaled, X_teste_scaled, y_treino, y_teste, label_encoder

def criar_modelo(input_dim, num_classes):
    """
    Cria o modelo Sequential para classificação de subcategorias
    """
    modelo = Sequential()
    
    # Camada oculta 1 (maior, pois temos mais features)
    modelo.add(Dense(128, activation='relu', input_dim=input_dim))
    modelo.add(Dropout(0.3))
    
    # Camada oculta 2
    modelo.add(Dense(64, activation='relu'))
    modelo.add(Dropout(0.3))
    
    # Camada oculta 3
    modelo.add(Dense(32, activation='relu'))
    modelo.add(Dropout(0.2))
    
    # Camada de saída - N subcategorias
    modelo.add(Dense(num_classes, activation='softmax'))
    
    return modelo

def compilar_modelo(modelo):
    """
    Compila o modelo
    """
    modelo.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

def treinar_modelo(modelo, X_treino, y_treino, X_teste, y_teste):
    """
    Treina o modelo
    """
    resultado = modelo.fit(
        X_treino, y_treino,
        validation_data=(X_teste, y_teste),
        epochs=150,  # Mais épocas para subcategorias (mais classes)
        batch_size=16,
        verbose=1
    )
    return resultado

def salvar_modelo(modelo):
    """
    Salva o modelo treinado
    """
    os.makedirs('data/saved_models', exist_ok=True)
    modelo.save('data/saved_models/subcategoria_model.h5')

def avaliar_modelo(modelo, X_teste, y_teste, label_encoder):
    """
    Avalia o modelo
    """
    print("\n=== AVALIAÇÃO DO MODELO DE SUBCATEGORIAS ===")
    
    # Fazer previsões
    y_pred_proba = modelo.predict(X_teste)
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    # Calcular métricas
    from sklearn.metrics import accuracy_score, classification_report
    accuracy = accuracy_score(y_teste, y_pred)
    
    print(f"📊 MÉTRICAS DE QUALIDADE:")
    print(f"   Acurácia: {accuracy*100:.2f}%")
    
    # Mostrar top subcategorias
    print(f"\n🔍 TOP 10 SUBCATEGORIAS MAIS COMUNS:")
    subcategorias_unicas = label_encoder.classes_
    for i, subcat in enumerate(subcategorias_unicas[:10]):
        count = (y_teste == label_encoder.transform([subcat])[0]).sum()
        print(f"   {i+1}. {subcat} ({count} amostras)")
    
    # Mostrar exemplos
    print(f"\n🔍 EXEMPLOS DE PREVISÕES:")
    for i in range(min(5, len(y_teste))):
        real = label_encoder.inverse_transform([y_teste[i]])[0]
        previsto = label_encoder.inverse_transform([y_pred[i]])[0]
        confianca = y_pred_proba[i][y_pred[i]] * 100
        status = "OK" if real == previsto else "ERRO"
        print(f"   {status} Real: {real:25s} | Previsto: {previsto:25s} | Confianca: {confianca:.1f}%")
    
    if accuracy > 0.7:
        print(f"\nOK EXCELENTE! Modelo com alta precisao (Acurácia > 70%)")
    elif accuracy > 0.5:
        print(f"\nOK BOM! Modelo com boa precisao (Acurácia > 50%)")
    else:
        print(f"\nAVISO: Modelo pode precisar de mais treinamento (Acurácia < 50%)")
    
    return accuracy

def plotar_resultado(resultado):
    """
    Plota os gráficos de treinamento
    """
    if not MATPLOTLIB_AVAILABLE:
        print("   AVISO: Matplotlib nao disponivel - pulando geracao de graficos")
        return
    
    try:
        plt.figure(figsize=(12, 4))
        
        # Plotar Loss
        plt.subplot(1, 2, 1)
        plt.plot(resultado.history['loss'], label='Treino')
        plt.plot(resultado.history['val_loss'], label='Teste')
        plt.title('Loss do Modelo de Subcategorias')
        plt.xlabel('Época')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        # Plotar Accuracy
        plt.subplot(1, 2, 2)
        plt.plot(resultado.history['accuracy'], label='Treino')
        plt.plot(resultado.history['val_accuracy'], label='Teste')
        plt.title('Accuracy do Modelo de Subcategorias')
        plt.xlabel('Época')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('resultado_treinamento_subcategoria.png')
        print("   Gráficos salvos em 'resultado_treinamento_subcategoria.png'")
        plt.close()
    except Exception as e:
        print(f"   AVISO: Erro ao gerar graficos: {e}")

def main():
    """
    Função principal
    """
    print("=== TREINAMENTO DO MODELO DE SUBCATEGORIAS ===\n")
    
    # 1. Carregar dados
    print("1. Carregando dados...")
    df = carregar_dados()
    print(f"   Dados carregados: {len(df)} amostras")
    print(f"   Colunas: {list(df.columns)}")
    
    # 2. Preparar dados
    print("\n2. Preparando dados...")
    X_treino, X_teste, y_treino, y_teste, label_encoder = preparar_dados(df)
    print(f"   Dados de treino: {X_treino.shape[0]} amostras")
    print(f"   Dados de teste: {X_teste.shape[0]} amostras")
    print(f"   Features totais: {X_treino.shape[1]}")
    
    # 3. Criar modelo
    print("\n3. Criando modelo...")
    num_classes = len(label_encoder.classes_)
    modelo = criar_modelo(X_treino.shape[1], num_classes)
    print("   Modelo criado!")
    print(f"   Arquitetura: {X_treino.shape[1]} features → 128 → 64 → 32 → {num_classes} subcategorias")
    
    # 4. Compilar modelo
    print("\n4. Compilando modelo...")
    compilar_modelo(modelo)
    print("   Modelo compilado!")
    
    # 5. Treinar modelo
    print("\n5. Treinando modelo...")
    print("   Isso pode levar alguns minutos (mais classes = mais tempo)...")
    resultado = treinar_modelo(modelo, X_treino, y_treino, X_teste, y_teste)
    print("   Treinamento concluído!")
    
    # 6. Salvar modelo
    print("\n6. Salvando modelo...")
    salvar_modelo(modelo)
    print("   Modelo salvo!")
    
    # 7. Avaliar modelo
    print("\n7. Avaliando qualidade do modelo...")
    accuracy = avaliar_modelo(modelo, X_teste, y_teste, label_encoder)
    
    # 8. Plotar resultado
    print("\n8. Gerando gráficos...")
    plotar_resultado(resultado)
    
    print("\n=== TREINAMENTO CONCLUÍDO ===")
    print("OK Modelo de subcategorias treinado e avaliado com sucesso!")
    print("📁 Arquivos salvos:")
    print("   - data/saved_models/subcategoria_model.h5 (modelo treinado)")
    print("   - data/saved_models/subcategoria_scaler_X.pkl (normalizador)")
    print("   - data/saved_models/subcategoria_label_encoder.pkl (codificador)")
    print("   - data/saved_models/subcategoria_tfidf.pkl (vetorizador)")
    print("   - data/saved_models/subcategoria_categoria_encoder.pkl (encoder de categoria)")
    print("   - data/saved_models/subcategoria_categoria_onehot.pkl (one-hot de categoria)")
    print("   - resultado_treinamento_subcategoria.png (gráficos)")
    print("\n💡 DICA: Agora você pode usar ambos os modelos no app.py!")

if __name__ == "__main__":
    main()

