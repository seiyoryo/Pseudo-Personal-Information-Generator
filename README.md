# Pseudo-Personal-Information-Generator

[English](README.md) | [日本語](README.ja.md)

This is a small Flask web app that generates Japanese pseudo personal information and supports distribution-aware data augmentation.

## Key features

- **New data generation**: create a synthetic customer-like CSV with configurable columns and row count.
- **Distribution copy**: generate new datasets that mimic the age / blood type / gender distributions of the original dataset.
- **Mixture distribution**: create a new dataset by mixing multiple previously generated datasets with weights.
- **CSV extension**: upload a base CSV and generate additional rows by inferring column-wise generation algorithms.
- **History tree**: visualize lineage when datasets are produced via mixture.
- **Downloads**: download generated CSVs from the UI.

## Architecture overview

- `app/main.py`: Flask entrypoint (run `python app/main.py`).
- `app/routes.py`: web layer (routing + request/response).
- `app/services.py`: application layer (use-case orchestration).
- `domain/*`: business logic (generation, distribution, statistics, extension).

### State & persistence

The app writes state and outputs to the local working directory:

- `state/*.json`: current UI parameters + archived distribution summaries/lineage metadata.
- `outputs/df/*.csv`: generated CSV outputs (created dummy, copied dummy, extended data).
- `outputs/figure/**`: generated plots (age/blood/gender distribution images).

These are **local artifacts** generated at runtime and are intentionally ignored by Git.

## Quick start

```bash
git clone https://github.com/seiyoryo/Pseudo-Personal-Information-Generator.git
cd Pseudo-Personal-Information-Generator
pip install -r requirements.txt
python app/main.py
```

Open `http://127.0.0.1:5000/` in your browser.

Tip: you can also use `make setup` and `make run` (see `Makefile`).

## Data files (required)

This project expects CSV master data under `data/`:

- `first_name_sorted.csv` (first names + kana + gender + romanized)
- `last_name.csv` (last names + kana + romanized)
- `KEN_ALL2.csv` (Japan postal code and address master)
- `compony_data.csv` (company names)

This repository should **not** include secrets or real personal data. Prepare these CSVs locally.

## Design decisions / trade-offs

- **JSON persistence for UI state**: simple, file-based state (`input/*.json`) keeps the app dependency-light.
- **Distribution copy approach**: uses cumulative distributions + sampling for a controllable similarity mechanism.
- **Single-process Flask app**: easy local setup; not optimized for multi-user concurrency.

## Limitations & future improvements

- **Input validation**: user-provided parameters and uploaded CSV schemas could be validated more strictly.
- **Tests**: add unit tests for core generation and distribution-copy behavior.
- **Configuration**: move hard-coded paths and parameters into config/env.

## Security notes

- Do **not** commit private keys, tokens, or `.env` files.
- Generated artifacts (CSV outputs and plot images) are produced locally at runtime.

## Docs

- Architecture walkthrough and flow diagrams: `docs/module-responsibility-matrix.md`
