import sys
import os

# Ajuste de path para asegurar imports correctos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import ply.yacc as yacc
from src.roman_lexer import tokens

# ==============================================================================
# GRAMÁTICA G1 (Recursiva a la IZQUIERDA - LALR)
# ==============================================================================

def p_romanNumber(p):
    """romanNumber : Hundreds Tens Units"""
    val = p[1]['val'] + p[2]['val'] + p[3]['val']
    valid = p[1]['valid'] and p[2]['valid'] and p[3]['valid']
    
    p[0] = {
        "val": val if valid else -1,
        "valid": valid
    }

# Regla dummy para evitar warnings (el esqueleto la pide)
def p_thousand(p):
    """thousand : empty"""
    p[0] = {'val': 0, 'valid': True}

# --- CENTENAS ---

def p_small_hundred(p):
    """LowHundreds : LowHundreds C
                   | C"""
    # Esta regla ahora gestiona 1 o más 'C'.
    if len(p) == 3: # LowHundreds C
        prev = p[1]
        new_count = prev['count'] + 1
        new_val = prev['val'] + 100
        is_valid = prev['valid'] and (new_count <= 3)
        p[0] = {'val': new_val, 'count': new_count, 'valid': is_valid}
    else: # C
        # Caso base: 1 sola C
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
             p[0] = p[1] # LowHundreds o empty dict
    elif p[1] == 'C' and p[2] == 'D':
        p[0] = {'val': 400, 'valid': True}
    elif p[1] == 'D': # D LowHundreds
        p[0] = {'val': 500 + p[2]['val'], 'valid': p[2]['valid']}
    elif p[1] == 'C' and p[2] == 'M':
        p[0] = {'val': 900, 'valid': True}

# --- DECENAS ---

def p_small_ten(p):
    """LowTens : LowTens X
               | X"""
    # 1 o más X
    if len(p) == 3: # LowTens X
        prev = p[1]
        new_count = prev['count'] + 1
        new_val = prev['val'] + 10
        is_valid = prev['valid'] and (new_count <= 3)
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
    elif p[1] == 'X' and p[2] == 'L':
        p[0] = {'val': 40, 'valid': True}
    elif p[1] == 'L': # L LowTens
        p[0] = {'val': 50 + p[2]['val'], 'valid': p[2]['valid']}
    elif p[1] == 'X' and p[2] == 'C':
        p[0] = {'val': 90, 'valid': True}

# --- UNIDADES ---

def p_small_digit(p):
    """LowUnits : LowUnits I
                | I"""
    # 1 o más I
    if len(p) == 3: # LowUnits I
        prev = p[1]
        new_count = prev['count'] + 1
        new_val = prev['val'] + 1
        is_valid = prev['valid'] and (new_count <= 3)
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
    elif p[1] == 'I' and p[2] == 'V':
        p[0] = {'val': 4, 'valid': True}
    elif p[1] == 'V': # V LowUnits
        p[0] = {'val': 5 + p[2]['val'], 'valid': p[2]['valid']}
    elif p[1] == 'I' and p[2] == 'X':
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
    # IMPORTANTE: Si hay un error, lanzamos una excepción o imprimimos
    # para que el parseo falle explícitamente y no devuelva un valor parcial.
    raise SyntaxError("Error de sintaxis")

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
            # Si parser.parse devuelve None (caso de error silenciado), lo tratamos como inválido
            if result is None:
                print(f"El valor numérico es: {{'val': -1, 'valid': False}}")
            else:
                print(f"El valor numérico es: {result}")
        except SyntaxError:
            # Capturamos el error que lanzamos en p_error
            print(f"El valor numérico es: {{'val': -1, 'valid': False}}")