import pandas as pd
import numpy as np
import argparse

# 1. Configuração dos argumentos de Terminal
parser = argparse.ArgumentParser(description='Script de Sanitização de Dados Pfizer')

parser.add_argument('--input', '-i', 
                    default=r"C:\Users\Vaio\Desktop\Amostra de analise\Pfizer_base\vendas_pfizer_dados_brutos.xlsx", 
                    help='Caminho completo do arquivo Excel de entrada (dados brutos)')

parser.add_argument('--output', '-o', 
                    default=r"C:\Users\Vaio\Desktop\Amostra de analise\Pfizer_base\vendas_pfizer_dados_tratados.xlsx", 
                    help='Caminho completo onde o arquivo Excel tratado será salvo')

args = parser.parse_args()

# 2. Carrega os dados brutos (Se o arquivo não existir, o erro vai parar o script aqui)
print(f"Lendo o arquivo de entrada:\n{args.input}")
df = pd.read_excel(args.input)

# ==========================================
# Funções de Sanitização
# ==========================================
def clean_date(d):
    if pd.isna(d) or d == 'N/A' or str(d).strip() == '': 
        return pd.NaT
    try: 
        return pd.to_datetime(str(d).strip(), format='mixed', dayfirst=True)
    except: 
        return pd.NaT

def clean_med(m):
    if pd.isna(m): 
        return ""
    m_str = str(m).strip().lower().replace('1', 'i').replace('@', 'a')
    known_meds = ['paxlovid', 'prevnar 13', 'eliquis', 'ibrance', 'xeljanz', 'comirnaty']
    for km in known_meds:
        if m_str == km:
            return km.title() if km != 'prevnar 13' else 'Prevnar 13'
    return m_str.title()

def clean_number(n):
    if pd.isna(n): 
        return np.nan
    n_str = str(n).strip().lower().replace('r$', '').replace('cx', '').strip()
    if ',' in n_str and '.' not in n_str:
        n_str = n_str.replace(',', '.')
    try: 
        return float(n_str)
    except: 
        return np.nan

# 3. Aplica as regras criando um novo DataFrame
print("Aplicando regras de sanitização...")
df_final = pd.DataFrame()

# Copia colunas e aplica limpeza
df_final['ID_Transacao'] = df['ID_Transacao'] if 'ID_Transacao' in df.columns else df.index

df_final['Data_Venda_Original'] = df['Data_Venda'] if 'Data_Venda' in df.columns else np.nan
df_final['Data_Venda_Sanitizada'] = df_final['Data_Venda_Original'].apply(clean_date)

df_final['Medicamento_Original'] = df['Medicamento'] if 'Medicamento' in df.columns else np.nan
df_final['Medicamento_Sanitizado'] = df_final['Medicamento_Original'].apply(clean_med)

df_final['Quantidade_Original'] = df['Quantidade'] if 'Quantidade' in df.columns else np.nan
df_final['Quantidade_Sanitizada'] = df_final['Quantidade_Original'].apply(clean_number)

df_final['Preco_Unitario_Original'] = df['Preco_Unitario'] if 'Preco_Unitario' in df.columns else np.nan
df_final['Preco_Unitario_Sanitizado'] = df_final['Preco_Unitario_Original'].apply(clean_number)

# Mantém outras colunas importantes, se existirem na base
colunas_extras = ['Lote', 'UF_Venda', 'Categoria_Terapeutica', 'Data_Validade', 
                  'Canal_Venda', 'Representante_Comercial', 'Desconto_Aplicado', 'Status_Pedido']
for col in colunas_extras:
    if col in df.columns:
        df_final[col] = df[col]

# 4. Motor de Validação
status_validacao = []
valid_meds = ['Paxlovid', 'Prevnar 13', 'Eliquis', 'Ibrance', 'Xeljanz', 'Comirnaty']

for index, row in df_final.iterrows():
    erros = []
    if pd.isna(row['Data_Venda_Sanitizada']): 
        erros.append("Data Ausente/Inválida")
    if row['Medicamento_Sanitizado'] not in valid_meds: 
        erros.append("Medicamento Desconhecido")
    if pd.isna(row['Quantidade_Sanitizada']): 
        erros.append("Quantidade Não-Numérica")
    elif row['Quantidade_Sanitizada'] <= 0: 
        erros.append("Quantidade Negativa ou Zero")
         
    status_validacao.append(" | ".join(erros) if erros else "Válido")

df_final['Status_Validacao'] = status_validacao

# 5. Exporta o resultado
print("Exportando arquivo final...")
df_final.to_excel(args.output, index=False)
print(f"\n[SUCESSO] Arquivo tratado salvo em:\n{args.output}")