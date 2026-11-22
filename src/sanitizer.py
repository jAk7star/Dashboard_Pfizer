"""Pharmaceutical data quality, sanitization, and lineage engine."""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

CANONICAL_MEDICATIONS: dict[str, str] = {
    "paxlovid": "Paxlovid",
    "prevnar 13": "Prevnar 13",
    "eliquis": "Eliquis",
    "ibrance": "Ibrance",
    "xeljanz": "Xeljanz",
    "comirnaty": "Comirnaty",
}


def clean_date_string(value: Any) -> str | None:
    """Sanitizes raw date values into ISO standard 'YYYY-MM-DD' strings.

    Returns None for NaNs, empty strings, or unparseable dates.
    """
    if pd.isna(value) or str(value).strip().lower() in ("", "nan", "n/a", "nat", "null"):
        return None

    cleaned_str = str(value).strip()
    try:
        dt = pd.to_datetime(cleaned_str, format="mixed", dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


def clean_medication_name(value: Any) -> str | None:
    """Normalizes noisy medication strings, correcting common OCR typos and leetspeak."""
    if pd.isna(value) or str(value).strip() == "":
        return None

    raw_str = str(value).strip().lower()

    # Check exact match first (e.g. 'prevnar 13' before replacing digits)
    if raw_str in CANONICAL_MEDICATIONS:
        return CANONICAL_MEDICATIONS[raw_str]

    # Handle known OCR typos
    raw_str = raw_str.replace("paxlov1d", "paxlovid").replace("@liquis", "eliquis")
    if raw_str in CANONICAL_MEDICATIONS:
        return CANONICAL_MEDICATIONS[raw_str]

    return raw_str.title()


def clean_numeric_currency_or_quantity(value: Any) -> float | None:
    """Parses numeric fields handling Brazilian currency symbols (R$), package abbreviations (cx),

    and localized comma vs dot decimal separators.
    """
    if pd.isna(value) or str(value).strip() == "":
        return None

    raw_str = (
        str(value).strip().lower().replace("r$", "").replace("cx", "").replace("un", "").strip()
    )

    # Handle localized decimal and thousand separators
    if "," in raw_str and "." not in raw_str:
        raw_str = raw_str.replace(",", ".")
    elif "," in raw_str and "." in raw_str:
        raw_str = raw_str.replace(".", "").replace(",", ".")

    try:
        val = float(raw_str)
        return val if np.isfinite(val) else None
    except ValueError:
        return None


def process_pharma_dataframe(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Applies end-to-end data sanitization, lineage tracking, and audit validation."""
    df_clean = pd.DataFrame()

    # Preserve transaction identifier
    df_clean["ID_Transacao"] = (
        df_raw["ID_Transacao"] if "ID_Transacao" in df_raw.columns else df_raw.index + 1
    )

    # Data lineage: retain original beside sanitized
    df_clean["Data_Venda_Original"] = (
        df_raw["Data_Venda"] if "Data_Venda" in df_raw.columns else np.nan
    )
    df_clean["Data_Venda_Sanitizada"] = df_clean["Data_Venda_Original"].apply(clean_date_string)

    df_clean["Medicamento_Original"] = (
        df_raw["Medicamento"] if "Medicamento" in df_raw.columns else np.nan
    )
    df_clean["Medicamento_Sanitizado"] = df_clean["Medicamento_Original"].apply(
        clean_medication_name
    )

    df_clean["Quantidade_Original"] = (
        df_raw["Quantidade"] if "Quantidade" in df_raw.columns else np.nan
    )
    df_clean["Quantidade_Sanitizada"] = df_clean["Quantidade_Original"].apply(
        clean_numeric_currency_or_quantity
    )

    df_clean["Preco_Unitario_Original"] = (
        df_raw["Preco_Unitario"] if "Preco_Unitario" in df_raw.columns else np.nan
    )
    df_clean["Preco_Unitario_Sanitizado"] = df_clean["Preco_Unitario_Original"].apply(
        clean_numeric_currency_or_quantity
    )

    # Copy contextual columns if available
    context_columns = [
        "Lote",
        "UF_Venda",
        "Categoria_Terapeutica",
        "Data_Validade",
        "Canal_Venda",
        "Representante_Comercial",
        "Desconto_Aplicado",
        "Status_Pedido",
    ]
    for col in context_columns:
        if col in df_raw.columns:
            df_clean[col] = df_raw[col]

    # Validation Engine
    validation_results: list[str] = []
    valid_names = set(CANONICAL_MEDICATIONS.values())

    for _, row in df_clean.iterrows():
        errors = []
        if pd.isna(row["Data_Venda_Sanitizada"]):
            errors.append("Data Ausente/Inválida")
        if (
            pd.isna(row["Medicamento_Sanitizado"])
            or row["Medicamento_Sanitizado"] not in valid_names
        ):
            errors.append("Medicamento Desconhecido")
        if pd.isna(row["Quantidade_Sanitizada"]):
            errors.append("Quantidade Não-Numérica")
        elif row["Quantidade_Sanitizada"] <= 0:
            errors.append("Quantidade Negativa ou Zero")
        if pd.isna(row["Preco_Unitario_Sanitizado"]) or row["Preco_Unitario_Sanitizado"] <= 0:
            errors.append("Preço Unitário Inválido")

        validation_results.append(" | ".join(errors) if errors else "Válido")

    df_clean["Status_Validacao"] = validation_results

    # Calculated Financial Revenue (only for valid rows)
    is_valid = df_clean["Status_Validacao"] == "Válido"
    df_clean["Faturamento_Sanitizado"] = np.where(
        is_valid,
        df_clean["Quantidade_Sanitizada"] * df_clean["Preco_Unitario_Sanitizado"],
        0.0,
    )

    return df_clean
