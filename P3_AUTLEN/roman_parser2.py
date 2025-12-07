import sys
import os

# Ajuste de path para asegurar imports correctos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import ply.yacc as yacc
from src.roman_lexer import tokens

# ==============================================================================
# GRAMÁTICA G2 (Recursiva a la DERECHA)
#
# Definición original:
# LowHundreds -> C LowHundreds | lambda
#
# Implementación LALR robusta:
# LowHundreds -> C LowHundreds | C  (1 o más)
# Hundreds -> ... | empty
# ==============================================================================

def p_romanNumber(p):
    """romanNumber : Hundreds Tens Units"""
    val = p[1]['val'] + p[2]['val'] + p[3]['val']
    valid = p[1]['valid'] and p[2]['valid'] and p[3]['valid']
    
    p[0] = {
        "val": val if valid else -1,
        "valid": valid
    }

# Regla dummy para evitar warnings
def p_thousand(p):
    """thousand : empty"""
    p[0] = {'val': 0, 'valid': True}

# --- CENTENAS (Recursividad Derecha) ---

def p_small_hundred(p):
    """LowHundreds : C LowHundreds
                   | C"""
    # p[1] es 'C', p[2] es el diccionario del resto (si existe)
    if len(p) == 3: # C LowHundreds
        rec = p[2]
        new_count = rec['count'] + 1
        new_val = 100 + rec['val']
        is_valid = rec['valid'] and (new_count <= 3)
        p[0] = {'val': new_val, 'count': new_count, 'valid': is_valid}
    else: # C (caso base de la recursión)
        p[0] = {'val': 100, 'count': 1, 'valid': True}

def p_hundred(p):
    """Hundreds : LowHundreds
                | empty
                | C D
                | D LowHundreds
                | D
                | C M"""
    if len(p) == 2: # LowHundreds | empty | D
        if isinstance(p[1], str) and p[1] == 'D':
             p[0] = {'val': 500, 'valid': True}
        else:
             p[0] = p[1]
    elif p[1] == 'C' and p[2] == 'D': # CD
        p[0] = {'val': 400, 'valid': True}
    elif p[1] == 'D': # D LowHundreds
        p[0] = {'val': 500 + p[2]['val'], 'valid': p[2]['valid']}
    elif p[1] == 'C' and p[2] == 'M': # CM
        p[0] = {'val': 900, 'valid': True}

# --- DECENAS (Recursividad Derecha) ---

def p_small_ten(p):
    """LowTens : X LowTens
               | X"""
    if len(p) == 3: # X LowTens
        rec = p[2]
        new_count = rec['count'] + 1
        new_val = 10 + rec['val']
        is_valid = rec['valid'] and (new_count <= 3)
        p[0] = {'val': new_val, 'count': new_count, 'valid': is_valid}
    else: # X
        p[0] = {'val': 10, 'count': 1, 'valid': True}

def p_ten(p):
    """Tens : LowTens
            | empty
            | X L
            | L LowTens
            | L
            | X C"""
    if len(p) == 2: # LowTens | empty | L
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

# --- UNIDADES (Recursividad Derecha) ---

def p_small_digit(p):
    """LowUnits : I LowUnits
                | I"""
    if len(p) == 3: # I LowUnits
        rec = p[2]
        new_count = rec['count'] + 1
        new_val = 1 + rec['val']
        is_valid = rec['valid'] and (new_count <= 3)
        p[0] = {'val': new_val, 'count': new_count, 'valid': is_valid}
    else: # I
        p[0] = {'val': 1, 'count': 1, 'valid': True}

def p_digit(p):
    """Units : LowUnits
             | empty
             | I V
             | V LowUnits
             | V
             | I X"""
    if len(p) == 2: # LowUnits | empty | V
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

# --- AUXILIARES ---

def p_empty(p):
    'empty :'
    p[0] = {'val': 0, 'count': 0, 'valid': True}

def p_roman(p):
    """roman : romanNumber"""
    p[0] = p[1]

# Manejo de errores sintácticos
def p_error(p):
    # Lanzamos excepción para que el análisis falle explícitamente si hay tokens sobrantes o inválidos
    raise SyntaxError("Error de sintaxis")

# Construir el parser
parser = yacc.yacc(start='romanNumber')

if __name__ == "__main__":
    while True:
        try:
            s = input("Ingrese un número romano: ")
        except EOFError:
            break
        if not s:
            continue
        
        try:
            result = parser.parse(s)
            if result is None:
                print(f"El valor numérico es: {{'val': -1, 'valid': False}}")
            else:
                print(f"El valor numérico es: {result}")
        except SyntaxError:
            print(f"El valor numérico es: {{'val': -1, 'valid': False}}")