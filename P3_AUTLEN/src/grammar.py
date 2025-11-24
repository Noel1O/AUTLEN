from __future__ import annotations

from collections import deque
from typing import AbstractSet, Collection, MutableSet, Optional, Dict, List, Optional

class RepeatedCellError(Exception):
    """Exception for repeated cells in LL(1) tables."""

class SyntaxError(Exception):
    """Exception for parsing errors."""

class Grammar:
    """
    Class that represents a grammar.

    Args:
        terminals: Terminal symbols of the grammar.
        non_terminals: Non terminal symbols of the grammar.
        productions: Dictionary with the production rules for each non terminal
          symbol of the grammar.
        axiom: Axiom of the grammar.

    """

    def __init__(
        self,
        terminals: AbstractSet[str],
        non_terminals: AbstractSet[str],
        productions: Dict[str, List[str]],
        axiom: str,
    ) -> None:
        if terminals & non_terminals:
            raise ValueError(
                "Intersection between terminals and non terminals "
                "must be empty.",
            )

        if axiom not in non_terminals:
            raise ValueError(
                "Axiom must be included in the set of non terminals.",
            )

        if non_terminals != set(productions.keys()):
            raise ValueError(
                f"Set of non-terminals and productions keys should be equal."
            )
        
        for nt, rhs in productions.items():
            if not rhs:
                raise ValueError(
                    f"No production rules for non terminal symbol {nt} "
                )
            for r in rhs:
                for s in r:
                    if (
                        s not in non_terminals
                        and s not in terminals
                    ):
                        raise ValueError(
                            f"Invalid symbol {s}.",
                        )

        self.terminals = terminals
        self.non_terminals = non_terminals
        self.productions = productions
        self.axiom = axiom

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"terminals={self.terminals!r}, "
            f"non_terminals={self.non_terminals!r}, "
            f"axiom={self.axiom!r}, "
            f"productions={self.productions!r})"
        )


    def compute_first(self, sentence: str) -> AbstractSet[str]:
        """
        Method to compute the first set of a string.

        Args:
            str: string whose first set is to be computed.

        Returns:
            First set of str.
        """
        if not sentence:
            return {''}
        
        first_set = set()
        first_char = sentence[0]
        
        if first_char in self.terminals: # Empieza con terminal
            first_set.add(first_char)
        else:
            for production in self.productions[first_char]: # No empieza con terminal
                if production == '':
                    rest_first = self.compute_first(sentence[1:]) # Cadena vacía 
                    first_set.update(rest_first)
                else:
                    prod_first = self.compute_first(production) # Cálculo recursivo del primero del no terminal
                    first_set.update(prod_first - {''})
                    
                    if '' in prod_first:
                        rest_first = self.compute_first(sentence[1:]) # Si se incluye la cadena vacía en esa recursión
                        first_set.update(rest_first)
        
        return first_set

    def compute_follow(self, symbol: str) -> AbstractSet[str]:
        """
        Method to compute the follow set of a non-terminal symbol.

        Args:
            symbol: non-terminal whose follow set is to be computed.

        Returns:
            Follow set of symbol.
        """

        first_sets = {}
        for nt in self.non_terminals:
            first_sets[nt] = self.compute_first(nt) # Precomputamos los conjuntos Primero para los no terminales
        
        follow_sets = {nt: set() for nt in self.non_terminals} # Inicializamos los conjuntos Siguiente
        follow_sets[self.axiom].add('$') # Inicializamos el conjunto Siguiente del axioma
        
        changed = True
        while changed: # Mientras siga habiendo cambios en los conjuntos Siguiente
            changed = False
            
            for left, productions in self.productions.items(): 
                for production in productions:
                    for i in range(len(production)):
                        X = production[i]
                        if X not in self.non_terminals: # X no es terminal
                            continue
                        
                        old_size = len(follow_sets[X])
                        
                        if i + 1 < len(production): # X está en medio de la producción
                            beta = production[i + 1:] # Beta es el simbolo siguiente a X
                            
                            first_beta = set() # Calcular primero de beta
                            all_lambda = True # Bandera para comprobar si beta puede derivar a lambda
                            
                            for sym in beta: # Comprobación de si beta puede derivar a lambda y el Primero de beta
                                if sym in self.terminals:
                                    first_beta.add(sym)
                                    all_lambda = False
                                    break
                                else:
                                    first_beta.update(first_sets[sym] - {''})
                                    if '' not in first_sets[sym]: # Comprobamos los primeros del no terminal
                                        all_lambda = False
                                        break
                            
                            if all_lambda:
                                first_beta.add('')
                            
                            follow_sets[X].update(first_beta - {''}) # Añadimos el Primero de beta al Siguiente de X
                            
                            if '' in first_beta: # Si beta puede derivar a lambda, añadimos su Siguiente al Siguiente de X
                                follow_sets[X].update(follow_sets[left])
                        
                        else: # X está al final de la producción
                            follow_sets[X].update(follow_sets[left]) # Añadimos el Siguiente del de la izquierda al Siguiente de X
                        
                        if len(follow_sets[X]) != old_size: # Comprobamos si se ha modificado algún Siguiente
                            changed = True
        
        return follow_sets[symbol]


    def get_ll1_table(self) -> Optional[LL1Table]:
        """
        Method to compute the LL(1) table.

        Returns:
            LL(1) table for the grammar, or None if the grammar is not LL(1).
        """

	# TO-DO: Complete this method for exercise 5...


    def is_ll1(self) -> bool:
        return self.get_ll1_table() is not None


class LL1Table:
    """
    LL1 table. Initially all cells are set to None (empty). Table cells
    must be filled by calling the method add_cell.

    Args:
        non_terminals: Set of non terminal symbols.
        terminals: Set of terminal symbols.

    """

    def __init__(
        self,
        non_terminals: AbstractSet[str],
        terminals: AbstractSet[str],
    ) -> None:

        if terminals & non_terminals:
            raise ValueError(
                "Intersection between terminals and non terminals "
                "must be empty.",
            )

        self.terminals: AbstractSet[str] = terminals
        self.non_terminals: AbstractSet[str] = non_terminals
        self.cells: Dict[str, Dict[str, Optional[str]]] = {nt: {t: None for t in terminals} for nt in non_terminals}

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"terminals={self.terminals!r}, "
            f"non_terminals={self.non_terminals!r}, "
            f"cells={self.cells!r})"
        )

    def add_cell(self, non_terminal: str, terminal: str, cell_body: str) -> None:
        """
        Adds a cell to an LL(1) table.

        Args:
            non_terminal: Non termial symbol (row)
            terminal: Terminal symbol (column)
            cell_body: content of the cell 

        Raises:
            RepeatedCellError: if trying to add a cell already filled.
        """
        if non_terminal not in self.non_terminals:
            raise ValueError(
                "Trying to add cell for non terminal symbol not included "
                "in table.",
            )
        if terminal not in self.terminals:
            raise ValueError(
                "Trying to add cell for terminal symbol not included "
                "in table.",
            )
        if not all(x in self.terminals | self.non_terminals for x in cell_body):
            raise ValueError(
                "Trying to add cell whose body contains elements that are "
                "not either terminals nor non terminals.",
            )            
        if self.cells[non_terminal][terminal] is not None:
            raise RepeatedCellError(
                f"Repeated cell ({non_terminal}, {terminal}).")
        else:
            self.cells[non_terminal][terminal] = cell_body

    def analyze(self, input_string: str, start: str) -> ParseTree:
        """
        Method to analyze a string using the LL(1) table.

        Args:
            input_string: string to analyze.
            start: initial symbol.

        Returns:
            ParseTree object with either the parse tree (if the elective exercise is solved)
            or an empty tree (if the elective exercise is not considered).

        Raises:
            SyntaxError: if the input string is not syntactically correct.
        """

        tree = ParseTree(start)
        stack = deque([tree, ParseTree("$")])
        input = deque(input_string)

        # Bucle LL(1)
        


        return tree
    
    
class ParseTree():
    """
    Parse Tree.

    Args:
        root: root node of the tree.
        children: list of children, which are also ParseTree objects.
    """
    def __init__(self, root: str, children: Collection[ParseTree] = []) -> None:
        self.root = root
        self.children = children

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.root!r}: {self.children})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            self.root == other.root
            and len(self.children) == len(other.children)
            and all([x.__eq__(y) for x, y in zip(self.children, other.children)])
        )

    def add_children(self, children: Collection[ParseTree]) -> None:
        self.children = children
