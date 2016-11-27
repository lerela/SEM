from obj.segmentation import Segmentation
from obj.corpus       import InCorpus, OnCorpus
from obj.logger       import log

def segmentation(incorpus, outcorpus=None, verbose=False):
    if not outcorpus:
        outcorpus = OnCorpus()

    segmenter = Segmentation(incorpus, outcorpus)
    
    if verbose:
        log('Segmenting "%s"...' %infile)
    
    segmenter.segmentation()
    
    if verbose:
        log('done.\n')

    return outcorpus

if __name__ == '__main__':
    import sys, argparse

    parser = argparse.ArgumentParser(description="Segments a text into tokens and separates sentences.")
    
    parser.add_argument("infile", type=str, help="the input file.")
    parser.add_argument("outfile", type=str, help="the output file.")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="Basic feedback for user (default: False).")
    
    arguments = (sys.argv[2:] if __package__ else sys.argv)
    parser    = parser.parse_args(arguments)

    with open(parser.infile, 'r') as infile, open(parser.outfile, 'w') as outfile:
        incorpus = InCorpus(infile)
        outcorpus = OnCorpus(outfile)
        segmentation(incorpus, outcorpus, verbose=parser.verbose)

    sys.exit(0)
