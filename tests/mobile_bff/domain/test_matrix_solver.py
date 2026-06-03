from domain.equations.strategies.matrix_solver import solve_matrix


def test_solve_matrix_with_comma_vector():
    res = solve_matrix("solve_matrix: 2,0;0,3 | 4,9", False)
    assert not res.error
    assert "x1 = 2" in res.result
    assert "x2 = 3" in res.result


def test_solve_matrix_with_semicolon_vector():
    res = solve_matrix("solve_matrix: 2,0;0,3 | 4;9", False)
    assert not res.error
    assert "x1 = 2" in res.result
    assert "x2 = 3" in res.result


def test_solve_matrix_dimension_mismatch():
    res = solve_matrix("solve_matrix: 1,0;0,1 | 1,2,3", False)
    assert res.error != ""
    assert "Dimensões" in res.error


def test_solve_matrix_singular_matrix():
    res = solve_matrix("solve_matrix: 1,2;2,4 | 3,6", False)
    assert res.error != "" or res.result == ""
