#!/usr/bin/env python3

import sys
import argparse

import cards
import utils


######## Actions

def dump(card, *ns):
    if len(ns) == 0:
        ns = range(0, len(card))
    for i in map(int, ns):
        print(utils.coloured(utils.Colour.YELLOW, '#{}:'.format(i)))
        print(card.sectors[i].pretty)
        print()

def all_keys(card):
    for key in sorted(map(utils.format_key, utils.all_keys(card))):
        print(key if key in utils.mfoc_default_keys else utils.coloured(utils.Colour.RED, key, highlighted=True))

def all_keys_mfoc(card):
    new_keys = set(map(utils.format_key, utils.all_keys(card))) - utils.mfoc_default_keys
    for key in sorted(new_keys):
        print('-k '+key, end=' ')
    print()

def all_keys_mfcuk(card):
    for (i,s) in enumerate(card.sectors, start=0):
        for k in s.keys:
            print('-V {}:X:{}'.format(i, utils.format_key(k)), end=' ')
    print()

########


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--no-colour', help='disable colour in output', action='store_true')
    parser.add_argument('action', help='action to perform')
    parser.add_argument('argument', nargs='*', help='argument to pass to the action')
    args = parser.parse_args()

    if args.no_colour:
        def no_colour(colour, msg, highlighted=False):
            return msg
        utils.coloured = no_colour

    card = cards.MifareClassic1k(sys.stdin.buffer)
    globals()[args.action](card, *args.argument)
