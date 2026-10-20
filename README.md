# Docs Link Auditor

Audit a local Markdown documentation tree for missing files, broken relative links, repeated-heading anchors and missing heading anchors, with JSON output and meaningful exit codes.

## Quick start

```sh
python audit.py sample/docs --json report.json
# Exit 0: clean; 1: broken links; 2: input/configuration error.
```

## Tests

`python -m unittest discover -s tests -v`

## Scope and limitations

Deliberately supports ordinary inline Markdown links/images, ATX headings and fenced code blocks, not full CommonMark/reference-link/HTML parsing. External http/https/mailto/tel links are skipped, never fetched. Paths cannot escape the chosen root, including symlinks. Unicode headings supported; anchor algorithm is documented in source and may differ from other renderers.

## Attribution and sample data

Built for Raj's portfolio with Wabi AI assistance. Sample data is invented and labelled synthetic; no real customer, employer or private account records are included. This is a learning/portfolio implementation, not a claim of commercial work or production deployment.

See source and tests for implementation decisions. Use invented data when exploring.

## How it works

Local Markdown tree → fenced-code-aware inline link extraction → bounded filesystem target + heading resolution → JSON result and exit code. External links never trigger network requests.

## Verified example

Included synthetic docs pass; separately created missing.md target returns exit1. Path escape, fenced code and duplicate-heading anchors are tested.

See [VALIDATION.md](VALIDATION.md) for tested environments and scope.
