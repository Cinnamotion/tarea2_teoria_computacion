# -*- coding: utf-8 -*-

"""
Este script implementa un analizador léxico a través de un enfoque manual,
procesando el código fuente carácter por carácter. Este método ofrece un
control total sobre el proceso de tokenización y es muy flexible.

El analizador está encapsulado en la clase `Lexer`, que mantiene el estado
del análisis (posición, línea, columna) y proporciona métodos para reconocer
diferentes tipos de tokens.
"""

from dataclasses import dataclass
from typing import Optional, Any, List

# --- 1. Definición de Tokens ---
# Se utilizan diccionarios y conjuntos para definir los componentes léxicos
# del lenguaje de una manera clara y eficiente.

# Conjunto de palabras clave. Usar un conjunto (set) permite una verificación
# de pertenencia (ej. `lex in KEYWORDS`) muy rápida.
KEYWORDS = {
    "if", "else", "while", "for", "return",
    "int", "float", "void", "char", "bool",
    "true", "false", "break", "continue"
}

# Operadores de dos caracteres. Se definen primero porque deben ser
# verificados antes que los de un carácter para evitar ambigüedades.
# Por ejemplo, '==' debe ser reconocido como IGL, y no como dos '=' (ES).
OPERATORS_2 = {
    "<=": "MEOI",    # Menor o igual
    ">=": "MAOI",    # Mayor o igual
    "==": "IGL",     # Igual
    "!=": "DIS",     # Distinto
    "++": "INC",     # Incremento
    "--": "DEC",     # Decremento
    "+=": "MASIG",   # Asignación con suma
    "-=": "MENOSIG", # Asignación con resta
    "*=": "MULIG",   # Asignación con multiplicación
    "/=": "DIVIG",   # Asignación con división
    "&&": "LAND",    # AND Lógico
    "||": "LOR"      # OR Lógico
}

# Operadores de un carácter.
OPERATORS_1 = {
    "+": "MAS",      # Suma
    "-": "MENOS",    # Resta
    "*": "MUL",      # Multiplicación
    "/": "DIV",      # División
    "%": "MOD",      # Módulo
    "<": "MEQ",      # Menor que
    ">": "MAQ",      # Mayor que
    "=": "ES",       # Asignación
    "!": "NO",       # NOT Lógico
    ":": "DPTS"      # Dos puntos
}

# Signos de puntuación.
PUNCT = {
    ";": "PYC",      # Punto y coma
    ",": "COMA",     # Coma
    "(": "IPAREN",   # Paréntesis izquierdo
    ")": "DPAREN",   # Paréntesis derecho
    "{": "ILLAVE",   # Llave izquierda
    "}": "DLLAVE",   # Llave derecha
    "[": "ICOR",     # Corchete izquierdo
    "]": "DCOR",     # Corchete derecho
    ".": "PUN"       # Punto
}

# --- 2. Estructuras de Datos Auxiliares ---

@dataclass
class Token:
    """
    Representa un token, la unidad léxica mínima.
    Utiliza un `dataclass` para una definición concisa.

    Atributos:
        type (str): El tipo de token (ej. 'NUM', 'KW_IF', 'ID').
        lexeme (str): El texto del código fuente que conforma el token (ej. '123', 'if').
        line (int): La línea donde comienza el token.
        col (int): La columna donde comienza el token.
        value (Optional[Any]): El valor semántico del token (ej. el número 123 para el lexema '123').
        lid (Optional[int]): Un ID único para los identificadores, útil para la tabla de símbolos.
    """
    type: str
    lexeme: str
    line: int
    col: int
    value: Optional[Any] = None
    lid: Optional[int] = None

class LexerError(Exception):
    """Excepción personalizada para errores durante el análisis léxico."""
    pass

# --- 3. Implementación del Analizador Léxico ---

class Lexer:
    """
    Implementa el analizador léxico (scanner). Recorre el texto de entrada
    y lo convierte en una secuencia de tokens.
    """
    def __init__(self, text: str):
        """
        Inicializa el estado del lexer.

        Args:
            text (str): El código fuente a tokenizar.
        """
        self.text = text
        self.n = len(text)
        self.pos = 0          # Posición actual en el texto (índice)
        self.line = 1         # Línea actual (para reportar errores)
        self.col = 1          # Columna actual (para reportar errores)
        self.lettab = {}      # Tabla de "letras" o símbolos para identificadores
        self._letseq = 0      # Secuencia para generar IDs únicos para identificadores

    def at_end(self) -> bool:
        """Verifica si se ha llegado al final del texto."""
        return self.pos >= self.n

    def peek(self, k: int = 0) -> str:
        """
        "Espía" el carácter en la posición actual + k sin avanzar el puntero.
        Devuelve una cadena vacía si está fuera de los límites.
        """
        return "" if self.pos + k >= self.n else self.text[self.pos + k]

    def advance(self) -> str:
        """
        Avanza a la siguiente posición en el texto y actualiza línea/columna.
        Devuelve el carácter sobre el que se avanzó.
        """
        ch = self.peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_ws_and_comments(self) -> None:
        """
        Salta todos los espacios en blanco, tabulaciones, saltos de línea
        y comentarios de una sola línea (estilo //).
        """
        # Se usa un bucle `while moved` para manejar casos como `codigo // comentario`
        # donde después de saltar el comentario, puede haber más espacios.
        moved = True
        while moved:
            moved = False
            # Salta espacios en blanco, tabulaciones, etc.
            while not self.at_end() and self.peek() in " \t\r\n":
                self.advance()
                moved = True
            # Salta comentarios de una sola línea
            if self.peek() == "/" and self.peek(1) == "/":
                while not self.at_end() and self.peek() != "\n":
                    self.advance()
                moved = True

    def read_identifier_or_keyword(self) -> Optional[Token]:
        """
        Lee un identificador o una palabra clave.
        Un identificador comienza con una letra o '_' y puede contener letras, números o '_'.
        """
        ch = self.peek()
        # Un identificador debe comenzar con una letra o guion bajo.
        if not (ch.isalpha() or ch == "_"):
            return None

        start_line, start_col = self.line, self.col
        lex = self.advance()
        while not self.at_end() and (self.peek().isalnum() or self.peek() == "_"):
            lex += self.advance()

        # Determina si el lexema es una palabra clave o un identificador.
        ttype = ("KW_" + lex.upper()) if lex in KEYWORDS else "ID"
        tok = Token(ttype, lex, start_line, start_col)

        # Si es un identificador, se gestiona su entrada en la tabla de símbolos.
        if ttype == "ID":
            if lex not in self.lettab:
                self.lettab[lex] = self._letseq
                self._letseq += 1
            # Se añade el ID único del símbolo como atributo del token.
            tok.lid = self.lettab[lex]
        return tok

    def read_number(self) -> Optional[Token]:
        """
        Lee un número entero.
        Nota: Esta implementación solo maneja enteros. Se podría extender para
        soportar números de punto flotante.
        """
        # Un número debe comenzar con un dígito.
        if not self.peek().isdigit():
            return None

        start_line, start_col = self.line, self.col
        lex = self.advance()
        while not self.at_end() and self.peek().isdigit():
            lex += self.advance()
        
        return Token("NUM", lex, start_line, start_col, value=int(lex))

    def read_operator_or_punct(self) -> Optional[Token]:
        """Lee un operador o un signo de puntuación."""
        start_line, start_col = self.line, self.col
        
        # Primero, intenta reconocer un operador de dos caracteres.
        # Esto es crucial para evitar que '==' se lea como dos '='.
        two_chars = self.peek() + self.peek(1)
        if two_chars in OPERATORS_2:
            self.advance()
            self.advance()
            return Token(OPERATORS_2[two_chars], two_chars, start_line, start_col)
        
        # Si no, intenta reconocer un operador de un carácter.
        one_char = self.peek()
        if one_char in OPERATORS_1:
            self.advance()
            return Token(OPERATORS_1[one_char], one_char, start_line, start_col)
        
        # Finalmente, intenta reconocer un signo de puntuación.
        if one_char in PUNCT:
            self.advance()
            return Token(PUNCT[one_char], one_char, start_line, start_col)
        
        return None

    def next_token(self) -> Token:
        """

        Obtiene el siguiente token del texto de entrada.
        Este método es el núcleo del Autómata Finito Determinista.
        """
        self.skip_ws_and_comments()

        if self.at_end():
            return Token("EOF", "", self.line, self.col)

        # El orden de las llamadas es importante para resolver ambigüedades:
        # 1. Identificadores/Palabras Clave: 'if' es una palabra clave, no dos letras.
        # 2. Números: '123' es un número, no tres dígitos separados.
        # 3. Operadores/Puntuación: Símbolos como '+', ';', etc.
        
        token = self.read_identifier_or_keyword()
        if token: return token
        
        token = self.read_number()
        if token: return token

        token = self.read_operator_or_punct()
        if token: return token

        # Si ningún método pudo reconocer un token, es un error léxico.
        ch = self.peek()
        raise LexerError(f"Carácter inesperado '{ch}' en línea {self.line}, col {self.col}")

    def tokenize(self) -> List[Token]:
        """
        Ejecuta el análisis léxico completo y devuelve una lista de todos los tokens.
        """
        tokens: List[Token] = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            # El bucle termina cuando se encuentra el token de Fin de Archivo (EOF).
            if tok.type == "EOF":
                break
        return tokens

# --- 4. Interfaz de Línea de Comandos (CLI) para Pruebas ---
if __name__ == "__main__":
    import sys
    # Verifica que se haya proporcionado un archivo como argumento.
    if len(sys.argv) < 2:
        print("Uso: python codigo.py <archivo_fuente>")
        sys.exit(1)

    try:
        # Lee el contenido del archivo.
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{sys.argv[1]}' no fue encontrado.")
        sys.exit(1)
    
    # Crea una instancia del Lexer y tokeniza el texto.
    lx = Lexer(text)
    try:
        # Imprime cada token con un formato claro.
        for t in lx.tokenize():
            lid_str = "" if t.lid is None else f"  lid={t.lid}"
            val_str = "" if t.value is None else f"  val={t.value}"
            print(f"{t.type:<10} {t.lexeme!r:<14} @({t.line},{t.col}){lid_str}{val_str}")
    except LexerError as e:
        # Captura y reporta cualquier error léxico.
        print(f"\nError durante el análisis: {e}")
        sys.exit(1)