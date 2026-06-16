# Tests

This directory contains focused tests for the project's local logic.

## Scope

The initial test set focuses on the most stable and important parts of the codebase:

- `utils/hash.py`
- `utils/dedup.py`
- `cleaners/format_cleaner.py`
- `cleaners/frontmatter_doctor.py`
- `cleaners/markdown.py`
- `cleaners/text.py`
- `cleaners/wechat_article.py`

## What these tests try to protect

- content normalization does not accidentally remove valid content
- frontmatter is standardized consistently
- URL extraction continues to work
- duplicate detection remains stable
- file hashing is deterministic
- HTML/Markdown cleaning stays safe for common inputs

## Suggested future test themes

- CLI argument parsing and help output
- FastGPT API wrapper with mocked HTTP responses
- MCP downloader with mocked remote responses
- file scanning and extension filtering
- error-path coverage for malformed input
- regression tests for newly added cleaner rules

## Run

```bash
python3 -m pytest
```

To run only the core logic set:

```bash
python3 -m pytest tests/test_core_logic.py
```
