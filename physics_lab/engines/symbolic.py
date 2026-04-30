"""Symbolic validation helpers for pendulum verification."""

from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class SymbolicValidationResult:
    """Result of a symbolic consistency check."""

    status: str
    details: str
    metrics: dict[str, float | int | str]


def symbolic_validation_available() -> bool:
    """Return whether symbolic validation is implemented in this version."""
    return True


def _pendulum_expression(model_id: str) -> tuple[str, dict[str, str], set[str], set[str]]:
    if model_id == "model_theta2":
        return "1 + a * theta**2", {}, {"theta", "a"}, {"sin"}
    if model_id == "model_theta2_theta4":
        return "1 + a * theta**2 + b * theta**4", {}, {"theta", "a", "b"}, {"sin"}
    if model_id == "model_sin2":
        return "1 + a * sin(theta / 2)**2", {}, {"theta", "a"}, {"sin"}
    if model_id == "model_x_x2":
        return (
            "1 + a * x + b * x**2",
            {"x": "sin(theta / 2)**2"},
            {"theta", "a", "b", "x"},
            {"sin"},
        )
    raise ValueError(f"Unsupported pendulum model for symbolic validation: {model_id}")


def _collect_names(node: ast.AST) -> set[str]:
    return {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}


def _is_numeric_literal(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return True
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return _is_numeric_literal(node.operand)
    if isinstance(node, ast.BinOp) and isinstance(
        node.op,
        (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow),
    ):
        return _is_numeric_literal(node.left) and _is_numeric_literal(node.right)
    return False


def _expr_is_dimensionless(
    node: ast.AST,
    dimensionless_symbols: set[str],
    supported_functions: set[str],
) -> bool:
    if isinstance(node, ast.Constant):
        return isinstance(node.value, (int, float))
    if isinstance(node, ast.Name):
        return node.id in dimensionless_symbols
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return _expr_is_dimensionless(node.operand, dimensionless_symbols, supported_functions)
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            return _expr_is_dimensionless(
                node.left,
                dimensionless_symbols,
                supported_functions,
            ) and _expr_is_dimensionless(
                node.right,
                dimensionless_symbols,
                supported_functions,
            )
        if isinstance(node.op, ast.Pow):
            return _expr_is_dimensionless(
                node.left,
                dimensionless_symbols,
                supported_functions,
            ) and _is_numeric_literal(node.right)
        return False
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            return False
        if node.func.id not in supported_functions or len(node.args) != 1:
            return False
        return _expr_is_dimensionless(node.args[0], dimensionless_symbols, supported_functions)
    return False


def validate_pendulum_model_dimensions(model_id: str) -> SymbolicValidationResult:
    """Verify that a pendulum candidate formula is symbolically dimensionless."""
    expression, auxiliary_definitions, dimensionless_symbols, supported_functions = (
        _pendulum_expression(model_id)
    )
    expression_ast = ast.parse(expression, mode="eval").body
    auxiliary_asts = {
        symbol: ast.parse(definition, mode="eval").body
        for symbol, definition in auxiliary_definitions.items()
    }

    unsupported_functions = {
        node.func.id
        for node in ast.walk(expression_ast)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id not in supported_functions
    }
    for definition_ast in auxiliary_asts.values():
        unsupported_functions.update(
            {
                node.func.id
                for node in ast.walk(definition_ast)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id not in supported_functions
            }
        )
    if unsupported_functions:
        return SymbolicValidationResult(
            status="FAIL",
            details="Candidate formula uses unsupported symbolic functions.",
            metrics={"unsupported_function_count": len(unsupported_functions)},
        )

    invalid_auxiliary = [
        symbol
        for symbol, definition_ast in auxiliary_asts.items()
        if not _expr_is_dimensionless(definition_ast, dimensionless_symbols, supported_functions)
    ]
    if invalid_auxiliary:
        return SymbolicValidationResult(
            status="FAIL",
            details="Auxiliary symbolic definitions are not dimensionless.",
            metrics={"invalid_auxiliary_count": len(invalid_auxiliary)},
        )

    if not _expr_is_dimensionless(expression_ast, dimensionless_symbols, supported_functions):
        return SymbolicValidationResult(
            status="FAIL",
            details="Candidate formula is not dimensionless under the pendulum variable contract.",
            metrics={"free_symbol_count": len(_collect_names(expression_ast))},
        )

    return SymbolicValidationResult(
        status="PASS",
        details=(
            "The candidate formula is dimensionless: theta is treated as a radian-valued "
            "dimensionless quantity, coefficients are dimensionless, and the target T/T0 "
            "is dimensionless."
        ),
        metrics={
            "free_symbol_count": len(_collect_names(expression_ast)),
            "auxiliary_definition_count": len(auxiliary_asts),
            "supported_function_count": len(supported_functions),
        },
    )
