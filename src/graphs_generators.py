"""
модуль функций генерации графов для моделирования эпидемий
"""
import networkx as nx
import numpy as np

def random_working_graph(N: int, E_num: int) -> nx.Graph:
    """
    функция генерирует случайный граф на N вершинах с E_num рёбрами без всяких атрибутов

    :param N: число вершин
    :param E_num: число ребёр
    :return: сам граф
    """
    G = nx.Graph()
    # узлы с номерами от 0 до N-1
    G.add_nodes_from([num for num in range(N)])

    # создаём все возможные рёбра
    all_edge_set = []
    for i in range(N):
        for j in range(i+1, N):
            all_edge_set.append((i, j))

    all_edge_set = np.array(all_edge_set)
    # выбираем E_num из них
    edge_list = np.random.choice(np.arange(all_edge_set.shape[0]), E_num, replace=False)
    edge_list = all_edge_set[edge_list]
    G.add_edges_from(edge_list)

    # добавляем рандомные веса интенсивностей [0, 1]
    for edge in G.edges:
        G.edges[edge]['w'] = np.round(np.random.rand(1)[0], 3)

    return G

def random_home_graph(N: int, max_click_size = 5) -> nx.Graph:
    """
    Генерирует случайный граф, состоящий из клик размера не более max_click_size

    Клики собираются из вершин последовательно, т.е. множество 0,...,N-1 разбивается на 0,...,k_1; k_1 + 1, ...
    и т.д.

    :param N: число вершин
    :param max_click_size: максимально допустимый размер клики
    :return: сам граф
    """
    G = nx.Graph()
    G.add_nodes_from([num for num in range(N)])

    # размер следующей клики
    next_size = np.random.random_integers(low=1, high=max_click_size)
    # номер вершины, с которой будет начинаться следующая клика
    next_num = 0
    total_number = N
    while total_number - next_size > 0:
        click = nx.complete_graph(range(next_num, next_num + next_size))
        G = nx.compose(G, click)

        next_num += next_size
        total_number -= next_size
        next_size = np.random.random_integers(1, max_click_size)

    click = nx.complete_graph(range(next_num, N))
    G = nx.compose(G, click)

    # добавляем рандомные веса интенсивностей [0, 1]
    for edge in G.edges:
        G.edges[edge]['w'] = np.round(np.random.rand(1)[0], 3)

    return G


# Tests
# G = random_working_graph(5, 5)
# G_h = random_home_graph(5, 2)