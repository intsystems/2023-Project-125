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

    def __init__(self, G: nx.Graph, ini_distr: List[int]):
        """

        :param G: граф контактов
        :param ini_distr:  начальное распределение больных
        """
        self.contact_graph = G
        self._ini_distr = ini_distr

        # инициализируем граф переданными начальными условиями
        for node in self.contact_graph.nodes:
            self.contact_graph[node]["state"] = ini_distr[node]

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
        self.personal_suceptabilities = beta

        # техническая копия текущего графа для корректного пересчёта вероятностей
        self._G_copy = G

    def _eval_individ_prob(self, n: int) -> None:
            """
                рассчитывает вероятность перехода в следующее состояние для данной вершины
            """
            if self.contact_graph[n]['state'] == NodeStates.Infected:
                self._G_copy[n]['prob'] = self.I_to_R_prob
            elif self.contact_graph[n]['state'] == NodeStates.Recovered:
                self._G_copy[n]['prob'] = self.R_to_S_prob
            elif self.contact_graph[n]['state'] == NodeStates.Sucept:
                # берём индивидуальную восприимчивость
                personal_sucept = None
                if type(self.personal_suceptabilities) is list:
                    personal_sucept = self.personal_suceptabilities[n]
                else:
                    personal_sucept = self.personal_suceptabilities

                # берём номера всех больных соседей
                infected_neighbours = list(filter(lambda x: x['state'] == NodeStates.Infected, self.contact_graph.adj[n]))
                infected_neighbours = list(map(lambda x: x.key, infected_neighbours))

                # считаем вероятность заразиться
                cur_prob = 1
                for neigb in infected_neighbours:
                    cur_prob *= 1 - personal_sucept * self.contact_graph[n][neigb]['w']
                cur_prob = 1 - cur_prob

                self._G_copy[n]['prob'] = cur_prob

    def eval_probs(self) -> None:
            super().eval_probs()

            # обновляем наш граф
            self.contact_graph = self._G_copy

    def set_quarantine(self) -> None:
        """
        Метод переводит граф в режим карантина.
        Вызывать только после set_ordinary или после инициализации!

        :return:
        """
        # сохраняем текущее состояние
        self.ordinary_contact_graph = self.contact_graph

        self.contact_graph = self.lockdown_contact_graph
        # переносим состояния вершин в новый граф
        for nodes in self.ordinary_contact_graph:
            node_num = nodes.key
            node_state = node_num['state']

            self.contact_graph[node_num]['state'] = node_state

        # пересчитываем вероятности для согласованности
        self.eval_probs()

    def set_ordinary(self) -> None:
        """
                Метод переводит граф в стандартный режим.
                Вызывать только после set_quarantine!

                :return:
                """
        # сохраняем текущее состояние
        self.lockdown_contact_graph = self.contact_graph

        self.contact_graph = self.ordinary_contact_graph
        # переносим состояния вершин в новый граф
        for nodes in self.lockdown_contact_graph:
            node_num = nodes.key
            node_state = node_num['state']

            self.contact_graph[node_num]['state'] = node_state

        # пересчитываем вероятности для согласованности
        self.eval_probs()



