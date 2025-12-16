# 🐧 Como Rodar no WSL

## Erro do Buildx - Soluções

Você está recebendo: `fork/exec /usr/local/lib/docker/cli-plugins/docker-buildx: no such file or directory`

### ✅ Solução 1: Build Direto (Mais Rápido)

```bash
# No WSL, dentro do diretório do projeto
cd /mnt/c/Users/Nilton/Documents/repos/NILTON/finance-ml

# Build da imagem diretamente
docker build -t finance-ml .

# Rodar o container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  --name finance-ml-app \
  --env-file .env \
  finance-ml

# Ver logs
docker logs -f finance-ml-app

# Acessar: http://localhost:5000
```

### ✅ Solução 2: Docker Compose Simples

```bash
# Usar docker-compose ao invés de docker compose
docker-compose up --build

# Ou em background
docker-compose up -d --build
```

### ✅ Solução 3: Instalar Buildx (Se quiser)

```bash
# Baixar buildx
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/buildx/releases/download/v0.12.0/buildx-v0.12.0.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx

# Depois rodar normalmente
docker compose up --build
```

### ✅ Solução 4: Rodar SEM Docker (Python direto)

```bash
# Instalar dependências (só funciona se não for tensorflow)
pip3 install flask pandas numpy scikit-learn python-dotenv openai anthropic groq

# Rodar só o fallback (funciona sem tensorflow!)
python3 llm_classifier.py

# Rodar o app (sem ML, só LLM)
python3 app.py
```

## 🚀 Comandos Rápidos WSL

### Navegar para o projeto
```bash
cd /mnt/c/Users/Nilton/Documents/repos/NILTON/finance-ml
```

### Verificar Docker
```bash
docker --version
docker ps
```

### Build e Run (Recomendado)
```bash
# Limpar containers antigos
docker stop finance-ml-app 2>/dev/null || true
docker rm finance-ml-app 2>/dev/null || true

# Build
docker build -t finance-ml .

# Run
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  --name finance-ml-app \
  --env-file .env \
  finance-ml

# Ver logs em tempo real
docker logs -f finance-ml-app
```

### Parar e Remover
```bash
docker stop finance-ml-app
docker rm finance-ml-app
```

### Entrar no Container
```bash
docker exec -it finance-ml-app bash
```

## 📝 Script Completo

```bash
#!/bin/bash
# rodar.sh

cd /mnt/c/Users/Nilton/Documents/repos/NILTON/finance-ml

echo "🧹 Limpando containers antigos..."
docker stop finance-ml-app 2>/dev/null || true
docker rm finance-ml-app 2>/dev/null || true

echo "🔨 Construindo imagem..."
docker build -t finance-ml .

echo "🚀 Iniciando container..."
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  --name finance-ml-app \
  --env-file .env \
  finance-ml

echo "✅ Container iniciado!"
echo "📊 Ver logs: docker logs -f finance-ml-app"
echo "🌐 Acessar: http://localhost:5000"
echo "🛑 Parar: docker stop finance-ml-app"

# Ver logs
docker logs -f finance-ml-app
```

Salvar como `rodar.sh` e executar:
```bash
chmod +x rodar.sh
./rodar.sh
```

## ⚡ Comandos Úteis

```bash
# Ver containers rodando
docker ps

# Ver todas as imagens
docker images

# Limpar tudo
docker system prune -a

# Ver uso de recursos
docker stats finance-ml-app

# Reiniciar container
docker restart finance-ml-app
```

## 🐛 Troubleshooting

### Erro: "Cannot connect to Docker daemon"
```bash
sudo service docker start
```

### Erro: "Port 5000 already in use"
```bash
# Ver o que está usando a porta
sudo lsof -i :5000

# Ou usar outra porta
docker run -p 5001:5000 ...
```

### Erro: "Permission denied"
```bash
sudo usermod -aG docker $USER
# Depois fazer logout/login
```

## 🎯 Fluxo Recomendado

```bash
# 1. Navegar
cd /mnt/c/Users/Nilton/Documents/repos/NILTON/finance-ml

# 2. Build
docker build -t finance-ml .

# 3. Run
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data --name finance-ml-app --env-file .env finance-ml

# 4. Treinar modelo (dentro do container)
docker exec -it finance-ml-app python train_model.py

# 5. Ver logs
docker logs -f finance-ml-app

# 6. Acessar
# http://localhost:5000
```

## 📌 Atalhos

Adicione ao seu `~/.bashrc`:

```bash
alias finance-build='cd /mnt/c/Users/Nilton/Documents/repos/NILTON/finance-ml && docker build -t finance-ml .'
alias finance-run='docker run -d -p 5000:5000 -v $(pwd)/data:/app/data --name finance-ml-app --env-file .env finance-ml'
alias finance-logs='docker logs -f finance-ml-app'
alias finance-stop='docker stop finance-ml-app && docker rm finance-ml-app'
alias finance-train='docker exec -it finance-ml-app python train_model.py'
```

Depois:
```bash
source ~/.bashrc
finance-build
finance-run
finance-logs
```

✅ Pronto para usar!

