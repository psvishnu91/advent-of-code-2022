"""Advent of code 2022 problem 3 solution

A B C - opponent Rock paper scissor resply
X Y Z - our Rock paper scissor resply

Usage::
    python prob3/prob3.py --file day2/input.txt
"""
import argparse
import dataclasses
import enum
import logging

from typing import Callable


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class RPS(enum.IntEnum):

    ROCK = 1
    PAPER = 2
    SCISSOR = 3


@dataclasses.dataclass(frozen=True)
class Round:

    mine: RPS
    opponent: RPS


def parse_args():
    parser = argparse.ArgumentParser("Problem 3")
    parser.add_argument(
        "--file", "-f", help="Path of the file with Rock paper scissor strategy."
    )
    return parser.parse_args()


def compute_rps_score(input_file: str, decode_line: Callable[[str], Round]) -> int:
    total_score = 0
    with open(input_file) as fl:
        for i, ln in enumerate(fl):
            if ln == "" or ln == "\n":
                continue
            round = decode_line(ln)
            score, win = round_score(round=round)
            total_score += score
            log.debug(
                f"\tRound: {i}\t{ln=}\t{round=}\twe {win}\t{score=}\t{total_score=}"
            )
    return total_score


def _decode_line(ln: str) -> Round:
    """Convert each round to human readable hand."""
    hand_map = {
        "A": RPS.ROCK,
        "X": RPS.ROCK,
        "B": RPS.PAPER,
        "Y": RPS.PAPER,
        "C": RPS.SCISSOR,
        "Z": RPS.SCISSOR,
    }
    return Round(
        mine=hand_map[ln[2]],
        opponent=hand_map[ln[0]],
    )


def round_score(round: Round) -> tuple[int, str]:
    if round.mine == round.opponent:
        # draw
        score = 3
        win = "drew"
    elif (
        (round.mine == RPS.ROCK and round.opponent == RPS.SCISSOR)
        or (round.mine == RPS.PAPER and round.opponent == RPS.ROCK)
        or (round.mine == RPS.SCISSOR and round.opponent == RPS.PAPER)
    ):
        # we win
        score = 6
        win = "won"
    else:
        # we lose
        score = 0
        win = "lost"
    return (score + round.mine, win)


if __name__ == "__main__":
    score = compute_rps_score(
        input_file=parse_args().file,
        decode_line=_decode_line,
    )
    print(f"Expected score: {score}")
