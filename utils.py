# Уникализирует элементы массива. Ускорено numba
from numba import njit
from tqdm import tqdm
import time


class Utils:

    @njit
    def unique(self, list1):
        unique = []
        for number in list1:
            if number not in unique:
                unique.append(number)
        return unique

    # Уникализирует элементы массива. Не ускорено numba)
    @staticmethod
    def usual_unique(list1):
        unique = []
        for number in tqdm(list1):
            if number not in unique:
                unique.append(number)
        return unique

    # добавляет длину ребра (1) к парам ID для передачи в get_graph
    def graph_data_preparation(self, a):
        c = []
        all_users = []
        for b in a:
            c.append([b[0], b[1], 1])

        return c  # возвращаем массив типа [[baseid, friendid, 1],...] и массив с перечнем всех уникальных юзеров

