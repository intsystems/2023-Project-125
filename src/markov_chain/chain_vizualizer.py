from . import markov_chain
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx


class ChainVisualizer:
    """
        Класс делает шаги по времени для цепи Маркова и визуализирует эволюцию цепи
    """

    def __init__(self, chain: markov_chain.MarkovChain):
        self.chain = chain

    def draw_edges(self, ax=None):
        """
        Отображение рёбер

        :param ax: объект Axis для matplotlib
        :return:
        """
        # конфигурация для отображения рёбер
        edge_colormap = mpl.colormaps['cool']
        vmin_edges = 0
        vmax_edges = 100
        node_size = 600
        line_width_node = 3

        # формируем массив цветов для рёбер
        edge_colors = []
        for edge_u, edfe_v, edge_attrs in self.chain.chain.edges.data():
            # берём вес
            edge_weight = edge_attrs['w']

            edge_colors.append(edge_weight * 100)

        edges_viz = nx.draw_networkx_edges(self.chain.chain, ax=ax, pos=nx.drawing.circular_layout(self.chain.chain),
                                           edge_color=edge_colors, edge_cmap=edge_colormap, edge_vmin=vmin_edges,
                                           edge_vmax=vmax_edges, node_size=node_size + line_width_node)

        return edges_viz

    def draw_nodes(self, ax=None):
        """
        Отображение вершин

        :param ax: объект Axis для matplotlib
        :return:
        """

        # конфигурация для отображения вершин
        node_colormap = mpl.colormaps['RdYlGn']
        vmin_nodes = -100
        vmax_nodes = 100
        node_size = 600
        line_width_node = 3

        # формуируем массив цветов для вершин и их границ, а также прозрачность
        node_colors = []
        node_edge_colors = []
        alpha_nodes = []
        for node, node_atrr in self.chain.chain.nodes.data():
            # распределение вероятностей
            pos_S = node_atrr[0]
            pos_I = node_atrr[1]
            pos_R = node_atrr[2]

            node_colors.append(int(100 * (pos_S - pos_I) / (pos_S + pos_I)))
            node_edge_colors.append(mpl.colors.hsv_to_rgb((256.0 / 358.0, pos_R, 1.0)))
            alpha_nodes.append(pos_S + pos_I)

        # рисуем вершины
        nodes_viz = nx.draw_networkx_nodes(self.chain.chain, ax=ax, pos=nx.drawing.circular_layout(self.chain.chain),
                                           node_size=node_size, node_color=node_colors, cmap=node_colormap,
                                           vmin=vmin_nodes, vmax=vmax_nodes, linewidths=line_width_node,
                                           edgecolors=node_edge_colors, alpha=alpha_nodes)

        return nodes_viz

    def make_animation(self, time: int = 3):
        """
        Делаем шаги во времени, после чего выводим анимированную картинку

        :param:time: кол-во шагов во времени для симуляции
        :return: обект Figure и обект анимации
        """

        # создаём холст и отрисовку рёбер (она не меняется)
        fig, ax = plt.subplots(figsize=(15, 10))
        edge_viz = self.draw_edges(ax)
        node_viz = self.draw_nodes(ax)

        # добавим colorbar для вершин
        norm_1 = mpl.colors.Normalize(vmin=-1, vmax=1)
        cmap_1 = mpl.colormaps['RdYlGn']
        fig.colorbar(mpl.cm.ScalarMappable(norm=norm_1, cmap=cmap_1), ax=ax, fraction=0.05, orientation='vertical', label='I-S')

        # добавим colorbar для границ вершин
        norm_2 = mpl.colors.Normalize(vmin=0, vmax=1)
        cmap_2 = mpl.colormaps['BuPu']
        fig.colorbar(mpl.cm.ScalarMappable(norm=norm_2, cmap=cmap_2), ax=ax, fraction=0.05, orientation='vertical', label='R (node edge color)')

        # добавим colorbar для рёбер
        norm_3 = mpl.colors.Normalize(vmin=0, vmax=1)
        cmap_3 = mpl.colormaps['cool']
        fig.colorbar(mpl.cm.ScalarMappable(norm=norm_3, cmap=cmap_3), ax=ax, fraction=0.05, 
                    location='left', orientation='vertical', label='Edges')

        # делаем шаги по времени
        def update(frame):
            if frame == 0:
                self.chain.set_init()

            self.chain.time_step()
            node_viz = self.draw_nodes(ax)
            ax.set_title(f'Frame {frame}')

        # объект анимации
        ani = animation.FuncAnimation(fig=fig, func=update, frames=time, interval=70, repeat=True)
        ani.save(filename=r'D:\6 sem\IS Lockdown\2023-Project-125\figs\markov_visualization.gif',
                 writer='pillow', fps=4)
        # plt.show()


