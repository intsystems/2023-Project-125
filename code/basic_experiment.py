import numpy as np
import matplotlib.pyplot as plt
from SEIRS_lib.models import *
from typing import List

# make click on the given set of nodes
def make_click(nodes: List[int], graph: np.ndarray) -> None:
    for i in nodes:
        for j in nodes:
            graph[i][j] = 1

# функция для причёсывания массива beta
def fix_beta(x: float) -> float:
    if x < 1:
        return 1 + np.random.rand()
    else:
        return x

# кол-во разных моделей
num_of_networks = 3

# кол-во вершин в графе
num_of_nodes = np.array([10, 100, 500])

# выбираем случайное кол-во узлов в графе
num_of_edges = np.empty(3, dtype=int)

for i in range(num_of_networks):
    max_num_of_edges = num_of_nodes[i] * (num_of_nodes[i] - 1) // 2
    num_of_edges[i] = max_num_of_edges // 2 + np.random.randint(0, max_num_of_edges // 2)

# инициализируем графы
graphs = []
graphs_quar = []

for i in range(num_of_networks):
    graphs.append(np.zeros((num_of_nodes[i], num_of_nodes[i]), dtype=int))
    graphs_quar.append(np.zeros((num_of_nodes[i], num_of_nodes[i]), dtype=int))

    # строим обычный граф
    for j in range(num_of_edges[i]):
        a, b = np.random.randint(0, num_of_nodes[i], 2)
        while a == b or graphs[i][a][b] == 1:
            a, b = np.random.randint(0, num_of_nodes[i], 2)

        graphs[i][a][b] = 1
        graphs[i][b][a] = 1

    # строим граф карантина
    # это будет набор из клик случайного размера от 2 до 5

    cur_size = num_of_nodes[i]
    cur_click_size = np.random.randint(2, 6)
    cur_index = 0

    while cur_size - cur_click_size > 0:
        make_click(np.arange(cur_index, cur_index + cur_click_size), graphs_quar[i])
        cur_index += cur_click_size
        cur_size -= cur_click_size
        cur_click_size = np.random.randint(2, 6)

    # последняя клика
    make_click(np.arange(cur_index, num_of_nodes[i]), graphs_quar[i])

# запускаем эпидемии на каждом графе
for net_num in range(num_of_networks):
    # задаём эпидемию без локдауна, параметры заданы ниже
    isolation_t = 10
    beta_array = np.random.normal(2, 1, num_of_nodes[net_num])
    beta_array = np.array(list(map(fix_beta, beta_array)))
    beta_array = 1 / beta_array
    ordinary_model = SEIRSNetworkModel(G=graphs[net_num], beta=beta_array, sigma=0.9, gamma=0.3,
                                       G_Q=graphs_quar[net_num],
                                       transition_mode="time_in_state", initE=num_of_nodes[net_num] // 10,
                                       isolation_time=isolation_t)

    # сэмплируем эпидемию до локдауна
    # ordinary_model.run(T=10)
    while (ordinary_model.t < 10):
        ordinary_model.run_iteration()

    # отметки начала/конца локдауна
    time_stamp_start = len(ordinary_model.tseries)
    time_stamp_finish = time_stamp_start
    time_start = ordinary_model.tseries[len(ordinary_model.tseries) - 1]

    # создаём модель с локдауном
    quar_model = ordinary_model
    for node in range(num_of_nodes[net_num]):
        quar_model.set_isolation(node, True)

    # продолжаем итерации до конца карантина
    while (ordinary_model.t < 10 + isolation_t):
        ordinary_model.run_iteration()
    while (quar_model.t < 10 + isolation_t):
        quar_model.run_iteration()
    # ordinary_model.run(T=isolation_t)
    # quar_model.run(T=isolation_t)

    time_stamp_finish = len(ordinary_model.tseries)
    time_finish = time_start + isolation_t

    # запускаем ещё на некоторое время
    while (ordinary_model.t < 10 + isolation_t + 10):
        ordinary_model.run_iteration()
    while (quar_model.t < 10 + isolation_t + 10):
        quar_model.run_iteration()
    # ordinary_model.run(T=10)
    # quar_model.run(T=10)

    # отрисовка эволюции кол-ва больных
    ord_infect = ordinary_model.numI
    quar_infect_free = quar_model.numI
    quar_infect_isol = quar_model.numQ_I

    fig, axis = plt.subplots()
    axis.plot(ordinary_model.tseries[::2], quar_infect_free[::2], color='red', label='quarantine_free', alpha=0.6)
    axis.plot(ordinary_model.tseries[::2], quar_infect_isol[::2], color='pink', label='quarantine_isol', alpha=0.6)
    axis.plot(quar_model.tseries[::2], ord_infect[::2], color='blue', label='natural', alpha=0.6)
    # линия введения дня карантина
    axis.plot([time_start, time_start],
              [-0.5, 0.5],
              label='lockdown_start', color='green', linewidth=2)
    axis.plot([time_finish, time_finish],
              [-0.5, 0.5],
              label='lockdown_end', color='green', linewidth=2)

    axis.set_xlabel("$ t $")
    axis.set_ylabel("V(I)")
    axis.legend()
    axis.grid(True)

    plt.show()
    pass








