# Уникализирует элементы массива. Ускорено numba
from numba import njit
from tqdm import tqdm
import os
import time


class Utils:
    os.environ["NUMBA_DISABLE_PERFORMANCE_WARNINGST"] = '1'

    @staticmethod
    @njit
    def unique(list1):
        unique1 = []
        for number in list1:
            if number not in unique1:
                unique1.append(number)
        return unique1

    # Уникализирует элементы массива. Не ускорено numba)
    @staticmethod
    def usual_unique(list1):
        unique = []
        for number in tqdm(list1):
            if number not in unique:
                unique.append(number)
        return unique



