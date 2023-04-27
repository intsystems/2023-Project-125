from copy import copy
import networkx as nx
import numpy as np
from typing import Dict
from typing import List
from enum import Enum


class NodeStates(Enum):
    """
        Синонимы для состояний вершин
    """
    Sucept = 0
    Infected = 1
    Recovered = 2


class MarkovChain:
    """
        Класс-реализация цепи Маркова в контексте решаемой задачи
    """

    def __init__(self, graph: nx.Graph, init_distr: Dict, epidemic_par: List):
        """

        :param graph: граф эпидемии (взвешенный, параметр 'w' для рёбер)
        :param init_distr: начальное распределение для всех вершин в виде словаря {node_num -> [S, I, R]}
        :param epidemic_par: парметры эпидемии в виде [\\gamma, \\sigma, \\beta]
        """
        self.chain = graph
        self.init_distr = init_distr
        self.params = epidemic_par

        # инициализируем все вершины нач. распределениями
        for node_num in self.chain.nodes.keys():
            self.chain.nodes[node_num][0] = init_distr[node_num][0]
            self.chain.nodes[node_num][1] = init_distr[node_num][1]
            self.chain.nodes[node_num][2] = init_distr[node_num][2]

    def time_step(self):
        """
        пересчитываем вероятности по правилам из статьи, т.е. по сути делаем один верменной шаг

        :return:
        """
        # сохраняем все данные по вершинам
        verts = dict(self.chain.nodes.data()).copy()
        # параметры эпидемии
        beta = self.params[2]
        gamma = self.params[0]
        sigma = self.params[1]

        for node_num, node_attrs in self.chain.nodes.data():
            # считаем A_v (см. статью)
            A_v = 1
            # соседи
            neigb_nums = list(self.chain.adj[node_num])

            for neigb_num in neigb_nums:
                # вес ребра
                cur_weight = self.chain[node_num][neigb_num]['w']
                # P(neigb_num) in I
                cur_prob_I = verts[neigb_num][1]
                A_v *= (1 - beta * cur_weight * cur_prob_I)

            # собственно пересчёт
            # для вероятности быть в S
            self.chain.nodes[node_num][0] = gamma * verts[node_num][2] + verts[node_num][0] * A_v
            # для вероятности быть в I
            self.chain.nodes[node_num][1] = (1 - sigma) * verts[node_num][1] + verts[node_num][0] * (1 - A_v)
            # для вероятности быть в R
            self.chain.nodes[node_num][2] = sigma * verts[node_num][1] + (1 - gamma) * verts[node_num][2]

    def set_init(self):
        """
        Переводит цепь в начальное состояние

        :return:
        """
        for node_num in self.chain.nodes.keys():
            self.chain.nodes[node_num][0] = self.init_distr[node_num][0]
            self.chain.nodes[node_num][1] = self.init_distr[node_num][1]
            self.chain.nodes[node_num][2] = self.init_distr[node_num][2]

    def expected_value(self, state: NodeStates) -> float:
        """
        Метод для подсчёта матожидания кол-ва узлов типа state

        :param state: для какого состояние считать матожидание
        :return:
        """
        # переводим enum в int
        node_state = state.value
        ans: float = 0
        for node_data in self.chain.nodes.data():
            # вытаскиваем аттрибуты вершины
            node_attrs = node_data[1]
            ans += node_attrs[node_state]

        return ans

