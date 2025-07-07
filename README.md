# Compilador Fortall

## 1. INTRODUÇÃO

Este documento apresenta detalhes da implementação do trabalho final de Compiladores, como a gramática criada, os passos para instalação das ferramentas para a execução do código e detalhes na implementação realizada para a linguagem Fortall. A linguagem possui comandos de declaração, atribuição, leitura, escrita, estrutura condicional, laços de repetição e expressões aritméticas e lógicas. O compilador foi implementado em Python 3.9+, utilizando as bibliotecas PLY (Python Lex-Yacc) para análise léxica e sintática.

---

## 2. GRAMÁTICA DA LINGUAGEM FORTALL

A linguagem Fortall implementada no trabalho segue a seguinte gramática, escrita na notação EBNF:

```ebnf
prog        = "programa" id ";" [ declaracoes ] "inicio" lista_comandos "fim" "." ;

declaracoes = "var" lista_ids ":" tipo ";" { lista_ids ":" tipo ";" } ;

lista_ids   = id { "," id } ;

tipo        = "inteiro" | "logico" ;

lista_comandos = comando ";" { comando ";" } ;

comando     = atribuicao
           | leitura
           | escrita
           | composto
           | condicional
           | repeticao ;

atribuicao  = id ":=" expr ;

leitura     = "ler" "(" lista_ids ")" | "ler" [ "(" lista_ids ")" ] ;

escrita     = "escrever" "(" stringvar { "," stringvar } ")" | "escrever" [ "(" stringvar { "," stringvar } ")" ] ;

composto    = "inicio" lista_comandos "fim" ";" ;

condicional = "se" exprLogico "então" comando [ "senao" comando ] ;

repeticao   = "enquanto" exprLogico "faca" comando ;

expr        = fator expr_tail ;

expr_tail   = "+" fator expr_tail
           | "-" fator expr_tail
           | "*" fator expr_tail
           | "/" fator expr_tail
           | ;

fator = "-" fator
     | "(" expr ")"
     | id
     | num ;

exprLogico  = expr "<" expr
           | expr "<=" expr
           | expr ">" expr
           | expr ">=" expr
           | expr "=" expr
           | expr "<>" expr
           | id ;

stringvar = str | expr ;
```

---

## 3. INSTALAÇÃO E EXECUÇÃO

### 3.1 Requisitos

- Python 3.9+
- PLY (Python Lex-Yacc)

### 3.2 Passos de instalação

```bash
git clone https://github.com/dbseitenfus/fortall-compiler
```

### 3.3 Execução

```bash
cd fortall-compiler
python main.py
```

---

## 4. IMPLEMENTAÇÃO

O projeto foi dividido em três arquivos principais: main, lexer e parser. A linguagem escolhida foi Python, devido à sua facilidade de implementação e pela existência de bibliotecas auxiliares que facilitaram o processo de desenvolvimento. Embora tenham sido separados os processos de análise sintática e análise semântica, as duas implementações estão no mesmo arquivo para facilitar o processo de criação de ambas. A análise léxica e sintática foram desenvolvidas com a utilização da biblioteca PLY.

O arquivo `main.py` é responsável por chamar as funções responsáveis por todo processo. Ele lê o arquivo de entrada, chama a função `parse()` que realiza a análise sintática (chamando o analisador léxico) e retorna uma AST. Posteriormente, ele chama a função `executar()` passando como argumento a AST, onde ocorre a análise semântica.

### 4.1 Analisador Léxico 

#### 4.1.1 Tokens

O conjunto de tokens reconhecidos pela linguagem são:

- **Identificadores e literais**: ID, NUM, STR  
- **Operadores**: MAIS (+), MENOS (-), MULT (*), DIV (/), ATRIB (:=)  
- **Delimitadores e símbolos**: VIRG (,), PONTOEVIRG (;), DOISPONTOS (:), PONTO (.), LPAREN ((), RPAREN ()), LBRACK ([), RBRACK (])  
- **Operadores relacionais**: LT (<), LE (<=), GT (>), GE (>=), EQ (=), NEQ (<>)  

Os tokens retornados pelo lexer são instâncias da classe `LexToken`, que possui os seguintes atributos:

- `type`: nome do tipo do token reconhecido (ex: ID, NUM)
- `value`: conteúdo reconhecido (int, str etc.)
- `lineno`: número da linha
- `lexpos`: posição absoluta no texto

#### 4.1.2 Palavras Reservadas

```python
reserved = {
   'programa': 'PROGRAMA',
   'var': 'VAR',
   'inteiro': 'INTEIRO',
   ...
}
```

#### 4.1.3 Especificação de Tokens

Cada token é especificado com regex usando o prefixo `t_`.

#### 4.1.4 Ação no Reconhecimento

```python
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t
```

#### 4.1.5 Número de Linha

```python
def t_newline(t): 
    r'\n+' 
    t.lexer.lineno += len(t.value)
```

#### 4.1.6 Comentários

Comentários `{ ... }` são ignorados. Comentários entre tokens não são aceitos.

#### 4.1.7 Tratamento de Erros Léxicos

```python
def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)
```

#### 4.1.8 Identificação de ID's

Verifica se o identificador está entre as palavras reservadas:

```python
t.type = reserved.get(t.value, 'ID')
```

---

### 4.2 Analisador Sintático

Utiliza o módulo YACC do PLY. Constrói a AST e utiliza análise LR (shift-reduce).

#### 4.2.1 Definição da Gramática

Exemplo:

```python
def p_expression_plus(p): 
    'expressão: expressão MAIS termo' 
    p[0] = p[1] + p[3]
```

#### 4.2.2 Construção da AST

Com classes como `Program`, `Bloco`, `Atrib`, etc.

#### 4.2.3 Tratamento de Erros Sintáticos

```python
def p_error(p):
    print(f"Erro de sintaxe na linha {p.lineno}: token '{p.value}'")
```

---

### 4.3 Análise Semântica

#### 4.3.1 Verificação de Tipos

- Verifica se variáveis foram declaradas
- Verifica compatibilidade de tipos nas atribuições
- Garante que operações aritméticas sejam entre inteiros
- Garante que comparações sejam entre tipos compatíveis
- `se` e `enquanto` avaliam expressões lógicas (com `0` ou `1`)

#### 4.3.2 Tabela de Símbolos

`symbol_table`: mapeia identificadores para tipos  
`mem`: armazena valores de variáveis

#### 4.3.3 Detecção de Erros Semânticos

Erros são tratados com `raise Exception()` e exibem mensagens explicativas.

---

## ✅ Conclusão

O compilador Fortall implementa as etapas tradicionais de compilação:

1. Análise Léxica  
2. Análise Sintática  
3. Construção de AST  
4. Análise Semântica  
5. Execução

Ele foi desenvolvido em Python com a biblioteca PLY e serve como base sólida para projetos didáticos de compiladores.
