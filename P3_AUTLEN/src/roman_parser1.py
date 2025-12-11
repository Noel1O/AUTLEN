import sys
import os

import ply.yacc as yacc
from src.roman_lexer import tokens

# Recursiva a la izquierda

# Función principal que lleva el recuento de unidades, decenas y centenas
def p_romanNumber(p):
    """romanNumber : Hundreds Tens Units"""
    val = p[1]['val'] + p[2]['val'] + p[3]['val'] # Valor total
    valid = p[1]['valid'] and p[2]['valid'] and p[3]['valid'] # Todas válidas
    
    p[0] = {
        "val": val if valid else -1,
        "valid": valid
    }

# def p_thousand(p): No forma parte de la gramática el millar

def p_small_hundred(p):
    """LowHundreds : LowHundreds C
                   | C"""
    if len(p) == 3: # LowHundreds C
        prev = p[1]
        new_count = prev['count'] + 1
        new_val = prev['val'] + 100
        is_valid = prev['valid'] and (new_count <= 3) # Comprobar que no van 3 C seguidas
        p[0] = {'val': new_val, 'count': new_count, 'valid': is_valid}
    else: # C
        p[0] = {'val': 100, 'count': 1, 'valid': True}

def p_hundred(p):
    """Hundreds : LowHundreds
                | lambda
                | C D
                | D LowHundreds
                | D
                | C M"""
    if len(p) == 2: # LowHundreds | lambda | D
        if isinstance(p[1], str) and p[1] == 'D':
             p[0] = {'val': 500, 'valid': True}
        else:
             p[0] = p[1] # LowHundreds o lambda dict
    elif p[1] == 'C' and p[2] == 'D': # CD
        p[0] = {'val': 400, 'valid': True}
    elif p[1] == 'D': # D LowHundreds
        p[0] = {'val': 500 + p[2]['val'], 'valid': p[2]['valid']}
    elif p[1] == 'C' and p[2] == 'M': # CM
        p[0] = {'val': 900, 'valid': True}

def p_small_ten(p):
    """LowTens : LowTens X
               | X"""
    if len(p) == 3: # LowTens X
        prev = p[1]
        new_count = prev['count'] + 1
        new_val = prev['val'] + 10
        is_valid = prev['valid'] and (new_count <= 3)  # Comprobar que no van 3 X seguidas
        p[0] = {'val': new_val, 'count': new_count, 'valid': is_valid}
    else: # X
        p[0] = {'val': 10, 'count': 1, 'valid': True}

def p_ten(p):
    """Tens : LowTens
            | lambda
            | X L
            | L LowTens
            | L
            | X C"""
    if len(p) == 2: # LowTens | lambda | L
        if isinstance(p[1], str) and p[1] == 'L':
             p[0] = {'val': 50, 'valid': True}
        else:
             p[0] = p[1]
    elif p[1] == 'X' and p[2] == 'L': # XL
        p[0] = {'val': 40, 'valid': True}
    elif p[1] == 'L': # L LowTens
        p[0] = {'val': 50 + p[2]['val'], 'valid': p[2]['valid']}
    elif p[1] == 'X' and p[2] == 'C': # XC
        p[0] = {'val': 90, 'valid': True}

def p_small_digit(p):
    """LowUnits : LowUnits I
                | I"""

    if len(p) == 3: # LowUnits I
        prev = p[1]
        new_count = prev['count'] + 1
        new_val = prev['val'] + 1
        is_valid = prev['valid'] and (new_count <= 3) # Comprobar que no van 3 I seguidas
        p[0] = {'val': new_val, 'count': new_count, 'valid': is_valid}
    else: # I
        p[0] = {'val': 1, 'count': 1, 'valid': True}

def p_digit(p):
    """Units : LowUnits
             | lambda
             | I V
             | V LowUnits
             | V
             | I X"""
    if len(p) == 2: # LowUnits | lambda | V
        if isinstance(p[1], str) and p[1] == 'V':
             p[0] = {'val': 5, 'valid': True}
        else:
             p[0] = p[1]
    elif p[1] == 'I' and p[2] == 'V': # IV
        p[0] = {'val': 4, 'valid': True}
    elif p[1] == 'V': # V LowUnits
        p[0] = {'val': 5 + p[2]['val'], 'valid': p[2]['valid']}
    elif p[1] == 'I' and p[2] == 'X': # IX
        p[0] = {'val': 9, 'valid': True}

# Definir lambda
def p_empty(p):
    'lambda :'
    p[0] = {'val': 0, 'count': 0, 'valid': True}

def p_roman(p):
    """roman : romanNumber"""
    p[0] = p[1]

# Manejo de errores sintácticos
def p_error(p):
    print("Error de sintaxis en '%s'" % p.value if p else "EOF")

# Construir el parser
parser = yacc.yacc(start='roman')

if __name__ == "__main__":
    while True:
        try:
            s = input("Ingrese un número romano: ")
        except EOFError:
            break
        if not s:
            continue
        result = parser.parse(s)
        print(f"El valor numérico es: {result}")
