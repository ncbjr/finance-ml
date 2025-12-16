"""
Sistema de Gestão Financeira - Treinamento do Modelo de CATEGORIAS
===================================================================

Treina modelo para classificar nas 7 categorias principais:
- CUSTOS FIXOS
- CONFORTO
- METAS
- PRAZERES
- LIBERDADE FINANCEIRA
- CONHECIMENTO
- CATEGORIZAR
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

# As 7 categorias corretas
CATEGORIAS_VALIDAS = [
    'CUSTOS FIXOS',
    'CONFORTO',
    'METAS',
    'PRAZERES',
    'LIBERDADE FINANCEIRA',
    'CONHECIMENTO',
    'CATEGORIZAR'
]

def mapear_tags_para_categoria(tags):
    """
    Mapeia tags para categorias corretas
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
    Carrega o arquivo CSV e mapeia categorias corretamente
    """
    df = pd.read_csv('data/expenses.csv')
    
    # Se a coluna categoria não tem as 7 categorias corretas, mapear usando tags
    if 'tags' in df.columns:
        # Mapear usando tags como fonte principal
        df['categoria_mapeada'] = df['tags'].apply(mapear_tags_para_categoria)
        
        # Se categoria atual não está nas válidas, usar a mapeada
        df['categoria'] = df.apply(
            lambda row: row['categoria_mapeada'] if row.get('categoria', '') not in CATEGORIAS_VALIDAS 
            else row['categoria'],
            axis=1
        )
        df = df.drop(columns=['categoria_mapeada'])
    else:
        # Se não tem tags, mapear categoria existente
        df['categoria'] = df['categoria'].apply(
            lambda x: mapear_tags_para_categoria(x) if x not in CATEGORIAS_VALIDAS else x
        )
    
    # Garantir que todas as categorias estão nas válidas
    df['categoria'] = df['categoria'].apply(
        lambda x: x if x in CATEGORIAS_VALIDAS else 'CATEGORIZAR'
    )
    
    return df

def preparar_dados(df):
    """
    Prepara os dados para classificação de CATEGORIAS (7 classes)
    """
    print("   Preparando features para categorias...")
    
    # Separar Y (categoria) - deve ter apenas as 7 categorias válidas
    y = df['categoria']
    
    # Validar que todas as categorias são válidas
    categorias_unicas = y.unique()
    print(f"   Categorias encontradas: {list(categorias_unicas)}")
    
    # Filtrar apenas categorias válidas
    df = df[df['categoria'].isin(CATEGORIAS_VALIDAS)]
    y = df['categoria']
    
    # Encoder para categorias
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Features de texto - TF-IDF da descrição (ÚNICA FEATURE)
    tfidf = TfidfVectorizer(max_features=100, stop_words=None)
    text_features = tfidf.fit_transform(df['descricao']).toarray()
    
    # Usar apenas descrição como feature
    X = text_features
    
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
    joblib.dump(scaler_X, 'data/saved_models/category_scaler_X.pkl')
    joblib.dump(label_encoder, 'data/saved_models/category_label_encoder.pkl')
    joblib.dump(tfidf, 'data/saved_models/category_tfidf.pkl')
    
    print(f"   Dados X normalizados: média={X_treino_scaled.mean():.3f}, std={X_treino_scaled.std():.3f}")
    print(f"   Categorias únicas: {len(label_encoder.classes_)}")
    print(f"   Classes: {list(label_encoder.classes_)}")
    
    return X_treino_scaled, X_teste_scaled, y_treino, y_teste, label_encoder

def criar_modelo(input_dim, num_classes):
    """
    Cria o modelo Sequential para classificação de categorias (7 classes)
    """
    modelo = Sequential()
    
    # Camada oculta 1
    modelo.add(Dense(64, activation='relu', input_dim=input_dim))
    modelo.add(Dropout(0.3))
    
    # Camada oculta 2
    modelo.add(Dense(32, activation='relu'))
    modelo.add(Dropout(0.3))
    
    # Camada de saída - 7 categorias
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
        epochs=100,
        batch_size=8,
        verbose=1
    )
    return resultado

def salvar_modelo(modelo):
    """
    Salva o modelo treinado
    """
    os.makedirs('data/saved_models', exist_ok=True)
    modelo.save('data/saved_models/category_model.h5')

def avaliar_modelo(modelo, X_teste, y_teste, label_encoder):
    """
    Avalia o modelo
    """
    print("\n=== AVALIAÇÃO DO MODELO DE CATEGORIAS ===")
    
    # Fazer previsões
    y_pred_proba = modelo.predict(X_teste)
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    # Calcular métricas
    from sklearn.metrics import accuracy_score, classification_report
    accuracy = accuracy_score(y_teste, y_pred)
    
    print(f"📊 MÉTRICAS DE QUALIDADE:")
    print(f"   Acurácia: {accuracy*100:.2f}%")
    
    print(f"\n🔍 RELATÓRIO POR CATEGORIA:")
    print(classification_report(y_teste, y_pred, target_names=label_encoder.classes_, zero_division=0))
    
    # Mostrar exemplos
    print(f"\n🔍 EXEMPLOS DE PREVISÕES:")
    for i in range(min(5, len(y_teste))):
        real = label_encoder.inverse_transform([y_teste[i]])[0]
        previsto = label_encoder.inverse_transform([y_pred[i]])[0]
        confianca = y_pred_proba[i][y_pred[i]] * 100
        status = "OK" if real == previsto else "ERRO"
        print(f"   {status} Real: {real:25s} | Previsto: {previsto:25s} | Confianca: {confianca:.1f}%")
    
    if accuracy > 0.8:
        print(f"\nOK EXCELENTE! Modelo com alta precisao (Acurácia > 80%)")
    elif accuracy > 0.6:
        print(f"\nOK BOM! Modelo com boa precisao (Acurácia > 60%)")
    else:
        print(f"\nAVISO: Modelo pode precisar de mais treinamento (Acurácia < 60%)")
    
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
        plt.title('Loss do Modelo de Categorias')
        plt.xlabel('Época')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        # Plotar Accuracy
        plt.subplot(1, 2, 2)
        plt.plot(resultado.history['accuracy'], label='Treino')
        plt.plot(resultado.history['val_accuracy'], label='Teste')
        plt.title('Accuracy do Modelo de Categorias')
        plt.xlabel('Época')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('resultado_treinamento_categoria.png')
        print("   Gráficos salvos em 'resultado_treinamento_categoria.png'")
        plt.close()
    except Exception as e:
        print(f"   AVISO: Erro ao gerar graficos: {e}")

def main():
    """
    Função principal
    """
    print("=== TREINAMENTO DO MODELO DE CATEGORIAS (7 CLASSES) ===\n")
    
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
    print(f"   Arquitetura: {X_treino.shape[1]} features → 64 → 32 → {num_classes} categorias")
    
    # 4. Compilar modelo
    print("\n4. Compilando modelo...")
    compilar_modelo(modelo)
    print("   Modelo compilado!")
    
    # 5. Treinar modelo
    print("\n5. Treinando modelo...")
    print("   Isso pode levar alguns minutos...")
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
    print("OK Modelo de categorias treinado e avaliado com sucesso!")
    print("📁 Arquivos salvos:")
    print("   - data/saved_models/category_model.h5 (modelo treinado)")
    print("   - data/saved_models/category_scaler_X.pkl (normalizador)")
    print("   - data/saved_models/category_label_encoder.pkl (codificador)")
    print("   - data/saved_models/category_tfidf.pkl (vetorizador)")
    print("   - resultado_treinamento_categoria.png (gráficos)")
    print("\n💡 DICA: Agora treine o modelo de subcategorias com train_model_subcategoria.py!")

if __name__ == "__main__":
    main()

