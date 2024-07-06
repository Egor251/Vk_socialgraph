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

    @staticmethod
    def set_unique(list1):
        return list(set(list1))


    @staticmethod
    def benchmark(func):  # Декоратор для вычисления времени работы функции. полезен при оптимизации
        # Вызывать @Utils().benchmark
        def calc_time(*args, **kwargs):
            start_time = time.time()
            original_result = func(*args, **kwargs)
            full_time = time.time() - start_time
            print(f'Function {func.__name__}() finished in {full_time} sec')
            return original_result
        return calc_time


if __name__ == '__main__':

    @Utils().benchmark
    def test():
        original_list = list(range(1000000))

    test()