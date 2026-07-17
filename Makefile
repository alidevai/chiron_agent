# Chiron gelistirme orkestrasyonu (sigstore-python / pip-audit desenine yakin).
# Windows'ta `make` yoksa asagidaki komutlari dogrudan calistirabilirsiniz.
.PHONY: install lint test cov security audit verify all clean

install:
	pip install -e .[dev]

lint:            ## ruff (lint) + bandit (guvenlik lint)
	ruff check core tests scripts
	bandit -c pyproject.toml -r core -q

fmt:             ## ruff ile otomatik duzelt + bicimlendir
	ruff check --fix core tests scripts
	ruff format core tests scripts

test:
	python -m pytest

cov:             ## coverage + esik (fail-under pyproject'te)
	python -m coverage run -m pytest
	python -m coverage report

security:        ## kendi kaynagimizin guvenlik lint'i
	bandit -c pyproject.toml -r core

audit:           ## bagimlilik CVE denetimi
	pip-audit -r requirements.txt

verify:          ## platform butunlugu (audit zinciri + politika muhru)
	python -m core verify

all: lint cov audit verify   ## PR oncesi tam kapi
