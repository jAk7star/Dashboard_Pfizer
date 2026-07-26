import pandas as pd
import numpy as np
import argparse
import sys
import os

# ==========================================
# 1. Configuração (Terminal)
# ==========================================
parser = argparse.ArgumentParser(description='Sanityzer V2 - Pipeline de Limpeza Pfizer')

# Caminho de entrada (Mude aqui se necessário)
caminho_padrao_entrada = r"COLE AQUI O CAMINHO DO ARQUIVO DE ENTRADA"
pasta_saida = r"COLE AQUI O CAMINHO DA PASTA DE SAÍDA"

parser.add_argument('--input', '-i', default=caminho_padrao_entrada, help='Caminho do arquivo bruto (.xlsx ou .csv)')
args = parser.parse_args()

# ==========================================
# 2. Leitura Inteligente (Aceita CSV ou XLSX)
# ==========================================
print(f"[{'Iniciando Sanityzer V2'.center(40, '-')}]")
print(f"Lendo base: {args.input}")

try:
    if args.input.lower().endswith('.csv'):
        df = pd.read_csv(args.input, sep=None, engine='python')
    else:
        df = pd.read_excel(args.input)
except FileNotFoundError:
    print(f"\n[ERRO] O arquivo não foi encontrado: {args.input}")
    sys.exit()
except Exception as e:
    print(f"\n[ERRO] Falha ao ler o arquivo: {e}")
    sys.exit()

# ==========================================
# 3. Funções de Sanitização (Blindadas)
# ==========================================
def clean_date(d):
    # Se for vazio, retorna um nulo verdadeiro (evita o 00:00:00)
    if pd.isna(d) or str(d).strip().lower() in ['', 'nan', 'n/a', 'nat']: 
        return np.nan
    try: 
        # Tenta extrair a data e formata como string YYYY-MM-DD para o Excel não distorcer
        dt = pd.to_datetime(str(d).strip(), format='mixed', dayfirst=True)
        return dt.strftime('%Y-%m-%d')
    except: 
        return np.nan

def clean_med(m):
    if pd.isna(m) or str(m).strip() == '': 
        return np.nan
    m_str = str(m).strip().lower().replace('1', 'i').replace('@', 'a')
    known_meds = ['paxlovid', 'prevnar 13', 'eliquis', 'ibrance', 'xeljanz', 'comirnaty']
    for km in known_meds:
        if m_str == km:
            return km.title() if km != 'prevnar 13' else 'Prevnar 13'
    return m_str.title()

def clean_number(n):
    if pd.isna(n) or str(n).strip() == '': 
        return np.nan
    n_str = str(n).strip().lower().replace('r$', '').replace('cx', '').strip()
    
    # Tratamento de decimais (BR vs US)
    if ',' in n_str and '.' not in n_str:
        n_str = n_str.replace(',', '.')
    elif ',' in n_str and '.' in n_str:
        n_str = n_str.replace('.', '').replace(',', '.')
        
    try: 
        return float(n_str)
    except: 
        return np.nan

# ==========================================
# 4. Aplicação das Regras (Linhagem de Dados)
# ==========================================
print("Aplicando higienização e validação de regras de negócio...")
df_final = pd.DataFrame()

# Colunas Essenciais
df_final['ID_Transacao'] = df['ID_Transacao'] if 'ID_Transacao' in df.columns else df.index

df_final['Data_Venda_Original'] = df['Data_Venda'] if 'Data_Venda' in df.columns else np.nan
df_final['Data_Venda_Sanitizada'] = df_final['Data_Venda_Original'].apply(clean_date)

df_final['Medicamento_Original'] = df['Medicamento'] if 'Medicamento' in df.columns else np.nan
df_final['Medicamento_Sanitizado'] = df_final['Medicamento_Original'].apply(clean_med)

df_final['Quantidade_Original'] = df['Quantidade'] if 'Quantidade' in df.columns else np.nan
df_final['Quantidade_Sanitizada'] = df_final['Quantidade_Original'].apply(clean_number)

df_final['Preco_Unitario_Original'] = df['Preco_Unitario'] if 'Preco_Unitario' in df.columns else np.nan
df_final['Preco_Unitario_Sanitizado'] = df_final['Preco_Unitario_Original'].apply(clean_number)

# Recuperando as outras colunas de negócio
colunas_extras = ['Lote', 'UF_Venda', 'Categoria_Terapeutica', 'Data_Validade', 
                  'Canal_Venda', 'Representante_Comercial', 'Desconto_Aplicado', 'Status_Pedido']
for col in colunas_extras:
    if col in df.columns:
        df_final[col] = df[col]

# ==========================================
# 5. Motor de Validação
# ==========================================
status_validacao = []
valid_meds = ['Paxlovid', 'Prevnar 13', 'Eliquis', 'Ibrance', 'Xeljanz', 'Comirnaty']

for index, row in df_final.iterrows():
    erros = []
    if pd.isna(row['Data_Venda_Sanitizada']): 
        erros.append("Data Ausente/Inválida")
    if pd.isna(row['Medicamento_Sanitizado']) or row['Medicamento_Sanitizado'] not in valid_meds: 
        erros.append("Medicamento Desconhecido")
    if pd.isna(row['Quantidade_Sanitizada']): 
        erros.append("Quantidade Não-Numérica")
    elif row['Quantidade_Sanitizada'] <= 0: 
        erros.append("Quantidade Negativa ou Zero")
         
    status_validacao.append(" | ".join(erros) if erros else "Válido")

df_final['Status_Validacao'] = status_validacao

# ==========================================
# 6. Exportação (XLSX e CSV)
# ==========================================
nome_base = "vendas_pfizer_dados_tratados_v2"
caminho_xlsx = os.path.join(pasta_saida, f"{nome_base}.xlsx")
caminho_csv = os.path.join(pasta_saida, f"{nome_base}.csv")

print("Exportando ficheiros finais...")
try:
    # Exporta para Excel (Auditoria humana) - Mantendo as células nulas 100% vazias
    df_final.to_excel(caminho_xlsx, index=False)
    
    # Exporta para CSV (Dashboard HTML)
    df_final.to_csv(caminho_csv, index=False, encoding='utf-8-sig', sep=';')
    
    print(f"\n[SUCESSO] Pipeline Concluída!")
    print(f"👉 Excel: {caminho_xlsx}")
    print(f"👉 CSV:   {caminho_csv}")
except Exception as e:
    print(f"\n[ERRO] Não foi possível salvar. Verifique se o arquivo já está aberto. Erro: {e}")