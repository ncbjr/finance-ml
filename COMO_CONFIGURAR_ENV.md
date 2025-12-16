# 🔧 Como Configurar o Arquivo .env

## Criar o Arquivo .env

O arquivo `.env` está no `.gitignore` por segurança (para não expor suas chaves API).

### Passo 1: Criar o arquivo

**No Windows PowerShell:**
```powershell
cd C:\Users\Nilton\Documents\repos\NILTON\finance-ml
New-Item .env -ItemType File
```

**No Linux/Mac/WSL:**
```bash
cd /mnt/c/Users/Nilton/Documents/repos/NILTON/finance-ml
touch .env
```

### Passo 2: Copiar o conteúdo abaixo no .env

```env
# Configuração do Sistema de Gestão Financeira
# =============================================

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# LLM API Keys (Opcionais - o sistema funciona com fallback se estiverem vazias)
# ============================================================================

# OpenAI (GPT-3.5, GPT-4)
# Obtenha em: https://platform.openai.com/api-keys
OPENAI_API_KEY=

# Anthropic (Claude)
# Obtenha em: https://console.anthropic.com/
ANTHROPIC_API_KEY=

# Google AI (Gemini)
# Obtenha em: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=

# Groq (Llama 3)
# Obtenha em: https://console.groq.com/
GROQ_API_KEY=

# xAI (Grok)
# Obtenha em: https://x.ai/
XAI_API_KEY=
```

### Passo 3: (Opcional) Adicionar suas chaves API

Se você tiver chaves de API, adicione-as após o `=`:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
GOOGLE_API_KEY=AIzxxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
XAI_API_KEY=xai-xxxxxxxxxxxxx
```

## ⚠️ IMPORTANTE

### O Sistema Funciona SEM Chaves API!

Se você **NÃO configurar nenhuma chave**, o sistema:
1. ✅ Tentará cada provedor (todos falharão)
2. ✅ Ativará o **fallback local** automaticamente
3. ✅ Classificará usando **palavras-chave**
4. ✅ **SEMPRE funcionará!**

### Já Testado e Aprovado!

```
✅ "Supermercado Carrefour" → Alimentação (90%)
✅ "Uber para trabalho" → Transporte (30%)
✅ "Consulta médica" → Saúde (30%)
✅ "Netflix assinatura" → Lazer (60%)
```

## 🚀 Como Usar Depois

### Com Docker:
```bash
docker-compose up --build
```
O Docker lerá o `.env` automaticamente.

### Sem Docker:
```bash
python app.py
```
O Flask carregará o `.env` via `python-dotenv`.

## 🔒 Segurança

- ✅ O `.env` está no `.gitignore`
- ✅ Suas chaves NÃO serão commitadas
- ✅ Compartilhe apenas o `.gitignore` e este guia

## 📝 Resumo

```bash
# 1. Criar arquivo
touch .env  # ou New-Item .env

# 2. Editar e colar o conteúdo acima
nano .env  # ou notepad .env

# 3. (Opcional) Adicionar suas chaves API

# 4. Rodar o sistema
python app.py  # ou docker-compose up
```

**Pronto! Seu `.env` está configurado!** ✅

