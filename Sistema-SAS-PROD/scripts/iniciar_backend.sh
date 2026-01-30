#!/bin/bash
# Script para reiniciar o backend SAS limpando a porta 5000

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/.."

echo "--- Reiniciando Sistema SAS ---"

# Tentar limpar a porta 5000 (usando sudo para garantir que limpa processos de outros usuários)
echo "Limpando porta 5000..."
sudo fuser -k 5000/tcp 2>/dev/null

# Pequena pausa para garantir que o SO liberou a porta
sleep 1

# Iniciar o servidor usando o ambiente virtual
echo "Iniciando o servidor SAS..."
source backend/venv/bin/activate
export FLASK_APP=backend/app.py
export FLASK_ENV=development

# Rodar o servidor
python -m backend.app
