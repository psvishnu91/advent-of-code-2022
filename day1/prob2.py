"""Advent of code 2022 problem 2 solution

Usage::
    python day1/prob2.py --elf-file day1/elf-calories.txt
"""
import argparse

#: Num top elves
TOP_N = 3


def _parse_args():
    parser = argparse.ArgumentParser("Problem 2")
    parser.add_argument(
        "--elf-file", "-f", help="Path of the file with the elf calories."
    )
    return parser.parse_args()


def find_max_calories(elf_file: str) -> int:
    max_cal = -1
    elf_cals = []
    each_elf_cals = 0
    with open(elf_file) as fl:
        for ln in fl:
            if ln != "\n":
                each_elf_cals += int(ln)
            else:
                elf_cals.append(each_elf_cals)
                each_elf_cals = 0
    return sum(sorted(elf_cals)[-TOP_N:])


if __name__ == "__main__":
    max_cal = find_max_calories(elf_file=_parse_args().elf_file)
    print(f"Calories of top {TOP_N} elves: {max_cal}")
