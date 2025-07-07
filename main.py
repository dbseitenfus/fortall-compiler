from lexer import lexer
from parser_1 import *

with open("teste.fortall") as f:
    source = f.read()

ast = parser.parse(source, lexer=lexer)
executar(ast)