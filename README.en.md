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

## Usage Examples

### List all datasets

```bash
python3 main.py list-datasets
```

### List articles in a dataset

```bash
python3 main.py list-collections --dataset-id 697b19a113081cf58b45cac3
```

### Search in a knowledge base

```bash
python3 main.py search --dataset-id 697b19a113081cf58b45cac3 --query "KRAS mutation"
```

### Upload a single file

```bash
python3 main.py upload-file --file article.md --dataset-id 697b19a113081cf58b45cac3
```

### Batch upload a folder

```bash
python3 main.py upload-folder --folder ./articles --dataset-id 697b19a113081cf58b45cac3
```

### Download WeChat articles

Create a `urls.txt` file with one WeChat article URL per line, then:

```bash
python3 main.py download-wechat --urls urls.txt --output ./wechat-downloads
```

### Clean WeChat articles

```bash
python3 main.py clean-wechat --input ./wechat-downloads --output ./cleaned-articles
```

### One-stop workflow (download → clean → upload)

```bash
python3 main.py download-and-clean \
  --urls urls.txt \
  --output ./wechat-downloads \
  --cleaned-output ./cleaned-articles \
  --dataset-id 697b19a113081cf58b45cac3
```

## Project Structure

```
fastgpt-content-processor/
├── main.py                      # CLI entry point
├── fastgpt_sync.py              # FastGPT API wrapper
├── fetchers/                    # Content fetchers
│   ├── wechat_mcp.py           # WeChat article downloader (MCP)
│   └── file.py                 # Local file reader
├── cleaners/                    # Content cleaners
│   ├── format_cleaner.py       # Stage 1: format cleanup
│   ├── frontmatter_doctor.py   # Stage 2: frontmatter normalization
│   ├── wechat_markdown.py      # WeChat Markdown cleaner (combined)
│   └── markdown.py             # General Markdown cleaner
├── utils/                       # Utilities
│   ├── hash.py                 # Hash calculation
│   └── dedup.py                # Deduplication logic
├── tests/                       # Test directory
├── .env.example                 # Environment variable template
├── requirements.txt             # Python dependencies
└── README.md                    # This document
```

## Testing

See [`tests/README.md`](tests/README.md) for the initial test scope and suggested themes.

```bash
python3 -m pytest
```

Core logic tests only:

```bash
python3 -m pytest tests/test_core_logic.py
```

## Roadmap

### Short-term: Reproducibility & Verification
- Unify `python3` usage and virtual environment documentation
- Add core logic tests
- Clarify boundaries for FastGPT, MCP, and example scripts
- Improve documentation consistency

### Mid-term: Maintainability & Collaboration
- Unify cleanup pipeline, reduce duplicate implementations
- Optimize CLI parameters and interactive experience
- Add dry-run / preview mode
- Add finer-grained logging and statistics
- Add test data and regression samples

### Long-term: Extensibility & Platform-ization
- Plugin-based fetchers / cleaners / upload adapters
- Support more content sources
- Support more knowledge base targets and export formats
- Workflow-based processing pipelines
- Configurable rules and batch job orchestration

## Contributing

Contributions of code, documentation, tests, and usage experience are welcome.

### Recommended practices
- Open an issue first to describe the requirement or problem
- Add tests before changing logic
- Keep documentation in sync with code
- Provide sample input/output when adding new cleanup rules
- Describe the applicable scenario when adding new fetchers or upload adapters

### Areas to contribute
- New content cleanup rules
- New data source fetchers
- FastGPT API adapter enhancements
- CLI experience improvements
- Test coverage improvements
- Examples and tutorials

## Acknowledgements

Thanks to the following projects and resources for inspiration and reference:

- [wechat-article-downloader](https://github.com/qiye45/wechatDownload)
- [baoyu-format-markdown](https://github.com/baoyu-tech/markdown-formatter)
- [markdown-frontmatter-doctor](https://github.com/example/frontmatter-doctor)
- [FastGPT API Documentation](https://doc.fastgpt.in/docs/development/api/)

## License

MIT License

---

**Other languages**: [中文](README.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [한국어](README.ko.md)
