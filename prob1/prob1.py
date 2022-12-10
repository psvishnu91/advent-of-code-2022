"""Advent of code 2022 problem 1 solution

Usage::
    python prob1.py --elf-file elf-calories.txt
"""
import argparse



def _parse_args():
    parser = argparse.ArgumentParser("Problem 1")
    parser.add_argument('--elf-file', '-f', help='Path of the file with the elf calories.')
    return parser.parse_args()


def find_max_calories(elf_file: str) -> int:
    max_cal = -1
    each_elf_cals = 0
    print(elf_file)
    with open(elf_file) as fl:
        for ln in fl:
            if ln != "\n":
                each_elf_cals += int(ln)
            else:
                max_cal = max(max_cal, each_elf_cals)
                each_elf_cals = 0
    return max_cal


if __name__ == "__main__":
    max_cal = find_max_calories(elf_file=_parse_args().elf_file)
    print(f"Maximum calories: {max_cal:,}")
    