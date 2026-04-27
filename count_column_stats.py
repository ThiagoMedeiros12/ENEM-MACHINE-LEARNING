import pandas as pd

def main():
    input_file = 'databases/DADOS_CONCATENADOS_2024.csv'
    report_file = 'databases/relatorio_estatisticas_colunas.csv'
    
    # Dicionários para armazenar as contagens por coluna
    total_linhas = 0
    empty_counts = {}
    filled_counts = {}
    
    print(f"🕵️  Lendo cabeçalhos de {input_file}...\n")
    try:
        with open(input_file, 'r', encoding='latin1') as f:
            sep = ';' if ';' in f.readline() else ','
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo {input_file} não encontrado.")
        return

    print("📊 Iniciando a contagem de vazios para cada coluna...")
    print("⏳ Isso pode levar alguns minutos devido ao tamanho do arquivo (4.3+ milhões de linhas).")
    
    chunk_size = 500000
    try:
        # Lemos em chunks (pedaços) para não explodir a memória do computador
        colunas_lidas = []
        for chunk in pd.read_csv(input_file, sep=sep, encoding='latin1', low_memory=False, chunksize=chunk_size):
            total_linhas += len(chunk)
            
            if not colunas_lidas:
                colunas_lidas = chunk.columns.tolist()
                for c in colunas_lidas:
                    empty_counts[c] = 0
                    filled_counts[c] = 0

            for col in chunk.columns:
                # Se a coluna for de texto, verifica espaços vazios "" ou null/NaN
                if chunk[col].dtype == object:
                    is_empty = chunk[col].astype(str).str.strip().eq("") | chunk[col].isnull()
                else:
                    # Se for número, apenas null/NaN
                    is_empty = chunk[col].isnull()
                
                qtd_vazios = is_empty.sum()
                qtd_preenchidos = len(chunk) - qtd_vazios
                
                empty_counts[col] += qtd_vazios
                filled_counts[col] += qtd_preenchidos
                
            print(f"  .. Progresso: {total_linhas} linhas processadas", end='\r')
            
    except Exception as e:
        print(f"\n❌ Erro crítico ao processar os dados: {e}")
        return

    print("\n\n✅ Processamento concluído! Resultados consolidados:\n")
    
    # Prepara os dados do relatório final e exibe no terminal um resumo
    pad_coluna = max([len(c) for c in colunas_lidas]) + 2
    
    linha_divisoria = "-" * (pad_coluna + 40)
    print(f"{'COLUNA'.ljust(pad_coluna)} | {'TOTAL'.ljust(10)} | {'PREENCHIDAS'.ljust(12)} | {'VAZIAS'.ljust(10)}")
    print(linha_divisoria)
    
    # Criar listas para facilitar a gravação em um novo CSV de relatório
    report_data = {
        'NOME_COLUNA': [],
        'TOTAL_LINHAS': [],
        'PREENCHIDAS': [],
        'VAZIAS': [],
        'PERC_PREENCHIMENTO': []
    }
    
    for col in colunas_lidas:
        if col in empty_counts:
            t = total_linhas
            p = filled_counts[col]
            v = empty_counts[col]
            percentual = (p / t * 100) if t > 0 else 0
            
            # Mostra no console
            print(f"{col.ljust(pad_coluna)} | {str(t).ljust(10)} | {str(p).ljust(12)} | {str(v).ljust(10)}")
            
            # Adiciona ao dicinário de relatório
            report_data['NOME_COLUNA'].append(col)
            report_data['TOTAL_LINHAS'].append(t)
            report_data['PREENCHIDAS'].append(p)
            report_data['VAZIAS'].append(v)
            report_data['PERC_PREENCHIMENTO'].append(f"{percentual:.2f}%")
            
    # Salvar em um arquivo para facilitar a consulta
    print(f"\n💾 Salvando relatório detalhado no formato CSV em {report_file}...")
    df_report = pd.DataFrame(report_data)
    df_report.to_csv(report_file, index=False, sep=';', encoding='latin1')
    print("=> Relatório salvo com sucesso!")

if __name__ == "__main__":
    main()
