# 💰 Sistema de Gestão Financeira - ML + LLM

Sistema inteligente de gestão financeira que combina **Machine Learning** e **Large Language Models (LLMs)** para classificação automática de despesas.

## 🎯 Funcionalidades

- ✅ **Classificação Automática de Categorias**
  - Machine Learning treinado com seu histórico
  - LLMs (OpenAI, Anthropic, Gemini, Groq, XAI)
  - Fallback inteligente (funciona sem APIs)
  
- ✅ **Interface Web Moderna**
  - Sugestões em tempo real
  - Dashboard intuitivo
  - Responsivo e acessível

- ✅ **Múltiplos Métodos de Classificação**
  - ML puro
  - LLM puro
  - Híbrido (ML + LLM com consenso)

## 🚀 Quick Start

### Opção 1: Com Docker (Recomendado)

```bash
# 1. Clonar o repositório
git clone <repo-url>
cd finance-ml

# 2. Configurar variáveis de ambiente (opcional)
cp .env.example .env
# Edite .env com suas chaves API (opcional - funciona sem elas!)

# 3. Construir e iniciar com Docker
docker-compose up --build

# 4. Acessar a aplicação
# http://localhost:5000
```

### Opção 2: Sem Docker

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Treinar modelo ML (primeira vez)
python train_model.py

# 4. Iniciar aplicação
python app.py

# 5. Acessar a aplicação
# http://localhost:5000
```

## 📊 Estrutura do Projeto

```
finance-ml/
├── app.py                    # Aplicação Flask principal
├── train_model.py            # Treinamento do modelo ML
├── llm_classifier.py         # Orquestrador de LLMs
├── llm_fallback.py           # Fallback sem APIs
├── providers/                # Provedores LLM
│   ├── openai.py
│   ├── anthropic.py
│   ├── gemini.py
│   ├── groq.py
│   └── xai.py
├── data/
│   ├── expenses.csv          # Planilha de despesas
│   └── saved_models/         # Modelos treinados
├── templates/
│   └── index.html            # Interface web
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 🎓 Como Funciona

### 1. Machine Learning

O modelo ML usa:
- **TF-IDF** para processar descrições de texto
- **Features numéricas** (valor, mês, dia da semana)
- **Rede Neural Sequential** para classificação
- **Categorias**: Alimentação, Transporte, Saúde, Lazer, Educação, Moradia

### 2. LLMs com Fallback

Ordem de tentativa:
1. OpenAI (GPT-3.5)
2. Anthropic (Claude)
3. Google (Gemini)
4. Groq (Llama 3)
5. xAI (Grok)
6. **Fallback Local** (palavras-chave) - sempre funciona!

### 3. Classificação Híbrida

Combina ML + LLM:
- Se ambos concordam → aumenta confiança
- Se discordam → usa o de maior confiança
- Retorna categoria + nível de confiança

## 🔧 APIs Disponíveis

### POST /api/classify/ml
Classifica usando apenas Machine Learning

```json
{
  "descricao": "Supermercado Carrefour",
  "valor": 350.50,
  "data": "2024-12-15"
}
```

### POST /api/classify/llm
Classifica usando apenas LLM

```json
{
  "descricao": "Uber para trabalho"
}
```

### POST /api/classify/hybrid
Classifica usando ML + LLM (recomendado)

```json
{
  "descricao": "Consulta médica Dr. Silva",
  "valor": 200.00,
  "data": "2024-12-15"
}
```

### POST /api/expense
Adiciona uma nova despesa

```json
{
  "descricao": "Netflix assinatura",
  "valor": 45.90,
  "data": "2024-12-15",
  "categoria": "Lazer",
  "subcategoria": "Streaming",
  "tags": "entretenimento"
}
```

### GET /api/expenses
Lista todas as despesas + estatísticas

### GET /status
Verifica status do sistema

## 📝 Treinar o Modelo

```bash
# Treinar/retreinar o modelo ML
python train_model.py

# Gera:
# - data/saved_models/category_model.h5
# - data/saved_models/scaler_X.pkl
# - data/saved_models/label_encoder.pkl
# - data/saved_models/tfidf.pkl
# - resultado_treinamento.png
```

## 🔑 Configuração de APIs (Opcional)

O sistema funciona **sem nenhuma chave API** usando fallback inteligente!

Para melhor precisão, configure no `.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google AI
GOOGLE_API_KEY=AI...

# Groq
GROQ_API_KEY=gsk_...

# xAI
XAI_API_KEY=xai-...
```

## 🧪 Testar o Sistema

### Testar Classificação LLM
```bash
python llm_classifier.py
```

### Testar Aplicação Completa
```bash
# 1. Iniciar servidor
python app.py

# 2. Abrir navegador
# http://localhost:5000

# 3. Digitar uma descrição e ver a sugestão em tempo real!
```

## 📊 Categorias Disponíveis

- 🍔 **Alimentação** - Supermercados, restaurantes, delivery
- 🚗 **Transporte** - Uber, gasolina, estacionamento
- 🏥 **Saúde** - Médicos, farmácias, academia
- 🎮 **Lazer** - Cinema, streaming, eventos
- 📚 **Educação** - Cursos, livros, materiais
- 🏠 **Moradia** - Aluguel, contas, condomínio
- 📦 **Outros** - Demais categorias

## 🎨 Adaptado de

Este projeto foi desenvolvido adaptando:
- `aulachave/esqueleto_treinamento.py` → `train_model.py`
- `aulachave/interface_web_completa.py` → `app.py`
- `aulasseguintes/aula_LLM/providers/*.py` → `providers/*.py`

**Estratégia**: Máxima reutilização de código, mínimo de código novo (~300 linhas).

## 📜 Licença

Projeto educacional - Adaptado das aulas de Machine Learning e LLMs.

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas!

---

**Desenvolvido com** ❤️ **usando Flask, TensorFlow, e múltiplos LLMs**

