import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from addEdge import addEdge
import analysis as an

np.random.seed(1)

britannica_file = "Britannica_Network.csv"

brit_df = pd.read_csv(britannica_file)

starts, ends = (brit_df[col].values for col in ["First Node", "Second Node"])

seed_file = "seed_nodes.csv"

seed_nodes = pd.read_csv(seed_file)["Britannica"].values

node_to_link = {n:l for n,l in zip(*(brit_df[col].values
                               for col in ["First Node","First Link"]))}

def determine_node_color(node):
    if node_to_link[node] in seed_nodes:
        return "green"

    return "#ffa950"

def determine_node_shape(node):
    if node_to_link[node] in seed_nodes:
        return "diamond"

    return "circle"
         
edges = np.stack((starts,ends), axis=1)

brit_network = nx.DiGraph()
brit_network.add_edges_from(edges)


def visualize(G):
    # If the graph is disconnected, there will be different graphs centered around different points
    current_center = np.zeros(2)
    edge_x = []
    edge_y = []
    node_x = []
    node_y = []
    node_labels = []
    node_sizes = []
    node_shapes = []
    node_colors = []

    # Keep plotting disconnected pieces of the graph
    while True:
        terminations = an.count_terminations(G)

        importance = an.calculate_termination_centrality(G)
        most_important = max(importance, key = lambda x: importance[x])
        connected = set(n for n in importance if importance[n] > 0)

        # Plot the connected part of G
        g = G.subgraph(connected)

        pos = an.determine_node_positions(g, *current_center)

        # In case you're curious how the spring layout would go
        #pos = nx.spring_layout(G)

        for edge in g.edges():
            start = pos[edge[0]]
            end =   pos[edge[1]]
            edge_x, edge_y = addEdge(start, end, edge_x, edge_y, .8, 'end', .2, 30, an.termination_centrality_to_plot_size(importance[edge[1]]))
       

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        

        for n, (x,y) in pos.items():
            node_x.append(x)
            node_y.append(y)
            node_labels.append(n)
            node_sizes.append(an.termination_centrality_to_plot_size(importance[n]))
            node_shapes.append(determine_node_shape(n))
            node_colors.append(determine_node_color(n))
 
        # Now that we've plotted the connected nodes in G, remove them
        G.remove_nodes_from(connected)
        
        # If we've plotted all the disconnected subgraphs of G, stop
        if len(G.nodes) == 0:
            break

        """
        For each subsequent subgraph, we need to center it at
        a new location such that it never overlaps with any
        other graph. I increase the distance of the center
        based on the furthest point in the graph, then pick a
        random angle. This happened to work, but a better 
        method likely exists 
        """

        orbit_dist = 1.5 * max(np.sqrt((x-current_center[0])**2 + (y-current_center[1])**2) for x,y in pos.values())

        orbit_angle = np.random.rand() * 2 * np.pi

        current_center += orbit_dist * np.array([np.cos(orbit_angle), np.sin(orbit_angle)])


    # We're out of the while loop here, plot all the nodes
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker = dict(
            size=node_sizes,
            #color='#ffa950',
            sizemode='area',
            sizemin=2,
            symbol = node_shapes,
            color = node_colors
        )
    )

    # This sets what to show when hovering over each node
    node_trace.text = node_labels

    # Now, finally make the plot 
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=dict(
                        text="Britannica First Link Network",
                        font=dict(
                            size=16
                        )
                    ),
                    showlegend=False,
                    hovermode='closest',
                    )
                 )
    fig.show()

visualize(brit_network)




