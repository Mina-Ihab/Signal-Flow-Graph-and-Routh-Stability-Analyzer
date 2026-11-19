from .loops import find_individual_loops, find_non_touching_loops


def compute_delta(loops: list[dict], non_touching: dict[int, list[dict]]) -> tuple[float, str]:
    """
    Computes the graph determinant Δ (or path cofactor Δ_i) and generates
    a multi-line string showing the symbolic formula, numerical substitution,
    and final calculated value.
    """
    if not loops:
        return 1.0, "Δ = 1"

    sum_l1 = sum(lp["total_gain"] for lp in loops)
    delta_val = 1.0 - sum_l1

    sym_terms = ["1", f"- ({' + '.join(lp['label'] for lp in loops)})"]
    sub_terms = ["1", f"- ({' + '.join(f'{lp['total_gain']:g}' for lp in loops)})"]

    for k, groups in sorted(non_touching.items()):
        sign = "+" if k % 2 == 0 else "-"
        group_sum = sum(g["product_gain"] for g in groups)
        delta_val += group_sum if k % 2 == 0 else -group_sum

        sym_terms.append(f"{sign} ({' + '.join(g['symbolic'] for g in groups)})")
        sub_terms.append(f"{sign} ({' + '.join(f'{g['product_gain']:g}' for g in groups)})")

    steps = (
        f"Delta = {' '.join(sym_terms)}\n"
        f"Delta = {' '.join(sub_terms)}\n"
        f"Delta = {delta_val:g}"
    )
    return delta_val, steps


def solve_mason(adj: dict[str, list[tuple[str, str, float]]], forward_paths: list[dict]) -> dict:
    """
    Executes Mason's Gain Formula end-to-end:
    1. Finds all individual loops and k non-touching loop combinations.
    2. Calculates Δ and every forward-path cofactor Δ_i.
    3. Computes T(s) and formats all intermediate equations for the GUI/report.
    """
    if not forward_paths:
        raise ValueError("No forward paths exist between the selected input and output nodes.")

    loops = find_individual_loops(adj)
    non_touching = find_non_touching_loops(loops)
    delta_val, delta_steps = compute_delta(loops, non_touching)

    if delta_val == 0:
        raise ValueError("Graph determinant is zero; overall transfer function T(s) is undefined.")

    cofactors = []
    numerator_val = 0.0
    num_sym_terms = []
    num_sub_terms = []

    for idx, path in enumerate(forward_paths, start=1):
        path_nodes = set(path["nodes"])
        # Exclude any loop that shares at least one node with forward path i
        untouched_loops = [lp for lp in loops if lp["node_set"].isdisjoint(path_nodes)]
        untouched_nt = find_non_touching_loops(untouched_loops)
        di_val, di_steps = compute_delta(untouched_loops, untouched_nt)

        cofactors.append({
            "label": f"Delta_{idx}",
            "value": di_val,
            "steps": di_steps.replace("Δ =", f"Δ{idx} ="),
        })

        mi_val = path["total_gain"]
        mi_label = path.get("label", f"M{idx}")
        numerator_val += mi_val * di_val
        num_sym_terms.append(f"{mi_label} * Delta{idx}")
        num_sub_terms.append(f"({mi_val:g} * {di_val:g})")

    transfer_val = numerator_val / delta_val
    mason_steps = (
        f"T(s) = ({' + '.join(num_sym_terms)}) / Delta\n"
        f"T(s) = ({' + '.join(num_sub_terms)}) / {delta_val:g}\n"
        f"T(s) = {numerator_val:g} / {delta_val:g} = {transfer_val:g}"
    )

    return {
        "loops": loops,
        "non_touching": non_touching,
        "delta": delta_val,
        "delta_steps": delta_steps,
        "cofactors": cofactors,
        "transfer_function": transfer_val,
        "mason_steps": mason_steps,
    }