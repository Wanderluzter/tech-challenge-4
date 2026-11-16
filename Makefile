PY ?= python

.PHONY: setup data prepare index eval examples app web web-dev api test

setup:
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e .

data:
	$(PY) scripts/download_data.py

prepare:
	$(PY) -m voc_rag.cli prepare

index:
	$(PY) -m voc_rag.cli index

eval:
	$(PY) -m voc_rag.cli eval --write --e2e

examples:
	$(PY) -m voc_rag.cli examples

app:
	streamlit run app/streamlit_app.py

# Interface React: constrói web/dist e serve interface + API em http://localhost:8000
web:
	cd web && npm install && npm run build
	$(PY) -m uvicorn voc_rag.api:app --port 8000

# Desenvolvimento do frontend com recarga automática (rode `make api` em outro terminal)
web-dev:
	cd web && npm run dev

api:
	$(PY) -m uvicorn voc_rag.api:app --port 8000 --reload

test:
	$(PY) -m pytest -q
