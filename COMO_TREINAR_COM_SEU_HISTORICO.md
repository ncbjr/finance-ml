# 📊 Como Treinar o Modelo ML com SEU Histórico

## 🎯 Objetivo

Treinar o modelo de Machine Learning com suas despesas reais para que ele aprenda seus padrões de gastos.

---

## 📋 Passo 1: Preparar Seus Dados

### Formato do CSV

Edite o arquivo `data/expenses.csv` com suas despesas:

```csv
data,descricao,valor,categoria,subcategoria,tags
2024-01-05,Supermercado Carrefour,350.50,Alimentação,Compras Mensais,supermercado
2024-01-08,Uber para trabalho,25.00,Transporte,App de transporte,uber
2024-01-10,Consulta médica Dr. Silva,200.00,Saúde,Consulta,médico
```

### Colunas Obrigatórias

- ✅ **data**: YYYY-MM-DD (ex: 2024-12-15)
- ✅ **descricao**: Descrição da despesa
- ✅ **valor**: Valor numérico (use ponto, não vírgula)
- ✅ **categoria**: Categoria principal
- ⚠️ **subcategoria**: Opcional (pode deixar vazio)
- ⚠️ **tags**: Opcional (pode deixar vazio)

### Categorias Disponíveis

Use EXATAMENTE estas categorias:
1. **Alimentação**
2. **Transporte**
3. **Saúde**
4. **Lazer**
5. **Educação**
6. **Moradia**

---

## 📝 Passo 2: Adicionar Suas Despesas

### Opção A: Editar o CSV Manualmente

```bash
# No Windows
notepad data/expenses.csv

# No Linux/WSL
nano data/expenses.csv
# ou
vim data/expenses.csv
```

### Opção B: Importar de Planilha Excel

```python
# converter_excel.py
import pandas as pd

# Ler sua planilha Excel
df = pd.read_excel('minhas_despesas.xlsx')

# Renomear colunas se necessário
df.rename(columns={
    'Data': 'data',
    'Descrição': 'descricao',
    'Valor': 'valor',
    'Categoria': 'categoria'
}, inplace=True)

# Formatar data
df['data'] = pd.to_datetime(df['data']).dt.strftime('%Y-%m-%d')

# Adicionar colunas opcionais se não existirem
if 'subcategoria' not in df.columns:
    df['subcategoria'] = ''
if 'tags' not in df.columns:
    df['tags'] = ''

# Salvar como CSV
df.to_csv('data/expenses.csv', index=False)
print("✅ CSV criado com sucesso!")
```

### Opção C: Adicionar Despesas pela Interface Web

Depois de treinar o modelo inicial, você pode adicionar despesas pela interface web em http://localhost:5000

---

## 🔨 Passo 3: Treinar o Modelo

### No Docker (Recomendado)

```bash
# WSL
cd /mnt/c/Users/Nilton/Documents/repos/NILTON/finance-ml

# Treinar modelo dentro do container
docker exec -it finance-ml-app python train_model.py
```

### Localmente (Sem Docker)

```bash
# Windows PowerShell
cd C:\Users\Nilton\Documents\repos\NILTON\finance-ml
python train_model.py
```

---

## 📊 O que Acontece Durante o Treino

```
1. Carregando dados...
   ✅ Dados carregados: 60 amostras

2. Preparando dados...
   ✅ Extraindo features de texto (TF-IDF)
   ✅ Normalizando valores
   ✅ Extraindo features temporais

3. Criando modelo...
   ✅ Arquitetura: 102 features → 64 → 32 → 6 categorias

4. Compilando modelo...
   ✅ Optimizer: Adam
   ✅ Loss: sparse_categorical_crossentropy
   ✅ Metrics: accuracy

5. Treinando modelo...
   Epoch 1/100 - loss: 1.7892 - accuracy: 0.2500
   Epoch 50/100 - loss: 0.3421 - accuracy: 0.8750
   Epoch 100/100 - loss: 0.1234 - accuracy: 0.9583
   ✅ Treinamento concluído!

6. Salvando modelo...
   ✅ Modelo salvo em: data/saved_models/category_model.h5

7. Avaliando modelo...
   📊 Acurácia: 92.50%
   ✅ EXCELENTE! Modelo com alta precisão
```

### Arquivos Gerados

```
data/saved_models/
├── category_model.h5      ← Modelo treinado
├── scaler_X.pkl           ← Normalizador de features
├── label_encoder.pkl      ← Codificador de categorias
└── tfidf.pkl              ← Vetorizador de texto
```

---

## ⚙️ Passo 4: Usar o Modelo Treinado

Depois do treino, o modelo estará automaticamente disponível na aplicação:

```bash
# Reiniciar a aplicação (se já estiver rodando)
docker restart finance-ml-app

# Ou iniciar novamente
python app.py
```

### Testar a API

```bash
# Classificar usando ML treinado
curl -X POST http://localhost:5000/api/classify/ml \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Padaria do bairro",
    "valor": 15.50,
    "data": "2024-12-15"
  }'
```

---

## 📈 Quantas Despesas Preciso?

### Mínimo Recomendado
- **Mínimo absoluto**: 30 despesas
- **Recomendado**: 60-100 despesas
- **Ideal**: 200+ despesas

### Por Categoria
- Mínimo 5 exemplos por categoria
- Ideal: 10-20 exemplos por categoria

### Exemplo de Distribuição Balanceada

```
Alimentação:  20 despesas ████████████
Transporte:   15 despesas █████████
Saúde:        10 despesas ██████
Lazer:        10 despesas ██████
Educação:     8 despesas  █████
Moradia:      12 despesas ███████
────────────────────────────────────
TOTAL:        75 despesas
```

---

## 🔄 Retreinar o Modelo

### Quando Retreinar?

- ✅ Adicionou muitas despesas novas (50+)
- ✅ Mudou seus padrões de gasto
- ✅ Modelo está errando muito
- ✅ Adicionou novas categorias

### Como Retreinar

```bash
# 1. Suas despesas já estão no CSV (adicionadas pela interface)

# 2. Retreinar
docker exec -it finance-ml-app python train_model.py

# 3. Reiniciar app
docker restart finance-ml-app
```

### Retreino Automático (Futuro)

Você pode configurar para retreinar automaticamente:

```python
# Em app.py, adicionar:
@app.route('/api/retrain', methods=['POST'])
def retrain():
    # Retreinar modelo
    import subprocess
    subprocess.run(['python', 'train_model.py'])
    # Recarregar modelo
    global modelo, scaler_X, label_encoder, tfidf
    modelo, scaler_X, label_encoder, tfidf = carregar_modelo_e_recursos()
    return jsonify({'status': 'success', 'message': 'Modelo retreinado!'})
```

---

## 💡 Dicas para Melhor Treinamento

### 1. Descrições Claras
```
❌ Ruim: "Compra"
✅ Bom:  "Supermercado Extra"

❌ Ruim: "Pagamento"
✅ Bom:  "Netflix assinatura mensal"
```

### 2. Categorização Consistente
```
✅ Sempre use "Alimentação" (não "Comida" ou "Alimentos")
✅ Sempre use "Transporte" (não "Locomoção" ou "Mobilidade")
```

### 3. Dados Balanceados
```
✅ Tente ter quantidade similar de despesas em cada categoria
❌ Evite ter 100 de Alimentação e 5 de Educação
```

### 4. Dados Realistas
```
✅ Use suas despesas reais
✅ Inclua variações de descrição
❌ Não copie exemplos genéricos
```

---

## 🧪 Testar a Qualidade do Modelo

### Verificar Acurácia

Durante o treino, observe:

```
📊 MÉTRICAS DE QUALIDADE:
   Acurácia: 92.50%

🔍 EXEMPLOS DE PREVISÕES:
   ✓ Real: Alimentação    | Previsto: Alimentação    | Confiança: 95.2%
   ✓ Real: Transporte     | Previsto: Transporte     | Confiança: 88.7%
   ✗ Real: Saúde          | Previsto: Alimentação    | Confiança: 52.1%
```

### Interpretação
- ✅ **> 80%**: EXCELENTE
- ✅ **60-80%**: BOM
- ⚠️ **< 60%**: Precisa mais dados

---

## 🎯 Exemplo Completo

### 1. Criar CSV com Seus Dados

```csv
data,descricao,valor,categoria,subcategoria,tags
2024-11-01,Mercado Pão de Açúcar,420.80,Alimentação,Compras,supermercado
2024-11-03,Uber para trabalho,18.50,Transporte,App,uber
2024-11-05,Plano Unimed,350.00,Saúde,Plano,saude
2024-11-07,Netflix,45.90,Lazer,Streaming,netflix
2024-11-10,Livro Python,89.90,Educação,Livros,programacao
2024-11-12,Conta de luz,180.00,Moradia,Energia,cemig
... (adicione pelo menos 30-60 despesas)
```

### 2. Treinar

```bash
# No Docker
docker exec -it finance-ml-app python train_model.py

# Ou local
python train_model.py
```

### 3. Testar

```bash
# Abrir interface
http://localhost:5000

# Digitar: "Padaria São José"
# Ver sugestão automática de categoria!
```

---

## 📱 Fluxo de Uso Contínuo

```
1. Adicionar despesas pela interface web
   ↓
2. Quando tiver 50+ despesas novas, retreinar:
   docker exec -it finance-ml-app python train_model.py
   ↓
3. Reiniciar app:
   docker restart finance-ml-app
   ↓
4. Modelo atualizado com seus novos padrões!
   ↓
5. Repetir o ciclo
```

---

## ✅ Checklist

- [ ] Preparei meu CSV com minhas despesas
- [ ] Tenho pelo menos 30 despesas
- [ ] Todas as categorias estão corretas
- [ ] Executei `python train_model.py`
- [ ] Arquivos foram criados em `data/saved_models/`
- [ ] Acurácia está acima de 60%
- [ ] Reiniciei a aplicação
- [ ] Testei na interface web

---

**🎉 Pronto! Seu modelo está treinado com SEU histórico!**

Agora o sistema vai aprender seus padrões de gastos e sugerir categorias automaticamente! 🚀

