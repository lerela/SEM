#! /usr/bin/python3
#-*- coding: utf-8 -*-

"""
file: tag.py

Description: performs a sequence of operations in a pipe given a configuration
file.

author: Yoann Dupont
copyright (c) 2014 Yoann Dupont - all rights reserved

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see GNU official website.
"""

from .obj.information   import Informations
from .obj.master_parser import Master
from .obj.wapiti        import Wapiti
from .obj.logger        import log

from .pretreatment.segmentation import segmentation
from .pretreatment.enrich       import enrich

from .posttreatment.clean_info   import clean_info
from .posttreatment.textualise   import textualise

import os.path, tempfile, io
join     = os.path.join
basename = os.path.basename
dirname  = os.path.dirname

class Tagger(object):
    def __init__(self, masterfile, fast = False):
        self.MASTER = Master(masterfile)
        self.masterfile = masterfile
        self.pipeline  = self.MASTER.pipeline
        self.options   = self.MASTER.options

        self.ienc = self.options.ienc
        self.oenc = self.options.oenc

        self.fast = fast
        if self.fast: 
            self.info_files = {}
            self.wapiti_models = {}

    def tag_file(self, input, directory=None):
        with open(input, 'rb') as f:
            return self.tag(masterfile, f.read(), directory + basename(input))

    def tag(self, input, directory=None):
        
        file_history   = []  # the files generated so far in the pipeline
        current_output = None # the current output in the pipeline
        current_input = io.StringIO(input.decode(self.ienc))
        
        nth  = 1
        
        filename = [directory and basename(directory) or ""]
        pipeline = self.pipeline.copy()

    #    tmp = None
    #    if not directory:
    #        tmp = True
    #        directory = tempfile.mkdtemp()
    #        input_fd, current_input_file = tempfile.mkstemp(dir=directory)

    #        with os.fdopen(input_fd, 'w') as f:
    #            f.write(current_input)
    #        current_input = current_input_file
    #        file_history.append(current_input) # We will have to destroy this file

        if pipeline[0].identifier == "segmentation":
            filename.append(".segmentation")

            current_output = segmentation(current_input, verbose=self.options.verbose)
            
            current_input  = current_output
            nth           += 1
            pipeline       = pipeline[1:]
            
            if self.options.verbose:
                log('\n')
        
        for process in pipeline:
            # segmentation may only be first. If we are in this loop, a segmentation
            # cannot occur as it was handled before.
            
            if process.identifier == "segmentation":
                raise RuntimeError("Segmentation can only be performed first. Asked as process number %d" %nth)
                
            elif process.identifier == "clean_info":
                filename.append('.clean')
                current_output = clean_info(current_input, process.args["to-keep"], verbose=self.options.verbose)
                
            elif process.identifier == "enrich":
                information    = join(dirname(self.masterfile), process.args["config"])
                filename.extend((".", basename(information[:-4])))
                
                info_file = None
                if self.fast:
                    info_file = self.info_files.get(information)
                if not info_file:
                    info_file = Informations(information)
                current_output = enrich(current_input, info_file, verbose=self.options.verbose)
                
                if self.fast:
                    self.info_files[information] = info_file
                else:
                    del info_file

            elif process.identifier == "label":
                model = join(dirname(self.masterfile), process.args["model"])
                filename.extend((".",  basename(model)))

                wapiti_model = None
                if self.fast:
                    wapiti_model = self.wapiti_models.get(model)
                if not wapiti_model:
                    wapiti_model = Wapiti(model)
                current_output = io.StringIO(wapiti_model.label(current_input))
                
                if self.fast:
                    self.wapiti_models[model] = wapiti_model
                else:
                    del wapiti_model
                
            elif process.identifier == "textualise":
                poscol         = int(process.args["pos"]) if "pos" in process.args else 0
                chunkcol       = int(process.args["chunk"]) if "chunk" in process.args else 0
                filename.append('.textualise')
                
                current_output = textualise(current_input, pos_column=poscol, chunk_column=chunkcol, verbose=self.options.verbose)
                
            else:
                raise RuntimeError('Unknown process "%s"' % process.identifier)
            
            if self.options.verbose:
                log("\n")
            
            current_input.close()
            current_input  = current_output
            current_output = None
            
            nth += 1
        
        current_input.seek(0)

        # Saving output
        output_string = []
        if directory:
            with open(join(dirname(directory), "".join(filename)), 'wb') as f:
                for line in current_input:
                    eline = line.encode(self.oenc)
                    f.write(eline)
                    output_string.append(eline)
        current_input.close()
        return "".join(eline)

if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser(description="Performs various operations given in a master configuration file that defines a pipeline.")
    
    parser.add_argument("master",
                        help="The master configuration file. Defines at least the pipeline and may provide some self.options.")
    parser.add_argument("input_file",
                        help="The input file for the tagger.")
    parser.add_argument("-o", "--output-directory", dest="output_directory", default=".",
                        help="The output directory (default: '.')")
    parser.add_argument("-f", "--fast", action='store_true',
                        help="Cache the models (increase memory usage).")
    
    if not __package__:
        parser = parser.parse_args()
    else:
        parser = parser.parse_args(sys.argv[2:])
    
    tagger = Tagger(parser.master, fast = parser.fast)

    tagger.tag_file(parser.input_file,
           directory=parser.output_directory)
    sys.exit(0)
