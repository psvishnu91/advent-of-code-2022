import multiprocessing as mpl

import json
from copy import deepcopy
import time
import functools as ft
import tqdm
import re


def parse_raw_input(fl):
    bps = {}
    input_lns = open("input.txt").read().splitlines()
    for ln in input_lns:
        (
            bp_id,
            ore_rbt_ore_cost,
            cly_rbt_ore_cost,
            obs_rbt_ore_cost,
            obs_rbt_clay_cost,
            geode_rbt_ore_cost,
            geode_rbt_obs_cost,
        ) = (
            int(n)
            for n in re.findall(
                r"Blueprint (\d+): Each ore robot costs (\d+) ore. Each clay robot costs (\d+) ore. Each obsidian robot costs (\d+) ore and (\d+) clay. Each geode robot costs (\d+) ore and (\d+) obsidian.",
                ln,
            )[0]
        )
        bps[bp_id] = {
            "ore_robot": {"ore": ore_rbt_ore_cost},
            "clay_robot": {"ore": cly_rbt_ore_cost},
            "obsidian_robot": {"ore": obs_rbt_ore_cost, "clay": obs_rbt_clay_cost},
            "geode_robot": {"ore": geode_rbt_ore_cost, "obsidian": geode_rbt_obs_cost},
        }
    return bps


def default_player():
    return dict(
        ore=0,
        clay=0,
        obsidian=0,
        geode=0,
        rate=dict(
            ore=1,
            clay=0,
            obsidian=0,
            geode=0,
        ),
    )


def parse_input(fl):
    blue_prints = [json.loads(ln) for ln in open(fl).read().splitlines()]
    out = {}
    for bp in blue_prints:
        bp = deepcopy(bp)
        bp_num = bp["Blueprint"]
        del bp["Blueprint"]
        out[bp_num] = bp
    return out


def max_geodes_bp(blueprint, max_time=24, toprint=False) -> int:
    player = default_player()
    return max_geodes_rec(
        bp=blueprint,
        player=deepcopy(player),
        cur_time=0,
        max_time=max_time,
        cache={},
        toprint=toprint,
    )


def max_geodes_rec(bp, player, cur_time, max_time, cache, toprint) -> int:
    if cur_time == max_time:
        return player["geode"]
    ckey = _cache_key(cur_time, player)
    if ckey in cache:
        return cache[ckey]
    buildable_bots = list(buildable_robots(bp=bp, player=player))
    _update_player_rsrc_inp(player=player)
    dflt_kwargs = dict(
        bp=bp, cur_time=cur_time + 1, cache=cache, toprint=toprint, max_time=max_time
    )
    build_opts = [
        max_geodes_rec(
            player=_build_bot_inp(bot=bot, bot_reqs=bp[bot], player=deepcopy(player)),
            **dflt_kwargs,
        )
        for bot in buildable_bots
    ]
    if toprint:
        print(
            f"Time: {cur_time}, {player}, buildable bots: {set(buildable_robots(bp=bp, player=player))}"
        )
    nobuild_geodes = max_geodes_rec(
        player=deepcopy(player),
        **dflt_kwargs,
    )
    build_geodes = max(build_opts) if build_opts else 0
    mx = max(build_geodes, nobuild_geodes)
    cache[ckey] = mx
    return mx


def _bot_to_rsrc(bot):
    if bot is None:
        return None
    return bot.rstrip("_robot")


def _build_bot_inp(bot, bot_reqs, player):
    for rsrc, rsrc_cnt in bot_reqs.items():
        player[rsrc] -= rsrc_cnt
    player["rate"][_bot_to_rsrc(bot)] += 1
    return player


def _update_player_rsrc_inp(player):
    for rsrc, rate in player["rate"].items():
        player[rsrc] += rate


def buildable_robots(bp, player):
    if _is_buildable(bot_reqs=bp["geode_robot"], player=player):
        yield "geode_robot"
        return
    for robot, reqs in bp.items():
        if not _is_buildable(bot_reqs=reqs, player=player):
            continue
        if robot == "geode_robot":
            yield robot
            continue
        # maximum required number of rsrcs tht is created by this bot
        # if we already are producing max num, there's no point building
        # more of such bots
        bot_rsrc = _bot_to_rsrc(robot)
        max_reqmt = max_rsrc_reqmt(bp=bp, bot_rsrc=bot_rsrc)
        if player["rate"][bot_rsrc] < max_reqmt:
            yield robot


def max_rsrc_reqmt(bp, bot_rsrc):
    return max(reqs.get(bot_rsrc, 0) for reqs in bp.values())


def _is_buildable(bot_reqs, player):
    for rsrc, min_val in bot_reqs.items():
        if player[rsrc] < min_val:
            return False
    else:
        return True


def _cache_key(cur_time, player):
    p, rates = player, player["rate"]
    return (
        f"{cur_time}, {p['ore']}, {p['clay']}, {p['obsidian']}, {p['geode']}"
        f"{rates['ore']}, {rates['clay']}, {rates['obsidian']}, {rates['geode']} "
    )


def wrapper(bp_id_bp, max_time):
    bp_id, bp = bp_id_bp
    return (bp_id, max_geodes_bp(blueprint=bp, max_time=max_time))


if __name__ == "__main__":
    test_bps = parse_input("parsed_test.txt")
    input_bps = parse_raw_input("input.txt")
    chosen_bps = list(input_bps.items())[:3]
    mx_fn = ft.partial(wrapper, max_time=32)
    st = time.time()
    with mpl.Pool(3) as p:
        vals = list(tqdm.tqdm(p.imap(mx_fn, chosen_bps), total=len(chosen_bps)))
    for _id, mx in sorted(vals):
        print(_id, mx)
    print(dict(sorted(vals)))
    score = 1
    for _, mx in vals:
        score *= mx
    print("Score:", score)
    print(f"Elapsed: {(time.time()-st)/60:.0f}m")
