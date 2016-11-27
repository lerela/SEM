# -*- coding: utf-8 -*-

"""
file: wapiti.py

Description: a very simple wrapper for calling wapiti. Provides train
and test procedures.
TODO: add every option for train and test
TODO: add support for other modes, such as dump and update (1.5.0+)

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

import logging
import os.path
import io
from wapiti import Model
import time
from obj.logger import default_handler
from software import SEM_HOME

wapiti_logger = logging.getLogger("sem.wapiti")
wapiti_logger.addHandler(default_handler)

__command_name = os.path.join(SEM_HOME, "ext", "wapiti", "wapiti")
    
class Wapiti(object):

    def __init__(self, model, nbest=None):
        d = {'model': model}
        if nbest is not None: d['nbest'] = nbest

        self.model = Model(**d)

    @staticmethod
    def train(input, pattern=None, output=None, algorithm=None, nthreads=1, maxiter=None, rho1=None, rho2=None, model=None):
        """
        The train command of Wapiti.
        """
        d = {}
    
        if pattern is not None:   d['pattern'] = str(pattern)
        if algorithm is not None: d['algo'] = str(algorithm)
        if nthreads > 1:          d['nthread'] = int(nthreads)
        if maxiter is not None:   d['maxiter'] = int(maxiter)
        if rho1 is not None:      d['rho1'] = float(rho1)
        if rho2 is not None:      d['rho2'] = float(rho2)
        if model is not None:     d['model'] = str(model)
        
        model = Model(**d)
        output = model.train(str(input))

    def label(self, input):
        """
        The label command of Wapiti.
        """
        
        if isinstance(input, io.IOBase):
            input = input.read()
        return self.model.label_sequence(input, include_input=True).decode('utf-8')

    def label_corpus(corpus, model, field, encoding):
        corpus_unicode = str(corpus).encode(encoding)      
        
        output = self.model.label_sequence(corpus_unicode, include_input=True).decode('utf-8')
        
        i = 0
        j = 0
        corpus.fields.append(field)
        for element in output.split("\n"):
            element = element.strip()
            if "" == element:
                i += 1
                j  = 0
            else:
                corpus.sentences[i][j][field] = element
                j += 1

    def label_document(document, model, field, encoding, annotation_name=None, annotation_fields=None):
        if annotation_fields is None:
            fields = document.corpus.fields
        else:
            fields = annotation_fields
        
        if annotation_name is None:
            annotation_name = str(field)
        
        corpus_unicode = document.corpus.unicode(fields).encode(encoding)
        
        output = self.model.label_sequence(corpus_unicode, include_input=True).decode('utf-8')

        i    = 0
        j    = 0
        tags = [[]]
        document.corpus.fields.append(field)
        for element in output.split("\n"):
            element = element.strip()
            if "" == element:
                if len(tags[-1]) > 0:
                    tags.append([])
                    i += 1
                    j  = 0
            else:
                tags[-1].append(element)
                j += 1
        
        tags = [t for t in tags if t]
        document.add_annotation_from_tags(tags, field, annotation_name)
