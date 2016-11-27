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
