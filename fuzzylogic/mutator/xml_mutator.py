import random
import xml.etree.ElementTree as ET
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator
from .complex_mutators import ListMutator, ObjectMutator

class XmlMutator:
    def __init__(self):
        self._seed = 0
        self._original = None   # xml tree
        self._found_bad = False   # indicator if

    def mutate(self, xml_input):
        print(xml_input)
        self._original = ET.fromstring(xml_input)
        # print(list(self._original))
        # final = self._mutate_(head)
        self._found_bad = False
        self._mutate_(self._original)

    """
    Find a node to mutate and mutate it.
    However it needs to be a node at random... how to?

    Original thought pattern: mutate a leaf node
    Fixed thought pattern: mutate any node that has an attribute field or a leaf (add/remove/mutate text)? 
    """
    def _mutate_(self, head):
        # finaly find a 
        if len(list(head)) == 0: # leaf
            if len(head.keys()) == 0:
                self._found_bad = True
                return head      # indiciate that a node wasn't mutated and needs to find another to mutate.
            
            rand_att = random.choice(list(head.keys()).append('text'))
            print(rand_att)
            return head
        
        # get nodes that contain attributes
        nodes_list = [node for node in list(head) if (len(node.keys()) != 0 or node.text != None)]
        print(f"Nodes with an attribute or text: {nodes_list}")
        if len(nodes_list) == 0:
            return head
        
        rand_node = random.choice(nodes_list)
        
        print(rand_node.tag)
        while True:
            new = self._mutate_(rand_node)
            if self._found_bad == False:
                break


            
        # print(new.tag)
        return head


    