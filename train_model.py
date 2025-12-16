"""
Sistema de Gestão Financeira - Treinamento do Modelo ML
========================================================

Adaptado de esqueleto_treinamento.py para classificação de categorias financeiras.
Usa TF-IDF para descrições + features numéricas para classificar despesas.
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

def carregar_dados():
    """
    Carrega o arquivo CSV com despesas financeiras
    """
    df = pd.read_csv('data/expenses.csv')
    return df

def preparar_dados(df):
    """
    Prepara os dados para classificação de categorias
    Extrai features de texto (TF-IDF) + features numéricas
    """
    print("   Preparando features...")
    
    # Separar Y (categoria) e X (features)
    y = df['categoria']
    
    # Encoder para categorias (transforma texto em números)
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Features de texto - TF-IDF da descrição
    tfidf = TfidfVectorizer(max_features=100, stop_words=None)
    text_features = tfidf.fit_transform(df['descricao']).toarray()
    
    # Features numéricas - valor
    numeric_features = df[['valor']].values
    
    # Features temporais - extrair mês e dia da semana
    df['data'] = pd.to_datetime(df['data'])
    df['mes'] = df['data'].dt.month
    df['dia_semana'] = df['data'].dt.dayofweek
    temporal_features = df[['mes', 'dia_semana']].values
    
    # Combinar todas as features
    X = np.hstack([text_features, numeric_features, temporal_features])
    
    # Dividir dados de treino e teste (80% treino, 20% teste)
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # NORMALIZAÇÃO DOS DADOS
    print("   Normalizando dados X (features)...")
    scaler_X = StandardScaler()
    X_treino_scaled = scaler_X.fit_transform(X_treino)
    X_teste_scaled = scaler_X.transform(X_teste)
    
    # Salvar os scalers e encoders para usar depois
    os.makedirs('data/saved_models', exist_ok=True)
    joblib.dump(scaler_X, 'data/saved_models/scaler_X.pkl')
    joblib.dump(label_encoder, 'data/saved_models/label_encoder.pkl')
    joblib.dump(tfidf, 'data/saved_models/tfidf.pkl')
    
    print(f"   Dados X normalizados: média={X_treino_scaled.mean():.3f}, std={X_treino_scaled.std():.3f}")
    print(f"   Categorias únicas: {len(label_encoder.classes_)}")
    print(f"   Classes: {list(label_encoder.classes_)}")
    
    return X_treino_scaled, X_teste_scaled, y_treino, y_teste, label_encoder

def criar_modelo(input_dim, num_classes):
    """
    Cria o modelo Sequential para classificação
    """
    modelo = Sequential()
    
    # Camada oculta 1
    modelo.add(Dense(64, activation='relu', input_dim=input_dim))
    modelo.add(Dropout(0.3))
    
    # Camada oculta 2
    modelo.add(Dense(32, activation='relu'))
    modelo.add(Dropout(0.3))
    
    # Camada de saída - softmax para classificação multiclasse
    modelo.add(Dense(num_classes, activation='softmax'))
    
    return modelo

def compilar_modelo(modelo):
    """
    Compila o modelo com loss e métricas adequadas para classificação
    """
    modelo.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',  # Para classificação multiclasse
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
    Avalia o modelo - já implementado
    """
    print("\n=== AVALIAÇÃO DO MODELO ===")
    
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
    
    # Mostrar algumas previsões de exemplo
    print(f"\n🔍 EXEMPLOS DE PREVISÕES:")
    for i in range(min(5, len(y_teste))):
        real = label_encoder.inverse_transform([y_teste[i]])[0]
        previsto = label_encoder.inverse_transform([y_pred[i]])[0]
        confianca = y_pred_proba[i][y_pred[i]] * 100
        status = "✓" if real == previsto else "✗"
        print(f"   {status} Real: {real:15s} | Previsto: {previsto:15s} | Confiança: {confianca:.1f}%")
    
    if accuracy > 0.8:
        print(f"\n✅ EXCELENTE! Modelo com alta precisão (Acurácia > 80%)")
    elif accuracy > 0.6:
        print(f"\n✅ BOM! Modelo com boa precisão (Acurácia > 60%)")
    else:
        print(f"\n⚠️  ATENÇÃO! Modelo pode precisar de mais treinamento (Acurácia < 60%)")
    
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
        plt.title('Loss do Modelo')
        plt.xlabel('Época')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        # Plotar Accuracy
        plt.subplot(1, 2, 2)
        plt.plot(resultado.history['accuracy'], label='Treino')
        plt.plot(resultado.history['val_accuracy'], label='Teste')
        plt.title('Accuracy do Modelo')
        plt.xlabel('Época')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('resultado_treinamento.png')
        print("   Gráficos salvos em 'resultado_treinamento.png'")
        plt.close()
    except Exception as e:
        print(f"   AVISO: Erro ao gerar graficos: {e}")

def main():
    """
    Função principal
    """
    print("=== TREINAMENTO DO MODELO DE CLASSIFICAÇÃO DE CATEGORIAS ===\n")
    
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
    print("🎉 Modelo treinado e avaliado com sucesso!")
    print("📁 Arquivos salvos:")
    print("   - data/saved_models/category_model.h5 (modelo treinado)")
    print("   - data/saved_models/scaler_X.pkl (normalizador das features)")
    print("   - data/saved_models/label_encoder.pkl (codificador de categorias)")
    print("   - data/saved_models/tfidf.pkl (vetorizador de texto)")
    print("   - resultado_treinamento.png (gráficos)")
    print("\n💡 DICA: Agora você pode usar app.py para classificar novas despesas!")

if __name__ == "__main__":
    main()

