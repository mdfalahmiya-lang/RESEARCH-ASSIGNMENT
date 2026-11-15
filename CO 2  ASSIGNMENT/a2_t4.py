"""A2 Task 4 - depth-limited minimax with own evaluation function on Connect-k (gravity board).
Boards: 4x4 connect-3 (b=4), 5x5 connect-4 (b=5), 6x7 connect-4 (b=7).  Seeds: games 500+g.
Evaluation (for the player to maximise): sum over all length-k windows free of enemy discs of 10^(own-1)
minus the same for the opponent, plus a small centre-column bonus.  Terminal win = +/-100000 (not counted as an evaluation call)."""
import random, time, math, sys

class Game:
    def __init__(self, R, C, K): self.R, self.C, self.K = R, C, K; self.windows = self._windows()
    def _windows(self):
        W = []
        for r in range(self.R):
            for c in range(self.C):
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    cells = [(r + i * dr, c + i * dc) for i in range(self.K)]
                    if all(0 <= x < self.R and 0 <= y < self.C for x, y in cells): W.append(cells)
        return W
    def moves(self, b): return [c for c in range(self.C) if b[0][c] == 0]
    def play(self, b, c, p):
        for r in range(self.R - 1, -1, -1):
            if b[r][c] == 0: b[r][c] = p; return r
    def undo(self, b, r, c): b[r][c] = 0
    def wins(self, b, r, c):
        p = b[r][c]
        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            n = 1
            for s in (1, -1):
                x, y = r + s * dr, c + s * dc
                while 0 <= x < self.R and 0 <= y < self.C and b[x][y] == p: n += 1; x += s * dr; y += s * dc
            if n >= self.K: return True
        return False
    def evaluate(self, b, me):
        s = 0
        for w in self.W if hasattr(self, 'W') else self.windows:
            m = o = 0
            for x, y in w:
                v = b[x][y]
                if v == me: m += 1
                elif v: o += 1
            if o == 0 and m: s += 10 ** (m - 1)
            elif m == 0 and o: s -= 10 ** (o - 1)
        for r in range(self.R):
            if b[r][self.C // 2] == me: s += 2
        return s

def minimax(G, b, depth, maxn, me, cnt, last=None):
    """Plain depth-limited minimax. cnt: expanded (internal), evals, terminals."""
    moves = G.moves(b)
    if not moves or depth == 0:
        cnt['evals'] += 1; return G.evaluate(b, me)
    cnt['exp'] += 1
    best = -math.inf if maxn else math.inf; p = me if maxn else -me
    for c in moves:
        r = G.play(b, c, p)
        if G.wins(b, r, c): v = 100000 + depth if maxn else -100000 - depth; cnt['terms'] += 1
        else: v = minimax(G, b, depth - 1, not maxn, me, cnt)
        G.undo(b, r, c)
        best = max(best, v) if maxn else min(best, v)
    return best

def choose(G, b, depth, me, cnt):
    best, bm = -math.inf, None
    order = sorted(G.moves(b), key=lambda c: abs(c - G.C // 2))          # tie-break: centre first
    for c in order:
        r = G.play(b, c, me)
        v = 100000 + depth if G.wins(b, r, c) else minimax(G, b, depth - 1, False, me, cnt)
        G.undo(b, r, c)
        if v > best: best, bm = v, c
    cnt['exp'] += 1
    return bm

def play_game(G, depth, mm_first, rnd):
    b = [[0] * G.C for _ in range(G.R)]; turn = 1; cnt = dict(exp=0, evals=0, terms=0); mm = 1 if mm_first else -1
    t = 0.0; nm = 0
    while True:
        mv = G.moves(b)
        if not mv: return 0, cnt, t, nm
        if turn == mm:
            t0 = time.perf_counter(); c = choose(G, b, depth, mm, cnt); t += time.perf_counter() - t0; nm += 1
        else: c = rnd.choice(mv)
        r = G.play(b, c, turn)
        if G.wins(b, r, c): return (1 if turn == mm else -1), cnt, t, nm
        turn = -turn

if __name__ == '__main__':
    print('GROWTH: first move on the EMPTY board (nodes counted by the code vs the derived formula)')
    print('| board | b | depth d | internal nodes expanded | formula (b^d-1)/(b-1) | eval calls | formula b^d | terminal wins seen | time s |'); print('|---|---|---|---|---|---|---|---|---|')
    for name, (R, C, K), dmax in (('4x4 c3', (4, 4, 3), 7), ('5x5 c4', (5, 5, 4), 6), ('6x7 c4', (6, 7, 4), 6)):
        G = Game(R, C, K); b = C
        for d in range(1, dmax + 1):
            board = [[0] * C for _ in range(R)]; cnt = dict(exp=0, evals=0, terms=0)
            t = time.perf_counter(); choose(G, board, d, 1, cnt); dt = time.perf_counter() - t
            # choose() itself expands the root once: internal nodes = root + below
            print(f"| {name} | {b} | {d} | {cnt['exp']:,} | {(b**d-1)//(b-1):,} | {cnt['evals']:,} | {b**d:,} | {cnt['terms']} | {dt:.3f} |")
            if dt > 12: break
    print('\nQUALITY: minimax player vs random, 20 games each (alternating who moves first), seeds 500+g')
    print('| board | depth | wins | draws | losses | win rate | mean time per move (s) | mean eval calls per game |'); print('|---|---|---|---|---|---|---|---|')
    for name, (R, C, K), depths in (('4x4 c3', (4, 4, 3), (1, 2, 3, 4)), ('5x5 c4', (5, 5, 4), (1, 2, 3, 4)), ('6x7 c4', (6, 7, 4), (1, 2, 3, 4, 5))):
        G = Game(R, C, K)
        for d in depths:
            w = dr = l = 0; tt = 0.0; nm = 0; ev = 0
            for g in range(20):
                res, cnt, t, n = play_game(G, d, g % 2 == 0, random.Random(500 + g))
                w += res == 1; dr += res == 0; l += res == -1; tt += t; nm += n; ev += cnt['evals']
            print(f'| {name} | {d} | {w} | {dr} | {l} | {w/20:.0%} | {tt/nm:.3f} | {ev/20:,.0f} |')
            sys.stdout.flush()
