"""
Wrapper to Wapiti. Provides the train and label procedures.
TODO: add every option for train and test
TODO: add support for other modes, such as dump and update (1.5.0+)

The way things "should" be done here : every method should be a class method,
so that they can be called the following way: Wapiti.<method>
"""

import io
from wapiti import Model

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
