# 🚀 Quick Start - Sistema de Gestão Financeira

## ⚡ Início Rápido em 3 Passos

### 1️⃣ Testar o Fallback (SEM instalar nada!)

```bash
cd C:\Users\Nilton\Documents\repos\NILTON\finance-ml
python llm_classifier.py
```

**Resultado esperado**: ✅ Classificações funcionando!

---

### 2️⃣ Instalar Dependências (Recomendado: Docker)

**Opção A: Docker** 🐳 (Recomendado)
```bash
docker-compose up --build
```

**Opção B: Local** 💻
```bash
pip install -r requirements.txt
```

---

### 3️⃣ Treinar o Modelo

```bash
python train_model.py
```

**Saída**:
- ✅ `data/saved_models/category_model.h5`
- ✅ `data/saved_models/scaler_X.pkl`
- ✅ `data/saved_models/label_encoder.pkl`
- ✅ `data/saved_models/tfidf.pkl`
- ✅ `resultado_treinamento.png`

---

### 4️⃣ Iniciar a Aplicação

```bash
python app.py
```

**Acesse**: http://localhost:5000

---

## 🎯 Teste Rápido da Interface

1. Abra: http://localhost:5000
2. Digite: "Supermercado Carrefour"
3. Digite valor: 350.50
4. Veja a sugestão em tempo real: **Alimentação**
5. Clique em "Adicionar Despesa"
6. ✅ Pronto!

---

## 🔧 Problemas Comuns

### Erro: "ModuleNotFoundError: tensorflow"

**Solução**: Use Docker
```bash
docker-compose up --build
```

### Erro: "No module named 'openai'"

**Solução**: Instale as dependências
```bash
pip install -r requirements.txt
```

### Sistema funciona sem APIs?

✅ **SIM!** O fallback local sempre funciona:
```bash
python llm_classifier.py
```

---

## 📊 Estrutura dos Dados

### expenses.csv
```csv
data,descricao,valor,categoria,subcategoria,tags
2024-01-05,Supermercado Carrefour,350.50,Alimentação,Compras Mensais,supermercado
```

### Categorias Disponíveis
- 🍔 Alimentação
- 🚗 Transporte
- 🏥 Saúde
- 🎮 Lazer
- 📚 Educação
- 🏠 Moradia

---

## 🔑 Configurar APIs (Opcional)

Edite o arquivo `.env`:

```env
OPENAI_API_KEY=sk-proj-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
GOOGLE_API_KEY=AIzxxxxx
GROQ_API_KEY=gsk_xxxxx
```

**Importante**: Funciona SEM APIs usando fallback!

---

## 📡 APIs Disponíveis

### Classificar com ML
```bash
curl -X POST http://localhost:5000/api/classify/ml \
  -H "Content-Type: application/json" \
  -d '{"descricao":"Uber para trabalho","valor":25,"data":"2024-12-15"}'
```

### Classificar com LLM
```bash
curl -X POST http://localhost:5000/api/classify/llm \
  -H "Content-Type: application/json" \
  -d '{"descricao":"Netflix assinatura"}'
```

### Classificar Híbrido (ML + LLM)
```bash
curl -X POST http://localhost:5000/api/classify/hybrid \
  -H "Content-Type: application/json" \
  -d '{"descricao":"Consulta médica","valor":200,"data":"2024-12-15"}'
```

### Adicionar Despesa
```bash
curl -X POST http://localhost:5000/api/expense \
  -H "Content-Type: application/json" \
  -d '{"descricao":"Padaria","valor":15.50,"data":"2024-12-15","categoria":"Alimentação"}'
```

### Listar Despesas
```bash
curl http://localhost:5000/api/expenses
```

### Status do Sistema
```bash
curl http://localhost:5000/status
```

---

## 🐳 Docker Commands

### Iniciar
```bash
docker-compose up
```

### Iniciar com rebuild
```bash
docker-compose up --build
```

### Parar
```bash
docker-compose down
```

### Ver logs
```bash
docker-compose logs -f
```

### Entrar no container
```bash
docker-compose exec finance-ml bash
```

---

## 📁 Arquivos Importantes

```
finance-ml/
├── app.py              ← Aplicação Flask principal
├── train_model.py      ← Treinar modelo ML
├── llm_classifier.py   ← Orquestrador LLM
├── llm_fallback.py     ← Fallback local
├── data/
│   └── expenses.csv    ← Seus dados
├── templates/
│   └── index.html      ← Interface web
└── .env                ← Configurações (criar se não existir)
```

---

## 🧪 Comandos de Teste

### Testar Fallback LLM
```bash
python llm_classifier.py
```

### Testar Treino do Modelo
```bash
python train_model.py
```

### Testar Flask App
```bash
python app.py
# Abrir: http://localhost:5000
```

### Testar Docker
```bash
docker-compose up
# Abrir: http://localhost:5000
```

---

## 🆘 Ajuda Rápida

### Ver documentação completa
- `README.md` - Guia completo
- `IMPLEMENTACAO_COMPLETA.md` - Detalhes técnicos
- `TESTES_EXECUTADOS.md` - Resultados de testes
- `COMO_CONFIGURAR_ENV.md` - Configurar .env

### Status do Projeto
- ✅ Implementação: 100%
- ✅ Testes: Aprovados
- ✅ Documentação: Completa
- ✅ Fallback: Funcionando

---

## 🎯 Fluxo de Uso Recomendado

```
1. Testar fallback → python llm_classifier.py
         ↓
2. Instalar deps → pip install -r requirements.txt
         ↓
3. Treinar modelo → python train_model.py
         ↓
4. Iniciar app → python app.py
         ↓
5. Acessar → http://localhost:5000
         ↓
6. Adicionar despesas → Interface web
         ↓
7. Ver estatísticas → API /api/expenses
```

---

## ✅ Checklist de Início

- [ ] Python 3.11 instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado (pode estar vazio)
- [ ] Modelo treinado (`python train_model.py`)
- [ ] App rodando (`python app.py`)
- [ ] Interface acessível (http://localhost:5000)

---

## 🎉 Pronto para Usar!

Seu sistema está 100% funcional!

**Escolha seu método preferido**:
- 🐳 Docker: `docker-compose up --build`
- 💻 Local: `python app.py`
- 🧪 Teste: `python llm_classifier.py`

**Todos funcionam!** ✅

---

**Desenvolvido com** ❤️ **ML + LLM + Fallback Inteligente**

