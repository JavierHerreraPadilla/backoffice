from typing import List, Literal, Optional
from time import sleep
from random import randint


"""A TESTING MODULE"""

def test_func(a: str, enviroment: Literal["prd", "stg"]) -> str:
    """func that retuns a set list"""
    sleep(30)
    num = randint(1,10)
    if num % 2 == 0:
        a = {}
    return enviroment + "-" + a

def output_literal(num: int = None) -> Literal[0, 1]:
    sleep(10)
    return 0 if not num else 1


def func_takes_list(names: List, gender: str = None, age: int = None) -> List:
    sleep(10)
    assert isinstance(names, List), "Function arg must be a list"
    result = []
    for name in names:
        result.append(name*2)
    return result


def func_takes_2_lists(lst1: List, lst2: List) -> List:
    return list(zip(lst1,lst2))
