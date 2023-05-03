# Tests
import pytest
from src.markov_chain.markov_chain import MarkovChain
from src.markov_chain.markov_chain import NodeStates
from src.graphs_generators import *
from src.markov_chain.chain_vizualizer import ChainVisualizer

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation


@pytest.fixture()
def chain_creation(request):
    # граф эпидемии
    graph = random_working_graph(6, 9)
    # делаем начальное распределение
    init_distr = np.random.rand(6, 3)
    init_distr = init_distr / np.sum(init_distr, axis=1).reshape(6, 1)

    chain = MarkovChain(graph, init_distr, epidemic_par=[0.3, 0.3, 0.5])

    return chain


@pytest.fixture()
def chain_creation_all_sick(request):
    # граф эпидемии
    graph = random_working_graph(6, 9)
    # делаем начальное распределение
    init_distr = np.array([0.0, 1.0, 0.0])
    init_distr = np.ones((6, 3)) * init_distr

    chain = MarkovChain(graph, init_distr, epidemic_par=[0.3, 0.3, 0.5])

    return chain


def test_viz_one_frame(chain_creation_all_sick):
    chain: MarkovChain = chain_creation_all_sick

    chain_viz = ChainVisualizer(chain)

    fig, ax = plt.subplots(figsize=(15, 15))
    node_viz = chain_viz.draw_nodes(ax)
    edge_viz = chain_viz.draw_edges(ax)
    fig.show()

    chain_viz.chain.time_step()
    node_viz = chain_viz.draw_nodes(ax)
    fig.show()


def test_animation(chain_creation):
    chain: MarkovChain = chain_creation

    chain_viz = ChainVisualizer(chain)
    chain_viz.make_animation(25)
    #plt.show()



