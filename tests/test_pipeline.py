from pathlib import Path

from src.pipeline import run_sanitization_pipeline


def test_pipeline_execution_with_real_dataset(tmp_path: Path):
    repo_root = Path(__file__).resolve().parent.parent
    raw_excel = repo_root / "vendas_pfizer_dados_brutos.xlsx"

    assert raw_excel.exists(), "vendas_pfizer_dados_brutos.xlsx should exist in repository"

    summary = run_sanitization_pipeline(raw_excel, output_dir=tmp_path)

    assert summary["total_records"] > 0
    assert summary["valid_records"] > 0
    assert summary["total_validated_revenue"] > 0.0

    out_xlsx = tmp_path / "vendas_pfizer_dados_tratados_v2.xlsx"
    out_csv = tmp_path / "vendas_pfizer_dados_tratados_v2.csv"

    assert out_xlsx.exists()
    assert out_csv.exists()
