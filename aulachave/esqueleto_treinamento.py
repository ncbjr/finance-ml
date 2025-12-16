"""
Aula 25/09/2025 - Professor: Tiago Ruiz de Castro
Engenharia de Software - Inteligência Artificial e Machine Learning
Simulado para Prova Prática - Sistema de Previsão de Preços Imobiliários
ESQUELETO DE TREINAMENTO - PREVISÃO DE PREÇOS DE CASAS
======================================================

INSTRUÇÕES PARA O ALUNO:
1. Complete as partes marcadas com # TODO
2. Use os conhecimentos que você aprendeu sobre:
   - Carregamento de CSV com pandas
   - Separação de variáveis X e Y
   - Divisão de dados de treino e teste
   - Criação de modelo Sequential
   - Compilação e treinamento
   - Salvamento do modelo

DICAS:
 - Olhe os arquivos upados no AVA para ver como fazer
 - Ultima Aula.
 - Rode o comando pip install -r requirements.txt para instalar as dependências
 - Execute o script de treinamento para gerar o modelo:
 - salve o modelo com o nome house_price_model.h5
 - salve o scaler com o nome scaler_X.pkl e scaler_y.pkl
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import StandardScaler
import os

def carregar_dados():
    """
    TODO: Complete esta função para carregar os dados do CSV
    Use: df = pd.read_csv('house_prices.csv')
    Retorne: df (DataFrame com os dados)
    """
    # TODO: Carregar o arquivo CSV
    # Dica: df = pd.read_csv('house_prices.csv')
    pass

def preparar_dados(df):
    """
    TODO: Complete esta função para preparar os dados X e Y
     df = .....
    """
    # TODO: Separar variáveis X e Y
    # Dica: 
    # y = 
    # x =   # todas as outras colunas
    
    # TODO: Dividir dados de treino e teste
    # Dica:
    # x_treino, x_teste = 
    # y_treino, y_teste = (observe quantas colunas temos no df)
    #--------------------------------------------------------

    # NORMALIZAÇÃO DOS DADOS - JÁ IMPLEMENTADA PARA VOCÊ! Porque? Calma Pequeno Gafanhoto. isto nao será cobrado (ainda)
    # Por que normalizar? Os dados têm escalas muito diferentes por exemplo:
    # - area: 50-300 (metros quadrados)
    # - bedrooms: 1-5 (quantidade)
    # - bathrooms: 1-4 (quantidade) 
    # - age: 0-30 (anos)
    # - price: 100000-800000 (reais)
    # 
    # Sem normalização, o modelo fica "confuso" porque:
    # - A área (valores grandes) domina o treinamento
    # - Os quartos (valores pequenos) são ignorados
    # - O modelo não converge bem
    #
    # Com normalização (StandardScaler):
    # - Todos os dados ficam com média ~0 e desvio padrão ~1
    # - O modelo treina melhor e mais rápido
    # - As previsões ficam mais precisas
    
    #Isso aqui normaliza os dados do X (features)
    print("   Normalizando dados X (features)...")
    scaler_X = StandardScaler()
    x_treino_scaled = scaler_X.fit_transform(x_treino)
    x_teste_scaled = scaler_X.transform(x_teste)
    
    #Isso aqui normaliza os dados do Y (preços)
    print("   Normalizando dados Y (preços)...")
    scaler_y = StandardScaler()
    y_treino_scaled = scaler_y.fit_transform(y_treino.values.reshape(-1, 1)).flatten()
    y_teste_scaled = scaler_y.transform(y_teste.values.reshape(-1, 1)).flatten()
    
    # Salvar os scalers para usar depois (importante!)
    import joblib
    joblib.dump(scaler_X, 'scaler_X.pkl')
    joblib.dump(scaler_y, 'scaler_y.pkl')
    
    print(f"   Dados X normalizados: média={x_treino_scaled.mean():.3f}, std={x_treino_scaled.std():.3f}")
    print(f"   Dados Y normalizados: média={y_treino_scaled.mean():.3f}, std={y_treino_scaled.std():.3f}")
    
    return x_treino_scaled, x_teste_scaled, y_treino_scaled, y_teste_scaled, scaler_y

def criar_modelo(input_dim):
    """
    TODO: Complete esta função para criar o modelo Sequential
    Use: modelo = Sequential()
    ....
    ....
    Retorne: modelo
    """
    # TODO: Criar modelo Sequential
    # Dica: modelo = ...
    
    # TODO: Adicionar primeira camada (camada oculta)
    # ....
    
    # TODO: Adicionar camada de saída
    # ...
    
    return modelo

def compilar_modelo(modelo):
    """
    TODO: Complete esta função para compilar o modelo
    
    """
    # TODO: Compilar o modelo
    # ...
    pass

def treinar_modelo(modelo, x_treino, y_treino, x_teste, y_teste):
    """
    TODO: Complete esta função para treinar o modelo
    Use: resultado = ... 
    Retorne: resultado
    """
    # TODO: Treinar o modelo
    # Dica: resultado = 
    # return ???
    pass

def salvar_modelo(modelo):
    """
    TODO: Complete esta função para salvar o modelo
    Use: 'saved_model/house_price_model.h5'
    """
    # TODO: Salvar o modelo
    # 
    pass

def avaliar_modelo(modelo, x_teste, y_teste, scaler_y):
    """
    Função para avaliar o modelo - JÁ IMPLEMENTADA ... com isso a gente vai ver se o modelo é bom ou não kkk
    """
    print("\n=== AVALIAÇÃO DO MODELO ===")
    
    # Fazer previsões
    y_pred_scaled = modelo.predict(x_teste)
    
    # Desnormalizar as previsões para valores reais
    y_pred_real = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
    y_teste_real = scaler_y.inverse_transform(y_teste.reshape(-1, 1)).flatten()
    
    # Calcular métricas
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    mae = mean_absolute_error(y_teste_real, y_pred_real)
    mse = mean_squared_error(y_teste_real, y_pred_real)
    rmse = mse ** 0.5
    
    print(f"📊 MÉTRICAS DE QUALIDADE:")
    print(f"   MAE (Erro Médio Absoluto): R$ {mae:,.2f}")
    print(f"   RMSE (Raiz do Erro Quadrático): R$ {rmse:,.2f}")
    print(f"   MSE (Erro Quadrático Médio): R$ {mse:,.2f}")
    
    # Mostrar algumas previsões de exemplo
    print(f"\n🔍 EXEMPLOS DE PREVISÕES:")
    for i in range(min(5, len(y_teste_real))):
        erro = abs(y_teste_real[i] - y_pred_real[i])
        erro_pct = (erro / y_teste_real[i]) * 100
        print(f"   Real: R$ {y_teste_real[i]:,.2f} | Previsto: R$ {y_pred_real[i]:,.2f} | Erro: {erro_pct:.1f}%")
    
    # Essa lógica aqui vai testar dizer se o modelo é bom ou não kkk
    if mae < 50000:
        print(f"\n✅ EXCELENTE! Modelo com alta precisão (MAE < R$ 50.000)")
    elif mae < 100000:
        print(f"\n✅ BOM! Modelo com boa precisão (MAE < R$ 100.000)")
    else:
        print(f"\n⚠️  ATENÇÃO! Modelo pode precisar de mais treinamento (MAE > R$ 100.000)")
    
    return mae, rmse

def plotar_resultado(resultado):
    """
    Função para plotar o resultado - JÁ IMPLEMENTADA (De nada kkk)
    """
    plt.figure(figsize=(12, 4))
    
    # Plotar Loss
    plt.subplot(1, 2, 1)
    plt.plot(resultado.history['loss'], label='Treino')
    plt.plot(resultado.history['val_loss'], label='Teste')
    plt.title('Loss do Modelo')
    plt.xlabel('Época')
    plt.ylabel('Loss')
    plt.legend()
    
    # Plotar MAE
    plt.subplot(1, 2, 2)
    plt.plot(resultado.history['mae'], label='Treino')
    plt.plot(resultado.history['val_mae'], label='Teste')
    plt.title('MAE do Modelo')
    plt.xlabel('Época')
    plt.ylabel('MAE')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('resultado_treinamento.png')
    plt.show()

def main():
    """
    Função principal - JÁ IMPLEMENTADA
    """
    print("=== TREINAMENTO DO MODELO DE PREVISÃO DE PREÇOS ===")
    print("Complete as funções marcadas com TODO\n")
    
    # 1. Carregar dados
    print("1. Carregando dados...")
    df = carregar_dados()
    print(f"   Dados carregados: {len(df)} amostras")
    print(f"   Colunas: {list(df.columns)}")
    
    # 2. Preparar dados
    print("\n2. Preparando dados...")
    x_treino, x_teste, y_treino, y_teste, scaler_y = preparar_dados(df)
    print(f"   Dados de treino: {x_treino.shape[0]} amostras")
    print(f"   Dados de teste: {x_teste.shape[0]} amostras")
    
    # 3. Criar modelo
    print("\n3. Criando modelo...")
    modelo = criar_modelo(x_treino.shape[1])
    print("   Modelo criado!")
    
    # 4. Compilar modelo
    print("\n4. Compilando modelo...")
    compilar_modelo(modelo)
    print("   Modelo compilado!")
    
    # 5. Treinar modelo
    print("\n5. Treinando modelo...")
    print("   Isso pode levar alguns minutos...")
    resultado = treinar_modelo(modelo, x_treino, y_treino, x_teste, y_teste)
    print("   Treinamento concluído!")
    
    # 6. Salvar modelo
    print("\n6. Salvando modelo...")
    salvar_modelo(modelo)
    print("   Modelo salvo!")
    
    # 7. Avaliar modelo
    print("\n7. Avaliando qualidade do modelo...")
    mae, rmse = avaliar_modelo(modelo, x_teste, y_teste, scaler_y)
    
    # 8. Plotar resultado
    print("\n8. Gerando gráficos...")
    plotar_resultado(resultado)
    print("   Gráficos salvos em 'resultado_treinamento.png'")
    
    print("\n=== TREINAMENTO CONCLUÍDO ===")
    print("🎉 Modelo treinado e avaliado com sucesso!")
    print("📁 Arquivos salvos:")
    print("   - meu_modelo.keras (modelo treinado)")
    print("   - scaler_X.pkl (normalizador das features)")
    print("   - scaler_y.pkl (normalizador dos preços)")
    print("   - resultado_treinamento.png (gráficos)")
    print("\n💡 DICA: Agora você pode usar este modelo para fazer previsões!")

if __name__ == "__main__":
    main()
