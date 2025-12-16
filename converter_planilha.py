"""
Conversor de Planilha Financeira Real
======================================
Converte sua planilha (data/Despesas.csv) para o formato do sistema.
"""

import pandas as pd
import re
from datetime import datetime

def limpar_valor(valor_str):
    """
    Converte 'R$ 120,00' para 120.00
    """
    if pd.isna(valor_str) or valor_str == '':
        return 0.0
    
    # Remover 'R$', espaços e aspas
    valor_limpo = str(valor_str).replace('R$', '').replace('"', '').replace(' ', '').strip()
    
    # Se tiver sinal negativo, preservar
    negativo = '-' in valor_limpo
    valor_limpo = valor_limpo.replace('-', '')
    
    # Trocar vírgula por ponto
    valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
    
    try:
        valor_float = float(valor_limpo)
        return -valor_float if negativo else valor_float
    except:
        return 0.0

def mapear_categoria_por_tags(tags):
    """
    Mapeia tags para as 7 categorias corretas do sistema
    """
    if pd.isna(tags) or tags == '':
        return 'CATEGORIZAR'
    
    tags_lower = str(tags).lower().strip()
    
    # Mapeamento direto de tags para categorias
    if 'custos fixos' in tags_lower:
        return 'CUSTOS FIXOS'
    elif 'conforto' in tags_lower:
        return 'CONFORTO'
    elif 'prazeres' in tags_lower:
        return 'PRAZERES'
    elif 'conhecimento' in tags_lower:
        return 'CONHECIMENTO'
    elif 'metas' in tags_lower:
        return 'METAS'
    elif 'liberdade financeira' in tags_lower:
        return 'LIBERDADE FINANCEIRA'
    elif 'categorizar' in tags_lower:
        return 'CATEGORIZAR'
    else:
        return 'CATEGORIZAR'  # Default

def mapear_categoria(categoria_original, subcategoria='', tags=''):
    """
    Mapeia as categorias da planilha para as 7 categorias corretas
    Usa tags como fonte principal de verdade
    """
    # Se tem tags, usar tags como fonte principal
    if tags and str(tags).strip() != '':
        return mapear_categoria_por_tags(tags)
    
    # Fallback: usar categoria_original e subcategoria
    categoria_upper = str(categoria_original).upper()
    sub_upper = str(subcategoria).upper()
    
    # Mapeamento baseado em padrões (fallback)
    if 'CUSTOS FIXOS' in categoria_upper:
        return 'CUSTOS FIXOS'
    elif 'CONFORTO' in categoria_upper:
        return 'CONFORTO'
    elif 'PRAZERES' in categoria_upper:
        return 'PRAZERES'
    elif 'CONHECIMENTO' in categoria_upper or 'EDUCAÇÃO' in categoria_upper:
        return 'CONHECIMENTO'
    elif 'METAS' in categoria_upper:
        return 'METAS'
    elif 'LIBERDADE' in categoria_upper:
        return 'LIBERDADE FINANCEIRA'
    else:
        return 'CATEGORIZAR'  # Default

def converter_planilha():
    """
    Converte data/Despesas.csv para o formato do sistema
    """
    print("=== CONVERSOR DE PLANILHA FINANCEIRA ===\n")
    
    # Ler arquivo original (com separador ;)
    print("1. Lendo planilha original...")
    try:
        df = pd.read_csv('data/Despesas.csv', sep=';', encoding='utf-8')
    except:
        try:
            df = pd.read_csv('data/Despesas.csv', sep=';', encoding='latin-1')
        except Exception as e:
            print(f"Erro ao ler planilha: {e}")
            return
    
    print(f"   Linhas originais: {len(df)}")
    print(f"   Colunas: {list(df.columns[:6])}")
    
    # Remover linhas vazias
    print("\n2. Limpando dados...")
    
    # Pegar nome real das colunas (pode ter encoding diferente)
    col_descricao = [c for c in df.columns if 'DESCRI' in c.upper()][0]
    
    # Filtrar apenas linhas válidas (que têm descrição e valor)
    df = df[df[col_descricao].notna()]
    df = df[df['VALOR'].notna()]
    
    # Remover linhas vazias (que só tem #REF! ou vazio)
    df = df[df[col_descricao].astype(str).str.strip() != '']
    df = df[~df[col_descricao].astype(str).str.contains('#REF!', na=False)]
    
    print(f"   Linhas apos limpeza inicial: {len(df)}")
    
    # Remover linhas com valores vazios ou zero
    df['VALOR_TEMP'] = df['VALOR'].apply(limpar_valor)
    df = df[df['VALOR_TEMP'] != 0]
    
    print(f"   Linhas validas: {len(df)}")
    
    # Criar DataFrame no novo formato
    # Ordem correta: data,descricao,valor,tags,subcategoria,categoria
    print("\n3. Convertendo formato...")
    
    # Tags (usar a coluna tags original se existir, senão usar CATEGORIA)
    col_tags = None
    for col in df.columns:
        if 'TAG' in col.upper() or 'TAGS' in col.upper():
            col_tags = col
            break
    
    tags_source = df[col_tags] if col_tags else df['CATEGORIA']
    
    # Criar DataFrame na ordem correta: data,descricao,valor,tags,subcategoria,categoria
    novo_df = pd.DataFrame({
        'data': pd.to_datetime('2024-01-01'),  # Data padrão
        'descricao': df[col_descricao].str.strip(),
        'valor': df['VALOR'].apply(limpar_valor),
        'tags': tags_source.fillna('').str.lower().str.strip(),
        'subcategoria': df['SubCategoria'].fillna('').str.strip(),
        'categoria': df.apply(
            lambda row: mapear_categoria(
                row.get('CATEGORIA', ''), 
                row.get('SubCategoria', ''),
                row.get(col_tags, '') if col_tags else ''
            ), 
            axis=1
        )
    })
    
    # Remover duplicatas exatas
    print("\n4. Removendo duplicatas...")
    antes = len(novo_df)
    novo_df = novo_df.drop_duplicates(subset=['descricao', 'valor'], keep='first')
    depois = len(novo_df)
    print(f"   Removidas: {antes - depois} duplicatas")
    
    # Ordenar por descrição
    novo_df = novo_df.sort_values('descricao').reset_index(drop=True)
    
    # Salvar
    print("\n5. Salvando arquivo convertido...")
    novo_df.to_csv('data/expenses_converted.csv', index=False)
    print(f"   Arquivo salvo: data/expenses_converted.csv")
    print(f"   Total de despesas: {len(novo_df)}")
    
    # Estatísticas
    print("\n6. Estatísticas por categoria:")
    stats = novo_df['categoria'].value_counts()
    for cat, count in stats.items():
        print(f"   {cat:15s}: {count:4d} despesas")
    
    print(f"\n7. Valor total: R$ {novo_df['valor'].sum():,.2f}")
    
    # Mostrar primeiras linhas
    print("\n8. Primeiras 5 despesas:")
    print(novo_df[['descricao', 'valor', 'categoria']].head().to_string(index=False))
    
    print("\nOK CONVERSAO CONCLUIDA!")
    print("\nProximo passo:")
    print("   1. Revise o arquivo: data/expenses_converted.csv")
    print("   2. Se estiver OK, substitua: cp data/expenses_converted.csv data/expenses.csv")
    print("   3. Treine o modelo: python train_model.py")

if __name__ == "__main__":
    converter_planilha()

