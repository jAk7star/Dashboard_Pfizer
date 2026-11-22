"""CLI Execution pipeline for Pharma Data Sanitizer."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from src.sanitizer import process_pharma_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("pharma-sanitizer-pipeline")


def run_sanitization_pipeline(
    input_path: str | Path, output_dir: str | Path | None = None
) -> dict[str, Any]:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input data file does not exist: {input_file}")

    target_dir = Path(output_dir) if output_dir else input_file.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Reading pharmaceutical dataset from: %s", input_file)
    if input_file.suffix.lower() == ".csv":
        df_raw = pd.read_csv(input_file, sep=None, engine="python")
    else:
        df_raw = pd.read_excel(input_file)

    logger.info("Executing data quality rules and lineage tracking across %d rows...", len(df_raw))
    df_clean = process_pharma_dataframe(df_raw)

    out_xlsx = target_dir / "vendas_pfizer_dados_tratados_v2.xlsx"
    out_csv = target_dir / "vendas_pfizer_dados_tratados_v2.csv"

    logger.info("Exporting audit Excel to: %s", out_xlsx)
    df_clean.to_excel(out_xlsx, index=False)

    logger.info("Exporting client-side dashboard CSV to: %s", out_csv)
    df_clean.to_csv(out_csv, index=False, encoding="utf-8-sig", sep=";")

    valid_mask = df_clean["Status_Validacao"] == "Válido"
    total_revenue = float(df_clean.loc[valid_mask, "Faturamento_Sanitizado"].sum())

    stats = {
        "total_records": len(df_clean),
        "valid_records": int(valid_mask.sum()),
        "invalid_records": int((~valid_mask).sum()),
        "validation_pass_rate": f"{(valid_mask.mean() * 100):.1f}%",
        "total_validated_revenue": round(total_revenue, 2),
        "output_xlsx": str(out_xlsx),
        "output_csv": str(out_csv),
    }

    logger.info("Pipeline completed successfully! Summary: %s", stats)
    return stats


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    default_input = repo_root / "vendas_pfizer_dados_brutos.xlsx"

    parser = argparse.ArgumentParser(
        description="Pharmaceutical Supply Chain & Sales Sanitization Engine"
    )
    parser.add_argument(
        "--input",
        "-i",
        default=str(default_input) if default_input.exists() else "vendas_pfizer_dados_brutos.xlsx",
        help="Path to raw Excel (.xlsx) or CSV data file.",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=str(repo_root),
        help="Target output directory for sanitized files.",
    )

    args = parser.parse_args()
    run_sanitization_pipeline(args.input, args.output_dir)


if __name__ == "__main__":
    main()
