from itertools import combinations
from math import prod


def _canonical_loop_key(nodes: list[str], branch_names: list[str]) -> tuple:
    """
    Normalizes a cycle [n0, n1, ..., nk-1] (without the repeated closing node)
    by rotating it to start at the lexicographically smallest node (and branch)
    so the same cycle discovered from different start nodes isn't duplicated.
    """
    n = len(nodes)
    rotations = [
        (tuple(nodes[i:] + nodes[:i]), tuple(branch_names[i:] + branch_names[:i]))
        for i in range(n)
    ]
    return min(rotations)


def find_individual_loops(adj: dict[str, list[tuple[str, str, float]]]) -> list[dict]:
    """Finds all unique simple directed cycles (including self-loops) from adj."""
    seen_keys = set()
    raw_loops = []

    def dfs(start_node: str, curr_node: str, path_nodes: list[str], path_branches: list[str], path_gains: list[float]):
        for neighbor, branch_name, gain in adj.get(curr_node, []):
            if neighbor == start_node:
                # Found a cycle returning to start_node
                key = _canonical_loop_key(path_nodes, path_branches + [branch_name])
                if key not in seen_keys:
                    seen_keys.add(key)
                    raw_loops.append({
                        "nodes": path_nodes + [start_node],
                        "node_set": set(path_nodes),
                        "branches": path_branches + [branch_name],
                        "gains": path_gains + [gain],
                        "total_gain": prod(path_gains + [gain]),
                    })
            elif neighbor not in path_nodes:
                dfs(
                    start_node,
                    neighbor,
                    path_nodes + [neighbor],
                    path_branches + [branch_name],
                    path_gains + [gain],
                )

    for node in adj:
        dfs(node, node, [node], [], [])

    # Assign standard L1, L2, ... labels
    for idx, loop in enumerate(raw_loops, start=1):
        loop["label"] = f"L{idx}"

    return raw_loops


def find_non_touching_loops(loops: list[dict]) -> dict[int, list[dict]]:
    """
    Finds all combinations of k >= 2 mutually non-touching loops.
    Returns {k: [{"labels": [...], "product_gain": float, "formula": str}, ...]}.
    """
    non_touching: dict[int, list[dict]] = {}
    k = 2

    while True:
        valid_groups = []
        for combo in combinations(loops, k):
            # Pairwise disjoint check across all loops in the combination
            all_nodes = [n for lp in combo for n in lp["node_set"]]
            if len(all_nodes) == len(set(all_nodes)):
                labels = [lp["label"] for lp in combo]
                gains = [lp["total_gain"] for lp in combo]
                valid_groups.append({
                    "loops": list(combo),
                    "labels": labels,
                    "product_gain": prod(gains),
                    "symbolic": " * ".join(labels),
                    "substitution": " * ".join(f"({g:g})" for g in gains),
                })

        if not valid_groups:
            break

        non_touching[k] = valid_groups
        k += 1

    return non_touching
