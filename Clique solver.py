import numpy as np

def reorder_adjacency_matrix(original, diag_cut=True):
    A = np.array(original != 0, dtype=np.int32)
    if diag_cut:
        np.fill_diagonal(A, 0)
    out_deg = A.sum(axis=1)
    post_order = np.argsort(-out_deg, kind="stable")
    amount_post_order = out_deg[post_order]
    sorted_matrix = A[np.ix_(post_order, post_order)]
    original_order = np.arange(A.shape[0], dtype=np.int32)
    return sorted_matrix, original_order, post_order, amount_post_order

def get_mask_of_outgoing_connections(sorted_matrix, amount_post_order, min_out=2):
    k = int((amount_post_order >= min_out).sum())
    sub = sorted_matrix[:k, :k]
    out_conns = amount_post_order[:k]
    out_matrix = sub * out_conns[None, :]
    return out_matrix, out_conns, k

def get_mask_of_incoming_connections(sorted_matrix, k):
    in_conns = sorted_matrix.sum(axis=0)[:k]
    sub = sorted_matrix[:k, :k]
    in_matrix = sub * in_conns[None, :]
    return in_matrix, in_conns

def get_meta_information(adjacency_matrix, min_out=2, diag_cut=True):
    sorted_matrix, original_order, post_order, amount_post_order = reorder_adjacency_matrix(adjacency_matrix, diag_cut)
    out_matrix, out_conns, last_non_trivial_row = get_mask_of_outgoing_connections(sorted_matrix, amount_post_order, min_out)
    in_matrix, in_conns = get_mask_of_incoming_connections(sorted_matrix, last_non_trivial_row)
    return sorted_matrix, original_order, post_order, amount_post_order, last_non_trivial_row, out_matrix, out_conns, in_matrix, in_conns

def max_possible_structure(degrees):
    d = np.sort(np.asarray(degrees))[::-1]
    h = int((d >= np.arange(1, len(d) + 1)).sum())
    return h + 1

class CliqueGenerator():
    """planted cliques + noise. planted cliques can merge, so solutions != all maximal cliques"""
    def __init__(self, noise_level, adjacency_matrix_size, num_cliques, max_clique_size,
                 info=False, symmetric_noise=False, seed=None):
        self.noise_level = noise_level
        self.adjacency_matrix_size = adjacency_matrix_size
        self.num_cliques = num_cliques
        self.max_clique_size = max_clique_size
        self.info = info
        self.symmetric_noise = symmetric_noise
        self.rng = np.random.default_rng(seed)

    def create(self, num_cliques=None, diag_cut=True):
        n = self.adjacency_matrix_size
        num_cliques = self.num_cliques if num_cliques is None else num_cliques
        assert 3 <= self.max_clique_size <= n
        clique_sizes = [int(self.rng.integers(3, self.max_clique_size + 1)) for _ in range(num_cliques)]
        candidates = []
        for size in clique_sizes:
            for _ in range(100):
                c = sorted(self.rng.choice(n, size, replace=False).tolist())
                if c not in candidates:
                    candidates.append(c)
                    break
        noise = self.rng.random((n, n)) < self.noise_level
        if self.symmetric_noise:
            noise = np.triu(noise, 1)
            noise = noise | noise.T
        A = noise.astype(np.float64)
        for c in candidates:
            A[np.ix_(c, c)] = 1
        if diag_cut:
            np.fill_diagonal(A, 0)
        if self.info:
            print("Clique sizes:", clique_sizes, "\nPlanted:", candidates, "\n", A)
        return A, candidates, clique_sizes

class Solver():
    def __init__(self,
                 noise_level=0.05,
                 adjacency_matrix_size=20,
                 num_cliques=5,
                 max_clique_size=5,
                 adjacency_matrix=None,
                 info=False,
                 diag_cut=True,
                 print_solutions=True,
                 min_clique_size=3,
                 mutual_pruning=False,
                 symmetric_noise=False,
                 seed=None,
                 batch_fraction=0.125):

        self.diag_cut = diag_cut
        self.batch_fraction = batch_fraction
        self.min_clique_size = min_clique_size
        self.mutual_pruning = mutual_pruning
        self.solutions = None
        if adjacency_matrix is None:
            self.gen = CliqueGenerator(noise_level=noise_level,
                                       adjacency_matrix_size=adjacency_matrix_size,
                                       num_cliques=num_cliques,
                                       max_clique_size=max_clique_size,
                                       info=info,
                                       symmetric_noise=symmetric_noise,
                                       seed=seed)
            self.adjacency_matrix, self.solutions, self.clique_sizes = self.gen.create(diag_cut=diag_cut)
            if print_solutions:
                print("Planted cliques: ", self.solutions)
        else:
            self.adjacency_matrix = adjacency_matrix

        self.size = self.adjacency_matrix.shape[0]
        B = np.asarray(self.adjacency_matrix) != 0
        if diag_cut:
            np.fill_diagonal(B, False)
        self.mutual_original = B & B.T
        self.reset()

    def reset(self, min_degree=None):
        self.min_degree = self.min_clique_size - 1 if min_degree is None else min_degree
        self.sorted_adjacency_matrix, self.original_order, self.post_order, self.amount_post_order, self.last_non_trivial_row, self.sorted_numerated_out_matrix, self.outgoing_connections, self.sorted_numerated_in_matrix, self.incoming_connections = get_meta_information(self.adjacency_matrix, min_out=max(self.min_degree, 1), diag_cut=self.diag_cut)

        self.current_order = self.post_order
        self.valid_index = np.arange(self.sorted_numerated_out_matrix.shape[0])
        self.nodes_of_interest = (self.outgoing_connections >= self.min_degree) & (self.incoming_connections >= self.min_degree)
        self.current_order = self.current_order[:len(self.outgoing_connections)]
        self.current_order = self.current_order[self.nodes_of_interest]
        self.sorted_numerated_out_matrix = self.sorted_numerated_out_matrix[self.nodes_of_interest, :][:, self.nodes_of_interest]
        self.sorted_numerated_in_matrix = self.sorted_numerated_in_matrix[self.nodes_of_interest, :][:, self.nodes_of_interest]
        self.valid_index = self.valid_index[self.nodes_of_interest]
        self.exclusion_prep = self.post_order[:len(self.outgoing_connections)]
        self.not_included = list(self.exclusion_prep[~self.nodes_of_interest]) + list(self.post_order[self.last_non_trivial_row:])
        self.exclusion_prep = self.exclusion_prep[self.nodes_of_interest]
        self.outgoing_connections = self.outgoing_connections[self.nodes_of_interest]
        self.incoming_connections = self.incoming_connections[self.nodes_of_interest]
        self.nodes_of_interest = self.nodes_of_interest[self.nodes_of_interest]
        self.create_helper()

        self.added_for_removal = []
        self.found_cliques = []
        self.best_clique = []
        self.update_in_out_conn()
        self.sorted_numerated_out_matrix = self.helper_adjacency_matrix * self.outgoing_connections[None, :]
        self.sorted_numerated_in_matrix = self.helper_adjacency_matrix * self.incoming_connections[None, :]
        self.update_nodes_of_interest()

    def info(self):
        print("self.sorted_numerated_out_matrix", self.sorted_numerated_out_matrix.shape)
        print("self.sorted_numerated_in_matrix", self.sorted_numerated_in_matrix.shape)
        print("self.valid_index", self.valid_index.shape)
        print("self.exclusion_prep", self.exclusion_prep.shape)
        print("self.outgoing_connections", self.outgoing_connections.shape)
        print("self.incoming_connections", self.incoming_connections.shape)
        print("self.nodes_of_interest", self.nodes_of_interest.shape)
        print("self.current_order", self.current_order.shape)
        print("self.post_order: ", self.post_order)
        print("self.current_order: ", self.current_order)
        print("self.outgoing_connections: ", self.outgoing_connections)
        print("self.incoming_connections: ", self.incoming_connections)
        print("self.mutual_connections: ", self.mutual_connections)
        print("-" * 60, "\nself.sorted_numerated_out_matrix\n")
        self.out_matrix()
        print("-" * 60, "\nself.sorted_numerated_in_matrix\n")
        self.in_matrix()
        print("-" * 60)
        print("Exclusion Prep: ", self.exclusion_prep, "Not included:", self.not_included)

    def out_matrix(self):
        print(self.sorted_numerated_out_matrix, "\n", self.sorted_numerated_out_matrix.shape, "\n")

    def in_matrix(self):
        print(self.sorted_numerated_in_matrix, "\n", self.sorted_numerated_in_matrix.shape, "\n")

    def correct_out(self, col):
        mask = self.helper_adjacency_matrix[:, col]
        self.sorted_numerated_out_matrix[:, col] -= mask
        self.outgoing_connections[col] -= 1

    def correct_in(self, col):
        mask = self.helper_adjacency_matrix[:, col]
        self.sorted_numerated_in_matrix[:, col] -= mask
        self.incoming_connections[col] -= 1

    def reduce_single_in(self, col, row):
        self.sorted_numerated_in_matrix[col, row] -= 1

    def reduce_single_out(self, col, row):
        self.sorted_numerated_out_matrix[col, row] -= 1

    def shrink(self, keep):
        H = self.helper_adjacency_matrix
        lost_in = H[~keep, :].sum(axis=0)
        lost_out = H[:, ~keep].sum(axis=1)
        self.sorted_numerated_in_matrix -= H * lost_in[None, :]
        self.sorted_numerated_out_matrix -= H * lost_out[None, :]

        ix = np.ix_(keep, keep)
        self.helper_adjacency_matrix = H[ix]
        self.sorted_numerated_out_matrix = self.sorted_numerated_out_matrix[ix]
        self.sorted_numerated_in_matrix = self.sorted_numerated_in_matrix[ix]
        self.not_included.extend(self.exclusion_prep[~keep].tolist())
        self.exclusion_prep = self.exclusion_prep[keep]
        self.current_order = self.current_order[keep]
        self.nodes_of_interest = self.nodes_of_interest[keep]
        self.valid_index = self.valid_index[keep]
        self.update_in_out_conn()

    def remove_idx(self, idx):
        keep = np.ones(len(self.current_order), dtype=bool)
        keep[idx] = False
        self.shrink(keep)

    def remove_job(self):
        if self.added_for_removal:
            keep = np.ones(len(self.current_order), dtype=bool)
            keep[self.added_for_removal] = False
            self.added_for_removal = []
            self.shrink(keep)

    def eliminable(self):
        if self.mutual_pruning:
            return self.mutual_connections < self.min_degree
        return (self.outgoing_connections < self.min_degree) | (self.incoming_connections < self.min_degree)

    def update_nodes_of_interest(self, delete=True):
        while True:
            bad = self.eliminable()
            self.nodes_of_interest = ~bad
            for i in np.flatnonzero(bad).tolist():
                if i not in self.added_for_removal:
                    self.added_for_removal.append(i)
            if not delete or not self.added_for_removal:
                break
            self.remove_job()

    def create_helper(self):
        self.helper_adjacency_matrix = self.sorted_numerated_in_matrix != 0

    def update_in_out_conn(self):
        H = self.helper_adjacency_matrix
        self.outgoing_connections = H.sum(axis=1)
        self.incoming_connections = H.sum(axis=0)
        self.mutual_connections = (H & H.T).sum(axis=1)

    def translator(self, candidates):
        return self.current_order[np.asarray(candidates, dtype=np.int64)].astype(np.int32)

    def pick_last(self):
        last_candidate = len(self.outgoing_connections) - 1
        return last_candidate, self.check_idx(last_candidate)

    def pick_weakest(self):
        weakest = int(np.argmin(self.mutual_connections))
        return weakest, self.check_idx(weakest)

    def final_check_if_clique(self, real_indeces):
        r = np.asarray(real_indeces)
        sub = self.mutual_original[np.ix_(r, r)]
        return bool(sub.sum() == len(r) * (len(r) - 1))

    def is_maximal(self, real_indeces):
        return len(self.check_for_bigger_clique(list(real_indeces), self.mutual_original)) == 0

    def set_inf_clique(self, real_indices):
        for i in real_indices:
            for j in real_indices:
                if i != j:
                    self.adjacency_matrix[i][j] = np.inf

    def check_idx_part1(self, idx):
        assert idx < len(self.outgoing_connections)
        H = self.helper_adjacency_matrix
        indices = np.flatnonzero(H[idx] & H[:, idx])
        check = len(indices)
        if check < self.min_clique_size - 1:
            if idx not in self.added_for_removal:
                self.added_for_removal.append(idx)
            return idx, 0, [], {}
        tmp_bool_dict = {}
        for i in indices.tolist():
            tmp_bool_dict[i] = H[idx] & H[i]
        return idx, check, indices.tolist(), tmp_bool_dict

    def check_idx_part2(self, idx, check, indices, tmp_bool_dict):
        candidates = []
        for index in reversed(indices):
            if tmp_bool_dict[index].sum() == 0:
                continue
            vec = tmp_bool_dict[index].copy()
            vec[idx] = 1
            vec[index] = 1
            for count in np.flatnonzero(tmp_bool_dict[index])[::-1].tolist():
                if count in (idx, index):
                    continue
                if (self.helper_adjacency_matrix[count] & vec).sum() >= 2 and count not in candidates:
                    candidates.append(count)
            if index not in candidates:
                candidates.append(index)
        return candidates

    def check_idx_part3(self, idx, candidates):
        c = list(candidates)
        if idx not in c:
            c.append(idx)
        checkbox = self.helper_adjacency_matrix[np.ix_(c, c)].astype(np.int32)
        np.fill_diagonal(checkbox, 1)
        real_candidates = (checkbox.sum(axis=0) > 1).astype(np.int32)
        return checkbox, real_candidates

    def check_for_bigger_clique(self, clique, M):

        box = M[clique].sum(axis=0)
        box[clique] = 0
        return np.flatnonzero(box == len(clique))

    def check_how_big_a_clique_can_be(self, candidates, M=None):
        if M is None:
            deg = np.minimum(self.outgoing_connections[candidates], self.incoming_connections[candidates])
        else:
            c = np.asarray(candidates)
            deg = M[np.ix_(c, c)].sum(axis=1)
        return max_possible_structure(deg)

    def check_idx_part4(self, idx, indices, best=0):
        nb = np.asarray(indices)
        Hn = self.helper_adjacency_matrix[np.ix_(nb, nb)]
        M = Hn & Hn.T
        found = []
        need = max(self.min_clique_size, best + 1)

        def expand(R, P, X):
            if len(R) + 1 + len(P) < need:
                return
            if best and P and len(R) + 1 + min(self.check_how_big_a_clique_can_be(sorted(P), M), len(P)) < need:
                return
            if not P:
                if not X:
                    found.append(R)
                return
            order = sorted(P, key=lambda v: -M[v, list(P)].sum()) if best else list(P)
            for v in order:
                ext = set(self.check_for_bigger_clique(R + [v], M).tolist())
                expand(R + [v], P & ext, X & ext)
                P.discard(v)
                X.add(v)
                if len(R) + 1 + len(P) < need:
                    return

        expand([], set(range(len(nb))), set())
        return [[idx] + nb[r].tolist() for r in found]

    def check_idx(self, idx, best=0):
        idx, check, indices, tmp_bool_dict = self.check_idx_part1(idx)
        if check == 0:
            return []
        cliques = self.check_idx_part4(idx, indices, best)
        return [sorted(self.translator(c).tolist()) for c in cliques]

    def next_batch(self, pick):
        n = len(self.current_order)
        size = max(1, int(n * self.batch_fraction))
        if pick == "weakest":
            return np.argsort(self.mutual_connections, kind="stable")[:size].tolist()
        return list(range(n - 1, n - 1 - size, -1))

    def solve(self, pick="weakest"):
        """all maximal cliques >= min_clique_size"""
        self.reset()
        found = set()
        while len(self.current_order) > 0:
            batch = self.next_batch(pick)
            for idx in batch:
                for c in self.check_idx(idx):
                    t = tuple(c)
                    if t not in found and self.is_maximal(c):
                        found.add(t)
            for idx in batch:
                if idx not in self.added_for_removal:
                    self.added_for_removal.append(idx)
            self.remove_job()
            self.update_nodes_of_interest()
        self.found_cliques = sorted((list(c) for c in found), key=lambda c: (-len(c), c))
        return self.found_cliques

    def greedy_clique(self):
        if len(self.current_order) == 0:
            return []
        H = self.helper_adjacency_matrix
        M = H & H.T
        clique = [int(np.argmax(self.mutual_connections))]
        while True:
            ext = self.check_for_bigger_clique(clique, M)
            if len(ext) == 0:
                break
            clique.append(int(ext[np.argmax(M[np.ix_(ext, ext)].sum(axis=1))]))
        return sorted(self.translator(clique).tolist())

    def solve_max(self, pick="weakest"):
        """one maximum clique"""
        self.reset()
        best = self.greedy_clique()
        if len(best) < self.min_clique_size:
            best = []
        while True:
            self.min_degree = max(self.min_clique_size - 1, len(best))
            self.update_nodes_of_interest()
            if len(self.current_order) == 0:
                break
            if max_possible_structure(self.mutual_connections) <= len(best):
                break
            batch = self.next_batch(pick)
            for idx in batch:
                for c in self.check_idx(idx, best=len(best)):
                    if len(c) > len(best):
                        best = c
                if idx not in self.added_for_removal:
                    self.added_for_removal.append(idx)
            self.remove_job()
        self.best_clique = best
        return best
