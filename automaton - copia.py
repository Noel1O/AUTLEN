"""
    Equipo docente de Autómatas y Lenguajes Curso 2025-26
    Última modificación: 18 de septiembre de 2025
"""

from collections import deque
from graphviz import Digraph
from utils import is_deterministic

"""
    Podéis implementar cualquier función auxiliar que consideréis necesaria
"""

class FiniteAutomaton:

    def __init__(self, initial_state, states, symbols, transitions, final_states): # Esta
        self.initial_state = initial_state
        self.states = states
        self.symbols = symbols
        self.transitions = transitions
        self.final_states = final_states

    def add_transition(self, start_state, symbol, end_state): # Esta 
        if start_state not in self.transitions:
            self.transitions[start_state] = {}
            
        if symbol not in self.transitions[start_state]:
            self.transitions[start_state][symbol] = set()
            
        self.transitions[start_state][symbol].add(end_state)

    def accepts(self, cadena):
        current_states = self._lambda_check({self.initial_state})
        
        for symbol in cadena:
            next_states = set()
            for state in current_states:
                if state in self.transitions and symbol in self.transitions[state]:
                    next_states |= self.transitions[state][symbol]
            current_states = self._lambda_check(next_states)
            if not current_states:
                return False
            
        return any(s in self.final_states for s in current_states)
    
    def to_deterministic(self):
        pass

    def to_minimized(self):
        pass
        
    def draw(self, path="./images/", filename="automata.png", view=False):
        dot = Digraph(comment="Automata", format="png")
        dot.attr(rankdir="LR")

        # Nodo invisible para punto inicial
        dot.node("", shape="none")

        # Almacenar estados
        for state in self.states:
            if state in self.final_states:
                dot.node(state, shape="doublecircle")
            else:
                dot.node(state, shape="circle")
        
        # Flecha al estado inicial
        dot.edge("", self.initial_state)

        # Almacenar transiciones
        for state_ini in self.transitions:
            for symbol in self.transitions[state_ini]:
                for state_fin in self.transitions[state_ini][symbol]:
                    dot.edge(state_ini, state_fin, symbol if symbol is not None else "λ")

        dot.render(path+filename, view=view)
        
    def _lambda_check(self, states):
        current_states = set(states)
        queue = deque(states) 
        
        while queue:
            state = queue.popleft()
            if state in self.transitions and None in self.transitions[state]:
                for next_state in self.transitions[state][None]:
                    if next_state not in current_states:
                        current_states.add(next_state)
                        queue.append(next_state)
        return current_states