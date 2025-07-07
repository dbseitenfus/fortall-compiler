import ply.yacc as yacc
from lexer import tokens


class Program:     
    def __init__(self, decls, commands):
        self.decls = decls
        self.commands = commands

class Atrib:
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

class Leitura:
    def __init__(self, vars):
        self.vars = vars

class Escrita:
    def __init__(self, valores):
        self.valores = valores

class Se:
    def __init__(self, cond, entao, senao=None):
        self.cond = cond
        self.entao = entao
        self.senao = senao

class Enquanto:
    def __init__(self, cond, corpo):
        self.cond = cond
        self.corpo = corpo

class Bloco:
    def __init__(self, comandos):
        self.comandos = comandos

class Num:
    def __init__(self, valor):
        self.valor = valor
        self.tipo = 'inteiro'

class Str:
    def __init__(self, valor):
        self.valor = valor
        self.tipo = 'string'

class Var:
    def __init__(self, nome):
        self.nome = nome
        self.tipo = None  # será preenchido na inferência

class BinOp:
    def __init__(self, op, esq, dir):
        self.op = op
        self.esq = esq
        self.dir = dir
        self.tipo = None

class UnOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
        self.tipo = None
        
precedence = (
    ('left', 'MAIS', 'MENOS'),
    ('left', 'MULT', 'DIV'),
    ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NEQ'),
    ('right', 'MENOSU') 
)

symbol_table = {}
mem = {}

# Regras de parsing
def p_prog(p):
    'prog : PROGRAMA ID PONTOEVIRG declaracoes_opt INICIO lista_comandos FIM PONTO'
    p[0] = Program(p[4], Bloco(p[6]))

def p_declaracoes_opt(p):
    '''declaracoes_opt : declaracoes
                       | empty'''
    p[0] = p[1] if p[1] is not None else []

def p_declaracoes(p):
    'declaracoes : VAR lista_ids DOISPONTOS tipo PONTOEVIRG declaracoes_rest'
    p[0] = p[2]
    for var in p[2]:
        if var in symbol_table:
            print(f"[Erro] Variável '{var}' já declarada")
        else:
            symbol_table[var] = p[4]
            mem[var] = 0

def p_declaracoes_rest(p):
    '''declaracoes_rest : lista_ids DOISPONTOS tipo PONTOEVIRG declaracoes_rest
                        | empty'''
    if len(p) > 2:
        for var in p[1]:
            if var in symbol_table:
                print(f"[Erro] Variável '{var}' já declarada")
            else:
                symbol_table[var] = p[3]
                mem[var] = 0
        p[0] = p[5]
    else:
        p[0] = []

def p_lista_ids(p):
    'lista_ids : ID lista_ids_rest'
    p[0] = [p[1]] + p[2]

def p_lista_ids_rest(p):
    '''lista_ids_rest : VIRG ID lista_ids_rest
                      | empty'''
    p[0] = [p[2]] + p[3] if len(p) > 2 else []

def p_tipo(p):
    '''tipo : INTEIRO
            | LOGICO'''
    p[0] = p[1]

def p_lista_comandos(p):
    '''lista_comandos : comando PONTOEVIRG lista_comandos
                      | comando PONTOEVIRG'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_comando(p):
    '''comando : atribuicao
               | leitura
               | escrita
               | composto
               | condicional
               | repeticao'''
    p[0] = p[1]

def p_atribuicao(p):
    'atribuicao : ID ATRIB expr'
    p[0] = Atrib(p[1], p[3])

def p_leitura(p):
    '''leitura : LER LPAREN lista_ids RPAREN
               | LER LBRACK LPAREN lista_ids RPAREN RBRACK'''
    p[0] = Leitura(p[3] if len(p) == 5 else p[4])

def p_escrita(p):
    '''escrita : ESCREVER LPAREN lista_stringvar RPAREN
               | ESCREVER LBRACK LPAREN lista_stringvar RPAREN RBRACK'''
    p[0] = Escrita(p[3] if len(p) == 5 else p[4])

def p_lista_stringvar(p):
    'lista_stringvar : stringvar lista_stringvar_rest'
    p[0] = [p[1]] + p[2]

def p_lista_stringvar_rest(p):
    '''lista_stringvar_rest : VIRG stringvar lista_stringvar_rest
                            | empty'''
    p[0] = [p[2]] + p[3] if len(p) == 4 else []

def p_stringvar(p):
    '''stringvar : STR
                 | expr'''
    if isinstance(p[1], str):
        p[0] = Str(p[1])
    else:
        p[0] = p[1]

def p_composto(p):
    'composto : INICIO lista_comandos FIM'
    p[0] = Bloco(p[2])

def p_condicional(p):
    '''condicional : SE exprLogico ENTAO comando
                   | SE exprLogico ENTAO comando SENAO comando'''
    if len(p) > 5:
        p[0] = Se(p[2], p[4], p[6])
    else:
        p[0] = Se(p[2], p[4])

def p_repeticao(p):
    'repeticao : ENQUANTO exprLogico FACA comando'
    p[0] = Enquanto(p[2], p[4])

def p_expr_binop(p):
    '''expr : expr MAIS expr
            | expr MENOS expr
            | expr MULT expr
            | expr DIV expr'''
    p[0] = BinOp(p[2], p[1], p[3])

def p_expr_unop(p):
    'expr : MENOS expr %prec MENOSU'
    p[0] = UnOp('-', p[2])

def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_expr_num(p):
    'expr : NUM'
    p[0] = Num(p[1])

def p_expr_id(p):
    'expr : ID'
    p[0] = Var(p[1])

def p_expr_str(p):
    'expr : STR'
    p[0] = Str(p[1])

def p_exprLogico_binop(p):
    '''exprLogico : expr LT expr
                  | expr LE expr
                  | expr GT expr
                  | expr GE expr
                  | expr EQ expr
                  | expr NEQ expr'''
    p[0] = BinOp(p[2], p[1], p[3])

def p_exprLogico_group(p):
    'exprLogico : LPAREN exprLogico RPAREN'
    p[0] = p[2]

def p_exprLogico_id(p):
    'exprLogico : ID'
    p[0] = Var(p[1])

def p_empty(p):
    'empty :'
    p[0] = []

def p_error(p):
    if p:
        print(f"Erro de sintaxe na linha {p.lineno}: token '{p.value}'")
    else:
        print("Erro de sintaxe: fim inesperado do arquivo")
    

parser = yacc.yacc()

# Execução da AST
def executar(node):
    if isinstance(node, Program):
        executar(node.commands)

    elif isinstance(node, Bloco):
        for cmd in node.comandos:
            executar(cmd)

    elif isinstance(node, Atrib):
        if node.var not in symbol_table:
            raise Exception(f"[Erro Semântico] Variável '{node.var}' não declarada")

        tipo_var = symbol_table[node.var]
        tipo_expr = inferir_tipo(node.expr)
        
        valor = avaliar(node.expr)
        

        if tipo_var != tipo_expr and not (tipo_var == 'logico' and (valor == 0 or valor == 1)):
            raise Exception(f"[Erro Semântico] Atribuição incompatível: '{tipo_var}' ← '{tipo_expr}'")

        
        mem[node.var] = valor

    elif isinstance(node, Leitura):
        for var in node.vars:
            if var not in symbol_table:
                print(f"[Erro Semântico] Variável '{var}' não declarada")

            tipo = symbol_table[var]
            entrada = input(f"Digite o valor de {var}: ")

            try:
                if tipo == 'inteiro':
                    mem[var] = int(entrada)
                elif tipo == 'logico':
                    if entrada.lower() in ['verdadeiro', 'true']:
                        mem[var] = True
                    elif entrada.lower() in ['falso', 'false']:
                        mem[var] = False
                    else:
                        raise Exception()
            except:
                raise Exception(f"[Erro Semântico] Valor inválido para tipo '{tipo}' em '{var}'")

    elif isinstance(node, Escrita):
        valores = [avaliar(v) for v in node.valores]
        print("Saída:", *valores)

    elif isinstance(node, Se):
        tipo_cond = inferir_tipo(node.cond)
        if tipo_cond != 'logico':
            raise Exception("[Erro Semântico] Condição do 'se' deve ser lógica")

        cond = avaliar(node.cond)
        if cond:
            executar(node.entao)
        elif node.senao:
            executar(node.senao)

    elif isinstance(node, Enquanto):
        tipo_cond = inferir_tipo(node.cond)
        if tipo_cond != 'logico':
            raise Exception("[Erro Semântico] Condição do 'enquanto' deve ser lógica")

        while avaliar(node.cond):
            executar(node.corpo)
            
def inferir_tipo(expr):
    if isinstance(expr, BinOp):
        tipo_esq = inferir_tipo(expr.esq)
        tipo_dir = inferir_tipo(expr.dir)

        if expr.op in ['+', '-', '*', '/']:
            if tipo_esq != 'inteiro' or tipo_dir != 'inteiro':
                raise Exception(f"[Erro Semântico] Operação '{expr.op}' requer operandos inteiros")
            return 'inteiro'

        elif expr.op in ['<', '>', '<=', '>=', '=', '<>']:
            if tipo_esq != tipo_dir:
                raise Exception(f"[Erro Semântico] Comparação entre tipos incompatíveis")
            return 'logico'

    elif isinstance(expr, UnOp):
        tipo = inferir_tipo(expr.expr)
        if tipo != 'inteiro':
            raise Exception(f"[Erro Semântico] Operador unário '{expr.op}' exige operando inteiro")
        return 'inteiro'

    elif isinstance(expr, Var):
        if expr.nome not in symbol_table:
            raise Exception(f"[Erro Semântico] Variável '{expr.nome}' não declarada")
        return symbol_table[expr.nome]

    elif isinstance(expr, Num):
        return 'inteiro'

    elif isinstance(expr, Str):
        return 'cadeia'  # útil só em Escrita

def avaliar(expr):
    if isinstance(expr, BinOp):
        a = avaliar(expr.esq)
        b = avaliar(expr.dir)

        if expr.op in ['+', '-', '*', '/']:
            if not isinstance(a, int) or not isinstance(b, int):
                raise Exception(f"[Erro Semântico] Operação '{expr.op}' requer operandos inteiros")
        elif expr.op in ['<', '>', '<=', '>=', '=', '<>']:
            if type(a) != type(b):
                raise Exception(f"[Erro Semântico] Comparação entre tipos incompatíveis")
        
        if expr.op == '+': return a + b
        if expr.op == '-': return a - b
        if expr.op == '*': return a * b
        if expr.op == '/': return a // b
        if expr.op == '<': return a < b
        if expr.op == '>': return a > b
        if expr.op == '<=': return a <= b
        if expr.op == '>=': return a >= b
        if expr.op == '=': return a == b
        if expr.op == '<>': return a != b

    elif isinstance(expr, UnOp):
        val = avaliar(expr.expr)
        return -val

    elif isinstance(expr, Var):
        if expr.nome not in symbol_table:
            raise Exception(f"[Erro Semântico] Variável '{expr.nome}' não declarada")
        return mem.get(expr.nome, 0)

    elif isinstance(expr, Num):
        return expr.valor

    elif isinstance(expr, Str):
        return expr.valor

# Funções auxiliares 
def print_symbol_table():
    print("Tabela de Símbolos:")
    for var, tipo in symbol_table.items():
        print(f"{var}: {tipo} = {mem.get(var, 'não inicializada')}")

def print_memory():
    print("Memória:")
    for var, valor in mem.items():
        print(f"{var}: {valor}")

# Impressão da AST
def print_ast(node, indent=0):
    prefix = '  ' * indent
    if isinstance(node, Program):
        print(f"{prefix}Program")
        print(f"{prefix}  Decls:")
        for d in node.decls:
            print(f"{prefix}    {d}")
        print(f"{prefix}  Commands:")
        print_ast(node.commands, indent + 1)

    elif isinstance(node, Bloco):
        print(f"{prefix}Bloco")
        for cmd in node.comandos:
            print_ast(cmd, indent + 1)

    elif isinstance(node, Atrib):
        print(f"{prefix}Atrib({node.var})")
        print_ast(node.expr, indent + 1)

    elif isinstance(node, Leitura):
        print(f"{prefix}Leitura: {node.vars}")

    elif isinstance(node, Escrita):
        print(f"{prefix}Escrita:")
        for v in node.valores:
            print_ast(v, indent + 1)

    elif isinstance(node, Se):
        print(f"{prefix}Se")
        print(f"{prefix}  Cond:")
        print_ast(node.cond, indent + 2)
        print(f"{prefix}  Entao:")
        print_ast(node.entao, indent + 2)
        if node.senao:
            print(f"{prefix}  Senao:")
            print_ast(node.senao, indent + 2)

    elif isinstance(node, Enquanto):
        print(f"{prefix}Enquanto")
        print(f"{prefix}  Cond:")
        print_ast(node.cond, indent + 2)
        print(f"{prefix}  Corpo:")
        print_ast(node.corpo, indent + 2)

    elif isinstance(node, BinOp):
        print(f"{prefix}BinOp({node.op})")
        print_ast(node.esq, indent + 1)
        print_ast(node.dir, indent + 1)

    elif isinstance(node, UnOp):
        print(f"{prefix}UnOp({node.op})")
        print_ast(node.expr, indent + 1)

    elif isinstance(node, Var):
        print(f"{prefix}Var({node.nome})")

    elif isinstance(node, Num):
        print(f"{prefix}Num({node.valor})")

    elif isinstance(node, Str):
        print(f"{prefix}Str(\"{node.valor}\")")