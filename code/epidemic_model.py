"""
    в модуле определяются классы моделей эпидемий (без сэмплирования), основанные на графах контактах
    с возможностью введения локдауна
"""
import networkx as nx
from typing import List
from typing import Tuple
from typing import Union
from abc import abstractmethod
from enum import Enum


class NodeStates(Enum):
    """
        Синонимы для состояний вершин
    """
    Sucept = 1
    Infected = 2
    Recovered = 3


class BasicEpidemic:
    """
    Базовый класс эпидемии. Хранит основной граф контактов и начальное распределение больных/здоровых
    """

    def __init__(self, G: nx.Graph, init_distr: List[int]):
        """

        :param G: граф контактов
        :param ini_distr:  начальное распределение больных
        """
        self.contact_graph = G
        self._ini_distr = init_distr

        # инициализируем граф переданными начальными условиями
        for node in self.contact_graph.nodes:
            self.contact_graph.nodes[node]['state'] = init_distr[node]

    @abstractmethod
    def _eval_individ_prob(self, n: int) -> None:
        """
        Метод оценки вероятности данной вершины перейти в следующее состояние
        Метод должен обновить соответсвующий атрибут вершины

        :param n: номер вершины
        :return:
        """
        pass

    def eval_probs(self) -> None:
        """
        Метод пересчитывает вероятности перехода для всего графа

        :return:
        """
        for vertex in self.contact_graph.nodes:
            self._eval_individ_prob(vertex)


class EpidemicWithLockdown(BasicEpidemic):
    """
        Эпидемия с локдауном и простым пересчётом вероятностей
    """

    def __init__(self, G: nx.Graph, ini_distr: List[int],
                 G_home: nx.Graph, sigma: float, xi: float, beta: Union[float, List[float]]):
        """
        :param G:
        :param ini_distr:
        :param G_home: граф режима карантин
        :param sigma: вероятность I -> R
        :param xi: вероятность R -> S
        :param beta: коэффициенты восприимчивости к болезни вершин, в простейшем случае у всех одинковы
        """
        super().__init__(G, ini_distr)
        self.lockdown_contact_graph = G_home
        self.ordinary_contact_graph = G
        self.I_to_R_prob = sigma
        self.R_to_S_prob = xi
        if beta is list:
            self.personal_suceptabilities = beta
        else:
            self.personal_suceptabilities = [beta for i in range(len(G.nodes))]

        # техническая копия текущего графа для корректного пересчёта вероятностей
        self._G_copy = G.copy()

    def _eval_individ_prob(self, n: int) -> None:
        """
                рассчитывает вероятность перехода в следующее состояние для данной вершины
            """
        if self.contact_graph.nodes[n]['state'] == NodeStates.Infected:
            self._G_copy.nodes[n]['prob'] = self.I_to_R_prob
        elif self.contact_graph.nodes[n]['state'] == NodeStates.Recovered:
            self._G_copy.nodes[n]['prob'] = self.R_to_S_prob
        elif self.contact_graph.nodes[n]['state'] == NodeStates.Sucept:
            # берём индивидуальную восприимчивость
            personal_sucept = self.personal_suceptabilities[n]

            # берём номера всех больных соседей
            infected_neighbours = list(filter(lambda x: self.contact_graph.nodes[x]['state'] ==
                                                        NodeStates.Infected, self.contact_graph.adj[n]))

            # считаем вероятность заразиться
            # все больные соседи могут заразить независимо друг от друга
            cur_prob = 1
            for neigb in infected_neighbours:
                cur_prob *= 1 - personal_sucept * self.contact_graph.edges[n, neigb]['w']
            cur_prob = 1 - cur_prob

            self._G_copy.nodes[n]['prob'] = cur_prob

    def eval_probs(self) -> None:
        super().eval_probs()

        # обновляем наш граф
        self.contact_graph = self._G_copy.copy()

    def set_quarantine(self) -> None:
        """
        Метод переводит граф в режим карантина и пересчитывает вероятности
        Вызывать только после set_ordinary или после инициализации!

        :return:
        """
        # сохраняем текущее состояние
        self.ordinary_contact_graph = self.contact_graph.copy()

        self.contact_graph = self.lockdown_contact_graph.copy()
        # переносим состояния вершин в новый граф
        for node_num, node in self.ordinary_contact_graph.nodes.data():
            node_state = node['state']

            self.contact_graph.nodes[node_num]['state'] = node_state

        # вычищаем старые вероятности
        for node_num, node in self.contact_graph.nodes.data():
            if 'prob' in node.keys():
                del self.contact_graph.nodes[node_num]['prob']

        # пересчитываем вероятности для согласованности
        self._G_copy = self.contact_graph.copy()
        self.eval_probs()

    def set_ordinary(self) -> None:
        """
                Метод переводит граф в стандартный режим и пересчитывает вероятности
                Вызывать только после set_quarantine!

                :return:
                """
        # сохраняем текущее состояние
        self.lockdown_contact_graph = self.contact_graph.copy()

        self.contact_graph = self.ordinary_contact_graph.copy()
        # переносим состояния вершин в новый граф
        for node_num, node in self.ordinary_contact_graph.nodes.data():
            node_state = node['state']

            self.contact_graph.nodes[node_num]['state'] = node_state

        # вычищаем старые вероятности
        for node_num, node in self.contact_graph.nodes.data():
            if 'prob' in node.keys():
                del self.contact_graph.nodes[node_num]['prob']

        # пересчитываем вероятности для согласованности
        self._G_copy = self.contact_graph.copy()
        self.eval_probs()


# # Tests
# import graphs_generators as gr_gen
# import numpy as np
# import matplotlib.pyplot as plt
#
# G_ordinary = gr_gen.random_working_graph(5, 5)
# G_home = gr_gen.random_home_graph(5, 2)
# init_distr = [NodeStates(np.random.random_integers(1, 2)) for i in range(len(G_ordinary.nodes))]
#
# epidemic = EpidemicWithLockdown(G_ordinary, init_distr, G_home, 0.3, 0.1, 0.4)
#
# plt.subplot(132)
# nx.draw_networkx(epidemic.contact_graph, with_labels=True)
# # nx.draw(epidemic.lockdown_contact_graph, node_color='orange', with_labels=True)
# # plt.show()
#
# epidemic.eval_probs()
# print(epidemic.contact_graph.nodes.data())
# epidemic.set_quarantine()
# print(epidemic.contact_graph.nodes.data())
# epidemic.set_ordinary()
# print(epidemic.contact_graph.nodes.data())

