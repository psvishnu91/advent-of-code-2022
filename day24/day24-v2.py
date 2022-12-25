from dataclasses import dataclass, field
import typing as t
import itertools as it
import collections as c
import json
from copy import deepcopy
import math
import time
import functools as ft
import numpy as np
import tqdm.notebook
import heapq


GRID_MP = {"#": "wall", ">": "rightw", "<": "leftw", "^": "upw", "v": "downw"}
INV_GRID_MP = {v: k for k, v in GRID_MP.items()}
BLIZZARD = {"rightw", "leftw", "upw", "downw"}


def parse_fl(fl, grid_mp=GRID_MP):
    lns = open(fl).read().splitlines()
    hlen, vlen = len(lns[0]), len(lns)
    world = {
        "time": 0,
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
            world[grid_mp[c]].add((i, j))
    return (0, 1), world


def state_to_grid(world, player=(0, 1), inv_grid_mp=INV_GRID_MP):
    grid = "\n".join(
        "".join(
            _char(i=i, j=j, world=world, player=player, inv_grid_mp=inv_grid_mp)
            for j in range(world["hlen"])
        )
        for i in range(world["vlen"])
    )
    return f"Time: {world['time']}\n\n{grid}"


def _char(i, j, world, player, inv_grid_mp) -> str:
    ch_char = None
    for cell_type, cval in inv_grid_mp.items():
        if (i, j) not in world[cell_type]:
            continue
        match ch_char:
            case None:
                ch_char = cval
            case int():
                ch_char += 1
            case str():
                ch_char = 2
    if (i, j) == player:
        ch_char = "P"
    elif ch_char is None and (i, j) == world["goal"]:
        ch_char = "G"
    elif ch_char is None:
        ch_char = "."
    return str(ch_char)


class World:
    def __init__(self, world_at_t0):
        self.cache = {0: world_at_t0}
        self.max_t = 0

    def at_time(self, t):
        """Brings new world, also caches world world as
        only thing that changes is player position.
        """
        if t in self.cache:
            new_world = self.cache[t]
        else:
            assert t == self.max_t + 1, "We move build world 1 second at a time"
            self.max_t = t
            world = self.cache[t - 1]
            hlen, vlen = world["hlen"], world["vlen"]
            hend, vend = hlen - 1, vlen - 1
            new_world = {
                "time": world["time"] + 1,
                "goal": world["goal"],
                # never changes no need to create copy
                "wall": world["wall"],
                "leftw": {_move_lt(pi, pj, hlen) for pi, pj in world["leftw"]},
                "rightw": set(_move_rt(pi, pj, hlen) for pi, pj in world["rightw"]),
                "upw": set(_move_up(pi, pj, vlen) for pi, pj in world["upw"]),
                "downw": set(_move_down(pi, pj, vlen) for pi, pj in world["downw"]),
                "hlen": hlen,
                "vlen": vlen,
            }
            self.cache[t] = new_world
        return new_world


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
    cur_time: int
    player: tuple

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
def search_wrapper(player, goal, st_world, disp_simple=True, one_trip=True):
    worlder = World(st_world)
    kwrgs = dict(worlder=worlder, disp_simple=disp_simple)
    if one_trip:
        trip_times = [search_path(player=player, goal=goal, cur_time=0, **kwrgs)]
    else:
        t1_tm = search_path(player=player, goal=goal, cur_time=0, **kwrgs)
        t2_tm = search_path(player=goal, goal=player, cur_time=t1_tm, **kwrgs)
        t3_tm = search_path(player=player, goal=goal, cur_time=t2_tm, **kwrgs)
        trip_times = [t1_tm, t2_tm, t3_tm]
    for tnum, tm in enumerate(trip_times, start=1):
        print(f"Trip {tnum} | Time taken: {tm} | Total time: {sum(trip_times)}")
    return trip_times


def search_path(player, goal, worlder, cur_time, disp_simple):
    q = [ScoreState(hscore=0, player=player, cur_time=cur_time)]
    it, seen, = (
        0,
        set(),
    )
    while q:
        state = heapq.heappop(q)
        ct, plyr = state.cur_time, state.player
        seen.add((ct, plyr))
        if plyr == goal:
            return ct
        new_world = worlder.at_time(ct + 1)
        for ss in _next_valid_states(new_world=new_world, player=plyr, goal=goal):
            if (ss.cur_time, ss.player) in seen:
                # If i have come back to the same state as before after several
                # steps, there is no point continuing the same options again
                continue
            heapq.heappush(q, ss)
        it += 1
        _disp_progress(
            it=it,
            player=plyr,
            cur_time=ct,
            worlder=worlder,
            disp_simple=disp_simple,
            qlen=len(q),
        )


def _next_valid_states(new_world, player, goal):
    """Provides next states but uses A* to select which
    states are searched first.
    """
    for adj_i, adj_j in it.product([-1, 0, 1], [-1, 0, 1]):
        if adj_i != 0 and adj_j != 0:
            # diag paths not allowed
            continue
        pi, pj = player
        npi, npj = pi + adj_i, pj + adj_j
        new_pos = (npi, npj)
        if (
            (npi < 0)
            or (npj < 0)
            or (npi >= new_world["vlen"])
            or (npj > new_world["hlen"])
            or any(
                new_pos in new_world[obs]
                for obs in ["wall", "leftw", "rightw", "upw", "downw"]
            )
        ):
            continue
        heuristic_score = _manhattan_dist(player, goal=goal) + new_world["time"]
        yield ScoreState(
            hscore=heuristic_score, player=new_pos, cur_time=new_world["time"]
        )


def _manhattan_dist(player, goal):
    (pi, pj), (gi, gj) = player, goal
    return abs(pi - gi) + abs(pj - gj)


def _disp_progress(it, player, cur_time, worlder, qlen, disp_simple):
    if disp_simple:
        _simple_progress(cur_time=cur_time, qlen=qlen, it=it)
        return
    # clear_output(wait=True)
    print(f"Iteration: {it:,}")
    print(state_to_grid(player=player, world=worlder.at_time(cur_time)))
    time.sleep(1.5)


def _simple_progress(cur_time, qlen, it):
    if it % 1000_000 == 0:
        # clear_output(wait=True)
        print(
            f"Iteration: {it:,} | Processing current time: {cur_time}"
            f" | Number of states to be explore in queue: {qlen:,}"
        )
    return cur_time


if __name__ == "__main__":
    orig_player, input_world = parse_fl("input.txt")
    player, small_test_world = parse_fl("small_test.txt")
    player, test_world = parse_fl("test.txt")
    wld = test_world
    rnd = search_wrapper(
        player=orig_player,
        goal=wld["goal"],
        st_world=wld,
        disp_simple=True,
        one_trip=False,
    )
