#!/usr/bin/env python
# coding: utf-8
from dataclasses import dataclass
import itertools as it
import time
import functools as ft
import heapq


GRID_MP = {"#": "wall", ">": "rightw", "<": "leftw", "^": "upw", "v": "downw"}
INV_GRID_MP = {v: k for k, v in GRID_MP.items()}
BLIZZARD = {"rightw", "leftw", "upw", "downw"}


def parse_fl(fl, grid_mp=GRID_MP):
    lns = open(fl).read().splitlines()
    hlen, vlen = len(lns[0]), len(lns)
    state = {
        "time": 0,
        "player": (0, 1),
        "goal": (vlen - 1, hlen - 2),
        "wall": set(),
        "leftw": set(),
        "rightw": set(),
        "upw": set(),
        "downw": set(),
        "hlen": hlen,
        "vlen": vlen,
    }
    for i, ln in enumerate(lns):
        for j, c in enumerate(ln):
            if c not in grid_mp:
                continue
            state[grid_mp[c]].add((i, j))
    return state


def state_to_grid(state, inv_grid_mp=INV_GRID_MP):
    grid = "\n".join(
        "".join(
            _char(i=i, j=j, state=state, inv_grid_mp=inv_grid_mp)
            for j in range(state["hlen"])
        )
        for i in range(state["vlen"])
    )
    return f"Time: {state['time']}\n\n{grid}"


def _char(i, j, state, inv_grid_mp) -> str:
    ch_char = None
    for cell_type, cval in inv_grid_mp.items():
        if (i, j) not in state[cell_type]:
            continue
        match ch_char:
            case None:
                ch_char = cval
            case int():
                ch_char += 1
            case str():
                ch_char = 2
    if (i, j) == state["player"]:
        ch_char = "P"
    elif ch_char is None and (i, j) == state["goal"]:
        ch_char = "G"
    elif ch_char is None:
        ch_char = "."
    return str(ch_char)


class NextState:
    def __init__(self):
        self.cache = {}

    def __call__(self, state):
        """Brings new state, also caches world state as
        only thing that changes is player position.
        """
        st_time = state["time"]
        if st_time in self.cache:
            new_state = self.cache[st_time].copy()
            new_state["player"] = state["player"]
        else:
            hlen, vlen = state["hlen"], state["vlen"]
            hend, vend = hlen - 1, vlen - 1
            new_state = {
                "time": state["time"] + 1,
                "player": state["player"],
                "goal": state["goal"],
                # never changes no need to create copy
                "wall": state["wall"],
                "leftw": {_move_lt(pi, pj, hlen) for pi, pj in state["leftw"]},
                "rightw": set(_move_rt(pi, pj, hlen) for pi, pj in state["rightw"]),
                "upw": set(_move_up(pi, pj, vlen) for pi, pj in state["upw"]),
                "downw": set(_move_down(pi, pj, vlen) for pi, pj in state["downw"]),
                "hlen": hlen,
                "vlen": vlen,
            }
            self.cache[st_time] = new_state
        return new_state


def _move_lt(pi, pj, hlen):
    # -1 because last col is a wall
    pj = pj - 1 if pj > 1 else hlen - 2
    return (pi, pj)


def _move_rt(pi, pj, hlen):
    pj = pj + 1 if pj < hlen - 2 else 1
    return (pi, pj)


def _move_up(pi, pj, vlen):
    pi = pi - 1 if pi > 1 else vlen - 2
    return (pi, pj)


def _move_down(pi, pj, vlen):
    pi = pi + 1 if pi < vlen - 2 else 1
    return (pi, pj)


@dataclass
class ScoreState:
    hscore: int
    state: dict

    def __lt__(self, other):
        return self.hscore < other.hscore


def timed_fn(f):
    @ft.wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        elp = te - ts
        print(f"Elapsed time: {elp:,.0f}s {elp//60:,.0f}m")
        return result

    return wrap


@timed_fn
def search_path(state, to_disp_state=False):
    cur_time, it, st_wc_time, seen = None, 0, time.time(), set()
    q = [ScoreState(hscore=0, state=state)]
    next_state_fn = NextState()
    while q:
        it += 1
        st = heapq.heappop(q).state
        seen.add(_cache_fn(st))
        _disp_state(it, st, to_disp_state)
        cur_time = __update_progress(
            st_wc_time, cur_time=cur_time, state=st, qlen=len(q), it=it
        )
        if st["player"] == st["goal"]:
            return st["time"]
        next_world_st = next_state_fn(state=st)
        for ss in _next_valid_states(state=next_world_st):
            if _cache_fn(ss.state) in seen:
                # If i have come back to the same state as before after several
                # steps, there is no point continuing the same options again
                continue
            heapq.heappush(q, ss)


def _cache_fn(s):
    return (s["player"], *(tuple(sorted(s[b])) for b in BLIZZARD))


def _disp_state(it, state, to_disp_state):
    if not to_disp_state:
        return
    # clear_output(wait=True)
    print(f"Iteration: {it:,}")
    print(state_to_grid(state))
    time.sleep(1.5)


def _next_valid_states(state):
    """Provides next states but uses A* to select which
    states are searched first.
    """
    for adj_i, adj_j in it.product([-1, 0, 1], [-1, 0, 1]):
        if adj_i != 0 and adj_j != 0:
            # diag paths not allowed
            continue
        pi, pj = state["player"]
        npi, npj = pi + adj_i, pj + adj_j
        new_pos = (npi, npj)
        if (
            (npi < 0)
            or (npj < 0)
            or (npi >= state["vlen"])
            or (npj > state["hlen"])
            or any(
                new_pos in state[obs]
                for obs in ["wall", "leftw", "rightw", "upw", "downw"]
            )
        ):
            continue
        # shallow copy as we are only changing player pos
        new_state = state.copy()
        if npi < 0:
            raise ValueError()
        new_state["player"] = new_pos
        heuristic_score = _manhattan_dist(state=new_state) + new_state["time"]
        yield ScoreState(hscore=heuristic_score, state=new_state)


def _manhattan_dist(state):
    (pi, pj), (gi, gj) = state["player"], state["goal"]
    return abs(pi - gi) + abs(pj - gj)


def __update_progress(st_wc_time, cur_time, state, qlen, it, to_print=True):
    if cur_time == state["time"]:
        return cur_time
    cur_time = state["time"]
    if to_print and it % 5000 == 0:
        el = time.time() - st_wc_time
        print(
            f"\rIteration: {it:,} | Processing current time: {cur_time}"
            f" | Number of states to be explore in queue: {qlen:,}"
            f" | Elapsed: {round(el):,}s {el//60:,}m"
        )
    return cur_time


if __name__ == "__main__":
    input_state = parse_fl("input.txt")
    small_test_state = parse_fl("small_test.txt")
    test_state = parse_fl("test.txt")
    rnd = search_path(input_state, to_disp_state=False)
    print(f"Number of rounds: {rnd}")
