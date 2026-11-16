PY ?= python

.PHONY: setup data prepare index eval examples app test

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

test:
	$(PY) -m pytest -q
