# pvsnp/algorithms/christofides.py
"""
name: Christofides
author: pvsnp
description: 1.5-approximation using MST + minimum weight matching. Classic.
category: approximation
"""
import networkx as nx


def solve(distance_matrix: list) -> list:
    n = len(distance_matrix)
    G = nx.Graph()
    for i in range(n):
        for j in range(i + 1, n):
            G.add_edge(i, j, weight=distance_matrix[i][j])

    # Step 1: Minimum spanning tree
    mst = nx.minimum_spanning_tree(G)

    # Step 2: Find odd-degree vertices
    odd_vertices = [v for v in mst.nodes() if mst.degree(v) % 2 == 1]

    # Step 3: Minimum weight perfect matching on odd-degree vertices
    odd_graph = nx.Graph()
    for i in range(len(odd_vertices)):
        for j in range(i + 1, len(odd_vertices)):
            u, v = odd_vertices[i], odd_vertices[j]
            odd_graph.add_edge(u, v, weight=distance_matrix[u][v])
    matching = nx.min_weight_matching(odd_graph)

    # Step 4: Combine MST + matching into multigraph
    multigraph = nx.MultiGraph(mst)
    for u, v in matching:
        multigraph.add_edge(u, v, weight=distance_matrix[u][v])

    # Step 5: Eulerian circuit
    circuit = list(nx.eulerian_circuit(multigraph, source=0))

    # Step 6: Shortcut to Hamiltonian tour
    visited = set()
    tour = []
    for u, v in circuit:
        if u not in visited:
            tour.append(u)
            visited.add(u)
    return tour
