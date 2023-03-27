from epidemic_sampling import *
import matplotlib.pyplot as plt
from typing import List, Tuple


class ViewEpidemic:
    """
    Класс базовой отрисовки хода эпидемии
    """
    def __init__(self, sampler: BasicSampler, fig_size = (10, 10)):
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

        :param fig_size: размер картинки на выходе
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
    def get_node_color(node_type: NodeStates):
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
            color_states.append(self.get_node_color(node_info['state']))

        # заголовок рисунка
        cur_step = len(self.sampler.node_states) - 1

        nx.draw_networkx(G=cur_graph, pos=nx.circular_layout(cur_graph), node_color=color_states, with_labels=True,
                         label=f'Current step = {cur_step}')
        plt.show()


# Tests
import graphs_generators as gr_gen
import numpy as np

G_ordinary = gr_gen.random_working_graph(10, 20)
G_home = gr_gen.random_home_graph(10, 3)
init_distr = [NodeStates(np.random.random_integers(1, 2)) for i in range(len(G_ordinary.nodes))]

epidemic = EpidemicWithLockdown(G_ordinary, init_distr, G_home, 0.3, 0.8, 0.4)
epidemic_sampler = SamplerWithLockdown(epidemic, lockdown_days=(10, 20))
epidemic_view = ViewEpidemic(epidemic_sampler)

# epidemic_sampler.make_one_step()
# epidemic_sampler.make_one_step()
# epidemic_sampler.make_one_step()
# epidemic_view.plot_numerical_dynamics()
# plt.show()

epidemic_view.visualize_current_state()
for day in range(30):
    if day in epidemic_sampler.lockdown_days:
        epidemic_view.visualize_current_state()
        epidemic_sampler.make_one_step()
        epidemic_view.visualize_current_state()
        continue

    epidemic_sampler.make_one_step()

epidemic_view.plot_numerical_dynamics().show()

