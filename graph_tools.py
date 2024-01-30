import networkx as nx
import matplotlib.pyplot as plt


class GraphTools:

    # Формирует итоговый граф
    def get_graph(self, lis, all_users, node_attrs):
        print('формируем граф')

        G = nx.Graph()
        G.add_weighted_edges_from(lis)
        #all_users = self.all_users_list(lis)
        print(f'Всего узлов графа: {len(all_users)}')
        #for item in tqdm(all_users):
            #node_attrs = {item: self.get_full_member_data(item)}
        nx.set_node_attributes(G, node_attrs)

        color_map = []
        labels = {}
        for node in G:  # формируем карту цветов из атрибутов нод
            labels[node] = G.nodes[node]['name']
            try:
                if G.nodes[node]['sex'] == 1:
                    color_map.append('red')
                elif G.nodes[node]['sex'] == 2:
                    color_map.append('blue')
                else:
                    color_map.append('blue')
            except Exception:
                color_map.append('gold')

        options = {
            'node_color': color_map,
            'node_size': 15,
            'width': 0.1,
            'labels': labels
        }
        try:  # Вообще хз, но только так работает!
            nx.draw(G, **options)
        except Exception:
            pass
        plt.show()
        return G  # Возвращает граф с которым дальше может работать networkx

# добавляет длину ребра (1) к парам ID для передачи в get_graph
    @staticmethod
    def graph_data_preparation(a):
        c = []
        for b in a:
            c.append([b[0], b[1], 1])

        return c  # возвращаем массив типа [[baseid, friendid, 1],...] и массив с перечнем всех уникальных юзеров

# Функция сохранения базы в gexf файле
    def save_data(self, G, filename="graph.gexf"):
        nx.write_gexf(G, filename, encoding='utf-8', prettyprint=True, version='1.2draft')
