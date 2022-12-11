import argparse
import logging

from typing import Any
from typing import Callable
from typing import Generator
from typing import Optional
from typing import Union


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def parse_args(args: Optional[dict[str, dict[str, Any]]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser("Advent of code problem")
    parser.add_argument("--file", "-f", help="Path to the input file.")
    args = args or {}
    for name, kwargs in args.items():
        parser.add_argument(name, **kwargs)
    return parser.parse_args()


def iter_input_fl(
    parser: Optional[Callable[[str], Any]] = None
) -> Generator[Union[Any, str], None, None]:
    for ln in iter_fl(fl=parse_args().file):
        if parser:
            yield parser(ln)
        else:
            yield ln


def iter_fl(fl: str) -> Generator[str, None, None]:
    with open(fl) as f:
        for ln in f:
            ln = ln.strip("\n")
            yield ln
