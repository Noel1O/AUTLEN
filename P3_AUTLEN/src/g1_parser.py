
import ply.yacc as yacc
from src.g1_lexer import tokens

# Gramática

def p_Language(p):
    """Language : A B C"""
    # Condición del lenguaje: a^n b^n c^k donde k >= n+1
    # A.count = n, B.count = n, C.c = k (usando 'c' para ser fiel al esqueleto original de p_C)
    
    count_a = p[1]["count"] # Conteo de 'a's (n)
    count_b = p[2]["count"] # Conteo de 'b's (n)
    count_c = p[3]["c"]     # Conteo de 'c's (k)
    
    # El resultado final (p[0]) es True si se cumplen las condiciones, False si no.
    if count_a == count_b and count_c >= count_a + 1:
        p[0] = True
    else:
        p[0] = False

def p_A(p):
    """A : a A
        | lambda"""

    if len(p) == 3:
        # A -> a A: Contamos 1 'a' + el conteo del hijo A (p[2])
        p[0] = {"count": 1 + p[2]["count"]}
    else: # A -> lambda
        # Caso base: A -> lambda, el conteo es 0
        p[0] = {"count": 0}
        
def p_B(p):
    """B : b B
        | lambda"""
    
    if len(p) == 3:
        # B -> b B: Contamos 1 'b' + el conteo del hijo B (p[2])
        p[0] = {"count": 1 + p[2]["count"]}
    else: # B -> lambda
        # Caso base: B -> lambda, el conteo es 0
        p[0] = {"count": 0}

def p_C(p):
    """C : c C
        | lambda"""
    # Función de C ya implementada en el esqueleto original. Usamos 'c' como clave de atributo.
    if len(p) == 3:
        p[0] = {"c": 1 + p[2]["c"]}
    else:
        p[0] = {"c": 0}

def p_lambda(p):
    """lambda :"""
    pass  # Producción vacía

# Manejo de errores sintácticos
def p_error(p):
    print("Error de sintaxis en '%s'" % p.value if p else "EOF")

# Construir el parser
parser = yacc.yacc(start='Language') # Definimos 'Language' como el axioma de inicio

if __name__ == "__main__":
    while True:
        try:
            s = input("Ingrese una cadena: ")
        except EOFError:
            break
        if not s:
            continue
        result = parser.parse(s)
        print(f"El valor numérico es:", result)