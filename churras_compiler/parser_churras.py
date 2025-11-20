from typing import List, Dict, Any, Optional
import tkinter as tk
from tkinter import simpledialog
from tokens_churras import Token, TokenType
from lexer_churras import Lexer, LexerError

class ParseError(Exception):
    def __init__(self, message, token):
        super().__init__(message)
        self.token = token

class InterpreterError(Exception):
    def __init__(self, message, token):
        super().__init__(message)
        self.token = token

class Parser:
    def __init__(self, tokens: List[Token], gui_root: Optional[tk.Tk] = None):
        self.tokens = tokens
        self.i = 0
        self.types: Dict[str, str] = {}
        self.values: Dict[str, Any] = {}
        self.outputs: List[str] = []
        self.gui_root = gui_root

    def _peek(self, k: int = 0) -> Token:
        idx = self.i + k
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def _match(self, *expected: TokenType) -> Token:
        current_token = self._peek()
        if current_token.type in expected:
            self.i += 1
            return current_token
        exp_str = ", ".join(t.name for t in expected)
        raise ParseError(f"Esperado [{exp_str}], mas veio {current_token.type.name}", current_token)

    def parse(self) -> List[str]:
        self._match(TokenType.INICIAR_CHURRAS)
        self._despensa()
        self._cozinhar()
        self._match(TokenType.FIM_CHURRAS)
        return self.outputs

    def _despensa(self):
        if self._peek().type == TokenType.DESPENSA:
            self._match(TokenType.DESPENSA)
            while self._peek().type == TokenType.ID:
                ident = self._match(TokenType.ID).lexeme
                self._match(TokenType.DOIS_PONTOS)
                tipo_tok = self._match(TokenType.PICANHA, TokenType.ARROZ)
                tipo = "int" if tipo_tok.type == TokenType.PICANHA else "real"
                self.types[ident] = tipo
                self.values.setdefault(ident, 0 if tipo == "int" else 0.0)
                self._match(TokenType.PONTO_VIRGULA)

    def _cozinhar(self):
        self._match(TokenType.COZINHAR)
        while self._peek().type != TokenType.FIM_CHURRAS:
            token_type = self._peek().type
            if token_type == TokenType.ID: self._cmd_atribuicao()
            elif token_type == TokenType.SERVIR: self._cmd_servir()
            elif token_type == TokenType.PROVAR: self._cmd_provar()
            else: break

    

    def _cmd_provar(self):
        self._match(TokenType.PROVAR)
        var_token = self._match(TokenType.ID)
        ident = var_token.lexeme
        self._match(TokenType.PONTO_VIRGULA)
        if ident not in self.types:
            raise InterpreterError(f"Erro Semântico: Variável '{ident}' não declarada.", var_token)

        variable_type = self.types[ident]
        user_input = None

        
        if self.gui_root:
            # Se a GUI existe, usa a caixa de diálogo
            prompt_text = f"Digite um valor para a variável '{ident}' (tipo: {variable_type}):"
            user_input = simpledialog.askstring("PROVAR (Entrada de Dados)", prompt_text, parent=self.gui_root)
        else:
            # Se não há GUI, usa o input() do terminal
            try:
                prompt_text = f"PROVAR > Digite um valor para '{ident}': "
                user_input = input(prompt_text)
            except EOFError: 
                user_input = None
        

        if user_input is None:
            return

        try:
            if variable_type == "int":
                self.values[ident] = int(user_input)
            else:
                self.values[ident] = float(user_input)
        except ValueError:
            raise InterpreterError(f"Entrada inválida '{user_input}' para variável do tipo '{variable_type}'.", var_token)

    def _cmd_servir(self):
        self._match(TokenType.SERVIR)
        value = self._expr()
        self._match(TokenType.PONTO_VIRGULA)
        self.outputs.append(str(value))

    def _cmd_atribuicao(self):
        var_token = self._match(TokenType.ID)
        ident = var_token.lexeme
        self._match(TokenType.OP_ATRIB)
        value = self._expr()
        self._match(TokenType.PONTO_VIRGULA)
        if ident not in self.types:
            raise InterpreterError(f"Erro Semântico: Variável '{ident}' não declarada.", var_token)
        
        if isinstance(value, str):
            raise InterpreterError(f"Erro Semântico: Não é possível atribuir String a uma variável numérica.", var_token)
            
        if self.types[ident] == "int": self.values[ident] = int(value)
        else: self.values[ident] = float(value)

    def _expr(self):
        value = self._termo()
        while self._peek().type in (TokenType.OP_SOMA, TokenType.OP_SUB):
            op = self._match(TokenType.OP_SOMA, TokenType.OP_SUB)
            rhs = self._termo()
            if op.type == TokenType.OP_SOMA: value += rhs
            else: value -= rhs
        return value

    def _termo(self):
        value = self._fator()
        while self._peek().type in (TokenType.OP_MULT, TokenType.OP_DIV):
            op = self._match(TokenType.OP_MULT, TokenType.OP_DIV)
            rhs = self._fator()
            if op.type == TokenType.OP_MULT: value *= rhs
            elif op.type == TokenType.OP_DIV:
                if rhs == 0:
                    raise InterpreterError("Erro Semântico: Divisão por zero.", op)
                value /= rhs
        return value

    def _fator(self):
        token = self._peek()
        if token.type in [TokenType.NUM_INTEIRO, TokenType.NUM_REAL]:
            self._match(token.type)
            return float(token.lexeme) if '.' in token.lexeme else int(token.lexeme)
        if token.type == TokenType.STRING:
            self._match(TokenType.STRING)
            return token.lexeme
        if token.type == TokenType.ID:
            var_token = self._match(TokenType.ID)
            var_name = var_token.lexeme
            if var_name not in self.values:
                raise InterpreterError(f"Erro Semântico: Variável '{var_name}' não declarada.", var_token)
            return self.values[var_name]
        if token.type == TokenType.PARENT_ESQ:
            self._match(TokenType.PARENT_ESQ)
            value = self._expr()
            self._match(TokenType.PARENT_DIR)
            return value
        raise ParseError("Expressão inválida", token)

def compile_churras(code: str, root_window: Optional[tk.Tk] = None) -> Dict:
    result = {
        "status": "success", "tokens": [], "output": "", 
        "error_stage": "", "error_message": "", "error_token": None
    }
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        result["tokens"] = [f"{t.type.name:<20} | {t.lexeme:<25} | L: {t.line}, C: {t.col}" for t in tokens if t.type != TokenType.EOF]

        parser = Parser(tokens, root_window)
        outputs = parser.parse()
        result["output"] = "\n".join(outputs) if outputs else "<nenhuma>"
        result["error_message"] = "Compilado e executado com sucesso!"

    except (LexerError, ParseError, InterpreterError) as e:
        result["status"] = "error"
        if isinstance(e, LexerError): result["error_stage"] = "Léxico"
        elif isinstance(e, ParseError): result["error_stage"] = "Sintático"
        else: result["error_stage"] = "Semântico"
        result["error_message"] = str(e)
        if hasattr(e, 'token') and e.token:
            result["error_token"] = e.token
    return result