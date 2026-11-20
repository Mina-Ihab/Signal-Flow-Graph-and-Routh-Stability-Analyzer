"""Routh Stability Criterion GUI (CSE 341, Part 2) - Tkinter.

The GUI only needs four things from the backend (see run_backend):
    table      : list of rows (jagged), row 0 = s^n ... last row = s^0
    stable     : bool
    rhp_count  : int
    poles      : list of complex numbers
The calculation steps are rebuilt from the table itself, so the solver
does not have to produce them.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass

TOL = 1e-6  # tolerance for "real part > 0" on numerically computed poles


# ======================================================================
#  BACKEND ADAPTER  -  the only part to edit when the real solver is finished
# ======================================================================
@dataclass
class RouthResult:
    table: list
    stable: bool
    rhp_count: int
    poles: list


def run_backend(equation: str) -> RouthResult:
    # --- REAL BACKEND: adapt these lines to the teammates' names ---
    # coeffs = RSC(equation).coffs
    # res = Solver(coeffs).solve()
    # return RouthResult(res.Table, res.Stability, res.RightPolesNum, res.Poles)

    # --- DEMO BACKEND (delete once the real one is wired in) ---
    import numpy as np
    coeffs = _demo_parse(equation)
    table = _demo_table(coeffs)
    changes = _sign_changes([row[0] for row in table])
    return RouthResult(table, changes == 0, changes, list(np.roots(coeffs)))


def _demo_parse(text):
    text = text.replace(" ", "").split("=")[0].replace("-", "+-")
    coeffs = {}
    for term in filter(None, text.split("+")):
        if "s" in term:
            c, _, p = term.partition("s")
            c = c.rstrip("*")
            coef = 1.0 if c == "" else (-1.0 if c == "-" else float(c))
            power = int(p.lstrip("^")) if p else 1
        else:
            coef, power = float(term), 0
        coeffs[power] = coeffs.get(power, 0.0) + coef
    n = max(coeffs)
    return [coeffs.get(k, 0.0) for k in range(n, -1, -1)]  # descending


def _demo_table(coeffs):
    n = len(coeffs) - 1
    rows = [coeffs[0::2], coeffs[1::2]]
    get = lambda r, k: r[k] if k < len(r) else 0.0
    for i in range(2, n + 1):
        A, B = rows[i - 2], rows[i - 1]
        if B[0] == 0:
            raise ValueError("Zero in first column (special case, not supported)")
        width = (n - i) // 2 + 1
        rows.append([(B[0] * get(A, j + 1) - A[0] * get(B, j + 1)) / B[0]
                     for j in range(width)])
    return rows


# ======================================================================
#  Helpers (formatting + step generation)
# ======================================================================
def fmt(x):
    x = float(x)
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.4f}".rstrip("0").rstrip(".")


def _sign_changes(first_col):
    return sum(1 for a, b in zip(first_col, first_col[1:]) if a * b < 0)


def build_steps(table):
    n = len(table) - 1
    get = lambda r, k: r[k] if k < len(r) else 0.0
    out = [
        f"Degree n = {n}  ->  the table has {n + 1} rows (s^{n} ... s^0).",
        "",
        "Rule for every row below the first two:",
        "   entry j = ( B0 * A(j+1)  -  A0 * B(j+1) ) / B0",
        "   A = row two above, B = row directly above, A0/B0 = their first entries",
        "",
        f"Row s^{n}   : coefficients of s^{n}, s^{n-2}, ...  ->  "
        + ", ".join(fmt(v) for v in table[0]),
        f"Row s^{n-1} : coefficients of s^{n-1}, s^{n-3}, ...  ->  "
        + ", ".join(fmt(v) for v in table[1]),
        "",
    ]
    for i in range(2, n + 1):
        A, B = table[i - 2], table[i - 1]
        a0, b0 = A[0], B[0]
        out.append(f"--- Row s^{n - i}  (A = row s^{n - i + 2}, B = row s^{n - i + 1}) ---")
        for j, val in enumerate(table[i]):
            a1, b1 = get(A, j + 1), get(B, j + 1)
            calc = (b0 * a1 - a0 * b1) / b0
            line = (f"  entry {j + 1} = ({fmt(b0)} x {fmt(a1)} - {fmt(a0)} x {fmt(b1)}) / {fmt(b0)}"
                    f" = ({fmt(b0 * a1)} - {fmt(a0 * b1)}) / {fmt(b0)} = {fmt(calc)}")
            if abs(calc - val) > 1e-6 * max(1, abs(val)):
                line += f"      !! solver table says {fmt(val)}"
            out.append(line)
        out.append("")

    first = [r[0] for r in table]
    ch = _sign_changes(first)
    out += [
        "First column: " + ", ".join(fmt(v) for v in first),
        f"Sign changes = {ch}  ->  {ch} pole(s) in the right half plane.",
        "System is STABLE (no sign changes)." if ch == 0
        else "System is UNSTABLE (sign changes in the first column).",
    ]
    return "\n".join(out)


# ======================================================================
#  GUI
# ======================================================================
class RouthApp(tk.Tk):
    EXAMPLES = {
        "Unstable example": "s^5 + s^4 + 10s^3 + 72s^2 + 152s + 240 = 0",
        "Stable example": "s^5 + 15s^4 + 85s^3 + 225s^2 + 274s + 120 = 0",
    }

    def __init__(self):
        super().__init__()
        self.title("Routh Stability Criterion - CSE 341")
        self.geometry("1150x680")
        self.minsize(950, 560)
        style = ttk.Style(self)
        style.configure("Treeview", rowheight=28, font=("Consolas", 11))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self._build()

    # ---------- layout ----------
    def _build(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Characteristic equation:").pack(side="left")
        self.entry = ttk.Entry(top, font=("Consolas", 12))
        self.entry.pack(side="left", fill="x", expand=True, padx=8)
        self.entry.bind("<Return>", lambda e: self.solve())
        ttk.Button(top, text="Solve", command=self.solve).pack(side="left", padx=2)
        for name, eq in self.EXAMPLES.items():
            ttk.Button(top, text=name, command=lambda e=eq: self.load(e)).pack(side="left", padx=2)
        ttk.Button(top, text="Clear", command=self.clear).pack(side="left", padx=2)

        ttk.Label(self, text="Format:  s^5 + s^4 + 10s^3 + 72s^2 + 152s + 240 = 0",
                  foreground="gray").pack(anchor="w", padx=12)

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # left: Routh table
        left = ttk.LabelFrame(body, text="Routh table", padding=6)
        body.add(left, weight=1)
        self.table = ttk.Treeview(left, show="headings", selectmode="none")
        self.table.pack(fill="both", expand=True)
        ttk.Label(left, text="Red = negative first-column entry; "
                             "orange row = sign change from the row above",
                  foreground="gray").pack(anchor="w", pady=(4, 0))

        # right: verdict + tabs
        right = ttk.Frame(body)
        body.add(right, weight=1)
        self.verdict = tk.Label(right, text="Enter an equation and press Solve",
                                font=("Segoe UI", 14, "bold"), anchor="w")
        self.verdict.pack(fill="x")
        self.verify = tk.Label(right, text="", font=("Segoe UI", 10), anchor="w")
        self.verify.pack(fill="x", pady=(0, 6))

        tabs = ttk.Notebook(right)
        tabs.pack(fill="both", expand=True)

        steps_frame = ttk.Frame(tabs)
        tabs.add(steps_frame, text="Calculation steps")
        self.steps = tk.Text(steps_frame, font=("Consolas", 10), wrap="none", state="disabled")
        sy = ttk.Scrollbar(steps_frame, command=self.steps.yview)
        sx = ttk.Scrollbar(steps_frame, orient="horizontal", command=self.steps.xview)
        self.steps.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        self.steps.pack(fill="both", expand=True)

        poles_frame = ttk.Frame(tabs)
        tabs.add(poles_frame, text="Poles")
        cols = ("pole", "real", "imag", "location")
        self.poles = ttk.Treeview(poles_frame, columns=cols, show="headings", selectmode="none")
        for c, w in zip(cols, (50, 130, 130, 130)):
            self.poles.heading(c, text=c.capitalize())
            self.poles.column(c, width=w, anchor="center")
        self.poles.tag_configure("rhp", foreground="#b00020", background="#fde8e8")
        self.poles.pack(fill="both", expand=True)

    # ---------- actions ----------
    def load(self, eq):
        self.entry.delete(0, "end")
        self.entry.insert(0, eq)
        self.solve()

    def clear(self):
        self.entry.delete(0, "end")
        self.table.delete(*self.table.get_children())
        self.poles.delete(*self.poles.get_children())
        self._set_steps("")
        self.verdict.config(text="Enter an equation and press Solve", fg="black")
        self.verify.config(text="")

    def solve(self):
        eq = self.entry.get().strip()
        if not eq:
            messagebox.showwarning("Input", "Please enter a characteristic equation.")
            return
        try:
            res = run_backend(eq)
        except Exception as e:
            messagebox.showerror("Error", f"Could not solve:\n{e}")
            return
        self._show_table(res.table)
        self._show_poles(res.poles, res)
        self._set_steps(build_steps(res.table))

    # ---------- display ----------
    def _set_steps(self, text):
        self.steps.config(state="normal")
        self.steps.delete("1.0", "end")
        self.steps.insert("1.0", text)
        self.steps.config(state="disabled")

    def _show_table(self, table):
        n = len(table) - 1
        width = max(len(r) for r in table)
        cols = ["row"] + [f"c{j + 1}" for j in range(width)]
        self.table.configure(columns=cols)
        for c in cols:
            self.table.heading(c, text="" if c == "row" else c)
            self.table.column(c, width=70 if c == "row" else 110, anchor="center")
        self.table.tag_configure("neg", foreground="#b00020")
        self.table.tag_configure("flip", background="#ffe0b2")
        self.table.delete(*self.table.get_children())
        prev = None
        for i, row in enumerate(table):
            cells = [f"s^{n - i}"] + [fmt(v) for v in row] + [""] * (width - len(row))
            tags = []
            if row[0] < 0:
                tags.append("neg")
            if prev is not None and prev * row[0] < 0:
                tags.append("flip")
            self.table.insert("", "end", values=cells, tags=tags)
            prev = row[0]

    def _show_poles(self, poles, res):
        self.poles.delete(*self.poles.get_children())
        numeric_rhp = 0
        for k, p in enumerate(poles, 1):
            p = complex(p)
            if p.real > TOL:
                loc, tag = "RHP", ("rhp",)
                numeric_rhp += 1
            elif p.real < -TOL:
                loc, tag = "LHP", ()
            else:
                loc, tag = "Imaginary axis", ()
            self.poles.insert("", "end", tags=tag,
                              values=(k, f"{p.real:.5f}", f"{p.imag:+.5f}j", loc))

        routh_count = _sign_changes([r[0] for r in res.table])
        if res.stable and res.rhp_count == 0:
            self.verdict.config(text="STABLE  -  0 right-half-plane poles", fg="#1b7f3b")
        else:
            self.verdict.config(
                text=f"UNSTABLE  -  {res.rhp_count} right-half-plane pole(s)", fg="#b00020")
        ok = routh_count == numeric_rhp
        self.verify.config(
            text=f"Check: Routh sign changes = {routh_count}  |  numerical RHP poles = "
                 f"{numeric_rhp} (tol {TOL:g})  ->  {'MATCH' if ok else 'MISMATCH'}",
            fg="#1b7f3b" if ok else "#b00020")

if __name__ == "__main__":
    RouthApp().mainloop()