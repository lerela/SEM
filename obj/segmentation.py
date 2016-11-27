# -*- coding: utf-8 -*-
import re
from .corpus import InCorpus, OnCorpus

class Segmentation(object):

    def __init__(self,
                 in_corpus, out_corpus = None,
                 opening_characters = "([{«", closing_characters = ")]}»",
                 strong_puncts = "?!…", weak_puncts = ",:;",
                 apostrophes = True):
        self.in_corpus = in_corpus
        self.out_corpus = out_corpus or OnCorpus()
        self.opening_chars = opening_characters
        self.closing_chars = closing_characters
        self.strong_puncts = strong_puncts
        self.weak_puncts = weak_puncts
        self.apostrophes = apostrophes

        self.opening_char_count = 0
        self.sentence = "" # the sentence to be written

    def isChar(self, s):
        return len(s) == 1

    def isCharIn(self, token, characters):
        if self.isChar(token):
            return characters.find(token) != -1
        else:
            return False

    def isOpeningChar(self, s): 
      return self.isCharIn(s, self.opening_chars)

    def isClosingChar(self, s):
        return self	.isCharIn(s, self.closing_chars)

    # '.' should not be considered as a strong punctuation
    # because it can be used to other purposes.
    def isStrongPunct(self, s):
        b = self.isCharIn(s, self.strong_puncts)
        b = b or ('...'.find(s) != -1)
        return b

    def isWeakPunct(self, s):
        return isCharIn(s, self.weak_puncts)

    def isSentenceDot(self, the_line, token, current_position):
        EOS = False # End Of Sentence
        if token[:-1].isdigit():
            EOS = True
        elif not current_position >= (len(the_line) - 2): # the token is not in the two last tokens of the line
            next_token = the_line[current_position+1]
            EOS = next_token[0].isupper() or (not next_token.isalpha())
        else: # the dot may be followed by a double-quote or a closing char
            EOS = (current_position == (len(the_line) - 2)) and (the_line[current_position + 1][0] not in self.closing_chars + '"')
            #EOS = False
        return EOS

    def isAcronym(self, token):
        return token.count(".") > 1 or token.replace(".","").isupper()

    def isAbbreviationBeforeNoun(self, token):
        abbr_list = ["dr.", "mme.", "mmes.", "melle.", "melles.", "mlle.", "mlles.", "m.", "mr.", "me.", "mrs.", "st."]
        return abbr_list.count(token.lower()) != 0

    # A token is a unit if:
    #  | it matches a quantity and then a unit
    #  | it matches a unit and then a quantity
    # if the token is not a unit, the returned index is -1
    def isUnit(self, token):
        quantity = r"\d+([\.,\d]\d+)?"
        unit = r"[^\.,\d]+"
        
        if token[0].isdigit():
            q_pat = re.compile(quantity)
            u_pat = re.compile(unit + "$")
            q_match = re.match(q_pat, token)

            if q_match != None:
                u_match = re.match(u_pat, token[q_match.end():])
                if u_match != None:
                    return q_match.end()
                    
        elif token[-1].isdigit():
            u_pat = re.compile(unit)
            q_pat = re.compile(quantity + "$")
            u_match = re.match(u_pat, token)
            
            if u_match != None:
                q_match = re.match(q_pat, token[u_match.end():])
                if q_match != None:
                    return u_match.end()

        return -1

    def cut(self, token):
        if self.isChar(token):
            res = token
        else:
            res = self.cutByOpeningChars(token)
            res = self.cutByClosingChars(res)
            res = self.cutByStrongPuncts(res)
            res = self.cutByWeakPuncts(res)
            res = self.cutByClitics(res)
            if self.apostrophes:
                res = self.separate(res, "'’", False)
                #res = self.separate(res, u"'’", True)
                res = self.separate(res, '"', False)
                res = self.separate(res, '"', True)
        return res

    def separate(self, token, separating_chars, Before):
        str_buffer = token

        for S_C in separating_chars:
            if Before:
                str_buffer = str_buffer.replace(S_C, ' '+S_C)
            else:
                str_buffer = str_buffer.replace(S_C, S_C+' ')

        return str_buffer

    def cutByOpeningChars(self, token):
        return self.separate(token, self.opening_chars, False)

    def cutByClosingChars(self, token):
        ###return self.separate(token, self.closing_chars, True)
        return self.separate(token, self.closing_chars, False)

    def cutByStrongPuncts(self, token):
        ###s = self.separate(token, self.strong_puncts, True)
        s = self.separate(token, self.strong_puncts, True)
        s = self.separate(s, self.strong_puncts, False)
        return s.replace('...', ' ...')

    def cutByWeakPuncts(self, token):
        ##return self.separate(token, self.weak_puncts, True)
        s = self.separate(token, self.weak_puncts, True)
        return self.separate(s, self.weak_puncts, False)

    def cutByClitics(self, token):
        cl_long = ['-t-']
        tmp = self.separate(token, cl_long, True)

        if len(tmp) == len(token): # nothing was done, thus we do not have a long clitic
            cl_short = ['-je','-tu','-il','-elle','-nous','-vous','-ils','-elles','-moi','-toi','-lui','-on','-ce','-le','-la','-les']
            tmp = self.separate(token, cl_short, True)

        return tmp

    def handleChar(self, token, current_position):
        if self.isOpeningChar(token):
            self.opening_char_count += 1
        if self.isClosingChar(token):
            self.opening_char_count -= 1
        if current_position == 0:
            self.sentence += token
        else:
            self.sentence += ' '+token
        if self.isStrongPunct(token) and self.opening_char_count == 0:
            self.out_corpus.put(self.sentence.split())
            self.sentence = ""

    # when the token ends with a dot
    # it has to be treated in the current line which is not modified in the process
    def handleTerminatingDot(self, the_line, token, current_position):
        if (self.isAcronym(token)) or (self.isAbbreviationBeforeNoun(token)):
            self.sentence += " " + token
        else:
            self.sentence += " " + token[:-1] + " " + token[-1]
            if self.isSentenceDot(the_line, token, current_position) and (self.opening_char_count == 0):
                self.out_corpus.put(self.sentence.split())
                self.sentence = ""


    def seg(self):
        for paragraph in self.in_corpus:
            for line in paragraph:
                self.out_corpus.put(line)

    def segmentation(self):
        the_line = ""
        current_position = 0
        EOL = False # end of line

        for paragraph in self.in_corpus:
            for line in paragraph:
                the_line = self.cut(line).strip().split() # splitting the line in tokens
                current_position = 0
                EOL = False
                index = 0
                while not EOL:
                    token = the_line[current_position]

                    if self.isChar(token):
                        if self.isStrongPunct(token) and current_position < len(the_line)-1 and self.isStrongPunct(the_line[current_position+1]):
                            self.sentence += " " + the_line[current_position]
                        else:
                            self.handleChar(token, current_position)
                    elif self.isUnit(token) != -1: # the token is a number with an unit at its start or at its end
                        index = self.isUnit(token)
                        self.sentence += " " + token[:index] + " " + token[index:]
                    elif token[-1] == ".": # the token ends with a dot
                        if token == "...":
                            self.sentence += " " + token
                            self.out_corpus.put(self.sentence.split())
                            self.sentence = ""
                        elif self.isUnit(token[:-1]) != -1:
                            self.sentence += " " + token[0 : index] + " " + token[index : len(token)-1] + " " + token[-1]
                        else:
                            self.handleTerminatingDot(the_line, token, current_position)
                    elif "." in token:
                        index = token.index(".")
                        if token[:index].isdigit() and token[index+1:].isdigit():
                            self.sentence += " " + token
                        else:
                            if self.isAbbreviationBeforeNoun(token[:index + 1]):
                                self.sentence += " " + token[:index + 1] + " " + token[index + 1:]
                            else:
                                self.sentence += " " + token[0 : index] + " " + token[index]
                                self.out_corpus.put(self.sentence.split())
                                self.sentence = token[index+1:]
                    else: # any other case : the token is added
                        self.sentence += " " + the_line[current_position]

                    current_position += 1
                    EOL = current_position >= len(the_line)

                    if EOL and self.sentence != "":
                        self.out_corpus.put(self.sentence.split())
                        self.sentence = ""

        return self.out_corpus.file
