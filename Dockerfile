# Dockerfile para Sistema de Gestão Financeira
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (cache layer)
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p data/saved_models templates providers

# Expor porta 5000
EXPOSE 5000

# Variáveis de ambiente padrão
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False

# Comando para iniciar a aplicação
CMD ["python", "app.py"]

