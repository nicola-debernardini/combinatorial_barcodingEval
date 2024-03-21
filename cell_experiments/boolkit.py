from typing import Callable
from enum import Enum

class Logical(Enum):
    OR = lambda b1, b2: b1 or b2
    AND = lambda b1, b2: b1 and b2

def reduce(bools: list[bool], logical_op: Logical) -> bool:
    """This function collapses a list of booleans into a single boolean according to a
    specified logical operator.

    Arguments
    -------
    bools
        a list of booleans
    logical_op
        a logical operation

    Returns
    -------
    bool
        a boolean obtained by applying logical_op to all the members of bools
    """
    assert len(bools) > 0, "reduce Error: Empty bools provided"
    def sub_reduce(res: bool, i: int):
        if i == len(bools):
            return res
        else:
            return sub_reduce(logical_op(res, bools[i]), i + 1)
    return sub_reduce(True, 0)