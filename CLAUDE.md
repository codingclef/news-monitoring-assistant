# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
streamlit run app.py
```

Runs on `http://localhost:8501`. No build step required.

## Required Secrets

Set via Streamlit Cloud Secrets or a local `.streamlit/secrets.toml` (gitignored):

```toml
OPENAI_API_KEY = "..."
NAVER_CLIENT_ID = "..."
NAVER_CLIENT_SECRET = "..."
APP_PASSWORD = "..."          # optional
GOOGLE_SHEET_ID = "..."

[gcp_service_account]
# Google service account JSON fields
```

The app falls back to environment variables if secrets are unavailable.

## Architecture

Single-file Streamlit app (`app.py`) that orchestrates three steps after the user clicks 모니터링 시작:

1. **Article collection** — `modules/naver_search.py` (Naver Search API, up to 1,000/keyword) and `modules/daum_search.py` (Daum HTML scraping, ~200–300/keyword). Results are deduplicated by URL with keyword merging, then sorted by search engine → datetime ascending.

2. **GPT classification** — `modules/classifier.py` calls `gpt-4o-mini` per article. Categories are user-defined; `보류` = borderline/ambiguous; `해당없음` = clearly irrelevant. Previous user corrections stored in Google Sheets are injected as few-shot examples.

3. **Excel generation** — `modules/excel_writer.py` builds an `.xlsx` with sheets: `일람` (all), user-defined categories, `보류`, `해당없음`.

## Key Module Responsibilities

| Module | Role |
|--------|------|
| `modules/i18n.py` | All UI strings as `KO` / `JA` dicts; `get_strings(lang)` returns the active dict. Every user-visible string must go here — never hardcode in `app.py`. |
| `modules/sheets.py` | Google Sheets for presets (`["프리셋명","키워드","분류기준","설정"]`) and feedback (`["기사제목","올바른분류"]`). |
| `modules/file_parser.py` | Extracts keywords/categories from `.docx` files via GPT (currently unused in main UI flow). |

## Session State Conventions

- Widget state is keyed: `keywords_input`, `start_time_input`, `end_time_input`, `use_naver`, `use_daum`, `preset_name_input`, `cat_name_{id}`, `cat_cond_{id}`, `cat_ids`, `cat_counter`.
- Results stored in: `classified`, `categories_state`, `excel_bytes`, `result_summary`, `result_lang`, `run_id`.
- Validation errors: `val_errors` (a `set` of string keys like `"keywords"`, `"engines"`, `"password"`).

## i18n Pattern

```python
S = get_strings(lang)   # lang = "ko" or "ja"
S["some_key"]           # use everywhere in app.py
```

When adding new UI text, add entries to **both** `KO` and `JA` dicts in `modules/i18n.py`. The Excel column names and sheet names are also i18n'd — `_CAT_HOLDUP = "보류"` and `_CAT_NA = "해당없음"` in `excel_writer.py` are fixed Korean constants used for data filtering (not display).

## Git Workflow

Always pull before pushing:
```bash
git pull origin main --no-rebase --no-edit && git push
```

Commit messages in English. Each logical change gets its own commit.
