from domain.equations.strategies.geometry_solver import solve_geometry


def test_area_circle():
    res = solve_geometry("area:circle 2", False)
    assert not res.error
    assert res.result == "12.566371"


def test_area_triangle_base_height():
    res = solve_geometry("area:triangle base=3,height=4", False)
    assert not res.error
    assert res.result == "6.0"


def test_perimeter_rectangle():
    res = solve_geometry("perimeter:rectangle 3,4", False)
    assert not res.error
    assert res.result == "14.0"


def test_area_triangle_heron():
    res = solve_geometry("area:triangle sides 3,4,5", False)
    assert not res.error
    assert res.result == "6.0"
