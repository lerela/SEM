#! /usr/bin/python
#-*- coding: utf-8 -*-

"""
file: tagger.py

Description: performs a sequence of operations in a pipeline.

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
along with this program. If not, see GNU official website.
"""

import codecs, logging, os, shutil

# measuring time laps
import time
from datetime import timedelta

from os.path import join, basename, dirname

import software

from obj import wapiti

from .obj.master_parser import Master
from obj.logger           import logging_format, default_handler
from obj.storage.document import Document
from obj.information      import Informations
from obj.wapiti        import Wapiti
from obj.logger        import log
from src.pretreatment.segmentation import segmentation, document_segmentation
from src.pretreatment.enrich       import enrich_file, document_enrich
from src.posttreatment.clean_info  import clean_info, document_clean
from src.posttreatment.export      import export
from src.posttreatment.textualise   import textualise
sem_tagger_logger = logging.getLogger("sem.tagger")
sem_tagger_logger.addHandler(default_handler)

class Tagger(object):
    def __init__(self, masterfile, file_name, fast = False):
        """
        Return a document after it passed through a pipeline.
    
        Parameters
        ----------
        masterfile : str
            the file containing the pipeline and global options
        file_name : str
            the input for the upcoming pipe. Its base value is the file to
            treat, it can be either "plain text" or CoNNL-formatted file.
        directory : str
            the directory where every file will be outputted.
        """
    
        start = time.time()
    
        self.MASTER = Master(masterfile)
        self.masterfile = masterfile
        self.pipeline  = self.MASTER.pipeline
        self.options   = self.MASTER.options

        if (options.log_file is not None):
            sem_tagger_logger.addHandler(file_handler(log_file))
        sem_tagger_logger.setLevel(options.log_level)
    
        exports           = {} # keeping track of already done exports
        current_output = u"" # the current output in the pipeline
        export_name       = os.path.join(directory, file_shortname)
        self.ienc = self.options.ienc
        self.oenc = self.options.oenc

        self.fast = fast
        if self.fast: 
            self.info_files = {}
            self.wapiti_models = {}

    def tag_file(self, file_name, directory=None):
    
        if self.options.format == "text":
            document = Document(basename(file_name), content=codecs.open(file_name, "r", self.ienc).read())
        elif self.options.format == "conll":
            document = Document.from_conll(file_name, self.options.fields, self.options.word_field)
        else:
            raise ValueError(u"unknown format: %s" % self.options.format)
        
        return self.tag(masterfile, document, directory + basename(input))

    def tag(self, document, directory=None):
        
        file_history   = []  # the files generated so far in the pipeline
        current_output = None # the current output in the pipeline
        current_input = io.StringIO(input.decode(self.ienc))
        
        nth  = 1
        
        filename = [directory and basename(directory) or ""]
        pipeline = self.pipeline.copy()



        if pipeline[0].identifier == u"segmentation":
            if len(document.corpus.sentences) == 0:
                document_segmentation(document, pipeline[0].args["name"], log_level=self.options.log_level, log_file=self.options.log_file)
            else:
                sem_tagger_logger.warn("segmentation asked for already segmented input, skipping...")
            nth      += 1
            pipeline  = pipeline[1:]
    
        for process in pipeline:
            # segmentation may only be first. If we are in this loop, a segmentation
            # cannot occur as it was handled before.
            if process.identifier == "segmentation":
                raise RuntimeError("Segmentation can only be performed first. Asked as process number %d" %nth)
            
            elif process.identifier == "clean_info":
                document_clean(document, process.args["to-keep"], log_level=self.options.log_level, log_file=self.options.log_file)
            
            elif process.identifier == "enrich":
                information = join(dirname(masterfile), process.args["config"])
            
                document_enrich(document, information, log_level=self.options.log_level, log_file=self.options.log_file)
            
            elif process.identifier == "label":
                model = join(dirname(masterfile), process.args["model"])
                field = process.args["field"]
            
                sem_tagger_logger.info("labeling %s with wapiti" %(field))
                
                wapiti_model = None
                if self.fast:
                    wapiti_model = self.wapiti_models.get(model)
                if not wapiti_model:
                    wapiti_model = Wapiti(model)

                label_start = time.clock()
                wapiti_model.label_document(document, model, field, oenc)
                label_laps  = time.clock() - label_start
                sem_tagger_logger.info("labeled in %s" %(timedelta(seconds=label_laps)))
            
            elif process.identifier == "export":
                export_format = process.args.get("format", "conll")
                poscol        = process.args.get("pos", None)
                chunkcol      = process.args.get("chunking", None)
                nercol        = process.args.get("ner", None)
                lang          = process.args.get("lang", "fr")
                lang_style    = process.args.get("lang_style", "default.css")
            
                if export_format not in exports:
                    exports[export_format] = 0
                exports[export_format] += 1
                current_output = export_name + ".export-%i.%s" %(exports[export_format], export_format)
            
                export(document, export_format, current_output, lang=lang, lang_style=lang_style, pos_column=poscol, chunk_column=chunkcol, ner_column=nercol, ienc=oenc, oenc=oenc, log_level=options.log_level, log_file=options.log_file)
            
                if export_format in ("html"):
                    shutil.copy(os.path.join(software.SEM_HOME, "resources", "css", "tabs.css"), directory)
                    shutil.copy(os.path.join(software.SEM_HOME, "resources", "css", lang, lang_style), directory)
            else:
                sem_tagger_logger.error('unknown process: "%s"' %process.identifier)
                raise RuntimeError('unknown process: "%s"' %process.identifier)
        
            if self.ienc != self.oenc:
                self.ienc = self.oenc
        
            nth += 1
    
        if not any([process.identifier == "export" for process in pipeline]): # no export asked
            if __name__ == "__main__": # we only export something if the module is called from command-line
                sem_tagger_logger.warn("no export in pipeline, exporting to conll by default")
                export(document, "conll", export_name + ".conll", ienc=self.ienc, oenc=self.oenc, log_level=self.options.log_level, log_file=self.options.log_file)
    
        laps = time.time() - start
        sem_tagger_logger.info('done in %s' %(timedelta(seconds=laps)))
    
        return document

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
        args = parser.parse_args()
    else:
        args = parser.parse_args(sys.argv[2:])
    
    tagger = Tagger(parser.master, fast = parser.fast)

    tagger.tag_file(parser.master, parser.input_file,
           directory=args.output_directory)
    sys.exit(0)
