from pathlib import Path
import sys
import unittest


APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from domain.equations.errors import InvalidEquationError
from domain.strategies.simplification_solver import solve_simplification


class SolveSimplificationTests(unittest.TestCase):
    def test_simplifies_like_terms(self) -> None:
        result = solve_simplification("2x + 3x", show_steps=False)

        self.assertEqual(result.result, "5x")

    def test_simplifies_mixed_terms(self) -> None:
        result = solve_simplification("2x + 5 + 3x + 2", show_steps=False)

        self.assertEqual(result.result, "5x+7")

    def test_simplifies_with_negative_coefficients(self) -> None:
        result = solve_simplification("5x - 2x + 3", show_steps=False)

        self.assertEqual(result.result, "3x+3")

    def test_simplifies_with_steps(self) -> None:
        result = solve_simplification("4x + 2x", show_steps=True)

        self.assertEqual(result.result, "6x")
        self.assertGreater(len(result.steps), 0)

    def test_rejects_expression_without_variables(self) -> None:
        with self.assertRaises(InvalidEquationError):
            solve_simplification("2 + 3", show_steps=False)

    def test_simplifies_with_multiple_variables(self) -> None:
        # TODO: Implemente este teste
        # Hint: A expressão "2x + 3y + x - y" deve simplificar para algo como "3x+2y"
        # Dica: Você precisará modificar a função _simplify_like_terms para 
        # rastrear variáveis diferentes (x, y, z) separadamente na ordem correta
        pass

    def test_simplifies_polynomial_expression(self) -> None:
        # TODO: Implemente este teste
        # Hint: A expressão "x^2 + 2x + 1 + 3x^2 - x" deve simplificar para "4x^2+x+1"
        # Dica: Você precisará expandir a detecção de termos para incluir potências (x^2, x^3, etc)
        # e ordená-los corretamente (primeiro x^2, depois x, depois constantes)
        pass


if __name__ == "__main__":
    unittest.main()
