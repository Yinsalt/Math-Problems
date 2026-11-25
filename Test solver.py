import sys
import time
import numpy as np
import networkx as nx
from clique_solver import Solver, CliqueGenerator


def reference(A):
    B = np.asarray(A) != 0
    np.fill_diagonal(B, False)
    M = B & B.T
    G = nx.from_numpy_array(M.astype(int))
    cl = sorted([sorted(c) for c in nx.find_cliques(G) if len(c) >= 3], key=lambda c: (-len(c), c))
    return cl, max((len(c) for c in cl), default=0)


def correctness(runs=300, max_n=60, seed=0):
    rng = np.random.default_rng(seed)
    fails = 0
    for t in range(runs):
        n = int(rng.integers(5, max_n))
        p = float(rng.uniform(0.02, 0.4))
        sym = bool(rng.integers(0, 2))
        mp = bool(rng.integers(0, 2))
        pick = ["weakest", "last"][int(rng.integers(0, 2))]
        gen = CliqueGenerator(p, n, int(rng.integers(1, 6)), int(rng.integers(3, min(8, n) + 1)),
                              symmetric_noise=sym, seed=int(rng.integers(1e9)))
        A, planted, _ = gen.create()
        ref, refmax = reference(A)
        S = Solver(adjacency_matrix=A.copy(), mutual_pruning=mp, print_solutions=False)
        got = S.solve(pick=pick)
        best = S.solve_max(pick=pick)
        ok = got == ref and len(best) == refmax and (not best or S.final_check_if_clique(best))
        if not ok:
            fails += 1
            if fails <= 3:
                print("FAIL", dict(n=n, p=round(p, 3), sym=sym, mutual_pruning=mp, pick=pick))
                print("  got ", got[:5], "\n  ref ", ref[:5], "\n  best", best, refmax)
    print(f"{runs - fails}/{runs} match networkx")
    return fails == 0


def benchmark(configs, reps=1):
    print(f"{'n':>6} {'p':>5} {'noise':>10} {'pruning':>8} | {'solve':>8} {'solve_max':>9} {'nx all':>8} {'nx max':>8} | {'#cl':>5} {'max':>3}")
    for n, p, sym, mp in configs:
        A, _, _ = CliqueGenerator(p, n, max(1, n // 20), 8, symmetric_noise=sym, seed=42).create()
        t = time.perf_counter(); S = Solver(adjacency_matrix=A, mutual_pruning=mp, print_solutions=False); got = S.solve(); t_s = time.perf_counter() - t
        t = time.perf_counter(); best = S.solve_max(); t_m = time.perf_counter() - t
        t = time.perf_counter(); ref, refmax = reference(A); t_r = time.perf_counter() - t
        B = A != 0; M = B & B.T
        t = time.perf_counter(); nx.max_weight_clique(nx.from_numpy_array(M.astype(int)), weight=None); t_rm = time.perf_counter() - t
        assert got == ref and len(best) == refmax
        print(f"{n:>6} {p:>5} {'sym' if sym else 'directed':>10} {'mutual' if mp else 'out/in':>8} | {t_s:>7.3f}s {t_m:>8.3f}s {t_r:>7.3f}s {t_rm:>7.3f}s | {len(ref):>5} {refmax:>3}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "test"):
        correctness()
    if mode in ("all", "bench"):
        benchmark([
            (100, 0.05, False, False), (500, 0.05, False, False), (1000, 0.05, False, False),
            (1000, 0.05, False, True),
            (100, 0.1, True, False), (300, 0.1, True, False), (1000, 0.02, True, False),
            (100, 0.3, True, False), (200, 0.3, True, False),
        ])
