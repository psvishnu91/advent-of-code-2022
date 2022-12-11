"""Advent of code 2022 day 4 solution

Usage::
    python -m day4.day4 --file day4/input.txt
"""
import dataclasses
import util

from typing import cast


@dataclasses.dataclass(frozen=True)
class Range:
    lt: int
    rt: int


@dataclasses.dataclass(frozen=True)
class RangePair:
    first: Range
    second: Range


def main() -> None:
    subsets = 0
    overlaps = 0
    for rp in util.iter_input_fl(parser=_parser):
        rp = cast(RangePair, rp)
        subsets += _is_subset_of(rp.first, rp.second) or _is_subset_of(
            rp.second, rp.first
        )
        overlaps += _any_rt_overlap(rp.first, rp.second) or _any_rt_overlap(
            rp.second, rp.first
        )
    print(f"Number of full subsets: {subsets}")
    print(f"Number of overlaps: {overlaps}")


def _is_subset_of(small_rng: Range, big_rng: Range) -> bool:
    return small_rng.lt >= big_rng.lt and small_rng.rt <= big_rng.rt


def _any_rt_overlap(rng1: Range, rng2: Range) -> bool:
    return (rng2.lt <= rng1.lt <= rng2.rt) or (rng2.lt <= rng1.rt <= rng2.rt)


def _parser(ln: str) -> RangePair:
    range_parse = lambda r: Range(*map(int, r.split("-")))
    lt, rt = ln.split(",")
    return RangePair(
        first=range_parse(lt),
        second=range_parse(rt),
    )


if __name__ == "__main__":
    main()
