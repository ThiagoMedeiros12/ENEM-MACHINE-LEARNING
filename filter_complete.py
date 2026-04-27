import pandas as pd

# Lista de colunas obrigatórias que DEVEM estar preenchidas nas linhas mantidas
colunas_obrigatorias = [
    'NU_INSCRICAO',
    'NU_ANO',
    'TP_FAIXA_ETARIA',
    'TP_SEXO',
    'TP_ESTADO_CIVIL',
    'TP_COR_RACA',
    'TP_NACIONALIDADE',
    'TP_ST_CONCLUSAO',
    'TP_ANO_CONCLUIU',
    'TP_ENSINO',
    'Q001', 'Q002', 'Q003', 'Q004', 'Q005', 'Q006', 'Q007', 'Q008', 'Q009', 'Q010',
    'Q011', 'Q012', 'Q013', 'Q014', 'Q015', 'Q016', 'Q017', 'Q018', 'Q019', 'Q020',
    'Q021', 'Q022', 'Q023',
    'NU_NOTA_CN',
    'NU_NOTA_CH',
    'NU_NOTA_LC',
    'NU_NOTA_MT',
    'TP_LINGUA',
    'TP_STATUS_REDACAO',
    'NU_NOTA_COMP1',
    'NU_NOTA_COMP2',
    'NU_NOTA_COMP3',
    'NU_NOTA_COMP4',
    'NU_NOTA_COMP5',
    'NU_NOTA_REDACAO'
]

def get_columns(filepath):
    """Descobre o delimitador e extrai apenas a lista de colunas iniciais do arquivo"""
    with open(filepath, 'r', encoding='latin1') as f:
        first_line = f.readline().strip()
    separator = ';' if ';' in first_line else ','
    cols = first_line.split(separator)
    return [c.strip('"') for c in cols], separator

def filter_complete_rows(df, cols_to_check):
    """Aplica o filtro para localizar e remover linhas que tenham campos vazios/nulos nas colunas de check"""
    if df.empty:
        return df
        
    mask = pd.Series([False] * len(df), index=df.index)
    
    for col in cols_to_check:
        if df[col].dtype == object:
            # text strings
            is_blank = df[col].astype(str).str.strip().eq("") | df[col].isnull()
        else:
            # numbers
            is_blank = df[col].isnull()
        
        # se uma coluna for true, toda a linha fica true (ela tem problemas)
        mask |= is_blank
        
    # manter somente onde a mask de problemas é False
    return df[~mask]

def main():
    input_file = 'databases/2014/MICRODADOS_ENEM_2014.csv'
    output_file = 'databases/2014/dados_concatenados_completos_2014.csv'

    print(f"Lendo cabeçalhos de {input_file}...")
    try:
        cols, sep = get_columns(input_file)
    except FileNotFoundError:
        print(f"Erro: Arquivo {input_file} não encontrado.")
        return
        
    # Seleciona as colunas do arquivo que fazem parte da lista de obrigatórias
    usecols = [c for c in cols if c in colunas_obrigatorias]
    print(f"-> Encontradas {len(usecols)} das {len(colunas_obrigatorias)} colunas obrigatórias na concatenação.")

    if not usecols:
        print("Erro: Nenhuma coluna obrigatória encontrada no arquivo!")
        return

    print("\nIniciando o processamento do arquivo de dados (aos pedaços)...")
    
    chunks = []
    chunk_size = 500000
    total_linhas = 0
    total_completas = 0
    
    try:
        # Lê por partes (chunksize) para garantir que arquivos de 4~8GB de RAM não travem o PC
        for chunk in pd.read_csv(input_file, sep=sep, encoding='latin1', usecols=usecols, 
                                 low_memory=False, chunksize=chunk_size):
            total_linhas += len(chunk)
            
            # Filtra todas as linhas
            chunk_filtered = filter_complete_rows(chunk, usecols)
            
            total_completas += len(chunk_filtered)
            chunks.append(chunk_filtered)
            
            # Print para feedback de que não está travado
            print(f"  ..Lidas: {total_linhas} | Linhas válidas preservadas: {total_completas}", end='\r')
            
        print("\n\n-> Terminou a triagem! Juntando as linhas válidas...")
        # Recria o dataframe completo filtrado
        df_final = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
        del chunks  # limpar mem de chunks
        
    except Exception as e:
        print(f"Erro crítico ao varrer dados: {e}")
        return

    print(f"\n=> Estatística Final:")
    print(f" - Quantidade de linhas originais (completas + incompletas): {total_linhas}")
    print(f" - Quantidade de linhas válidas (todas colunas preenchidas): {total_completas}")
    
    if df_final.empty:
        print("Nenhuma linha válida passou nos filtros. Abortando exportação.")
        return

    # Garantir a ordem exata em que o colunas_obrigatorias foi definida
    final_cols = [c for c in colunas_obrigatorias if c in df_final.columns]
    df_final = df_final[final_cols]

    print(f"\nSalvando resultado restrito às colunas e linhas válidas em {output_file}...")
    # Exporta
    df_final.to_csv(output_file, index=False, sep=';', encoding='latin1', chunksize=100000)
    print("=> Salvo com sucesso! Processo Finalizado!")

if __name__ == "__main__":
    main()
