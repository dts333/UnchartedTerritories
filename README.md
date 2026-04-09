# Brunelleschi's Dome Explorer

Small Python/Cairo project that renders Brunelleschi's dome and builds a static interactive explorer.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Build

```bash
.venv/bin/python dome.py
```

This writes the interactive site to `output/interactive/index.html`.

## Test

```bash
.venv/bin/pytest -q
```
