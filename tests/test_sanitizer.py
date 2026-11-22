import pandas as pd

from src.sanitizer import (
    clean_date_string,
    clean_medication_name,
    clean_numeric_currency_or_quantity,
    process_pharma_dataframe,
)


def test_clean_date_string():
    assert clean_date_string("15/04/2026") == "2026-04-15"
    assert clean_date_string("2026-05-20") == "2026-05-20"
    assert clean_date_string(None) is None
    assert clean_date_string("N/A") is None
    assert clean_date_string("invalid_date") is None


def test_clean_medication_name_ocr_normalization():
    assert clean_medication_name("paxlov1d") == "Paxlovid"
    assert clean_medication_name("@liquis") == "Eliquis"
    assert clean_medication_name("XELJANZ") == "Xeljanz"
    assert clean_medication_name("prevnar 13") == "Prevnar 13"
    assert clean_medication_name(None) is None


def test_clean_numeric_currency_and_units():
    assert clean_numeric_currency_or_quantity("R$ 2.628,02") == 2628.02
    assert clean_numeric_currency_or_quantity("cx 7751") == 7751.0
    assert clean_numeric_currency_or_quantity("100.50") == 100.50
    assert clean_numeric_currency_or_quantity("-10") == -10.0
    assert clean_numeric_currency_or_quantity(None) is None
    assert clean_numeric_currency_or_quantity("texto_sem_numero") is None


def test_process_pharma_dataframe_lineage_and_validation():
    data = {
        "ID_Transacao": [101, 102, 103],
        "Data_Venda": ["15/04/2026", "invalid_date", "20/05/2026"],
        "Medicamento": ["paxlov1d", "DesconhecidoMed", "eliquis"],
        "Quantidade": ["cx 100", "50", "-5"],
        "Preco_Unitario": ["R$ 200,00", "R$ 150,00", "R$ 100,00"],
    }
    df_raw = pd.DataFrame(data)
    df_clean = process_pharma_dataframe(df_raw)

    assert len(df_clean) == 3
    assert "Data_Venda_Sanitizada" in df_clean.columns
    assert "Medicamento_Sanitizado" in df_clean.columns
    assert "Status_Validacao" in df_clean.columns
    assert "Faturamento_Sanitizado" in df_clean.columns

    # Row 1 is completely valid
    assert df_clean.loc[0, "Status_Validacao"] == "Válido"
    assert df_clean.loc[0, "Faturamento_Sanitizado"] == 20000.0

    # Row 2 has date and medication errors
    assert "Data Ausente/Inválida" in df_clean.loc[1, "Status_Validacao"]
    assert "Medicamento Desconhecido" in df_clean.loc[1, "Status_Validacao"]

    # Row 3 has negative quantity
    assert "Quantidade Negativa ou Zero" in df_clean.loc[2, "Status_Validacao"]
