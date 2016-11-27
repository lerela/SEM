import io

class InCorpus(object):

    def __init__(self, fd, ienc=None):
        self._fd = fd
        self._size = None
        self.ienc = ienc

    def __iter__(self):
        skipping = True
        entry = []
        for line in self._fd:
            line = line.strip()
            if self.ienc:
                line = line.decode(self.ienc)
            if not line:
                if entry:
                    yield tuple(entry)
                    del entry[:]
            else:
                entry.append(line)
        if entry:
            yield tuple(entry)

    @property
    def size(self):
        n = self._size
        if n is None:
            n = 0
            for x in self:
                n += 1
            self._fd.seek(0)
        return n

class OnCorpus(object):

    def __init__(self, fd=None, oenc=None):
        if fd is None:
            self._fd = io.StringIO()
        else:
            self._fd = fd
        self.bof = True
        self.oenc = oenc

    def close(self):
        self._fd.close()
        self._fd = None

    def write(self, s):
        if self.oenc:
            self._fd.write(s.encode(self.oenc))
        else:
            self._fd.write(s)

    def put(self, entry):
        if self.bof:
            self.bof = False
        else:
            self.write("\n")
        for line in entry:
            self.write(line)
            self.write("\n")

    def put_concise(self, entry):
        if self.bof:
            self.bof = False
        else:
            self.write("\n")
        self.write("\n".join(entry))

    def putformat(self, entry, format):
        if self.bof:
            self.bof = False
        else:
            self.write("\n")
        for line in entry:
            print((format, line))
            self.write(format % line)
            self.write("\n")
    
    @property
    def file(self):
        self._fd.seek(0)
        return self._fd