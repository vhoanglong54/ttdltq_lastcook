$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot

python scripts/download_data.py --include-history --skip-ipeds
python scripts/build_dataset.py
python scripts/run_eda.py
python scripts/train_model.py --prefer-temporal
python -m pytest -q
python scripts/build_report.py

Write-Host "Pipeline completed. Start dashboard with: streamlit run dashboard/app.py"
