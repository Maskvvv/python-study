# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python learning/study repository containing progressive examples covering:
- Basic Python syntax (numbered files: `1.print.py` through `21.分布式进程.py`)
- TCP network programming (`24. TCP/`)
- Flask web framework (`25. flask/`)
- Django web framework (`26. django/`)

## Development Environment

**Package Manager:** [uv](https://docs.astral.sh/uv/) (modern Python package manager)
- Dependencies are defined in `pyproject.toml`
- Lock file: `uv.lock`
- Python version: 3.13 (specified in `.python-version`)

**Key Dependencies:**
- `django>=6.0.3`
- `flask>=3.1.3`
- `psutil>=7.2.2`
- `requests>=2.33.1`

## Common Commands

**Install dependencies:**
```bash
uv sync
```

**Run a Python file:**
```bash
uv run python <filename>.py
```

**Add a new dependency:**
```bash
uv add <package-name>
```

**Run Flask examples:**
```bash
# Each Flask example runs on a different port
uv run python "25. flask/01_hello.py"      # Port 5000
uv run python "25. flask/02_routes.py"     # Port 5001
uv run python "25. flask/03_templates.py"  # Port 5002
uv run python "25. flask/00_index.py"      # Port 5555 (index page)
```

**Run TCP examples:**
```bash
# Terminal 1 - Start server
uv run python "24. TCP/tcp_server.py"

# Terminal 2 - Run client
uv run python "24. TCP/tcp_client.py"
```

## Code Organization

**Numbered files (root directory):** Sequential learning files covering Python fundamentals:
- Files 1-13: Basic syntax, data structures, functional programming
- Files 14-21: Advanced topics (metaclasses, error handling, file I/O, multiprocessing/threading)

**Directory naming convention:** `数字. 主题` (Number. Topic in Chinese)
- `24. TCP/`: TCP socket programming examples (client/server pairs)
- `25. flask/`: Flask web framework examples with templates
- `26. django/`: Django learning notes as executable Python files with docstrings

**Django learning files structure:**
Files follow a progressive learning path (01-15):
- `00_learning_roadmap.py`: Overview and study guide
- `01_django_basics.py` through `03_models.py`: Phase 1 (Fundamentals)
- `04_templates.py` through `06_authentication.py`: Phase 2 (Core features)
- `07_admin.py` through `09_static_media.py`: Phase 3 (Advanced features)
- `10_caching.py` through `12_deployment.py`: Phase 4-5 (Performance & Deployment)
- `13_drf.py` through `15_third_party_packages.py`: Phase 6 (Advanced applications)

## Notes

- Django examples in `26. django/` are learning notes stored as Python files with extensive Chinese docstrings, not runnable Django projects
- Flask examples in `25. flask/` are runnable standalone applications
- TCP examples include both simple and chat implementations
