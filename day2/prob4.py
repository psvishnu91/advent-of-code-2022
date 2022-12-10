"""Advent of code 2022 problem 4 solution

A B C - opponent Rock paper scissor resply
X Y Z - lose, draw, win resply

Usage::
    python prob3/prob3.py --file day2/input.txt
"""
import prob3 as P3
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def _decode_line(ln: str) -> P3.Round:
    """Convert each round to human readable hand."""
    hand_map = {
        "A": P3.RPS.ROCK,
        "B": P3.RPS.PAPER,
        "C": P3.RPS.SCISSOR,
    }
    opponent = hand_map[ln[0]]
    our_strat = ln[2]
    if our_strat == "Y":
        # draw
        mine = opponent
    elif our_strat == "Z":
        # win
        mine = {
            P3.RPS.ROCK: P3.RPS.PAPER,
            P3.RPS.PAPER: P3.RPS.SCISSOR,
            P3.RPS.SCISSOR: P3.RPS.ROCK,
        }[opponent]
    else:
        # we lose
        mine = {
            P3.RPS.ROCK: P3.RPS.SCISSOR,
            P3.RPS.PAPER: P3.RPS.ROCK,
            P3.RPS.SCISSOR: P3.RPS.PAPER,
        }[opponent]
    return P3.Round(mine=mine, opponent=opponent)


if __name__ == "__main__":
    score = P3.compute_rps_score(
        input_file=P3.parse_args().file,
        decode_line=_decode_line,
    )
    print(f"Expected score: {score}")
