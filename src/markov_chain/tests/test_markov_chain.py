# Tests
from typing import Type
import pytest
from pytest import FixtureRequest
from src.markov_chain.markov_chain import MarkovChain
from src.markov_chain.markov_chain import NodeStates
from src.graphs_generators import *


@pytest.fixture()
def greeting_fixt(request: Type[FixtureRequest]):
    print("Diving into test for one init")

@pytest.fixture()
def chain_creation(request: Type[FixtureRequest]):
    # граф эпидемии
    graph = random_working_graph(5, 5)
    # делаем начальное распределение
    init_distr = np.random.rand(5, 3)
    init_distr = init_distr / np.sum(init_distr, axis=1).reshape(5, 1)

    chain = MarkovChain(graph, init_distr, epidemic_par=[0.3, 0.3, 0.3])

    return chain


def test_init_chain(greeting_fixt: None):
    # граф эпидемии
    graph = random_working_graph(5, 5)
    # делаем начальное распределение
    init_distr = np.random.rand(5, 3)
    init_distr = init_distr / np.sum(init_distr, axis=1).reshape(5, 1)

    chain = MarkovChain(graph, init_distr, epidemic_par=[0.3, 0.3, 0.3])

    for node_num in list(chain.chain.nodes):
        assert init_distr[node_num][0] == chain.chain.nodes[node_num][0]
        assert init_distr[node_num][1] == chain.chain.nodes[node_num][1]
        assert init_distr[node_num][2] == chain.chain.nodes[node_num][2]


def test_one_step():
    # граф эпидемии
    graph = random_working_graph(5, 5)
    # делаем начальное распределение
    init_distr = np.random.rand(5, 3)
    init_distr = init_distr / np.sum(init_distr, axis=1).reshape(5, 1)

    chain = MarkovChain(graph, init_distr, epidemic_par=[0.3, 0.3, 0.3])

    chain.time_step()


def test_several_steps():
    # время симулирования эпидемии
    T = 500
    # граф эпидемии
    graph = random_working_graph(5, 5)
    # делаем начальное распределение
    init_distr = np.random.rand(5, 3)
    init_distr = init_distr / np.sum(init_distr, axis=1).reshape(5, 1)

    chain = MarkovChain(graph, init_distr, epidemic_par=[0.3, 0.3, 0.3])

    # наблюдаем за одной вершиной
    for i in range(T):
        if i % 50 == 0:
            print(f"Distribution on step {i} is {chain.chain.nodes[0]}\n")

        chain.time_step()


def test_expected_value(chain_creation: MarkovChain):
    """
    Тест рассчёта среднего кол-ва вершин того или иного типа
    """
    chain: MarkovChain = chain_creation

    # считаем матожидание для каждого класса вершин
    all_nodes = 0

    for state in range(3):
        cur_expected_val = chain.expected_value(NodeStates(state))
        print(f"Expected val of {NodeStates(state).__str__()} is {cur_expected_val}\n")
        all_nodes += cur_expected_val

    assert abs(all_nodes - len(chain.chain.nodes)) < 1e-2



