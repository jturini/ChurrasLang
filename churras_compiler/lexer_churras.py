from typing import List
from tokens_churras import Token, TokenType, KEYWORDS

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, source: str):
        self.src = source
        self.i = 0
        self.line = 1
        self.col = 1
        self.length = len(source)

    def _peek(self, k=0):
        j = self.i + k
        if j >= self.length:
            return '\0'
        return self.src[j]

    def _advance(self):
        ch = self._peek()
        self.i += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _is_alpha(self, ch): return (ch.isalpha()) or ch == '_'
    def _is_alnum(self, ch): return self._is_alpha(ch) or ch.isdigit()
    def _is_digit(self, ch): return ch.isdigit()

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            tok = self._next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens

    def _skip_whitespace_and_comments(self):
        while True:
            ch = self._peek()
            if ch in [' ', '\t', '\r', '\n']:
                self._advance()
                continue
            if ch == '#':
                while self._peek() not in ['\n','\0']:
                    self._advance()
                continue
            break

    def _next_token(self) -> Token:
        self._skip_whitespace_and_comments()
        start_line, start_col = self.line, self.col
        ch = self._peek()

        if ch == '\0':
            return Token(TokenType.EOF, "", start_line, start_col)

        if ch == '=': self._advance(); return Token(TokenType.OP_ATRIB, "=", start_line, start_col)
        if ch == '+': self._advance(); return Token(TokenType.OP_SOMA, "+", start_line, start_col)
        if ch == '-': self._advance(); return Token(TokenType.OP_SUB, "-", start_line, start_col)
        if ch == '*': self._advance(); return Token(TokenType.OP_MULT, "*", start_line, start_col)
        if ch == '/': self._advance(); return Token(TokenType.OP_DIV, "/", start_line, start_col)
        if ch == '(': self._advance(); return Token(TokenType.PARENT_ESQ, "(", start_line, start_col)
        if ch == ')': self._advance(); return Token(TokenType.PARENT_DIR, ")", start_line, start_col)
        if ch == ';': self._advance(); return Token(TokenType.PONTO_VIRGULA, ";", start_line, start_col)
        if ch == ':': self._advance(); return Token(TokenType.DOIS_PONTOS, ":", start_line, start_col)

        if ch == '"':
            self._advance() # Consome o '"' inicial
            lex = []
            while self._peek() != '"':
                if self._peek() == '\0':
                    raise LexerError(f"String não terminada na linha {start_line}, coluna {start_col}.")
                lex.append(self._advance())
            
            self._advance() # Consome o '"' final
            value = ''.join(lex)
            return Token(TokenType.STRING, value, start_line, start_col)

        if self._is_alpha(ch):
            lex = [self._advance()]
            while self._is_alnum(self._peek()):
                lex.append(self._advance())
            value = ''.join(lex)
            ttype = KEYWORDS.get(value.upper(), TokenType.ID)
            return Token(ttype, value, start_line, start_col)

        if self._is_digit(ch):
            lex = [self._advance()]
            while self._is_digit(self._peek()):
                lex.append(self._advance())
            if self._peek() == '.':
                self._advance()
                if not self._is_digit(self._peek()):
                    raise LexerError(f"Número real malformado na linha {start_line}, coluna {start_col}: esperado dígitos após '.'")
                frac = [self._advance()]
                while self._is_digit(self._peek()):
                    frac.append(self._advance())
                value = ''.join(lex) + '.' + ''.join(frac)
                return Token(TokenType.NUM_REAL, value, start_line, start_col)
            else:
                value = ''.join(lex)
                return Token(TokenType.NUM_INTEIRO, value, start_line, start_col)

        bad = self._advance()
        raise LexerError(f"Símbolo inválido '{bad}' na linha {start_line}, coluna {start_col}")