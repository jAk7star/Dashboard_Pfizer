# 📊 Projeto Didático: Pipeline de Sanitização de Dados e Dashboard (Case Pfizer)

Este repositório contém uma solução completa (Back-end em Python e Front-end em HTML/JS) para tratamento e visualização de dados de vendas. O projeto foi desenvolvido com **fins didáticos** para demonstrar um fluxo de trabalho de *Data Engineering* e *Data Analytics*, desde a ingestão de dados sujos até a exibição de insights de negócio.

## 🚀 Arquitetura do Projeto

O fluxo de trabalho é dividido em duas etapas principais:

1. **ETL e Sanitização (Python):** O script `Sanityzer.py` atua como um motor de validação. Ele lê uma planilha de dados brutos com inconsistências (erros de digitação, datas inválidas, números como texto), aplica regras estritas de limpeza, cria linhagem de dados (preservando o dado original ao lado do tratado) e gera uma coluna de `Status_Validacao`.
2. **Visualização (HTML/JS):** O arquivo `dashboard_pfizer.html` é um painel de controle que roda 100% no navegador (Client-side). Utilizando *SheetJS* para ler o arquivo tratado e *Chart.js* para os gráficos, ele filtra exclusivamente as linhas validadas para calcular métricas financeiras precisas.

## 🛠️ Tecnologias Utilizadas
* **Python 3:** Lógica de tratamento de dados.
* **Pandas & NumPy:** Manipulação e higienização de DataFrames.
* **Argparse:** Interface de Linha de Comando (CLI).
* **HTML5 / CSS3:** Estrutura e estilização do Dashboard (UI/UX limpa e responsiva).
* **JavaScript (Vanilla) + Chart.js:** Lógica de negócio no front-end e renderização gráfica.
* **SheetJS (xlsx):** Leitura de planilhas Excel diretamente no navegador.

---

## 📋 Como testar este projeto na sua máquina

> **Nota sobre Dados:** Por questões de boas práticas e privacidade, os arquivos `.xlsx` de base não estão inclusos neste repositório. Para testar, você precisará criar uma planilha Excel simulada com a estrutura descrita abaixo.

### 1. Estrutura Esperada da Planilha Bruta
Crie um arquivo `.xlsx` (ex: `dados_brutos.xlsx`) contendo, no mínimo, as seguintes colunas na primeira aba:

| ID_Transacao | Data_Venda | Medicamento | Quantidade | Preco_Unitario | Status_Pedido |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 001 | 15/04/2026 | paxlov1d | 6685 | 100.50 | Concluído |
| 002 | 20-05-2026 | XELJANZ | cx 7751 | R$ 2628,02 | Concluído |
| 003 | N/A | @liquis | -10 | 150,00 | Cancelado |

*Os dados podem conter erros propositais (como "cx" na quantidade, "@" no nome do remédio ou vírgulas em vez de pontos). O Python lidará com isso!*

## ⚙️ Como Executar a Pipeline (Python)

O script principal (`Sanityzer_V2.py`) é responsável por ler os dados brutos, aplicar as regras de negócio e gerar as bases limpas.

### 1. Pré-requisitos
Certifique-se de que tem o Python 3 instalado na sua máquina. Em seguida, instale as bibliotecas necessárias executando o seguinte comando no seu terminal:

bash
pip install pandas openpyxl

Executando o Script
Abra o seu terminal (CMD, PowerShell ou o terminal integrado do VS Code), navegue até a pasta onde o script está salvo e execute:

Bash
python Sanityzer_V2.py

python Sanityzer_V2.py --input "C:\Caminho\Para\Sua\Base\dados_brutos.xlsx"

✅ Saída Esperada
Se a execução for bem-sucedida, você verá um log de processamento no terminal informando a leitura da base e a aplicação das regras. Ao final, o script irá gerar automaticamente dois novos arquivos na mesma pasta:

vendas_pfizer_dados_tratados_v2.xlsx: Arquivo ideal para auditoria humana e conferência de fórmulas no Excel.

vendas_pfizer_dados_tratados_v2.csv: Arquivo leve e formatado em UTF-8, otimizado para ser carregado instantaneamente no Dashboard Web.

##3. Visualizando o Dashboard
Dê um duplo-clique no arquivo dashboard_pfizer.html para abri-lo no seu navegador.

Na interface do dashboard, utilize o botão de upload para carregar o arquivo dados_tratados.xlsx gerado no passo anterior.

O sistema irá automaticamente ignorar os dados sujos, processar apenas as linhas "Válidas" e apresentar os indicadores de negócio (Faturamento Total, Top Medicamentos por Volume e Receita).

🧠 Regras de Negócio Implementadas
Validação de Catálogo: Apenas medicamentos reconhecidos (ex: Paxlovid, Prevnar 13, Eliquis, Ibrance, Xeljanz, Comirnaty) são validados.

Consistência Numérica: Quantidades menores ou iguais a zero invalidam a transação.

Cálculo de Faturamento: Realizado multiplicando exclusivamente Quantidade_Sanitizada por Preco_Unitario_Sanitizado.

Desenvolvido para estudos em governança, qualidade de dados e visualização web client-side.
