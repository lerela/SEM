#-*- encoding: utf-8-*-

import sys

from os.path import dirname, abspath

SEM_HOME     = dirname(dirname(abspath(__file__)))
SEM_HOMEPAGE = "http://www.lattice.cnrs.fr/sites/itellier/SEM.html"

_name = "SEM"
"""
The name of the software. Obviously, it is SEM.
"""

_version_major = 2
"""
The major version number.
Is only incremented when deep changes (that usually lead to a change of how the whole software is used) are made to the program.
Such changes include various feature additions / deletions / modifications, source code reorganisation and so on.
On a more NLP side, such changes could also include a change in corpora used in learning (if going from proprietary to free for example).
If this number is incremented, _version_minor and _version_patch are to be reseted to 0.
"""

_version_minor = 4
"""
The minor version number.
Is only incremented when medium changes are made to the program.
Such changes include feature addition / deletion, creation of a new language entry for manual.
If this number is incremented, _version_patch is to be reseted to 0.
"""

_version_patch = 2
"""
The patch version number.
Is only incremented when shallow changes are made to the program.
Such changes include bug correction, typo correction and any modification to existing manual(s) are made.
On a more NLP side, such changes would also include model changes.
"""

_main_features = [
                    ["segmentation",
                        [
                            "segmentation for: French, English",
                            "easy creation and integration of new tokenisers"
                        ]
                    ],
                    [
                        "feature generation", 
                        [
                            "XML file to write features without coding them",
                            "single-token and multi-token dictionary features",
                            "Regular expression features",
                            "sequenced features",
                            "train/label mode",
                            "display option for features that are useful for generation, but not needed in output"
                        ]
                    ],
                    ["exporting output",
                        [
                            "supported export formats: CoNLL, text, HTML (from plain text)",
                            "easy creation and integration of new exporters"
                        ]
                    ],
                    ["extension of existing features",
                        [
                            "automatic integration of new segmenters and exporters",
                            "semi automatic integration of new feature functions",
                            "easy creation of new CSS formats for HTML exports"
                        ]
                    ]
                  ]

_first_steps = [
                    ["make Wapiti",
                        [
                            "open a terminal in ext/",
                            'type "make" (".\\make.bat" on Windows) without quotes',
                            "note: on Windows, either install [POSIX threads for Windows](https://sourceforge.net/p/pthreads4w/wiki/Home/) or disable them as explained in ext/src/wapiti.h"
                        ],
                    ],
                    ["uncompress models in resources/models/*", []],
                    ["run tests",
                        ["python sem --test"]
                    ]
                ]

_external_resources = [
                        ["[French Treebank](http://www.llf.cnrs.fr/fr/Gens/Abeille/French-Treebank-fr.php) by [Abeillé et al. (2003)](http://link.springer.com/chapter/10.1007%2F978-94-010-0201-1_10): corpus used for POS and chunking.", []],
                        ["NER annotated French Treebank by [Sagot et al. (2012)](https://halshs.archives-ouvertes.fr/file/index/docid/703108/filename/taln12ftbne.pdf): corpus used for NER.", []],
                        ["[Lexique des Formes Fléchies du Français (LeFFF)](http://alpage.inria.fr/~sagot/lefff.html) by [Clément et al. (2004)](http://www.labri.fr/perso/clement/lefff/public/lrec04ClementLangSagot-1.0.pdf): french lexicon of inflected forms with various informations, such as their POS tag and lemmatization.", []],
                        ["[Wapiti](http://wapiti.limsi.fr) by [Lavergne et al. (2010)](http://www.aclweb.org/anthology/P10-1052): linear-chain CRF library.", []],
                        ["Windows only: [MinGW64](https://sourceforge.net/projects/mingw-w64/?source=navbar): used to compile Wapiti on Windows.", []],
                        ["Windows only: [POSIX threads for Windows](https://sourceforge.net/p/pthreads4w/wiki/Home/): if you want to multithread Wapiti on Windows.", []]
                      ]

_latest_changes = [
                    ["Added sources for manual", []],
                    ["Improved readme.md", 
                        [
                            "added first steps and external resources",
                            "added link to online version"
                        ]
                    ],
                    ["tagger module now handles CoNLL-like files again! Hooray!",
                        [
                            'in master file, within the options section: <file format="conll" fields="your,fields,separated,by,commas,the_field_where_words_are_supposed_to_be" word_field="the_field_where_words_are_supposed_to_be">'
                        ]
                    ],
                    ["Wapiti changes", 
                        [
                            'now SEM only uses a local version of Wapiti (available in ext) that needs to be compiled.'
                        ]
                    ]
                  ]

_planned_changes = [
                        ["redo triggered features and sequence features.", []],
                        ["add lemmatiser.", []],
                        ["migration to python3 ? (already made for revision 39 by lerela).", []],
                        ["translate manual in English.", []],
                        ["update manual.", []],
                        ['improve pipeline: allow calling a pipeline within a pipeline.', []],
                        ['make SEM callable modules the same way segmenters and exporters. This would allow better integration in a pipeline.', []],
                        ['have more unit tests', []],
                        ['handle HTML input files for tagger module',
                            [
                                "create specific tokeniser",
                                "need to handles cases such as words cut by a HTML tag"
                            ]
                        ],
                        [
                            "improve segmentation",
                            [
                                'handle URLs starting with country indicator (ex: "en.wikipedia.org")',
                                'handle URLs starting with subdomain (ex: "blog.[...]")',
                            ]
                        ]
                   ]

def name():
    return _name

def version():
    return ".".join([str(x) for x in [_version_major, _version_minor, _version_patch]])

def full_name():
    return "%s v%s" %(name(), version())

def informations():
    def make_md(element_list):
        accumulator = []
        for i_index, element in enumerate(element_list, 1):
            accumulator.append("%s. %s" %(i_index, element[0]))
            for ii_index, subelement in enumerate(element[1], 1):
                accumulator.append("   %s. %s" %(ii_index, subelement))
        return "\n".join(accumulator)
        
    return """# %s
[SEM (Segmenteur-Étiqueteur Markovien)](%s) is a free NLP tool relying on Machine Learning technologies, especially CRFs. SEM provides powerful and configurable preprocessing and postprocessing. [SEM also has an online version](http://apps.lattice.cnrs.fr/sem/index).

## Main SEM features
%s

## first steps before using SEM
%s

## External resources used by SEM
%s

## latest changes (2.4.0 > %s)
%s

## planned changes (no priority)
%s""" %(full_name(), SEM_HOMEPAGE, make_md(_main_features), make_md(_first_steps), make_md(_external_resources), version(), make_md(_latest_changes), make_md(_planned_changes))
