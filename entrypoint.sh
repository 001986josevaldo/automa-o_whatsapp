#!/bin/bash
set -e

PDF_PATH="/app/rag/data/banco_notas_base_expandida.pdf"
CHROMA_DIR="/app/chroma_data"
INDEX_SCRIPT="/app/rag.py"   # ← ajuste se o nome do script for outro

echo "=== Verificando base Chroma ==="

# Cria a pasta se não existir
mkdir -p "$CHROMA_DIR"

# Verifica se a base já foi criada (arquivo principal do Chroma)
if [ ! -f "$CHROMA_DIR/chroma.sqlite3" ]; then
    echo "Base Chroma não encontrada."

    if [ -f "$PDF_PATH" ]; then
        echo "PDF encontrado. Gerando base vetorial..."
        python "$INDEX_SCRIPT"
        echo "Base Chroma criada com sucesso!"
    else
        echo "AVISO: PDF não encontrado em $PDF_PATH"
        echo "Coloque o arquivo banco_notas_base_expandida.pdf em rag/data/ e reinicie o container."
    fi
else
    echo "Base Chroma já existe. Pulando indexação."
fi

echo "=== Iniciando a aplicação ==="
# Comando original do container (ajuste se for diferente)
exec flask run --host=0.0.0.0 --port=5000