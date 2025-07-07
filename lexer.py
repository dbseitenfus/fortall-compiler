import ply.lex as lex

tokens = (
    'ID', 'NUM', 'STR',
    'MAIS', 'MENOS', 'MULT', 'DIV',
    'ATRIB', 'VIRG', 'PONTOEVIRG', 'DOISPONTOS', 'PONTO',
    'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'NEQ',
    'LT', 'LE', 'GT', 'GE', 'EQ',
)

precedence = (
    ('left', 'MAIS', 'MENOS'),
    ('left', 'MULT', 'DIV'),
    ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NEQ'),
    ('right', 'MENOSU'), 
)

reserved = {
    'programa': 'PROGRAMA',
    'var': 'VAR',
    'inteiro': 'INTEIRO',
    'logico': 'LOGICO',
    'inicio': 'INICIO',
    'fim': 'FIM',
    'ler': 'LER',
    'escrever': 'ESCREVER',
    'se': 'SE',
    'senao': 'SENAO',
    'entao': 'ENTAO',
    'enquanto': 'ENQUANTO',
    'faca': 'FACA',
}

tokens += tuple(reserved.values())

t_MAIS      = r'\+'
t_MENOS     = r'-'
t_MULT      = r'\*'
t_DIV       = r'/'
t_ATRIB     = r':='
t_VIRG      = r','
t_PONTOEVIRG= r';'
t_DOISPONTOS= r':'
t_PONTO     = r'\.'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACK    = r'\['
t_RBRACK    = r'\]'
t_NEQ       = r'<>'
t_LT        = r'<'
t_LE        = r'<='
t_GT        = r'>'
t_GE        = r'>='
t_EQ        = r'='

t_ignore = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STR(t):
    r'(\'([^\'\\]|\\.)*\'|\"([^\"\\]|\\.)*\")'
    t.value = t.value[1:-1]  # remove as aspas
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    
def t_COMENTARIO(t):
    r'{.*'
    pass 

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

