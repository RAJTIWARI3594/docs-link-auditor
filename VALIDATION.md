# Validation

14 Python test cases passed on CPython3.10.21 and3.14.7 on Linux.

Test command: `python -m unittest discover -s tests -v`

Included synthetic docs pass; separately created missing.md target returns exit1. Path escape, fenced code and duplicate-heading anchors are tested.

Tests are a bounded check, not a production/security certification. Browser checks used Linux Chromium, not physical phones or Safari/Firefox. Local data is unencrypted. All examples are synthetic; screenshots show actual running output, not design mockups.
