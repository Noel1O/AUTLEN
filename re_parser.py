"""
    Equipo docente de Autómatas y Lenguajes Curso 2025-26
    Última modificación: 18 de septiembre de 2025
"""

from automaton import FiniteAutomaton
from utils import AutomataFormat

def _re_to_rpn(re_string):
    """
    Convert re to reverse polish notation (RPN).

    Does not check that the input re is syntactically correct.

    Args:
        re_string: Regular expression in infix notation. Type: str

    Returns:
        Regular expression in reverse polish notation. Type: str

    """
    stack = [] # List of strings
    rpn_string = ""
    for x in re_string:
        if x == "+":
            while len(stack) > 0 and stack[-1] != "(":
                rpn_string += stack.pop()
            stack.append(x)
        elif x == ".":
            while len(stack) > 0 and stack[-1] == ".":
                rpn_string += stack.pop()
            stack.append(x)
        elif x == "(":
            stack.append(x)
        elif x == ")":
            while stack[-1] != "(":
                rpn_string += stack.pop()
            stack.pop()
        else:
            rpn_string += x

    while len(stack) > 0:
        rpn_string += stack.pop()

    return rpn_string



class REParser():
    """Class for processing regular expressions in Kleene's syntax."""
    
    def __init__(self) -> None:
        self.state_counter = 0

    def _create_automaton_empty(self):
        """
        Create an automaton that accepts the empty language.

        Returns:
            Automaton that accepts the empty language. Type: FiniteAutomaton

        """
        description = """
        Automaton:
            Symbols: 

            q0

            ini q0
        """

        return AutomataFormat.read(description)
        

    def _create_automaton_lambda(self):
        """
        Create an automaton that accepts the empty string.

        Returns:
            Automaton that accepts the empty string. Type: FiniteAutomaton

        """
        description = """
        Automaton:
            Symbols: 

            q0 final

            ini q0
        """
        return AutomataFormat.read(description)


    def _create_automaton_symbol(self, symbol):
        """
        Create an automaton that accepts one symbol.

        Args:
            symbol: Symbol that the automaton should accept. Type: str

        Returns:
            Automaton that accepts a symbol. Type: FiniteAutomaton

        """
        description = f"""
        Automaton:
            Symbols: {symbol}

            q0
            q1 final

            ini q0 -{symbol}-> q1
        """
        return AutomataFormat.read(description)


    def _create_automaton_star(self, automaton):
        """
        Create an automaton that accepts the Kleene star of another.

        Args:
            automaton: Automaton whose Kleene star must be computed. Type: FiniteAutomaton

        Returns:
            Automaton that accepts the Kleene star. Type: FiniteAutomaton

        """
        empty_initial = f"Empty_initial_{self.state_counter}"
        empty_final = f"Empty_final_{self.state_counter}"
        self.state_counter += 1
        
        kleene_automaton = FiniteAutomaton(
            initial_state = empty_initial,
            states = automaton.get_states() + [empty_initial, empty_final],
            symbols = automaton.get_symbols(),
            transitions = automaton.get_transitions(),
            final_states = {empty_final}
        )

        kleene_automaton.add_transition(empty_initial, "λ", automaton.get_initial_state())
        for final_state in automaton.get_final_states():
            kleene_automaton.add_transition(final_state, "λ", empty_final)
        kleene_automaton.add_transition(empty_initial, "λ", empty_final)
        for final_state in automaton.get_final_states():
            kleene_automaton.add_transition(final_state, "λ", automaton.get_initial_state())

        return kleene_automaton

    def _create_automaton_union(self, automaton1, automaton2):
        """
        Create an automaton that accepts the union of two automata.

        Args:
            automaton1: First automaton of the union. Type: FiniteAutomaton.
            automaton2: Second automaton of the union. Type: FiniteAutomaton.

        Returns:
            Automaton that accepts the union. Type: FiniteAutomaton.

        """
        empty_initial = f"Empty_initial_{self.state_counter}"
        empty_final = f"Empty_final_{self.state_counter}"
        self.state_counter += 1
        automaton1state_transfer = {}
        for state in automaton1.get_states():
            automaton1state_transfer[state] = "q" + str(self.state_counter)
            self.state_counter += 1
        automaton1states = list(automaton1state_transfer.values())
        automaton1transitions = {}
        for ss, dct in automaton1.get_transitions().items():
            n_ss = automaton1state_transfer[ss]
            for k,v in dct.items():
                n_v = set()
                for state in v:
                    n_v.add(automaton1state_transfer[state])
            automaton1transitions[n_ss] = {k: n_v}
        
        automaton2state_transfer = {}
        for state in automaton2.get_states():
            automaton2state_transfer[state] = "q" + str(self.state_counter)
            self.state_counter += 1
        automaton2states = list(automaton2state_transfer.values())
        automaton2transitions = {}
        for ss, dct in automaton2.get_transitions().items():
            n_ss = automaton2state_transfer[ss]
            for k,v in dct.items():
                n_v = set()
                for state in v:
                    n_v.add(automaton2state_transfer[state])
            automaton2transitions[n_ss] = {k: n_v}
            
        union_automaton = FiniteAutomaton(
            initial_state = empty_initial,
            states = automaton1states + automaton2states + [empty_final, empty_initial],
            symbols = automaton1.get_symbols() + automaton2.get_symbols(),
            transitions = automaton1transitions | automaton2transitions,
            final_states = {empty_final}
        )

        union_automaton.add_transition(empty_initial, "λ", automaton1state_transfer[automaton1.get_initial_state()])
        union_automaton.add_transition(empty_initial, "λ", automaton2state_transfer[automaton2.get_initial_state()])
        for final_state in automaton1.get_final_states():
            union_automaton.add_transition(automaton1state_transfer[final_state], "λ", empty_final)
        for final_state in automaton2.get_final_states():
            union_automaton.add_transition(automaton2state_transfer[final_state], "λ", empty_final)

        return union_automaton


    def _create_automaton_concat(self, automaton1, automaton2):
        """
        Create an automaton that accepts the concatenation of two automata.

        Args:
            automaton1: First automaton of the concatenation. Type: FiniteAutomaton.
            automaton2: Second automaton of the concatenation. Type: FiniteAutomaton.

        Returns:
            Automaton that accepts the concatenation. Type: FiniteAutomaton.

        """
        empty_initial = f"Empty_initial_{self.state_counter}"
        empty_final = f"Empty_final_{self.state_counter}"
        self.state_counter += 1
        automaton1state_transfer = {}
        for state in automaton1.get_states():
            automaton1state_transfer[state] = "q" + str(self.state_counter)
            self.state_counter += 1
        automaton1states = list(automaton1state_transfer.values())
        automaton1transitions = {}
        print(automaton1state_transfer)
        for ss, dct in automaton1.get_transitions().items():
            print(ss)
            n_ss = automaton1state_transfer[ss]
            for k,v in dct.items():
                n_v = set()
                for state in v:
                    n_v.add(automaton1state_transfer[state])
            automaton1transitions[n_ss] = {k: n_v}
        
        automaton2state_transfer = {}
        for state in automaton2.get_states():
            automaton2state_transfer[state] = "q" + str(self.state_counter)
            self.state_counter += 1
        automaton2states = list(automaton2state_transfer.values())
        automaton2transitions = {}
        for ss, dct in automaton2.get_transitions().items():
            n_ss = automaton2state_transfer[ss]
            for k,v in dct.items():
                n_v = set()
                for state in v:
                    n_v.add(automaton2state_transfer[state])
            automaton2transitions[n_ss] = {k: n_v}
            
        concat_automaton = FiniteAutomaton(
            initial_state = empty_initial,
            states = automaton1states + automaton2states + [empty_final, empty_initial],
            symbols = automaton1.get_symbols() + automaton2.get_symbols(),
            transitions = automaton1transitions | automaton2transitions,
            final_states = {empty_final}
        )
        
        concat_automaton.add_transition(empty_initial, "λ", automaton1state_transfer[automaton1.get_initial_state()])
        for final_state in automaton1.get_final_states():
            concat_automaton.add_transition(final_state, "λ", automaton2state_transfer[automaton2.get_initial_state()])
        for final_state in automaton2.get_final_states():
            concat_automaton.add_transition(final_state, "λ", empty_final)
            

        return concat_automaton

    def create_automaton(
        self,
        re_string,
    ):
        """
        Create an automaton from a regex.

        Args:
            re_string: String with the regular expression in Kleene notation. Type: str

        Returns:
            Automaton equivalent to the regex. Type: FiniteAutomaton

        """
        if not re_string:
            return self._create_automaton_empty()
        
        rpn_string = _re_to_rpn(re_string)

        stack = [] # list of FiniteAutomatons

        self.state_counter = 0
        for x in rpn_string:
            if x == "*":
                aut = stack.pop()
                stack.append(self._create_automaton_star(aut))
            elif x == "+":
                aut2 = stack.pop()
                aut1 = stack.pop()
                stack.append(self._create_automaton_union(aut1, aut2))
            elif x == ".":
                aut2 = stack.pop()
                aut1 = stack.pop()
                stack.append(self._create_automaton_concat(aut1, aut2))
            elif x == "λ":
                stack.append(self._create_automaton_lambda())
            else:
                stack.append(self._create_automaton_symbol(x))

        return stack.pop()