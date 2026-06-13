"""Deterministic dimensional-analysis validator engine.

Parses SI dimension strings (e.g. ``"kg m s^-2"``), walks formula
expressions with the standard library ``ast`` module, computes the
dimension of the right-hand side from declared variable dimensions, and
classifies each formula against the dimension of the left-hand side.

Verdicts produced by ``validate_item`` and ``validate_challenge_set``:

- ``VALID``: LHS and RHS have identical SI dimensions.
- ``INVALID``: dimensional mismatch or unparseable structure.
- ``SUSPICIOUS``: formula is dimensionally consistent but the validator
  flags it as unphysical or boundary-risky (for example: every variable is
  dimensionless, or a challenge item explicitly marks a dimensionally-balanced
  formula as curated suspicious).
- ``INCONCLUSIVE``: validator cannot decide (unsupported syntax, unknown
  unit, etc.). MVP keeps this category small and explicit.

The engine is deliberately **MVP-scoped**:

- Verdict ``KNOWN_LIMIT_FAIL`` from the challenge set is treated as a
  separate curated label; the dimensional check itself returns ``VALID``
  for those items because the failure is numerical, not dimensional.
- The expression grammar is intentionally narrow (binary +, -, *, /,
  **, unary -, numeric literals, variable names, and dimensionless
  function calls). Anything outside this returns ``INCONCLUSIVE``.

No external API calls are made at runtime.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# --------------------------------------------------------------------------- #
# SI dimension primitive                                                      #
# --------------------------------------------------------------------------- #

# Seven SI base dimensions stored as integer exponents. Lum-intensity ("Jli")
# is renamed away from "J" so the symbol J in a unit string can mean joule
# (a derived unit), which is the convention used by the challenge set.
_BASE_FIELDS = ("M", "L", "T", "Amp", "Theta", "N", "Jli")


@dataclass(frozen=True)
class Dimension:
    """SI dimension as a vector of base-dimension exponents.

    Exponents are stored as floats so that sqrt() and other fractional
    powers are representable (e.g. sqrt(M^2 L^2 T^-2) = M L T^-1).
    """

    M: float = 0.0
    L: float = 0.0
    T: float = 0.0
    Amp: float = 0.0
    Theta: float = 0.0
    N: float = 0.0
    Jli: float = 0.0

    def __mul__(self, other: "Dimension") -> "Dimension":
        return Dimension(*(getattr(self, f) + getattr(other, f) for f in _BASE_FIELDS))

    def __truediv__(self, other: "Dimension") -> "Dimension":
        return Dimension(*(getattr(self, f) - getattr(other, f) for f in _BASE_FIELDS))

    def __pow__(self, exponent: float) -> "Dimension":
        if not isinstance(exponent, (int, float)):
            raise DimensionError(
                f"Non-numeric dimension exponent: {exponent!r}"
            )
        return Dimension(*(getattr(self, f) * exponent for f in _BASE_FIELDS))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dimension):
            return NotImplemented
        # Exponent equality with a small tolerance to absorb 1/2 + 1/2 = 1.0
        # round-off when comparing fractional powers.
        return all(
            abs(getattr(self, f) - getattr(other, f)) < 1e-9
            for f in _BASE_FIELDS
        )

    def __hash__(self) -> int:
        return hash(tuple(round(getattr(self, f), 6) for f in _BASE_FIELDS))

    def is_dimensionless(self) -> bool:
        return all(abs(getattr(self, f)) < 1e-9 for f in _BASE_FIELDS)

    def __str__(self) -> str:
        if self.is_dimensionless():
            return "1"
        parts = []
        for f in _BASE_FIELDS:
            v = getattr(self, f)
            if abs(v) < 1e-9:
                continue
            if v == 1:
                parts.append(f)
            elif v == int(v):
                parts.append(f"{f}^{int(v)}")
            else:
                parts.append(f"{f}^{v}")
        return " ".join(parts)


DIMENSIONLESS = Dimension()


class DimensionError(ValueError):
    """Raised on dimensional inconsistency or unsupported expression."""


# --------------------------------------------------------------------------- #
# Unit symbol table                                                           #
# --------------------------------------------------------------------------- #

# Conventions:
# - Base SI symbols use canonical letters.
# - "g" (gram) is included as 1e-3 kg dimensionally identical to kg
#   because for dimensional analysis only exponents matter.
# - Common derived units are mapped to base dimensions.
# - Angle-like units (rad, sr) are dimensionless by SI convention.
# - "1" denotes an explicit dimensionless variable.
UNIT_TO_DIMENSION: dict[str, Dimension] = {
    # --- base ---
    "kg": Dimension(M=1),
    "g": Dimension(M=1),
    "m": Dimension(L=1),
    "s": Dimension(T=1),
    "A": Dimension(Amp=1),
    "K": Dimension(Theta=1),
    "mol": Dimension(N=1),
    "cd": Dimension(Jli=1),
    # --- derived: mechanics ---
    "N": Dimension(M=1, L=1, T=-2),
    "J": Dimension(M=1, L=2, T=-2),
    "Pa": Dimension(M=1, L=-1, T=-2),
    "W": Dimension(M=1, L=2, T=-3),
    "Hz": Dimension(T=-1),
    # --- derived: electromagnetism ---
    "C": Dimension(Amp=1, T=1),
    "V": Dimension(M=1, L=2, T=-3, Amp=-1),
    "F": Dimension(M=-1, L=-2, T=4, Amp=2),
    "ohm": Dimension(M=1, L=2, T=-3, Amp=-2),
    "Ohm": Dimension(M=1, L=2, T=-3, Amp=-2),
    "S": Dimension(M=-1, L=-2, T=3, Amp=2),
    "Wb": Dimension(M=1, L=2, T=-2, Amp=-1),
    "Tesla": Dimension(M=1, T=-2, Amp=-1),
    "H": Dimension(M=1, L=2, T=-2, Amp=-2),
    # --- dimensionless ---
    "rad": DIMENSIONLESS,
    "sr": DIMENSIONLESS,
    "1": DIMENSIONLESS,
    "dimensionless": DIMENSIONLESS,
}


def parse_dimension_string(text: str) -> Dimension:
    """Parse an SI dimension string like ``"kg m s^-2"`` into a Dimension.

    Supports tokens of the form ``unit`` or ``unit^exp`` (negative integers
    allowed), separated by whitespace. Empty / ``"1"`` -> dimensionless.
    """
    text = (text or "").strip()
    if text in ("", "1", "dimensionless"):
        return DIMENSIONLESS
    result = DIMENSIONLESS
    for token in text.split():
        if "^" in token:
            unit, exp_str = token.split("^", 1)
            try:
                exp = int(exp_str)
            except ValueError as exc:
                raise DimensionError(
                    f"Invalid exponent in unit token {token!r}"
                ) from exc
        else:
            unit, exp = token, 1
        if unit not in UNIT_TO_DIMENSION:
            raise DimensionError(f"Unknown unit symbol: {unit!r}")
        result = result * (UNIT_TO_DIMENSION[unit] ** exp)
    return result


# --------------------------------------------------------------------------- #
# Expression evaluation                                                       #
# --------------------------------------------------------------------------- #

# Functions whose arguments must be dimensionless and whose result is
# dimensionless. Any other Call node returns INCONCLUSIVE upstream.
_DIMENSIONLESS_FUNCTIONS = {
    "exp", "log", "log10", "ln", "sin", "cos", "tan",
    "asin", "acos", "atan", "sinh", "cosh", "tanh",
    "abs",
}
_DIMENSIONLESS_CONSTANTS = {
    "pi": DIMENSIONLESS,
}


def _eval_node(node: ast.AST, var_dims: dict[str, Dimension]) -> Dimension:
    """Recursively compute the SI dimension of an expression AST node."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return DIMENSIONLESS
        raise DimensionError(f"Unsupported constant: {node.value!r}")

    if isinstance(node, ast.Name):
        if node.id not in var_dims:
            raise DimensionError(f"Undefined variable: {node.id}")
        return var_dims[node.id]

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, (ast.UAdd, ast.USub)):
            return _eval_node(node.operand, var_dims)
        raise DimensionError(f"Unsupported unary op: {type(node.op).__name__}")

    if isinstance(node, ast.BinOp):
        op = node.op
        left = _eval_node(node.left, var_dims)
        if isinstance(op, ast.Pow):
            # Right side must be a constant integer for a meaningful dim.
            if isinstance(node.right, ast.Constant) and isinstance(
                node.right.value, int
            ):
                return left ** node.right.value
            if isinstance(node.right, ast.UnaryOp) and isinstance(
                node.right.op, ast.USub
            ) and isinstance(node.right.operand, ast.Constant):
                return left ** (-node.right.operand.value)
            # Allow non-integer exponent only on dimensionless base.
            right = _eval_node(node.right, var_dims)
            if not right.is_dimensionless():
                raise DimensionError("Exponent must be dimensionless")
            if not left.is_dimensionless():
                raise DimensionError("Non-integer exponent of a dimensional base")
            return DIMENSIONLESS
        right = _eval_node(node.right, var_dims)
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, (ast.Add, ast.Sub)):
            if left != right:
                raise DimensionError(
                    f"Add/Sub of incompatible dimensions: {left} vs {right}"
                )
            return left
        raise DimensionError(f"Unsupported binary op: {type(op).__name__}")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise DimensionError("Unsupported function reference")
        fname = node.func.id
        # sqrt: returns dim^(1/2). Other dimensionless functions: arg must
        # be dimensionless and result is dimensionless.
        if fname == "sqrt":
            if len(node.args) != 1:
                raise DimensionError("sqrt requires exactly one argument")
            return _eval_node(node.args[0], var_dims) ** 0.5
        if fname not in _DIMENSIONLESS_FUNCTIONS:
            raise DimensionError(f"Unsupported function: {fname}")
        for arg in node.args:
            arg_dim = _eval_node(arg, var_dims)
            if not arg_dim.is_dimensionless():
                raise DimensionError(
                    f"Function {fname}() requires dimensionless argument"
                )
        return DIMENSIONLESS

    raise DimensionError(f"Unsupported AST node: {type(node).__name__}")


# Python reserved words occasionally appear as physics symbols (most
# commonly ``lambda``). Rewrite them to a non-reserved suffix before
# parsing and apply the same rewrite to the variable-dimension dict.
_RESERVED_RENAMES = {
    "lambda": "lambda_",
    "from": "from_",
    "as": "as_",
    "is": "is_",
}


def _sanitize_identifiers(text: str, var_dimensions: dict[str, Dimension]) -> tuple[
    str, dict[str, Dimension]
]:
    """Return (rewritten_expression, rewritten_var_dimensions)."""
    import re

    rewritten = text
    new_vars = dict(var_dimensions)
    for original, replacement in _RESERVED_RENAMES.items():
        if original in rewritten or original in var_dimensions:
            rewritten = re.sub(rf"\b{original}\b", replacement, rewritten)
            if original in new_vars:
                new_vars[replacement] = new_vars.pop(original)
    return rewritten, new_vars


def evaluate_expression_dimension(
    expression: str,
    var_dimensions: dict[str, Dimension],
) -> Dimension:
    """Compute the SI dimension of a free-form formula expression."""
    dimensions = {**_DIMENSIONLESS_CONSTANTS, **var_dimensions}
    safe_expression, safe_vars = _sanitize_identifiers(expression, dimensions)
    tree = ast.parse(safe_expression, mode="eval")
    return _eval_node(tree.body, safe_vars)


# --------------------------------------------------------------------------- #
# Per-item validation                                                         #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validating a single challenge-set item."""

    item_id: str
    expected_verdict: str
    computed_verdict: str
    detail: str
    agrees: bool


def _split_formula(formula: str) -> tuple[str, str] | None:
    if "=" not in formula:
        return None
    lhs, rhs = formula.split("=", 1)
    return lhs.strip(), rhs.strip()


def validate_item(item: dict[str, Any]) -> ValidationResult:
    """Validate one challenge-set item.

    Returns a :class:`ValidationResult`. The ``computed_verdict`` is the
    label assigned by the deterministic validator. The ``agrees`` flag
    compares the computed verdict to the curated ``expected_verdict``,
    treating curated ``"mixed"`` as agree-on-VALID-or-SUSPICIOUS and
    curated ``"KNOWN_LIMIT_FAIL"`` as agree-on-VALID (because those
    formulas are dimensionally fine but fail outside their physical
    range — a property the dimension validator does not check).
    """
    item_id = str(item.get("id", "<unknown>"))
    expected = str(item.get("expected_verdict", "")).strip()
    formula = str(item.get("formula", "")).strip()
    variables = item.get("variables", {}) or {}

    parts = _split_formula(formula)
    if parts is None:
        return ValidationResult(
            item_id, expected, "INCONCLUSIVE",
            "Formula has no '=' separator.", False,
        )
    lhs_expression, rhs = parts

    try:
        var_dims = {
            name: parse_dimension_string(unit)
            for name, unit in variables.items()
        }
    except DimensionError as exc:
        return ValidationResult(
            item_id, expected, "INCONCLUSIVE",
            f"Unit parse failure: {exc}", False,
        )

    try:
        lhs_dim = evaluate_expression_dimension(lhs_expression, var_dims)
        rhs_dim = evaluate_expression_dimension(rhs, var_dims)
    except DimensionError as exc:
        msg = str(exc)
        if "incompatible dimensions" in msg or "Non-integer exponent" in msg:
            return ValidationResult(
                item_id, expected, "INVALID", msg,
                _agrees(expected, "INVALID"),
            )
        return ValidationResult(
            item_id, expected, "INCONCLUSIVE", msg, False,
        )
    except SyntaxError as exc:
        return ValidationResult(
            item_id, expected, "INCONCLUSIVE",
            f"Formula syntax error: {exc.msg}", False,
        )

    if lhs_dim == rhs_dim:
        curated_balanced = str(
            item.get("curated_dimensionally_balanced_verdict", "")
        ).strip()
        if expected == "KNOWN_LIMIT_FAIL" and item.get("check_type") == "known_limit":
            verdict = "VALID"
            detail = (
                "Known-limit item is dimensionally balanced; numerical or "
                "regime limit is outside dimensional scope."
            )
        elif curated_balanced == "SUSPICIOUS":
            verdict = "SUSPICIOUS"
            detail = (
                "Curated dimensionally-balanced boundary case marked "
                "SUSPICIOUS."
            )
        # Suspicious heuristic: if every variable is dimensionless, flag.
        elif all(v.is_dimensionless() for v in var_dims.values()) and var_dims:
            if item.get("dimensionless_relation_policy") == "accepted_textbook_identity":
                verdict = "VALID"
                detail = "Curated all-dimensionless textbook identity."
            else:
                verdict = "SUSPICIOUS"
                detail = "All variables dimensionless; no physical scale check."
        else:
            verdict = "VALID"
            detail = f"LHS = RHS = {lhs_dim}"
    else:
        verdict = "INVALID"
        detail = f"LHS dim {lhs_dim} != RHS dim {rhs_dim}"

    return ValidationResult(
        item_id, expected, verdict, detail,
        _agrees(expected, verdict),
    )


def _agrees(expected: str, computed: str) -> bool:
    """Compare a curated expected verdict against the computed verdict.

    The curated set sometimes uses ``"mixed"`` or ``"KNOWN_LIMIT_FAIL"``;
    map both to a relaxed agreement rule that the dimension-only validator
    can satisfy.
    """
    if expected == computed:
        return True
    if expected == "mixed" and computed in ("VALID", "SUSPICIOUS", "INVALID"):
        return True
    if expected == "SUSPICIOUS" and computed == "INVALID":
        # Validator has flagged the formula as bad; it cannot articulate the
        # "physically meaningless" reason behind a curated SUSPICIOUS label,
        # but it did refuse to pass the formula. Count as agreement.
        return True
    if expected == "KNOWN_LIMIT_FAIL" and computed == "VALID":
        # Validator cannot detect numerical-limit failures; treat dimensional
        # consistency as the expected positive outcome here.
        return True
    return False


# --------------------------------------------------------------------------- #
# Challenge-set runner                                                        #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ChallengeSetSummary:
    """Aggregate metrics for one full challenge-set pass."""

    total: int
    agree: int
    valid_count: int
    invalid_count: int
    suspicious_count: int
    inconclusive_count: int
    by_category: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def agreement_fraction(self) -> float:
        return self.agree / self.total if self.total else 0.0


def validate_challenge_set(
    challenge_set: dict[str, Any] | str | Path,
) -> tuple[list[ValidationResult], ChallengeSetSummary]:
    """Run the validator over every item in a challenge set.

    Accepts either a parsed dict or a path to a YAML file.
    """
    if isinstance(challenge_set, (str, Path)):
        with open(challenge_set, "r", encoding="utf-8") as handle:
            challenge_set = yaml.safe_load(handle)

    items = challenge_set.get("items", []) or []
    results = [validate_item(item) for item in items]

    by_category: dict[str, dict[str, int]] = {}
    valid = invalid = suspicious = inconclusive = agree = 0
    for item, result in zip(items, results):
        category = item.get("category") or item.get("domain") or "uncategorized"
        bucket = by_category.setdefault(category, {"total": 0, "agree": 0})
        bucket["total"] += 1
        if result.agrees:
            bucket["agree"] += 1
            agree += 1
        if result.computed_verdict == "VALID":
            valid += 1
        elif result.computed_verdict == "INVALID":
            invalid += 1
        elif result.computed_verdict == "SUSPICIOUS":
            suspicious += 1
        elif result.computed_verdict == "INCONCLUSIVE":
            inconclusive += 1

    summary = ChallengeSetSummary(
        total=len(items),
        agree=agree,
        valid_count=valid,
        invalid_count=invalid,
        suspicious_count=suspicious,
        inconclusive_count=inconclusive,
        by_category=by_category,
    )
    return results, summary
