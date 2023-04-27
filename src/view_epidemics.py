"""
    В модуле описываются классы для графического отображения протекания эпидемии.
     Реализованы отображения трэков кол-ва вершин разных классов во времени. Также отображение графов контактов
     в конкретные моменты времени

"""

import networkx as nx

from epidemic_sampling import *
import matplotlib.pyplot as plt
from typing import List, Tuple


class ViewEpidemic:
    """
    Класс базовой отрисовки хода эпидемии
    """
    def __init__(self, sampler: SamplerWithLockdown, fig_size=(10, 10)):
        """

        :param sampler: сэмплер эпидемии
        :param fig_size: размер графиков
        """
        self.fig_size = fig_size
        self.sampler = sampler
        # триггеры отрисовки динамики эпидемии
        self.triggers = {NodeStates.Infected: True, NodeStates.Sucept: False, NodeStates.Recovered: False}

    def _get_num_of_nodes_by_class(self, node_type: NodeStates):
        """
        Функция возвращает массив кол-ва веришин заданного типа на каждой итерации

        :param node_type: тип искомых вершин (S, I, R)
        :return:
        """
        ans_ar = np.array(self.sampler.node_states, dtype=int)
        for i in range(len(self.sampler.node_states)):
            flag_func = np.vectorize(lambda x: x if x == node_type.value else 0)
            ans_ar[i] = flag_func(ans_ar[i])

        # вычисляем кол-во вершин искомого класса на каждой итерации
        ans = ans_ar.sum(axis=1) / node_type.value

        return ans

    def plot_numerical_dynamics(self) -> plt.Figure:
        """
        Метод отрисовывает динамику эпидемии по числу вершин в разных классах в течении
        моделирования эпидемии

        :return:
        """

        # дни локдауна
        lockdown_days = self.sampler.lockdown_days
        # макс. значение кол-ва вершин того или иного типа за всё время
        # для красивой отрисовки границы локдауна
        max_nodes_num = 0

        # массив из номеров итераций
        iter_nums = list(range(len(self.sampler.node_states)))
        data_to_plot = list()

        # проходимся по тригерам, сохраняем данные для графика
        # и названия типа отрисовываемых вершин
        for key, val in self.triggers.items():
            if val:
                data = self._get_num_of_nodes_by_class(key)
                data_to_plot.append((data, key.name))

        fig, axis = plt.subplots(figsize=self.fig_size)

        for data in data_to_plot:
            axis.plot(iter_nums, data[0], label=data[1], marker='.', markersize=10)
            max_nodes_num = np.max([np.max(data[0]), max_nodes_num])

        # отрисовка границ локдауна
        if lockdown_days[0] != -1:
            for day in lockdown_days:
                axis.plot(np.repeat(day, 2), [0, max_nodes_num + 0.5], color='red', label='lockdown')

        axis.set_xlabel(r'$ t $')
        axis.set_ylabel(r'Num of nodes')
        axis.grid(True)
        axis.legend()

        return fig

    @staticmethod
    def _get_node_color(node_type: NodeStates):
        """
            Цвет вершины для визуализации графа
        """
        if node_type == NodeStates.Sucept:
            return '#77FF00'
        if node_type == NodeStates.Infected:
            return '#FF0A27'
        if node_type == NodeStates.Recovered:
            return '#009DFF'

    def visualize_current_state(self):
        cur_graph = self.sampler.epidemic.contact_graph
        # массив цветов для раскраски вершин
        color_states = []

        for node_num, node_info in cur_graph.nodes.data():
            color_states.append(self._get_node_color(node_info['state']))

        # заголовок рисунка
        cur_step = len(self.sampler.node_states) - 1

        fig, axis = plt.subplots(1, figsize=self.fig_size)
        nx.draw_networkx(G=cur_graph, pos=nx.circular_layout(cur_graph), node_color=color_states, with_labels=True,
                         ax=axis)

        axis.set_title(f'Cur step = {cur_step}')
        fig.show()


class ViewComparasion:
    """
        Класс слежения за протеканием эпидемии с и без локдауна
    """
    def __init__(self, comp_sampler: ComparasionSampler):
        self.comp_sampler = comp_sampler

        self.lk_view = ViewEpidemic(comp_sampler.lockdown_sampler)
        self.no_lk_view = ViewEpidemic(comp_sampler.no_lockdown_sampler)

        # техническая переменная для настройки отображения эпидемии без локдауна; флаг
        self._changed_mode = False

    @staticmethod
    def _get_node_color(node_type: NodeStates):
        """
            Цвет вершины для визуализации графа
        """
        if node_type == NodeStates.Sucept:
            return '#77FF00'
        if node_type == NodeStates.Infected:
            return '#FF0A27'
        if node_type == NodeStates.Recovered:
            return '#009DFF'

    def _visualize_particular_state(self, sampler_from: BasicSampler, lk_code: int):
        """

        :param sampler_from: sampler для отрисовки его графа
        :param lk_code: аттрибут для отображения типа эпидемии: 0 - no lk, 1 - lk, 2 - common time
        :return:
        """
        cur_graph = sampler_from.epidemic.contact_graph
        # массив цветов для раскраски вершин
        color_states = []

        for node_num, node_info in cur_graph.nodes.data():
            color_states.append(self._get_node_color(node_info['state']))

        # заголовок рисунка
        cur_step = len(sampler_from.node_states) - 1
        lk_type = ''
        if lk_code == 0:
            lk_type = 'No lockdown'
        elif lk_code == 1:
            lk_type = 'With lockdown'
        else:
            lk_type = 'Common'

        fig, axis = plt.subplots(1, figsize=self.lk_view.fig_size)
        nx.draw_networkx(G=cur_graph, pos=nx.circular_layout(cur_graph), node_color=color_states, with_labels=True,
                         ax=axis)

        axis.set_title(f'Cur step = {cur_step}, epidemic type = {lk_type}')
        fig.show()

    def _get_data_from(self, cur_view: ViewEpidemic):
        """
        Метод возвращает данные для отображения из какой-то эпидемии

        :param cur_view: эпидемия, откуда берём данные
        :return:
        """

        data_to_plot = list()

        # проходимся по тригерам, сохраняем данные для графика
        # и названия типа отрисовываемых вершин
        for key, val in cur_view.triggers.items():
            if val:
                data = cur_view._get_num_of_nodes_by_class(key)
                data_to_plot.append((data, key.name))

        return data_to_plot

    def plot_numerical_dynamics(self) -> plt.Figure:
        """
        Метод отрисовывает динамику эпидемии по числу вершин в разных классах в течении
        моделирования эпидемии

        :return:
        """

        # дни локдауна
        lockdown_days = self.lk_view.sampler.lockdown_days
        # макс. значение кол-ва вершин того или иного типа за всё время
        # для красивой отрисовки границы локдауна
        max_nodes_num = 0

        # массив из номеров итераций
        iter_nums = list(range(len(self.lk_view.sampler.node_states)))

        data_from_lk = self._get_data_from(self.lk_view)

        fig, axis = plt.subplots(figsize=self.lk_view.fig_size)

        # до локдауна (или если его нет) отрисовываем один трек
        if self.comp_sampler.cur_day <= self.comp_sampler._independance_day:
            for data in data_from_lk:
                axis.plot(iter_nums, data[0], label=f'{data[1]} in lk_type', marker='.', markersize=10)
        # отрисовываем оба
        else:
            # проверяем здесь обновление состояния для эпидемии без локдауна
            if not self._changed_mode:
                self.no_lk_view = ViewEpidemic(self.comp_sampler.no_lockdown_sampler)
                self._changed_mode = True

            data_from_no_lk = self._get_data_from(self.no_lk_view)

            for data in data_from_lk:
                axis.plot(iter_nums, data[0], label=f'{data[1]} in lk_type', marker='.', markersize=10)
                max_nodes_num = np.max([np.max(data[0]), max_nodes_num])

            for data in data_from_no_lk:
                axis.plot(iter_nums, data[0], label=f'{data[1]} in no_lk_type', marker='.', markersize=10)
                max_nodes_num = np.max([np.max(data[0]), max_nodes_num])

            # собираем данные, общие для треков
            for data in data_from_no_lk:
                axis.plot(iter_nums[:self.comp_sampler._independance_day], data[0][:self.comp_sampler._independance_day],
                          label=f'{data[1]} in common', marker='.', markersize=15)

            # отрисовка границ локдауна
            if lockdown_days[0] != -1:
                for day in lockdown_days:
                    axis.plot(np.repeat(day, 2), [0, max_nodes_num + 0.5], color='red', label='lockdown')

        axis.set_xlabel(r'$ t $')
        axis.set_ylabel(r'Num of nodes')
        axis.grid(True)
        axis.legend()

        return fig

    def visualize_current_state(self):
        # всякий раз, когда нужно отрисовать, проверяем, не разделилась ли эпидемия
        if self.comp_sampler._independance_day < self.comp_sampler.cur_day:
            # проверка смены изображения для эпидемии без локдауна
            if not self._changed_mode:
                self.no_lk_view = ViewEpidemic(self.comp_sampler.no_lockdown_sampler)
                self._changed_mode = True

            self._visualize_particular_state(self.comp_sampler.lockdown_sampler, 1)
            self._visualize_particular_state(self.comp_sampler.no_lockdown_sampler, 0)
        else:
            self._visualize_particular_state(self.comp_sampler.lockdown_sampler, 2)

# Tests
import graphs_generators as gr_gen
import numpy as np
#
# G_ordinary = gr_gen.random_working_graph(10, 20)
# G_home = gr_gen.random_home_graph(10, 3)
# init_distr = [NodeStates(np.random.random_integers(1, 2)) for i in range(len(G_ordinary.nodes))]
#
# epidemic = EpidemicWithLockdown(G_ordinary, init_distr, G_home, 0.2, 0.3, 0.6)
# epidemic_sampler = SamplerWithLockdown(epidemic, lockdown_days=(10, 20))
# epidemic_view = ViewEpidemic(epidemic_sampler)
# epidemic_view.triggers[NodeStates.Recovered] = True
#
# # epidemic_sampler.make_one_step()
# # epidemic_sampler.make_one_step()
# # epidemic_sampler.make_one_step()
# # epidemic_view.plot_numerical_dynamics()
# # plt.show()
#
# epidemic_view.visualize_current_state()
# for day in range(30):
#     if day in epidemic_sampler.lockdown_days:
#         epidemic_view.visualize_current_state()
#         epidemic_sampler.make_one_step()
#         epidemic_view.visualize_current_state()
#         continue
#
#     epidemic_sampler.make_one_step()
#
# epidemic_view.plot_numerical_dynamics().show()

# G_ordinary = gr_gen.random_working_graph(10, 20)
# G_home = gr_gen.random_home_graph(10, 3)
# init_distr = [NodeStates(np.random.random_integers(1, 2)) for i in range(len(G_ordinary.nodes))]
#
# epidemic = EpidemicWithLockdown(G_ordinary, init_distr, G_home, 0.2, 0.7, 0.7)
# sampler = SamplerWithLockdown(epidemic, (5, 10))
# comparasion_sampler = ComparasionSampler(sampler)
# comp_view = ViewComparasion(comparasion_sampler)
#
# lockdown_days = sampler.lockdown_days
# comp_view.visualize_current_state()
# for time in range(20):
#     if time == lockdown_days[0] + 1:
#         comp_view.visualize_current_state()
#
#     comparasion_sampler.make_one_step()
#
# comp_view.visualize_current_state()
# comp_view.plot_numerical_dynamics().show()

