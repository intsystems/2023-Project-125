import numpy as np

from epidemic_model import *

class BasicSampler:
    """
    Базовый класс сэмплирования эпидемии. Умеет делать одну итерацию
    моделирования эпидемии
    """

    def __init__(self, epidemic: BasicEpidemic):
        """

        :param epidemic: эпидемия для сэмплирования
        """
        self.epidemic = epidemic
        # массив для хранения состояния вершин на каждой итерации
        self.node_states = []

    def _next_state(self, cur_state: NodeStates) -> NodeStates:
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
        for node in self.epidemic.contact_graph.nodes:
            if np.random.rand() >= node['prob']:
                node['state'] = self._next_state(node['state'])

        # пересчитываем вероятности
        self.epidemic.eval_probs()

    def _save_cur_state(self):
        """
        Сохраняет текущее состояние всех вершин
        :return:
        """
        # выделяю память под текущюю итерацию
        self.node_states.append(np.empty(self.epidemic.contact_graph.number_of_nodes()))
        cur_stage = len(self.node_states) - 1

        for node in self.epidemic.contact_graph.nodes:
            # сохраняю состояние
            self.node_states[cur_stage][node.key] = node['state']

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
    def __init__(self, epidemic: EpidemicWithLockdown, lockdown_days: Tuple[int]):
        """
        :param epidemic:
        :param lockdown_days: номер итерации для начала и конца эпидемии (невключительно; нумерация от единицы)
        """
        super().__init__(epidemic)

        self.lockdown_days = lockdown_days
        # переводим время начала и конца в интервал от 0 до N
        self.lockdown_days[0] -= 1
        self.lockdown_days[1] -= 1

    def _make_iteration(self) -> None:
        """
        Делает по две итерации в зависимости от времени для моделирования "реальной жизни"
        См. описание класса
        :return:
        """
        cur_step = len(self.node_states) - 1

        if cur_step < self.lockdown_days[0]:
            super()._make_iteration()
            self.epidemic.set_quarantine()
            super()._make_iteration()
            self.epidemic.set_ordinary()
        elif cur_step >= self.lockdown_days[0] and cur_step < self.lockdown_days[1]:
            # ставим режим карантина в начале локдауна
            if cur_step == self.lockdown_days[0]:
                self.epidemic.set_quarantine()

            super()._make_iteration()
            super()._make_iteration()
        else:
            # снимаем режим карантина в конце локдауна
            if cur_step == self.lockdown_days[1]:
                self.epidemic.set_ordinary()

            super()._make_iteration()
            self.epidemic.set_quarantine()
            super()._make_iteration()
            self.epidemic.set_ordinary()


