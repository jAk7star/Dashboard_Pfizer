# Pharmaceutical Supply Chain & Sales Analytics Engine
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements-dev.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . .

# Run validation tests and execute pipeline
CMD ["sh", "-c", "pytest -v && python -m src.pipeline"]
