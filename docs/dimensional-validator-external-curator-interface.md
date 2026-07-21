# External Dimensional Benchmark Curator Interface

## Purpose

This is the only dimensional-validator interface document that an external
curator may read while executing `TASK-1071`. It defines the prospective item
schema and scope without exposing existing challenge rows, expected answers,
validator outputs, result metrics, or implementation behavior.

The curator must not use other APL dimensional-analysis files during curation.
Questions about repository compatibility must be routed to a separate reviewer
without showing historical answers or validator output to the curator.

## Scope

The future benchmark is SI-focused dimensional classification. Each item asks
whether the dimensions of the two sides of one symbolic relation agree under
the supplied variable-dimension declarations.

Primary labels are:

- `VALID`: both sides have the same dimensions under the declarations;
- `INVALID`: the dimensions differ;
- `INCONCLUSIVE`: the expression is outside the predeclared parser or scope
  boundary and cannot receive an unambiguous dimensional verdict.

These labels concern dimensional agreement only. They do not establish
numerical correctness, physical plausibility, regime validity, or support for
natural-unit conventions.

## Curator Item Fields

Every proposed item must contain:

- a stable external item id;
- one symbolic relation as plain text;
- a complete variable-to-SI-dimension declaration;
- one primary label from the vocabulary above;
- a physics-domain label;
- a concise dimensional rationale written without reference to APL output;
- a source or provenance note;
- a reuse classification for the formula and curator-authored annotation;
- optional semantic, regime, or known-limit notes on non-scoring fields only.

The external package must not contain copied source prose, figures, tables,
publisher files, or archive bytes.

## Expression Boundary

Use conventional symbolic arithmetic with named variables, numeric constants,
parentheses, products, quotients, integer or rational powers, and standard
functions whose arguments have an explicit dimensional interpretation. Every
symbol needed to determine dimensions must be declared. Do not assume natural
units or silently set physical constants to one.

Items with parser-dependent notation, undeclared symbols, ambiguous grouping,
or disputed dimensional conventions must be excluded or placed in the small
predeclared `INCONCLUSIVE` stratum. The curator must not adapt notation after
seeing APL inference behavior.

## Blindness Boundary

During curation, the curator may read only this document and `TASK-1071`. They
must not inspect:

- APL dimensional-validator source code or tests;
- existing APL challenge-set rows or expected labels;
- item-level predictions, score ledgers, result files, or claim evidence;
- historical formula lists, review notes, or overlap reports.

After the curator freezes the ordered candidate package and its digest, a
different reviewer may compare formula structure against historical APL
surfaces. That reviewer reports only overlap identities/counts and a bounded
pass/block verdict. Historical labels and validator outputs must not be sent
back to the curator, and the curator may not replace rows in response to
performance information.

## No-Claim Boundary

Curating and freezing this package does not show that the APL validator is
accurate, general, semantically complete, or scientifically novel. Validator
execution and one-shot scoring require a later task after the external package
and independent overlap review are merged.
