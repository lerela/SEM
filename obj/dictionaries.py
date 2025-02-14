# -*- coding: utf-8 -*-

"""
file: dictionaries.py

Description: define dictionary compilation procedures: one for token
dictionaries (builds a set) and one for multiword dictionaries (builds
a Trie object as defined in trie.py).

author: Yoann Dupont
copyright (c) 2016 Yoann Dupont - all rights reserved

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import codecs, cPickle

from obj.trie import Trie

NUL = u""

def compile_token(infile, encoding):
    """tokens = set()
    for line in codecs.open(infile, "rU", encoding):
        line = line.strip()
        if line != "":
            tokens.add(line)
    return tokens"""
    return set(codecs.open(infile, "rU", encoding).read().split(u"\n"))

def compile_multiword(infile, encoding):
    trie = Trie()
    for line in codecs.open(infile, "rU", encoding):
        seq = line.strip().split()
        trie.add(seq)
    return trie
