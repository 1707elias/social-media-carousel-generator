# Codex Task Spec: Clean Portfolio Refactor — Social Media Carousel Generator

Ziel: Dieses Repo soll als **Portfolio-Projekt** „richtig clean“ werden:
- saubere Architektur (Modularisierung statt God-Module)
- modernes Packaging (`src/` Layout, `pyproject.toml`)
- CLI (`python -m socialgen ...`)
- Konfigurations-Validation (klare Fehlermeldungen)
- Tests (pytest)
- Linting/Formatting (ruff; optional mypy)
- deterministische Builds (Seed)

> Wichtig: Funktionalität bleibt erhalten. Outputs sollen sich nicht ändern, außer bewusst dokumentierte Fixes.

---

## Ausgangslage
- Einstieg: `main.py` lädt globale Config + Modul-Configs und ruft `generator.create_socialmedia_carousel`.
- Rendering: `generator/generator.py` enthält Config-Parsing, Layout, Text, Assets, Background, Saving.
- Fingerprint: `generator/fingerprint.py` erzeugt einen Hintergrund (Mask + Overlay).
- Configs: `config/config.json` + `config/<module>.json` (siehe `config/README.md`)
- Assets: `assets/` inkl. Palette/Fonts/Bilder.
- Dependencies: Pillow, pyphen.

---

## Zielstruktur (Endzustand)

```text
.
├── pyproject.toml
├── README.md
├── CODEX_CLEAN_REFACTOR.md
├── src/
│   └── socialgen/
│       ├── __init__.py
│       ├── cli.py
│       ├── config/
│       │   ├── models.py
│       │   └── loader.py
│       ├── render/
│       │   ├── renderer.py
│       │   ├── layout.py
│       │   ├── text.py
│       │   └── assets.py
│       ├── fingerprint/
│       │   └── generator.py
│       └── utils/
│           └── paths.py
└── tests/
    ├── test_config_validation.py
    ├── test_text_wrap.py
    ├── test_fingerprint_mask.py
    └── test_cli_smoke.py