#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Ryan Mackenzie White <ryan.white4@canada.ca>
#
# Distributed under terms of the  license.

"""
Generate pachyderm pipeline specifications from command line

"""
from collections import OrderedDict
import json
import sys
import argparse


class PFSGenerator(object):

    def __init__(self, pipeline, inpt, repo, glob, image, cmd):
        self._specs = OrderedDict()
        self._input = {"atom": self.input_atom,
                       "cross": self.input_cross,
                       "union": self.input_union}
        self._inputkey = inpt
        self._pipeline = pipeline
        self._glob = glob
        self._repo = repo
        self._secondary = ''
        self._cmd = cmd
        self._image = image
        self.configure()
    
    def configure(self):
        self.pipeline(self._pipeline)
        self.input(self._inputkey)
        self.transform(self._cmd, self._image)

    def pipeline(self, pipeline):
        self._specs['pipeline'] = {'name': pipeline}

    def input(self, key):
        self._specs['input'] = self._input[key]()
    
    def input_atom(self):
        return {"atom": {"glob": self._glob,
                         "repo": self._repo
                         }
                }
    
    def input_cross(self):
        atom1 = {"atom": {"glob": self._glob,
                          "repo": self._repo
                          }
                 }
                
        atom2 = {"atom": {"glob": self._glob,
                          "repo": self._secondary
                          }
                 }
        
        return {"cross": [atom1, atom2]}

    def input_union(self):
        atom1 = {"atom": {"glob": self._glob,
                          "repo": self._repo
                          }
                 }
                
        atom2 = {"atom": {"glob": self._glob,
                          "repo": self._secondary
                          }
                 }
        
        return {"cross": [atom1, atom2]}
    
    def transform(self, cmd, image):
        self._specs['transform'] = {'cmd': self._cmd,
                                    'image': self._image}
    
    def save_to_json(self, filename):
        print('Saving metadata model to json ', filename)
        try:
            with open(filename, 'x') as ofile:
                json.dump(self._specs, ofile, indent=4)
        except IOError as e:
            print('I/O Error({0}: {1})'.format(e.errno, e.strerror))
            return False
        except:
            print('Unexpected error:', sys.exc_info()[0])
            return False
        return True

    def display_from_json(self):
        print(json.dumps(self._specs, indent=2))

    def parse_from_json(self, filename):
        with open(filename, 'r') as ifile:
            data = json.loads(ifile, object_pairs_hook=OrderedDict)
        print(data)    


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pipeline', dest='pipeline', action='store', 
                        required=True, help='Pipeline')
    parser.add_argument('-i', '--input', dest='input', 
                        action='store', 
                        required=True, 
                        choices=['atom', 'cross', 'union'],
                        help='Atom, Cross, Union')
    parser.add_argument('-r', '--repo', 
                        dest='repo', 
                        action='store',
                        required=True,
                        help='Input repository')
    parser.add_argument('-s', '--secondary', 
                        dest='second', 
                        action='store',
                        required=False,
                        help='Secondary input repository')
    parser.add_argument('-g', '--glob',
                        dest='pattern',
                        action='store',
                        required=True,
                        help='globbing pattern')
    parser.add_argument('-d', '--docker',
                        dest='docker',
                        action='store',
                        required=True,
                        help='Docker Image')
    parser.add_argument('-c', '--cmd',
                        dest='command',
                        nargs='+',
                        required=True,
                        action='store')

    args = parser.parse_args(sys.argv[1:])
    print(args) 
    
    specs = PFSGenerator(args.pipeline,
                         args.input,
                         args.repo,
                         args.pattern,
                         args.docker,
                         args.command)
    
    specs.display_from_json()




