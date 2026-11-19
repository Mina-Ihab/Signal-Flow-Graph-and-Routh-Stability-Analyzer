def graph_repr(List_edge_nodes: list) -> tuple:
    graph = {}
    source = List_edge_nodes[0][0]
    # [a,b,c] == a->b and c is gain, the end is frm a-> goal
    for a,b,c in List_edge_nodes:
        if a not in graph:
            graph[a] = []
        if b is None:
            goal = a
            continue
        graph[a].append((b,c))

    return graph, source, goal

# result {'r':[(e1,g1),....],....}

def get_forward_paths(Graph_info: tuple) -> list:
    # result is list of tuples first place have path and second is its gain
    # stack has node and path till now (visited) and gain
    graph, source, goal = Graph_info
    paths = []
    stack = [(source, [source], 1)]
    while stack:
        node, path_now, gain_now = stack.pop()
        # if goal reached add the path and the goal and gain
        if node == goal:
            paths.append((path_now, gain_now))
            continue

        for neighbour, gain in graph[node]:
            # check cycles on this path only
            if neighbour in path_now:
                continue
            stack.append((neighbour, path_now + [neighbour], gain_now * gain))

    return paths

# please input be R->R to be consistent and c->c leave two ends alone with gain one
