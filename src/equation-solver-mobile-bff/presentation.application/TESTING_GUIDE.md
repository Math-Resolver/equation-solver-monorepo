# Padrão de Testes do Equation Solver

## Visão Geral

Este documento descreve o padrão de testes adotado no projeto `equation-solver`. Os testes seguem uma estrutura consistente que facilita a manutenção, extensão e compreensão do código.

## Estrutura Geral de um Teste

### Imports e Setup

Todos os arquivos de teste seguem este padrão de imports:

```python
from pathlib import Path
import sys
import unittest

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from services.equations.errors import InvalidEquationError
from services.solvers.<solver_name> import <SolverFunction>
```

**Por quê?**

- `Path` e `sys`: Permitem localizar e importar módulos do projeto
- `unittest`: Framework padrão do Python para testes
- `APP_ROOT`: Garante que o módulo seja encontrado independentemente de onde o teste é executado

### Estrutura da Classe de Teste

```python
class Solve<TipoEquacao>Tests(unittest.TestCase):
    def test_<descricao_do_comportamento>(self) -> None:
        # Arrange
        result = solve_<tipo>("equacao", show_steps=True/False)

        # Assert
        self.assertEqual(result.result, "resultado_esperado")
        self.assertEqual(len(result.steps), numero_esperado)
```

**Convenções:**

- Nome da classe: `Solve<TipoEquacao>Tests` (ex: `SolveLinearTests`)
- Nome do método: `test_<descricao_clara>` (começa com `test_`)
- Sempre use assertions específicas: `assertEqual`, `assertGreater`, `assertRaises`

## Padrão de Testes por Tipo de Solver

### 1. Teste de Caso Válido com `show_steps=False`

```python
def test_solves_<tipo>_equation(self) -> None:
    result = solve_<tipo>("x+5=10", show_steps=False)

    self.assertEqual(result.result, "x = 5")
```

**O que testar:**

- A solução está correta?
- O formato do resultado é consistente?

### 2. Teste de Caso Válido com `show_steps=True`

```python
def test_solves_<tipo>_equation_with_steps(self) -> None:
    result = solve_<tipo>("x+5=10", show_steps=True)

    self.assertEqual(result.result, "x = 5")
    self.assertEqual(len(result.steps), 2)
    # Opcionalmente, valide os passos individuais:
    self.assertEqual(result.steps[0].before, "x + 5 = 10")
```

**O que testar:**

- A solução está correta?
- O número de passos é esperado?
- (Bônus) Os passos intermediários estão corretos?

### 3. Teste de Entrada Inválida

```python
def test_rejects_<tipo>_<condicao_invalida>(self) -> None:
    with self.assertRaises(InvalidEquationError):
        solve_<tipo>("<entrada_invalida>", show_steps=False)
```

**O que testar:**

- O solver lança `InvalidEquationError` para entradas inválidas?
- A mensagem de erro é clara (você pode validar isto também)?

### 4. Casos Especiais (Opcional)

```python
def test_solves_<tipo>_with_<caracteristica_especial>(self) -> None:
    result = solve_<tipo>("...", show_steps=False)

    self.assertEqual(result.result, "...")
```

**Exemplos:**

- Equação com coeficiente negativo
- Solução com números decimais/complexos
- Múltiplas variáveis

## Estrutura de Resultado (SolveResult)

Todo solver retorna um objeto `SolveResult` com esta estrutura:

```python
@dataclass
class SolveResult:
    result: str            # A solução em formato string
    steps: list[StepResult]  # Lista de passos para chegar à solução
```

```python
@dataclass
class StepResult:
    rule: str    # Descrição do passo (ex: "Isola a variável")
    before: str  # Estado antes do passo
    after: str   # Estado depois do passo
```

## Executando os Testes

### Executar um arquivo de teste específico:

```bash
python -m unittest tests.test_<solver_name> -v
```

### Executar toda a suíte de testes:

```bash
python -m unittest discover tests -v
```

### Executar um teste específico dentro de um arquivo:

```bash
python -m unittest tests.test_<solver_name>.<NomeDaClasse>.<nome_do_metodo> -v
```

## Erros Comuns

### ❌ AssertionError: "x = 5" != "x=5"

Verifique se o formato de espaçamento está correto no resultado.

**Solução:** Use `_format_number()` ou ferramentas de formatação consistentes no seu solver.

### ❌ ModuleNotFoundError

Verifique se `APP_ROOT` está correto e se os imports estão usando o caminho relativo certo.

**Solução:** Certifique-se de que o arquivo de teste está em `tests/` e use `parents[1]` para subir até `presentation.application`.

### ❌ len(result.steps) == 0 quando deveria ser > 0

O seu solver não está gerando passos quando `show_steps=True`.

**Solução:** Certifique-se que o solver cria objetos `StepResult` e os adiciona à lista de `steps`.

## Checklist para Novo Teste

Antes de considerar um teste completo, verifique:

- [ ] O teste tem nome descritivo?
- [ ] Testa um caso válido?
- [ ] Testa um caso inválido (com `assertRaises`)?
- [ ] Testa o comportamento com `show_steps=True` e `show_steps=False`?
- [ ] As assertions são específicas (não genéricas)?
- [ ] O teste passa localmente?
- [ ] A suíte completa ainda passa?

## Tarefas Abertas para o Estagiário

### ✏️ Teste 1: `test_simplifies_with_multiple_variables`

**Arquivo:** `tests/test_simplification_solver.py`

**O que fazer:**

1. Leia o enunciado do teste (está com `pass` e comentários)
2. Entenda o que a expressão `"2x + 3y + x - y"` deve resultar
3. Complete o corpo do teste com:
   - Uma chamada a `solve_simplification()` com a expressão
   - Validações usando `self.assertEqual()` para:
     - O resultado estar correto
     - Se `show_steps=True`, validar que há passos

**Dicas:**

- Revise como testes similares em `test_linear_solver.py` e `test_quadratic_solver.py` validam os resultados
- Use `show_steps=True` para entender o fluxo interno
- Teste primeiro na linha de comando: `python -m unittest tests.test_simplification_solver.SolveSimplificationTests.test_simplifies_with_multiple_variables -v`

**Exemplo de estrutura:**

```python
def test_simplifies_with_multiple_variables(self) -> None:
    # Arrange: chame o solver
    result = solve_simplification("2x + 3y + x - y", show_steps=False)

    # Assert: valide o resultado
    self.assertEqual(result.result, "3x+2y")
```

---

### ✏️ Teste 2: `test_simplifies_polynomial_expression`

**Arquivo:** `tests/test_simplification_solver.py`

**O que fazer:**

1. Leia o enunciado (está com `pass` e comentários)
2. Entenda o que uma expressão polinomial `"x^2 + 2x + 1 + 3x^2 - x"` deve resultar
3. Complete o teste:
   - Chamada a `solve_simplification()` com a expressão
   - Assertions para validar o resultado correto

**Dicas:**

- Polinômios têm termos de graus diferentes (x^2, x^1, x^0)
- Você precisará **modificar a função `_simplify_like_terms` em `simplification.py`** para:
  - Detectar potências (ex: `x^2`, `x^3`)
  - Rastrear termos por grau separadamente
  - Ordenar a saída corretamente (maiores graus primeiro)

**Processo sugerido:**

1. Primeiro, escreva o teste como espera que funcione
2. Rode o teste e veja falhar (deve falhar porque `_simplify_like_terms` não suporta polinômios ainda)
3. Modifique `simplification.py` para detectar e processar potências
4. Rode novamente até passar

**Exemplo de saída esperada:**

```
"x^2 + 2x + 1 + 3x^2 - x" → "4x^2+x+1"
```

---

## Recursos Adicionais

- [Documentação do unittest](https://docs.python.org/3/library/unittest.html)
- [SolveResult e StepResult](../services/solvers/models.py)
- [Exemplo de solver completo](../services/solvers/linear.py)
