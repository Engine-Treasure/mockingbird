# -*- coding: utf-8 -*-

__author__ = "kissg"
__date__ = "2017-02-23"

import random
import string


def gen_random_str(mode=1, length=8):
    s = {
        1: string.letters,
        2: string.digits,
        3: string.letters + string.digits,
        4: string.punctuation,
        5: string.letters + string.punctuation,
        6: string.letters + string.digits + string.punctuation,
    }.get(mode, string.letters)
    return "".join(
        random.SystemRandom().choice(string.letters) for _ in range(length))


if __name__ == '__main__':
    print(gen_random_str())
