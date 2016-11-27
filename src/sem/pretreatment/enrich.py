<<<<<<< HEAD
from obj.tree        import Tree, BooleanNode, ListNode, TokenNode, MultiWordNode
from obj.information import Informations
from obj.corpus      import InCorpus, OnCorpus
from obj.logger      import log

def enrich(incorpus, info, outcorpus=None, verbose=False):
    
    if not outcorpus:
        outcorpus = OnCorpus()

    if verbose:
        log('Enriching file "%s"...\n' %infile)

    infile.seek(0)

    if isinstance(info, str):
        log('loading %s' %info)
        info = Informations(info)

    l   = mkentry(incorpus, info.bentries() + info.aentries())
    fmt = "\t".join(["%(" + entry + ")s" for entry in info.bentries()])

    if verbose:
        log("Loading endogene traits...")
    for endo in info.endogenes():
        l    = add(l, endo)
        fmt += "\t%(" + endo.get_name() + ")s"
    if verbose:
        log(" Done.\n")

    if verbose:
        log("Loading exogene traits...")
    for exo in info.exogenes():
        if isinstance(exo.root, TokenNode):
            l = add(l, exo)
        elif isinstance(exo.root, MultiWordNode):
            l = addSequence(l, exo)
        else:
            raise RuntimeError('Unknown node type "%s"...' %exo.__class__.__name__)
        fmt += "\t%(" + exo.get_name() + ")s"
    if verbose:
        log(" Done.\n")
    
    if info.aentries() != []:
        fmt += "\t" + "\t".join(["%(" + entry + ")s" for entry in info.aentries()])

    if verbose:
        log("Outputting...")
    for sent in l:
        outcorpus.putformat(sent, fmt)
    if verbose:
        log(" Done.\n")

    return outcorpus

def add(corpus, trait):
    def to_pseudo_boolean_if_possible(string):
        s = string.lower()
        return ("1" if s=="true" else "0" if s=="false" else string)

    name = trait.get_name()
    for sent in corpus:
        token = []
        for i in range(len(sent)):
            enriched = dict(sent[i])
            enriched[name] = to_pseudo_boolean_if_possible(trait.eval(sent, i))
            token.append(enriched)
        yield token

def addSequence(corpus, trait):
    """
    multi-words dictionaries are "recursive" dictionaries which form a prefix
    tree. Each word is a key of the dictionary and the depth of the tree is the
    nth word in the multi-word entity.
    There is a match when the empty string key is found. Currently, the shortest
    matching entity is used.
    """
    
    name     = trait.get_name()
    resource = trait.root.value
    NUL      = ""
    
    if not resource:
        for sent in corpus:
            l = []
            for token in sent:
                y = dict(token)
                y[name] = 'O'
                l.append(y)
            yield l
    
    for sent in corpus:
        tmp       = resource
        l         = [dict(elt) for elt in sent]
        length    = len(sent)
        fst       = 0
        cur       = 0
        criterion = False
        ckey      = None

        while not criterion:
            cont = True
            while cont and (cur < length):
                if (NUL not in tmp):
                    ckey = sent[cur]["word"]
                    
                    if (ckey in tmp):
                        tmp = tmp[ckey]
                        cur += 1
                    else:
                        cont = False
                else:
                    cont = False
            
            if NUL in tmp:
                l[fst][name] = 'B'
                for i in range(fst+1, cur):
                    l[i][name] = 'I'
                fst = cur
            else:
                l[fst][name] = 'O'
                fst += 1
                cur = fst
            tmp = resource

            criterion = fst >= length - 1

        if not name in list(l[-1].keys()):
            l[-1][name] = 'O'
        yield l

def mkentry(it, cols):
    for x in it:
        lines = []
        for l in x:
            l2 = {}
            for c,v in zip(cols, l.split()):
                l2[c] = v
            lines.append(l2)
        yield lines


if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Adds information to a file using and XML-styled configuration file.")

    parser.add_argument("infile",
                        help="The input file (CoNLL format)")
    parser.add_argument("infofile",
                        help="The information file (XML format)")
    parser.add_argument("outfile",
                        help="The output file (CoNLL format)")
    parser.add_argument("--input-encoding", dest="ienc",
                        help="Encoding of the input (default: UTF-8)")
    parser.add_argument("--output-encoding", dest="oenc",
                        help="Encoding of the input (default: UTF-8)")
    parser.add_argument("--encoding", dest="enc", default="UTF-8",
                        help="Encoding of both the input and the output (default: UTF-8)")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="Basic feedback for user (default: False).")
    
    arguments = (sys.argv[2:] if __package__ else sys.argv)
    parser    = parser.parse_args(arguments)
    
    with open(parser.infile, 'rb') as infile, open(parser.outfile, 'wb') as outfile:
        incorpus = InCorpus(infile, ienc=parser.ienc or parser.enc)
        outcorpus = OnCorpus(outfile, oenc=parser.oenc or parser.enc)

        enrich(incorpus, parser.infofile, outcorpus,
           verbose=parser.verbose)

    sys.exit(0)
=======
#-*- coding: utf-8 -*-

"""
file: enrich.py

Description: this program is used to enrich a CoNLL-formatted file with
various features.

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

import logging

# measuring time laps
import time
from datetime import timedelta

from obj.information import Informations
from obj.IO.KeyIO    import KeyReader, KeyWriter
from obj.logger      import default_handler, file_handler

import os.path
enrich_logger = logging.getLogger("sem.%s" %os.path.basename(__file__).split(".")[0])
enrich_logger.addHandler(default_handler)

def enrich(keycorpus, informations):
    """
    An iterator to enrich a corpus. It will go through the data and
    generate features, one feature at a time. If the feature has the
    is_sequence property, it be called once and enrich the whole
    sentence. If a feature does not have the is_sequence property, it
    will be called at each and every token.
    
    Parameters
    ----------
    keycorpus : list of list of dict / obj.storage.Corpus
        the input data, contains an object representing CoNLL-formatted
        data. Each token is a dict which works like TSV.
    informations : list of feature
        the features to enrich the keycorpus with.
    
    Yields
    ------
    list of dict
        the current sentence enriched with informations
    """
    
    for p in keycorpus:
        for feature in informations.features:
            if feature.is_sequence:
                for i, value in enumerate(feature(p)):
                    p[i][feature.name] = value
            else:
                for i in range(len(p)):
                    p[i][feature.name] = feature(p, i)
                    if feature.is_boolean:
                        p[i][feature.name] = int(p[i][feature.name])
        yield p

def document_enrich(document, informations, log_level="WARNING", log_file=None):
    """
    Updates the CoNLL-formatted corpus inside a document with various
    features.
    
    Parameters
    ----------
    document : obj.storage.Document
        the input data, contains an object representing CoNLL-formatted
        data. Each token is a dict which works like TSV.
    informations : list of feature
        the features to enrich the keycorpus with.
    log_level : str or int
        the logging level
    log_file : str
        if not None, the file to log to (does not remove command-line
        logging).
    """
    
    start = time.time()
    
    if log_file is not None:
        enrich_logger.addHandler(file_handler(log_file))
    enrich_logger.setLevel(log_level)
    
    if type(informations) in (str, unicode):
        enrich_logger.info('loading %s' %informations)
        informations = Informations(informations)
    
    missing_fields = set(informations.bentries + informations.aentries) - set(document.corpus.fields)
    
    if len(missing_fields) > 0:
        raise ValueError("Missing fields in input corpus: %s" u",".join([sorted(missing_fields)]))
    
    enrich_logger.debug('enriching file "%s"' %document.name)
    
    new_fields             = [feature.name for feature in informations.features if feature.display]
    document.corpus.fields = informations.bentries + new_fields + informations.aentries
    nth                    = 0
    for i, sentence in enumerate(enrich(document.corpus, informations)):
        for j, token in enumerate(sentence):
            for field in new_fields:
                document.corpus.sentences[i][j][field] = token[field]
        nth += 1
        if (0 == nth % 1000):
            enrich_logger.debug('%i sentences enriched' %nth)
    enrich_logger.debug('%i sentences enriched' %nth)
    
    laps = time.time() - start
    enrich_logger.info("done in %s" %timedelta(seconds=laps))

def enrich_file(infile, infofile, outfile,
                mode=u"label",
                ienc="UTF-8", oenc="UTF-8",
                log_level="WARNING", log_file=None):
    """
    Takes a CoNLL-formatted file and write another CoNLL-formatted file
    with additional features in it.
    
    Parameters
    ----------
    infile : str
        the CoNLL-formatted input file.
    infofile : str
        the XML file containing the different features.
    mode : str
        the mode to use for infofile. Some inputs may only be present in
        a particular mode. For example, the output tag is only available
        in "train" mode.
    log_level : str or int
        the logging level.
    log_file : str
        if not None, the file to log to (does not remove command-line
        logging).
    """
    
    start = time.time()
    
    if log_file is not None:
        enrich_logger.addHandler(file_handler(log_level))
    enrich_logger.setLevel(log_level)
    enrich_logger.info('parsing enrichment file "%s"' %infofile)
    
    informations = Informations(path=infofile, mode=mode)
    
    enrich_logger.debug('enriching file "%s"' %infile)
    
    with KeyWriter(outfile, oenc, informations.bentries + [feature.name for feature in informations.features if feature.display] + informations.aentries) as O:
        nth = 0
        for p in enrich(KeyReader(infile, ienc, informations.bentries + informations.aentries), informations):
            O.write_p(p)
            nth += 1
            if (0 == nth % 1000):
                enrich_logger.debug('%i sentences enriched' %nth)
        enrich_logger.debug('%i sentences enriched' %nth)
    
    laps = time.time() - start
    enrich_logger.info("done in %s", timedelta(seconds=laps))



if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Adds information to a file using and XML-styled configuration file.")

    parser.add_argument("infile",
                        help="The input file (CoNLL format)")
    parser.add_argument("infofile",
                        help="The information file (XML format)")
    parser.add_argument("outfile",
                        help="The output file (CoNLL format)")
    parser.add_argument("-m", "--mode", dest="mode", default=u"label", choices=(u"train", u"label", u"annotate", u"annotation"),
                        help="The mode for enrichment. May make entries vary (default: %(default)s)")
    parser.add_argument("--input-encoding", dest="ienc",
                        help="Encoding of the input (default: UTF-8)")
    parser.add_argument("--output-encoding", dest="oenc",
                        help="Encoding of the input (default: UTF-8)")
    parser.add_argument("--encoding", dest="enc", default="UTF-8",
                        help="Encoding of both the input and the output (default: UTF-8)")
    parser.add_argument("-l", "--log", dest="log_level", choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), default="WARNING",
                        help="Increase log level (default: critical)")
    parser.add_argument("--log-filename", dest="log_filename",
                        help="The name of the log file")
    
    if __package__:
        args = parser.parse_args(sys.argv[2:])
    else:
        args = parser.parse_args()
    
    enrich_file(args.infile, args.infofile, args.outfile,
                mode=args.mode,
                ienc=args.ienc or args.enc, oenc=args.oenc or args.enc,
                log_level=args.log_level, log_file=args.log_filename)
    sys.exit(0)
>>>>>>> master
