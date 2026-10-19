# Security and responsible use

## Distribution model

This repository provides a Python library that users run in their own environment
with their own files, credentials, and compute. Installing or importing it does
not start Flask, expose a network port, install executables, or initialize models.
The optional Flask frontend/backend is a separate local development application.
Its default bind address is loopback, debugging is disabled, and CORS allows only
the local Vite frontend origins. CORS is not authentication or a network firewall.
Do not expose it through a tunnel, router forwarding, or a public host without
adding authentication, authorization, rate limits, worker isolation, and cleanup.

## Credentials

- Use environment variables, Colab Secrets, or a secret manager. The package does
  not load `.env` files automatically; `.env.example` contains a placeholder only.
- Never commit real keys, credential files, private documents, or notebook outputs
  that contain them. Ignoring files does not remove existing commits or history.
- Every notebook user supplies their own Gemini key. No shared developer key is
  provided or required. Do not place a Gemini key in React or `VITE_*` variables.
- Rotate exposed keys and review provider usage. Configure appropriate restrictions,
  quotas, and billing alerts; an alert alone is not a spending cap.
- Report suspected problems through a private contact channel chosen by the
  repository owner. Do not post secrets or private documents in public issues.

## Documents and model output

Parsing runs locally in the user's runtime. Docling may download model weights.
Generation sends extracted text and custom prompts to Google's Gemini API.
Obtain permission to process documents and check the provider's applicable data
handling terms. Generated Markdown, items, PDF, and LaTeX may contain private
information; keep outputs private and remove them when no longer needed.

File count and size limits are enforced, but document parsers and native libraries
still process untrusted input. Keep dependencies updated and use a disposable,
isolated runtime when processing files from strangers. A Python virtual environment
is dependency isolation, not a filesystem or process security boundary.

LaTeX compilation uses a fixed argument list, a timeout, Tectonic untrusted mode,
and a limited child-process environment without Gemini or Google application
credentials. These controls do not make arbitrary LaTeX fully safe. Do not give
an untrusted compilation worker access to personal folders or secrets. Install
Tectonic from its official distribution; it may download TeX support files.

## Before sharing a release

Build archives contain only the `cheatsheet_maker` package and selected metadata.
Packaging has an explicit package allowlist and excludes environment files,
bytecode, notebooks, user documents, outputs, and the web application. Review the
actual wheel/source archive, Git changes, and notebook outputs before publishing.
These exclusions are not a substitute for checking source code for embedded keys.
No package publication, Git push, or service deployment is performed by the code.
