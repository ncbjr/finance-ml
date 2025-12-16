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

def mapear_categoria(categoria_original, subcategoria=''):
    """
    Mapeia as categorias da sua planilha para as 6 categorias do sistema
    """
    categoria_upper = str(categoria_original).upper()
    sub_upper = str(subcategoria).upper()
    
    # Mapeamento de categorias
    if 'ALIMENTAÇÃO' in categoria_upper or 'ALIMENTAÇÃO' in sub_upper:
        return 'Alimentação'
    
    elif any(x in sub_upper for x in ['TRANSPORTE', 'UBER', 'COMBUSTÍVEL', 'MANUTENÇÃO']):
        return 'Transporte'
    
    elif any(x in sub_upper for x in ['SAUDE', 'SAÚDE', 'CONSULTA', 'FARMÁCIA', 'EXAME', 'MANIPULAÇÃO', 'ASSINATURA']):
        return 'Saúde'
    
    elif any(x in sub_upper for x in ['LAZER', 'RESTAURANTE', 'LANCHE']):
        return 'Lazer'
    
    elif any(x in categoria_upper for x in ['CONHECIMENTO', 'EDUCAÇÃO']) or 'EDUCAÇÃO' in sub_upper:
        return 'Educação'
    
    elif any(x in sub_upper for x in ['HABITAÇÃO', 'TELEFONE', 'FERRAMENTAS']):
        return 'Moradia'
    
    elif 'CUSTOS FIXOS' in categoria_upper:
        # Para custos fixos, ver subcategoria
        if 'HABITAÇÃO' in sub_upper or 'TELEFONE' in sub_upper:
            return 'Moradia'
        elif 'TRANSPORTE' in sub_upper:
            return 'Transporte'
        elif 'SAUDE' in sub_upper or 'SAÚDE' in sub_upper:
            return 'Saúde'
        else:
            return 'Alimentação'  # Default para custos fixos
    
    elif 'CONFORTO' in categoria_upper:
        # Conforto pode ser várias coisas
        if 'TRANSPORTE' in sub_upper:
            return 'Transporte'
        elif 'RESTAURANTE' in sub_upper:
            return 'Lazer'
        else:
            return 'Moradia'
    
    elif 'PRAZERES' in categoria_upper:
        if 'RESTAURANTE' in sub_upper or 'LANCHE' in sub_upper:
            return 'Lazer'
        elif 'SAUDE' in sub_upper or 'SAÚDE' in sub_upper:
            return 'Saúde'
        else:
            return 'Lazer'
    
    # Default
    return 'Outros'

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
    print("\n3. Convertendo formato...")
    novo_df = pd.DataFrame()
    
    # Data - usar coluna MÊS como referência (será aproximado)
    # Como a planilha original não tem data completa, vamos criar uma
    novo_df['data'] = pd.to_datetime('2024-01-01')  # Data padrão
    
    # Descrição (usar nome real da coluna)
    novo_df['descricao'] = df[col_descricao].str.strip()
    
    # Valor
    novo_df['valor'] = df['VALOR'].apply(limpar_valor)
    
    # Categoria (mapear)
    novo_df['categoria'] = df.apply(
        lambda row: mapear_categoria(row['CATEGORIA'], row.get('SubCategoria', '')), 
        axis=1
    )
    
    # Subcategoria (usar a subcategoria original)
    novo_df['subcategoria'] = df['SubCategoria'].fillna('').str.strip()
    
    # Tags (criar baseado na categoria original)
    novo_df['tags'] = df['CATEGORIA'].fillna('').str.lower().str.strip()
    
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

