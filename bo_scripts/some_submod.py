from typing import List, Literal, Optional


"""A TESTING MODULE"""

def test_func(a: str, enviroment: Literal["prd", "stg"]) -> int:
    """func that retuns a set list"""
    return 35

def output_literal() -> Literal[0, 1]:
    ...