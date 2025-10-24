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
        aut_aux = FiniteAutomaton(
            initial_state="",
            states=set(),
            symbols=self.symbols,
            transitions={},
            final_states=set()
        )
                
        new_states_dict = {}
        initial_states = set()
        initial_states |= self._lambda_check({self.initial_state})
        initial_states.add(self.initial_state)
        initial_states = sorted(initial_states)
        
        for state in initial_states :
            aut_aux.initial_state += state
            
        aut_aux.states.add(aut_aux.initial_state)
        
        new_states_dict[aut_aux.initial_state] = initial_states
        
        aut_aux.states.add("empty")


        pending = [aut_aux.initial_state]
        
        while pending:
            state_name = pending.pop(0)
            state = new_states_dict[state_name]
            for st in state: #A
                for symbol, states_tr in self.get_transitions_from_state(st).items(): #a
                    final = 0
                    if symbol is not None:
                        if states_tr in self.get_final_states():
                            final = 1
                        n_states = set()
                        n_state_name = ""
                        for s in states_tr:
                            n_states.add(s)
                            n_state_name += s
                            n_states |= self._lambda_check({s})
                            n_states = sorted(n_states)
                            for ns in n_states:
                                n_state_name += ns
                        new_states_dict[n_state_name] = n_states
                        if n_state_name not in aut_aux.states:
                            pending.append(n_state_name)
                        aut_aux.states.add(n_state_name)
                        aut_aux.add_transition(state_name, symbol, n_state_name)
                        if final == 1:
                            aut_aux.final_states.add(n_state_name)
                for symbol in self.get_symbols():
                    if aut_aux.get_transitions_from_state(n_state_name).get(symbol) == None:
                        aut_aux.add_transition(state_name, symbol, "empty")

        
        
        self.states = aut_aux.states
        self.initial_state = aut_aux.initial_state
        self.final_states = aut_aux.final_states
        self.transitions = aut_aux.transitions

        return aut_aux
        

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
    
    def get_states(self):
        return self.states
    
    def get_symbols(self):
        return self.symbols
    
    def get_transitions(self):
        return self.transitions
    
    def get_initial_state(self):
        return self.initial_state
    
    def get_final_states(self):
        return self.final_states
    def get_transitions_from_state(self, state):
        
        if state not in self.transitions:
            return {}
        return self.transitions[state]