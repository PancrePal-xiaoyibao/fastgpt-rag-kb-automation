# FastGPT Content Processor

A command-line tool for managing and processing FastGPT knowledge base content, including knowledge base queries, content search, file uploads, and WeChat article download/cleanup/upload workflows.

## Features

- **list-datasets**: list all FastGPT datasets
- **list-collections**: list articles/collections in a dataset
- **search**: semantic search inside a knowledge base
- **upload-file**: upload a single Markdown file
- **upload-folder**: batch upload Markdown files from a folder
- **download-wechat**: batch download WeChat articles via MCP
- **clean-wechat**: two-stage WeChat Markdown cleanup
- **download-and-clean**: one-stop workflow: download → clean → upload

## Installation and Usage

### Recommended: uv

```bash
cd fastgpt-content-processor
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
```

### Alternative: standard venv

```bash
cd fastgpt-content-processor
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
```

### Run commands

```bash
python3 main.py --help
python3 main.py list-datasets
python3 main.py search --dataset-id 697b19a113081cf58b45cac3 --query "KRAS mutation"
```

## Testing

See [`tests/README.md`](tests/README.md) for the initial test scope and suggested themes.

## Roadmap

See the roadmap section in the localized README files for contribution directions and future plans.
