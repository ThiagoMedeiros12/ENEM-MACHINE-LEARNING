import pandas as pd
import glob
import os

def main():
    # Caminho base (procurando os arquivos nas pastas de anos dento de databases)
    pattern = 'databases/**/dados_concatenados_completos*.csv'
    files = glob.glob(pattern, recursive=True)
    
    # O arquivo final será colocado na pasta root databases/
    output_file = 'databases/todos_anos_dados_concatenados_completos.csv'
    
    # Se existirem outras variações (ex sem pasta de ano no root), vamos incluir também
    files_alt = glob.glob('databases/dados_concatenados_completos*.csv')
    all_files = list(set(files + files_alt))
    
    # Remove o próprio output da lista se ele for pego acidentalmente
    all_files = [f for f in all_files if os.path.normpath(f) != os.path.normpath(output_file)]
    
    if not all_files:
        print("Nenhum arquivo encontrado com o nome 'dados_concatenados_completos_*.csv'")
        return
        
    print(f"Encontrados {len(all_files)} arquivos para consolidar:")
    for f in all_files:
        print(f" - {f}")
        
    print(f"\nGerando arquivo unificado: {output_file}")
    
    # Remove se já existir para reiniciar limpo
    if os.path.exists(output_file):
        os.remove(output_file)
        print("-> Arquivo antigo removido.")
        
    total_linhas = 0
    primeiro_arquivo = True
    
    import gc

    # Processamos um arquivo (ano) por vez, salvamos e limpamos a RAM
    for idx, file in enumerate(all_files, 1):
        print(f"\n[{idx}/{len(all_files)}] Lendo {file}...")
        
        # Descobre separador lendo a primeira linha
        with open(file, 'r', encoding='latin1') as f:
            primeira_linha = f.readline()
            sep = ';' if ';' in primeira_linha else ','
            
        try:
            # Lemos o arquivo completo do ano atual
            df_ano = pd.read_csv(file, sep=sep, encoding='latin1', dtype=str, on_bad_lines='skip')
            
            # Append do ano no arquivo consolidado
            mode = 'w' if primeiro_arquivo else 'a'
            header = primeiro_arquivo
            
            df_ano.to_csv(output_file, index=False, sep=';', encoding='latin1', mode=mode, header=header)
            
            linhas_arquivo = len(df_ano)
            total_linhas += linhas_arquivo
            primeiro_arquivo = False
            
            print(f"-> Concluído {file} (Adicionou {linhas_arquivo} linhas). Volume total: {total_linhas}")
            
            # Força a limpeza da memória apóes salvar cada ano terminado
            del df_ano
            gc.collect()
            
        except Exception as e:
            print(f"-> Erro ao processar o arquivo {file}: {e}")

    print(f"\n=> PROCESSO COMPLETO! O arquivo '{output_file}' foi criado com {total_linhas} linhas totais combinadas!")

if __name__ == "__main__":
    main()
