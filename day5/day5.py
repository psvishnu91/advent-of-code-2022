"""Advent of code 2022 day 5 solution

https://adventofcode.com/2022/day/5

Usage::

    # CrateMover 9001, does not reverse stacks
    python -m day5.day5 --file day5/input.txt

    # CrateMover 9000, does reverses stacks
    python -m day5.day5 --file day5/input.txt --reverse
"""
import dataclasses
import re
import util

from typing import cast
from typing import NewType
from typing import Generator


Stacks = NewType("Stacks", list[list[str]])


@dataclasses.dataclass
class Move:
    src: int
    tgt: int
    num: int


def main():
    opts = util.parse_args(
        args={
            "--reverse": dict(
                help="Should we reverse the crate while moving stacks",
                default=False,
                action="store_true",
            ),
        }
    )
    iter_fl = util.iter_fl(fl=opts.file)
    stacks = _parse_stacks(iter_fl)
    for ln in iter_fl:
        move = _parse_move(ln)
        _move_stacks_inplace(stacks=stacks, move=move, to_reverse=opts.reverse)
    util.log.info(f"Top of stacks {_fetch_top_crates(stacks=stacks)}")


def _parse_stacks(iter_fl: Generator[str, None, None]) -> Stacks:
    """Parse stack lines

    Sample input::

        iter_fl = iter(
            [
                "    [G]        ",
                "    [D]        ",
                "    [C] [S]    ",
                "[N] [N] [R] [B]",
                "[R] [P] [W] [N]",
                " 1   2   3   4 ",
                "",
            ],
        )

    Sample output::

       [["R", "N"], ["P", "N", "C", "D", "G"], ["W", "R", "S"], ["N", "B"]]
    """
    stk_lns = []
    num_stks = None
    for ln in iter_fl:
        # The stacks are indicated with a line of stack numbers like below
        # " 1   2   3   4   5   6   7   8   9 "
        if ln[1] != "1":
            stk_lns.append(ln)
        else:
            num_stks = int(ln[-2])
            break
    # skip the blank line after stack identifier
    next(iter_fl)
    return _parse_stacks_helper(lns=stk_lns, num_stks=cast(int, num_stks))


def _parse_stacks_helper(lns: list[list[str]], num_stks: int) -> Stacks:
    util.log.info(f"{num_stks=}")
    stks = Stacks([[] for _ in range(num_stks)])
    for ln in reversed(lns):
        for j, char in enumerate(ln):
            # "[R] [P] [W] [N] [M] [P] [R] [Q] [L]"
            if char == " " or (j - 1) % 4 != 0:
                continue
            stk_ix = (j - 1) // 4
            stks[stk_ix].append(char)
    return stks


def _parse_move(ln: str) -> Move:
    """
    Sample input: "move 11 from 4 to 1"
    Sample output: Move(src=4, tgt=1, num=11)
    """
    num, src, tgt = map(int, re.findall(r"move (\d+) from (\d+) to (\d+)", ln)[0])
    return Move(src=src - 1, tgt=tgt - 1, num=num)


def _move_stacks_inplace(stacks: Stacks, move: Move, to_reverse: bool = True) -> None:
    """CrateMover 9000 moves one crate at a time and CrateMover 9001 moves all
    crates at once. So for CrateMover 9000, the order is reversed in the target
    stack and not for CM 9001.
    """
    util.log.debug(stacks, move)
    src_stk, tgt_stk, num = stacks[move.src], stacks[move.tgt], move.num
    moved_crates = reversed(src_stk[-num:]) if to_reverse else src_stk[-num:]
    tgt_stk.extend(moved_crates)
    stacks[move.src] = src_stk[:-num]


def _fetch_top_crates(stacks: Stacks) -> str:
    return "".join(str(stk[-1]) for stk in stacks)


if __name__ == "__main__":
    main()
