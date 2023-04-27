"""
    В модуле описываются классы, проводящие итерирование эпидемий во времени с сохранением характеристик
     эпидемии при её протекании.
"""

import numpy as np
from epidemic_model import *


class BasicSampler:
    """
    Базовый класс сэмплирования эпидемии. Умеет делать одну итерацию
    моделирования эпидемии. Сохраняет картину распределения вершин по болезни после каждой итерации
    """

    def __init__(self, epidemic: BasicEpidemic):
        """

        :param epidemic: эпидемия для сэмплирования
        """
        self.epidemic = epidemic
        # массив для хранения состояния вершин на каждой итерации
        self.node_states = []

        # оцениваем вероятности для начального распределения
        # корректно инициализируем эпидемию для сэмплирования
        self.epidemic.eval_probs()

    @staticmethod
    def _next_state(cur_state: NodeStates) -> NodeStates:
        """
        Возвращает следующее возможное состояние для вершины

        :param cur_state: текущее состояние
        :return:
        """
        if cur_state == NodeStates.Sucept:
            return NodeStates.Infected
        elif cur_state == NodeStates.Infected:
            return NodeStates.Recovered
        else:
            return NodeStates.Sucept

    def _make_iteration(self) -> None:
        """
        Делает один шаг итерации моделирования эпидемиию
        В конце каждой итерации должны оставаться в согласованом состоянии

        :return:
        """
        # сэмплируем
        for node in self.epidemic.contact_graph.nodes.data():
            node_info = node[1]
            if np.random.rand(1)[0] < node_info['prob']:
                node_info['state'] = self._next_state(node_info['state'])

        # пересчитываем вероятности
        self.epidemic.eval_probs()

    def _save_cur_state(self):
        """
        Сохраняет текущее состояние всех вершин. Тип сохраняется как число, которое можно
        преобразовать в NodeState

        :return:
        """
        # выделяю память под текущюю итерацию
        self.node_states.append(np.empty(self.epidemic.contact_graph.number_of_nodes()))
        cur_stage = len(self.node_states) - 1

        for node in self.epidemic.contact_graph.nodes.data():
            # сохраняю состояние
            node_info = node[1]
            node_number = node[0]
            self.node_states[cur_stage][node_number] = node_info['state'].value

    def copy(self):
        new_epidemic = self.epidemic.copy()
        node_states = self.node_states.copy()

        new_obj = BasicSampler(new_epidemic)
        new_obj.node_states = node_states

        return new_obj

    def make_one_step(self):
        """
        Метод делает шаг сэмлирования и сохраняет состояния вершин
        :return:
        """
        self._make_iteration()
        self._save_cur_state()

    def run_epidemic(self, t: int = 50):
        """
        Запускает t итераций

        :param t: кол-во итераций
        :return:
        """
        for i in range(t):
            self.make_one_step()


class SamplerWithLockdown(BasicSampler):
    """
    Класс для моделирования эпидемии с локдауном.
    Каждая итерация в обычном режиме: одно сэмплирование ordinary, одно home
    Каждая итерация в lockdown режиме: два сэмплирования home
    """
    def __init__(self, epidemic: EpidemicWithLockdown, lockdown_days: Tuple[int, int] = (-1, -1)):
        """
        :param epidemic:
        :param lockdown_days: номер итерации для начала и конца эпидемии (невключительно; нумерация от единицы)
        """
        super().__init__(epidemic)

        self.lockdown_days = list(lockdown_days)
        # переводим время начала и конца в интервал от 0 до N
        self.lockdown_days[0] -= 1
        self.lockdown_days[1] -= 1

    def _make_iteration(self) -> None:
        """
        Делает по две итерации в зависимости от времени для моделирования "реальной жизни"
        См. описание класса
        :return:
        """
        # номер очередной итерации (не старой)
        cur_step = (len(self.node_states) - 1) + 1
        cur_epidemic: EpidemicWithLockdown = self.epidemic

        if cur_step < self.lockdown_days[0]:
            super()._make_iteration()
            cur_epidemic.set_quarantine()
            super()._make_iteration()
            cur_epidemic.set_ordinary()
        elif self.lockdown_days[0] <= cur_step < self.lockdown_days[1]:
            # ставим режим карантина в начале локдауна
            if cur_step == self.lockdown_days[0]:
                cur_epidemic.set_quarantine()

            super()._make_iteration()
            super()._make_iteration()
        else:
            # снимаем режим карантина в конце локдауна
            if cur_step == self.lockdown_days[1]:
                cur_epidemic.set_ordinary()

            super()._make_iteration()
            cur_epidemic.set_quarantine()
            super()._make_iteration()
            cur_epidemic.set_ordinary()

    def copy(self) -> 'SamplerWithLockdown':
        """

        :return:
        """

        new_epidemic = self.epidemic.copy()
        lockdown_days = self.lockdown_days.copy()
        lockdown_days = list(map(lambda x: x + 1, lockdown_days))
        node_states = self.node_states.copy()

        new_obj = SamplerWithLockdown(new_epidemic, lockdown_days)
        new_obj.node_states = node_states

        return new_obj


class ComparasionSampler:
    """
    Сэмплер, хранящий внутри себя две версии эпидемии: с локдауном и без.
    До дня локдауна эпидемии совпадают. После же эпидемии эволюционируют независимо: одна с локдауном
    другая без.
    """
    def __init__(self, lockdown_sampler: SamplerWithLockdown):
        # два сэмплера изначально ссылаются на одно и то же
        self.lockdown_sampler = lockdown_sampler
        self.no_lockdown_sampler = lockdown_sampler
        # день, когда сэмплеры разделяться
        self._independance_day = lockdown_sampler.lockdown_days[0]
        # счётчик дней
        self.cur_day = 0

    def make_one_step(self):
        """
        Делает один шаг для каждого сэмплера

        :return:
        """
        # момент разделения
        if self.cur_day == self._independance_day:
            self.no_lockdown_sampler = self.lockdown_sampler.copy()
            # снимаем эпидемию для no_lockdown
            self.no_lockdown_sampler.lockdown_days = [-1, -1]

        if self.cur_day < self._independance_day:
            self.lockdown_sampler.make_one_step()
        else:
            self.lockdown_sampler.make_one_step()
            self.no_lockdown_sampler.make_one_step()

        self.cur_day += 1

    def run(self, t: int):
        """
        Итерируеся t раз

        :param t: кол-во итераций
        :return:
        """
        for i in range(t):
            self.make_one_step()



# # Tests
# import graphs_generators as gr_gen
# import numpy as np
#
# G_ordinary = gr_gen.random_working_graph(5, 5)
# G_home = gr_gen.random_home_graph(5, 2)
# init_distr = [NodeStates(np.random.random_integers(1, 2)) for i in range(len(G_ordinary.nodes))]
#
# epidemic = EpidemicWithLockdown(G_ordinary, init_distr, G_home, 0.3, 0.1, 0.4)
#
# epidemic_sampler = SamplerWithLockdown(epidemic, (2, 3))
# epidemic_sampler.make_one_step()
# epidemic_sampler.make_one_step()


