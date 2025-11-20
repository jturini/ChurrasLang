from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    INICIAR_CHURRAS = auto()
    FIM_CHURRAS = auto()
    DESPENSA = auto()
    COZINHAR = auto()
    PICANHA = auto()      # int
    ARROZ = auto()        # real
    PROVAR = auto()       # input
    SERVIR = auto()       # output
    OP_ATRIB = auto()
    OP_SOMA = auto()
    OP_SUB = auto()
    OP_MULT = auto()      
    OP_DIV = auto()     
    PARENT_ESQ = auto()   
    PARENT_DIR = auto()   
    STRING = auto()       
    PONTO_VIRGULA = auto()
    DOIS_PONTOS = auto()
    ID = auto()
    NUM_INTEIRO = auto()
    NUM_REAL = auto()
    EOF = auto()

KEYWORDS = {
    "INICIAR_CHURRAS": TokenType.INICIAR_CHURRAS,
    "FIM_CHURRAS": TokenType.FIM_CHURRAS,
    "DESPENSA": TokenType.DESPENSA,
    "COZINHAR": TokenType.COZINHAR,
    "PICANHA": TokenType.PICANHA,
    "ARROZ": TokenType.ARROZ,
    "PROVAR": TokenType.PROVAR,
    "SERVIR": TokenType.SERVIR,
}

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    col: int