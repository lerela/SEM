from sem.obj.misc   import ranges_to_set
from sem.obj.logger import log
from sem.obj.corpus import InCorpus

import io

def clean_info(input, ranges,
               ienc="utf-8", oenc="utf-8", verbose=False):
    input.seek(0)
    allowed = ranges_to_set(ranges, input.readline().strip().split())
    input.seek(0)

    if verbose:
        log('Cleaning input file...')

    O = io.StringIO()

    for line in input:
        line = line.strip().split()
        if line != []:
            tokens = [line[i] for i in range(len(line)) if i in allowed]

            O.write("\t".join(tokens))
        O.write("\n")
    
    if verbose:
        log(' Done.\n')
    return O

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="...")

    parser.add_argument("infile",
                        help="The input file")
    parser.add_argument("outfile",
                        help="The output file ")
    parser.add_argument("ranges",
                        help="The ranges of indexes to keep in the file.")
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
    
    clean_info(parser.infile, parser.outfile, parser.ranges,
               ienc=parser.ienc or parser.enc, oenc=parser.oenc or parser.enc, verbose=parser.verbose)
    sys.exit(0)
