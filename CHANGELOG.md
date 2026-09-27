## Unreleased

- Add structural `MarcDto.validate()` record validation.
- Preserve the MARC leader in ISO 2709 and MARCXML round trips.
- Add partial MARC 21 to BIBFRAME 2 resource-type mappings via
  `bibframe_types_for()`.
- Fix MARCXML serialization of MARC attributes and reject silently discarded
  subfields.

## 0.6.0 (2025-11-03)

- Performance: add fast tag->definition map in `MarcDictionary` for O(1) lookups.
- API: add convenience helpers to `MarcDto`:
  - `get_value`, `list_values`, `set_value`, `add_subfield`, `remove`.
- Fix: avoid mutating dictionary subfield definitions when creating fields.
- Fix: ignore empty MARCXML subfields when importing.

Notes: No breaking changes expected. ISO 2709 and MARCXML roundtrips unaffected.


