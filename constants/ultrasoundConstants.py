import numpy as np
from enum import Enum

class IMAGE_TYPE(Enum):
    GRAYSCALE = 'GRAYSCALE'
    COLOR = 'COLOR'

class HSV_COLOR_THRESHOLD(Enum):
    LOWER = [60, 50, 50]
    UPPER = [100, 255, 255]

class HSV_GRAYSCALE_THRESHOLD(Enum):
    LOWER = [78, 250, 0]
    UPPER = [86, 255, 2]