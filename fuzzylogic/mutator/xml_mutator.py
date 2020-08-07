import random
import json
# import xml.etree.ElementTree as ET
import xmltodict
import pprint
from collections import OrderedDict
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator
from .complex_mutators import ListMutator, ObjectMutator

class XmlMutator:
    def __init__(self):
        self._seed = 0
        self._original = None   # xml tree
        self._yields = []       # yileds to yield
        self._strategy = None   # strat
        self._mutators = {str:StringMutator(),int:IntMutator(),float:FloatMutator(),bool:BooleanMutator()}

    """
    Go through each node and mutate it...

    Original mutate logic: mutate a leaf node
    Current mutate logic: mutate a node by:
     - mutate attribute value
     - mutate text
     - add attr (new)
     - add text (when there wasn't previously one)
     - remove att
     - remove text

    Return to string format using ET.tostring(root_node)
    """

    def mutate(self, xml_input):
        self._analyse_(xml_input)
        # print(xmltodict.unparse(self._original))
        # print(json.dumps(self._original))
        self._preprocessing_recurse_(self._original)
        # print(xmltodict.unparse(self._original))
        self.recurse(self._original)
        print('\n'.join(self._yields))
        

    """
    Prases string input
    """
    def _analyse_(self, _input):
        self._original = xmltodict.parse(_input,process_namespaces=True)
    
    """
    TODO
    """
    def _preprocessing_recurse_(self, original):
        # print("recursing into ", json.dumps(original))
        # print(type(original))
        if type(original) is OrderedDict:
            for k,v in original.items():
                self._preprocessing_recurse_(v)
                
        elif type(original) is list:
            for k in range(len(original)):
                v = original[k]
                if type(v) is str:
                    original[k] = {"#text":v}
                elif type(v) is OrderedDict:
                    self._preprocessing_recurse_(v)
                elif type(v) is list:
                    self._preprocessing_recurse_(v)
        
    """
    individual types:
        - finding the type
        - calling the right mutator
    A None mutator
        - creates a filled element
    Add/Remove attributes
    Add/Remove text
    stategies
        - Add/remove elements functionality
    
    """
    def recurse(self, original):
        print("recursing into ", json.dumps(original))
        if type(original) is OrderedDict:
            for k,v in original.items():
                print ("k = ", k, " v = ", v)
                if type(v) is OrderedDict:
                    self.recurse(v)
                elif type(v) is list:
                    self.recurse(v)
                elif v is None:
                    pass
                else:
                    v_type = self._get_type_(v)
                    typed_v = v_type(v)
                    for mutation in self._mutators[v_type].mutate(typed_v):
                        tmp = v
                        print(self._mutators[v_type], mutation)
                        original[k] = str(mutation)
                        self._yields.append(xmltodict.unparse(self._original, full_document=False))
                        original[k] = tmp
                # else:
                #     if self._strategy != None:
                #         for mutation in self._static_mutators[type(v)].deterministic_mutator(v, self._strategy):
                #             tmp = v
                #             original[k] = mutation
                #             self._yields.append(json.dumps(self._original))
                #             original[k] = tmp

        elif type(original) is list:
            for k in range(len( original)):
                v = original[k]
                if type(v) is OrderedDict:
                    self.recurse(v)
                elif type(v) is list:
                    self.recurse(v)
                elif type(v) is None:
                    #TODO
                    pass

    
    def _get_type_(self, v):
        if self._is_int_(v):
            return int
        elif self._is_float_(v):
            return float
        elif self._is_str_(v):
            return str
        elif self._is_None_(v):
            return None
        raise TypeError(f'*** {v} is an unhandled type ***')

    @staticmethod
    def _is_float_(v):
        try:
            float(v)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_int_(v):
        try:
            int(v)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_str_(v):
        try:
            str(v)
            return True
        except ValueError:
            raise Exception('Can you imagine something that will fail this?')

    @staticmethod
    def _is_None_(v):
        if v is None:
            return True
        return False