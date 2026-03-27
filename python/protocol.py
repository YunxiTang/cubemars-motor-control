import numpy as np


def float_to_uint(x, x_min, x_max, bits):
    """Convert a float to an unsigned int."""
    span = x_max - x_min
    return int((x - x_min) * (2**bits - 1) / span)