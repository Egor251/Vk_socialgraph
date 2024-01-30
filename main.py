from vk_social_graph import VK
from db import DB

class Main:
    def vk_socialgraph(self, targetid, roundy, name='normal', start=0):
        VK.targetid = targetid
        VK.name = name
        VK.roundy = roundy

        if name == 'normal':
            VK().open_account_start()
        elif name == 'hidden':
            if start == 0:
                print('Не указана точка старта')
            else:
                VK().hidden_account_start(start)


if __name__ == '__main__':
    targetid = ''  # Кого пробиваем (id или ник)
    roundy = 2  # число раундов. 0 - бесполезно, 1 - пару минут, 2 - час или больше, 3 - 1 или 2 дня, 4 - дурак, чтоль?
    Main().vk_socialgraph(targetid, roundy)
