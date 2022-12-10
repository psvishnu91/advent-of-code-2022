"""Advent of code 2022 problem 5 solution

Usage::
    python day3/prob5-6.py --file day3/input.txt
"""
import argparse
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

ORD_A = ord("A")
ORD_a = ord("a")


def parse_args():
    parser = argparse.ArgumentParser("Problem 3")
    parser.add_argument(
        "--file", "-f", help="Path of the file with Rock paper scissor strategy."
    )
    return parser.parse_args()


def compute_misplaced_priority(input_file: str) -> int:
    score = 0
    for ln in iter_file(fl=input_file):
        score += _ln_to_score(ln=ln)
    return score


def iter_file(fl):
    with open(fl) as f:
        for ln in f:
            ln = ln.strip("\n")
            yield ln


def _ln_to_score(ln: str) -> int:
    rs1 = len(ln) // 2
    common_item = list(set(ln[:rs1]) & set(ln[rs1:]))[0]
    return _to_priority(item=common_item)


def _to_priority(item: str) -> int:
    item_ord = ord(item)
    if item_ord < ORD_a:
        return item_ord - ORD_A + 27
    else:
        return item_ord - ORD_a + 1


def compute_badge_priority(input_file: str) -> int:
    score = 0
    group = []
    # with open(input_fl) as fl:
    #     for ln in fl:
    #         ln.strip("\n")
    for i, ln in enumerate(iter_file(fl=input_file), start=1):
        if i % 3 == 0:
            common = list(group[0] & group[1] & set(ln))[0]
            score += _to_priority(item=common)
            group = []
        else:
            group.append(set(ln))
    return score


if __name__ == "__main__":
    misplaced_priority = compute_misplaced_priority(input_file=parse_args().file)
    print(f"Misplaced Priority: {misplaced_priority}")
    badge_priority = compute_badge_priority(input_file=parse_args().file)
    print(f"Badge Priority: {badge_priority}")
