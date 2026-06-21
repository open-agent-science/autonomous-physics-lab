# Extraction Notes

The source is an ASCII table with comment lines beginning with `#` and five
whitespace-delimited columns:

1. native spectral axis in `cm^-1`;
2. absolute monopole intensity in `MJy/sr`;
3. residual monopole spectrum in `kJy/sr`;
4. one-sigma uncertainty in `kJy/sr`;
5. modeled Galactic spectrum at the Galactic poles in `kJy/sr`.

`scripts/normalize_firas_monopole_source.py` verifies the exact SHA-256 before
parsing and requires exactly five columns and 43 rows. It records the NASA
constructed absolute intensity as `source_derived_absolute`; source values are
not recomputed.
