import networkx as nx
import numpy as np

def count_terminations(G):
    """
    Recall how our first link network is constructed:
    Continuously follow a link until you reach a node
    already traversed, terminating. 

    For each node in the network, perform this walk 
    to determine where you terminate. The node you
    terminate on gets a +1 to its termination score. 

    Return a dictionary of them form:
        {node: termination score}    

    """

    nodes = G.nodes

    termination_counts = {n: 0 for n in nodes}
    
    for N in nodes:
        visited_nodes = {N}
        current_node = N
        while True:
            # Each node only has one neighbor
            next_node = next(G.neighbors(current_node)) 
            if next_node in visited_nodes:
                termination_counts[next_node] += 1
                break
            current_node = next_node
            visited_nodes.add(current_node)

    return termination_counts

def calculate_termination_centrality(G):
    """
    Let n* (written n_star) = the node with the most terminations in G
    
    For each node, n, in G, find the shortest path from 
    n to n*. Each node in this shortest path gets a +1 
    to its termination centrality.
    
    return a dictionary of the form:
        {node: termination centrality}
    """

    nodes = G.nodes
    term_counts = count_terminations(G)
    n_star = max(term_counts, key = lambda n: term_counts[n])
    
    termination_centrality = {n: 0 for n in nodes}
    
    for n in nodes:
        # try-except needed in case n is disconnected from n* 
        try:
            SP = nx.shortest_path(G, n, n_star)
            for node in SP:
                termination_centrality[node] += 1
        except nx.exception.NetworkXNoPath:
            # Notice that nodes which can't reach n* will have 0
            pass

    return termination_centrality

# This needs to be fiddled with a bunch, 
def termination_centrality_to_plot_size(importance):
   return importance # If this returns 0 no point will be drawn 

def determine_node_positions(G, center_x, center_y):
    """
    Assume: there is a central "most important"
    node. This is true for Britannica. This 
    may not be true for Wikipedia. Let the 
    "most important" node be n*

    This function places n* at (center_x, center_y)
    and fans out in a circular fashion. For each 
    node that points to n*, give it a "pie", i.e.
    two angles in which it and its neighbors will 
    sit. A node's "pie" is weighted by its import-
    ance, so nodes that are more important get more
    space. 

    This function uses the termination centrality
    as its importance metric, since this indicates 
    the number of nodes which must be crammed into
    the pie. 
    """

    term_counts = count_terminations(G)

    # If you wanted to change the importance metric, do it here
    #importance = nx.betweenness_centrality(G)
    importance = calculate_termination_centrality(G)

    nodes = G.nodes
    n_star = max(term_counts, key = lambda n: term_counts[n])

    positions = {n: [] for n in nodes}
    
    # Pies is a dictionary since each node needs to "remember"
    # what angles it has access to
    pies = {}

    # Keep track of which nodes have been branched
    branched_nodes = set([])

    # Place n_star at the center
    positions[n_star] = np.array([center_x,center_y])

    # Fan out from n_star by reversing the direction of all edges
    g = G.reverse()
    
    N = n_star
    pie = [0, np.pi * 2]
    # When there are no pies left, we'll have placed every node

    # Think recursively, but I didn't implement using recursion
    while True:
        branches = list(g.neighbors(N))
        num_branches = len(branches)
       
        # Two reasons we wouldn't want to look at the "branches" off a node:
        #  - It doesn't have any
        #  - We've already looked at them  
        if (num_branches > 0) and (N not in branched_nodes):

            branched_nodes.add(N)

            mean_weight = np.mean([importance[n] for n in branches])
            pie_weights = {n: importance[n]/mean_weight for n in branches}

            # Pretend we'll split the pie evenly
            delta_angle = (pie[1] - pie[0]) / num_branches
            
            current_pie_edge = pie[0]

            for i,n in enumerate(branches):
                next_pie_edge = current_pie_edge + delta_angle * pie_weights[n]
                new_pie = [current_pie_edge, next_pie_edge]

                # Place nodes in the middle of their pie
                placement_angle = sum(new_pie) / 2

                # A nodes position is the 1 unit away from the start of its branch
                    # Otherwise all the nodes would sit on the same circle
                x = positions[N][0] + np.cos(placement_angle) #* termination_centrality_to_plot_size(importance[N])
                y = positions[N][1] + np.sin(placement_angle) #* termination_centrality_to_plot_size(importance[N])

                # If there's a cycle, a node would be placed multiple times. Avoid this by checking whether it has a positoin
                if len(positions[n]) == 0:
                    positions[n] = np.array([x,y])
                
                # Notice that, if a node had no branches, no pies would be created and one pie would be eaten
                pies[n] = new_pie
                # Since not all pies have children, the program must terminate
                
                current_pie_edge = next_pie_edge
        # Eventually, we'll run out of pies and halt
        if len(pies) == 0:
            break
        
        # Restart the branching and pie-eating process for the next node
        N, pie = pies.popitem()
    
    return positions








