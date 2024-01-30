import argparse
import os
import sys
import inspect

from main import Main


def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False):  # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


# Объявляем парсер
parser = argparse.ArgumentParser(description='Поиск пересечений среди друзей в ВК',
                                 epilog="Использовать с осторожностью")

parser.add_argument('-t', '--target', dest='targetid', help='ID или ник в вк искомого человека', required=True)
parser.add_argument('-r', '--round', dest='roundy', default=2, help='Количество итераций (радиус поиска)', type=int,  required=True)
parser.add_argument('-x', '--hidden', action="count", help="Указать если пользователь имеет скрытый профиль")
parser.add_argument('-s', '--start', dest='start', default=0, type=int, help="Стартовый открытый профиль для поиска друзей скрытого профиля")



args = parser.parse_args()
if args.hidden:
    name = 'hidden'
else:
    name = 'normal'
Main().vk_socialgraph(args.targetid, args.roundy, name, args.start)

if __name__ == '__main__':

    os.chdir(get_script_dir())

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
