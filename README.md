# Cheatsheet Maker

[Repository](https://github.com/VllyVlly/Cheatsheet-Maker) · Package version **0.1.0** · Work in progress

A Python package that turns PDF, DOCX, and PPTX lecture materials into a condensed
LaTeX cheatsheet, with optional PDF compilation. Run it in your own Python
project, Jupyter notebook, or Google Colab runtime using your own Gemini API key.

Importing the package does not start a web server, load Docling models, read a
`.env` file, or make API requests. Document parsing loads models only when needed.
Generation sends extracted content and your custom prompts to Gemini.

## Current features

- Combine PDF, DOCX, and PPTX materials into one cheatsheet.
- Use the Python API, command line, or example Colab notebook.
- Parse documents without a Gemini key and reuse the extracted Markdown later.
- Configure layout, custom prompts, model, OCR, and accelerator selection.
- Download LaTeX source, with optional PDF compilation through Tectonic.
- Run the optional React/Vite frontend with the local Flask backend.

## Install from a clone

Requires Python 3.10 or newer and Git. Clone the repository, then install from its
root directory. A separate Python virtual environment is recommended for local use.

```bash
git clone https://github.com/VllyVlly/Cheatsheet-Maker.git
cd Cheatsheet-Maker
python -m pip install -e .
```

This installs the Python package and its direct dependencies. It does not install
Flask or the React frontend. For the optional web application:

```bash
python -m pip install -e ".[web]"
```

To use the Python package without keeping an editable clone, install directly
from GitHub:

```bash
python -m pip install "git+https://github.com/VllyVlly/Cheatsheet-Maker.git"
```

For reproducible shared notebooks, pin that Git URL to a release tag or commit.
The package uses automatic accelerator selection by default. It does not pin a
particular CUDA build of PyTorch; check that your runtime has working GPU support
if you choose `device="cuda"` explicitly.

PDF compilation additionally requires the **Tectonic executable** on `PATH`.
Follow the [official installation guide](https://tectonic-typesetting.github.io/en-US/install.html).
Use `compile_pdf=False` when you only need LaTeX or Tectonic is unavailable.
The package never downloads or installs an executable automatically.

## Python API

Set `GEMINI_API_KEY` in your environment, or pass your own key explicitly from a
secret store. Never put a real key in source code or notebook cells.

For an interactive Python session, you can enter a key without embedding its
value in your code:

```python
import os
from getpass import getpass

os.environ["GEMINI_API_KEY"] = getpass("Your Gemini API key: ")
```

In Colab, use Colab Secrets as shown in the example notebook. `.env.example`
contains only a placeholder; the package does not load `.env` automatically.

```python
from cheatsheet_maker import CheatsheetMaker, FormatSettings

with CheatsheetMaker(device="auto") as maker:
    result = maker.generate(
        files=["lecture.pdf", "notes.docx", "slides.pptx"],
        settings=FormatSettings(
            columns=3,
            font_size="footnotesize",
            margin="1cm",
            orientation="landscape",
        ),
        output_dir="output",
        extra_classifier="Focus on definitions and formulas.",
        extra_summarizer="Keep explanations short.",
        compile_pdf=False,
    )

print(result.tex_path)
# result.pdf_path is None when compilation is disabled.
```

`generate()` accepts a single path, an iterable of paths, a mapping of filenames
to bytes (including `google.colab.files.upload()` results), or a list of
`(filename, bytes)` pairs. It creates **one combined cheatsheet** in input order.
Limits are 10 files, 25 MB per file, and 100 MB total. Unreadable documents cause
an error naming the file; no document is silently skipped.

The result exposes:

| Field | Value |
| --- | --- |
| `tex_path` | Path to the generated LaTeX source |
| `pdf_path` | Path to the PDF, or `None` when compilation is disabled |
| `markdown` | Combined extracted text with source-file headings |
| `items` | Summarized structured items used to assemble the cheatsheet |

Set `compile_pdf=True` to produce both source and PDF when Tectonic is installed.
Default output names are unique. Set `output_name`
to a plain name such as `algebra_review` when you want a predictable filename;
using an existing name replaces its output files. Paths and extensions are not
accepted as output names. Use `output_dir` to choose the destination.

Constructor options:

| Option | Default | Purpose |
| --- | --- | --- |
| `api_key` | `GEMINI_API_KEY` when needed | Your key; never bundled with the package |
| `client` | Created lazily | Optional Gemini client you manage yourself |
| `model` | `gemini-3.6-flash` | Select a Gemini model available to your account |
| `device` | `auto` | `auto`, `cpu`, `cuda`, or `mps` |
| `ocr` | `True` | Enable OCR for scanned pages |
| `formula_enrichment` | `True` | Enable Docling formula extraction |
| `compile_timeout` | `120` | Maximum compilation time in seconds |

Use one maker instance for repeated notebook calls to reuse its converters.
Instances are intended for sequential use, not concurrent worker threads.
The context manager closes clients created by the maker. Supplied clients remain
owned by the caller.

## Parse without an API key

```python
from pathlib import Path
from cheatsheet_maker import CheatsheetMaker

maker = CheatsheetMaker(device="auto")
markdown = maker.parse(["lecture.pdf", "notes.docx"])
Path("parsed_notes.md").write_text(markdown, encoding="utf-8")
```

Parsing does not call Gemini and does not require a key. Ordinary PDF text is
extracted with PyMuPDF. Math-heavy or scanned pages use Docling; DOCX and PPTX use
Docling directly. Docling may download its model weights on first use.

To change prompts or formatting without parsing the original files again:

```python
from pathlib import Path
from cheatsheet_maker import CheatsheetMaker, FormatSettings

markdown = Path("parsed_notes.md").read_text(encoding="utf-8")
with CheatsheetMaker() as maker:
    result = maker.generate_from_markdown(
        markdown,
        settings=FormatSettings(columns=4),
        compile_pdf=False,
    )
```

This still makes Gemini calls. There is no automatic persistent cache of parsed
content or model responses; saving and reusing Markdown is explicit.

## Google Colab

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/VllyVlly/Cheatsheet-Maker/blob/main/examples/colab_quickstart.ipynb)

Open [examples/colab_quickstart.ipynb](examples/colab_quickstart.ipynb) in Colab.
The notebook includes clone/install, credentials, multi-file upload, extraction,
generation, and download cells. It clones this repository into
`/content/cheatsheet-maker` and installs the package there.

1. Choose a GPU runtime if needed; `device="auto"` also works on CPU runtimes.
2. Install the package using the notebook's setup cells.
3. Add your own `GEMINI_API_KEY` through Colab Secrets and enable notebook access.
4. Upload your materials and run extraction and generation.

The notebook defaults to LaTeX output and does not automatically install Tectonic.
For PDF output, install Tectonic from its official distribution, then set
`compile_pdf=True` in the generation cell. The package does not need Google Drive
access; download generated files before your temporary runtime is deleted.

## Command line

```bash
cheatsheet-maker lecture.pdf notes.docx slides.pptx --columns 3 --no-pdf
python -m cheatsheet_maker lecture.pdf --device cpu --no-pdf
```

From a clone, `python main.py lecture.pdf --no-pdf` also works. Use
`cheatsheet-maker --help` for options. The CLI reads `GEMINI_API_KEY`; there is no
command-line key option that could put credentials in shell history.

Omit `--no-pdf` to also compile a PDF with Tectonic. Options include `--model`,
`--device`, `--columns`, `--output-dir`, and `--output-name`.

## Optional Flask and React application

Requires Node.js and npm in addition to the Python setup. From the repository
root, install `python -m pip install -e ".[web]"`, configure
`GEMINI_API_KEY` in the server environment, and install Tectonic. Start Flask:

```bash
python -m backend.app
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Flask binds to `127.0.0.1` with debugging disabled. This is a local development
application, not an authenticated or hardened public service. Vite proxies
`/api` to Flask at `http://127.0.0.1:5000`.

`POST /api/generate` accepts multipart `files`, JSON `settings`,
`classifier_prompt`, and `summarizer_prompt`; legacy `file` and `/generate` are
also accepted. Responses contain `pdf_url` and `tex_url`. The adapter calls the
same Python package. Progress is general activity because processing is synchronous.

Unlike the package's LaTeX-only mode, the web application always requests PDF
generation and therefore requires Tectonic. Generated files remain in `output/`
until you remove them. The web application has no user accounts, rate limiting,
or automatic output cleanup and should remain local.

## How it works

1. Parse the selected documents and combine their text with source headings.
2. Gemini classifies definitions, theorems, formulas, explanations, and examples.
3. Gemini shortens prose while being instructed to preserve math and theorems.
4. Python assembles the LaTeX deterministically.
5. Optionally compile with Tectonic in untrusted mode and with a timeout.

Math preservation depends on extraction and model quality. Review the output
before use. A one-page result is the intended use, not an enforced page limit.
GPU acceleration does not speed up remote Gemini calls or LaTeX compilation.
Large documents may exceed the selected model's context or quota limits. Parsing
is sequential; multiple-file support does not mean files are processed in parallel.
Live GPU parsing, Colab execution, Gemini generation, and Tectonic compilation
have not yet been verified end to end as part of this version's automated checks.

## Project structure

```text
cheatsheet_maker/         # Installable Python package
    __init__.py          # Public API exports
    maker.py             # Parse/generate interface and result object
    inputs.py            # Input normalization and upload limits
    settings.py          # Validated formatting settings
    errors.py            # Document parsing exception
    cli.py               # Installed command-line interface
    parsing/             # PyMuPDF/Docling extraction and Gemini calls
    latex/               # Deterministic LaTeX assembly and compilation
backend/                 # Optional Flask app and package adapter
frontend/                # Optional React/Vite app
examples/                # Colab starter notebook
tests/                   # Public package tests
parsing/, latex/         # Legacy import wrappers and parser tests
pyproject.toml           # Package metadata, dependencies, and CLI entry point
MANIFEST.in              # Source-distribution inclusion/exclusion rules
SECURITY.md              # Credentials, document privacy, and deployment notes
```

## Safety and sharing

Read [SECURITY.md](SECURITY.md) before sharing a notebook or deploying the web app.
Users provide their own credentials and compute. No credentials, documents,
frontend files, or Flask application are included in the built Python package.
Tectonic untrusted mode is additional protection, not an operating-system sandbox.
Environment files, local `inputs/` and `secrets/` directories, logs, private-key
files, and generated outputs are ignored by Git. Ignore rules do not remove files
already tracked or erase sensitive data from earlier commits. Review the actual
Git changes and build archives before sharing them.

## Development and validation

```bash
python -m pip install -e ".[web,dev]"
python -m unittest tests.test_package backend.test_app backend.test_pipeline parsing.test_parser
python -m build
```

For frontend checks, from `frontend/`:

```bash
npm test
npm run build
```

The automated tests mock Docling extraction, Gemini requests, and compilation;
they do not exercise a real GPU or spend API quota. Inspect build archives before
sharing a release. Core code lives under `cheatsheet_maker/`; the original
`parsing/` and `latex/` imports remain as compatibility wrappers in a clone.

## License

No license has been selected yet. A license will be added once the project owner
has decided on the terms for use and distribution.
