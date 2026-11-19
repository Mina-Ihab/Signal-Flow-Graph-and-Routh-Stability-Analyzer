from signal_flow_graph.forward_path import graph_repr, get_forward_paths

graph = graph_repr(input_gui)
paths = get_forward_paths(graph)

# edit here the input_gui