"""Dataset loaders for APL benchmark campaigns.

Each loader module here implements a deterministic, dry-run-safe
ingestion path for one campaign's pinned dataset shape. Loaders do
not fetch live external data, do not promote claims, and do not
compute baseline residuals; they only read normalized YAML and emit
row-count summaries with explicit inclusion/exclusion accounting.
"""

from __future__ import annotations
