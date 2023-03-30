from view_epidemics import *


graph_size = 10

# полный граф
G_ordinary: nx.Graph = nx.complete_graph(graph_size)

# задаём веса для G_ordinary
for edge in G_ordinary.edges.data():
    edge_data = edge[2]
    edge_data['w'] = 1

# клики по 3 вершины, в каждой будет по 1 заражённому
G_home = nx.Graph()
G_home.add_nodes_from(list(range(graph_size)))
for i in range(0, graph_size, 3):
    next_click_size = 3
    if i + 3 > graph_size - 1:
        next_click_size = graph_size - i
    G_home = nx.compose(G_home, nx.complete_graph(list(range(i, i + next_click_size))))

# задаём веса для G_home
for edge in G_home.edges.data():
    edge_data = edge[2]
    edge_data['w'] = 1

init_distr = [NodeStates.Infected if i % 3 == 0 else NodeStates.Sucept for i in range(len(G_ordinary.nodes))]

epidemic = EpidemicWithLockdown(G_ordinary, init_distr, G_home, 0.2, 0.7, 0.7)
sampler = SamplerWithLockdown(epidemic, (5, 10))
comparasion_sampler = ComparasionSampler(sampler)
comp_view = ViewComparasion(comparasion_sampler)

lockdown_days = sampler.lockdown_days
comp_view.visualize_current_state()
for time in range(20):
    if time == lockdown_days[0] + 1:
        comp_view.visualize_current_state()

    comparasion_sampler.make_one_step()

comp_view.visualize_current_state()
comp_view.plot_numerical_dynamics().show()