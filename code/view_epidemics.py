from epidemic_sampling import *
import matplotlib.pyplot as plt
from typing import Tuple

class ViewEpidemic:
    """
    Класс базовой отрисовки хода эпидемии
    """
    def __init__(self, sampler: BasicSampler):
        """

        :param sampler: сэмплер эпидемии
        """
        self.sampler = sampler
        # триггеры отрисовки динамики эпидемии
        self.triggers = {NodeStates.Infected: True, NodeStates.Sucept: False, NodeStates.Recovered: False}


    def _get_num_of_node_by_class(self, node_type: NodeStates):
        """
        Функция возвращает массив кол-ва веришин заданного типа на каждой итерации

        :param node_type: тип искомых вершин (S, I, R)
        :return:
        """
        ans_ar = np.array(self.sampler.node_states)
        for i in range(len(ans_ar)):
            ans_ar[i] = ans_ar[i][ans_ar[i] == node_type]

        # вычисляем кол-во вершин искомого класса на каждой итерации
        ans = ans_ar.sum(axis=1) / node_type.value

        return ans


    def plot_numerical_dynamics(self, fig_size: Tuple[float, float]) -> plt.Figure:
        """
        Метод отрисовывает динамику эпидемии по числу вершин в разных классах в течении
        моделирования эпидемии

        :param fig_size: размер картинки на выходе
        :return:
        """
        # массив из номеров итераций
        iter_nums = range(len(self.sampler.node_states))
        data_to_plot = list()

        # проходимся по тригерам, сохраняем данные для графика
        # и названия типа отрисовываемых вершин
        for key, val in self.triggers:
            if val:
                data = self._get_num_of_node_by_class(key)
                data_to_plot.append((data, key.name))

        fig, axis = plt.subplots(fig_size=fig_size)

        for data in data_to_plot:
            axis.plot(iter_nums, data[0], label=data[1], marker='.', markersize=5)

        axis.set_xlabel(r'$ t $')
        axis.set_ylabel(r'Num of nodes')
        axis.grid(True)
        axis.legend()

        return fig


