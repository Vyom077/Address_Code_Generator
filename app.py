from flask import Flask, render_template, request
import ply.lex as lex
import ply.yacc as yacc

# Initialize Flask application
app = Flask(__name__)

# Token definitions for lexical analysis
tokens = (
    'ID', 'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMI', 'COMMA', 'ASSIGN', 'PRINT',
    'INT', 'RETURN'
)

# Regular expressions for tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI = r';'
t_COMMA = r','
t_ASSIGN = r'='
t_ignore = ' \t'

# Token rules for identifiers, numbers, keywords
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if t.value == 'int':
        t.type = 'INT'
    elif t.value == 'printf':
        t.type = 'PRINT'
    elif t.value == 'return':
        t.type = 'RETURN'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# Precedence and associativity of operators
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

# TAC generation helpers
temp_count = 0
label_count = 1

def new_temp():
    global temp_count
    temp_name = f"t{temp_count}"
    temp_count += 1
    return temp_name

def new_label():
    global label_count
    label_name = f"L{label_count}"
    label_count += 1
    return label_name

# Parsing rules and TAC generation
tac_code = []

def p_program(p):
    '''program : function_list'''
    p[0] = p[1]

def p_function_list(p):
    '''function_list : function_list function
                     | function'''
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]

def p_function(p):
    '''function : INT ID LPAREN params RPAREN LBRACE declarations statements RBRACE'''
    function_label = new_label()
    p[0] = [f"{function_label}:"] + p[4] + p[7]

def p_params(p):
    '''params : param_list
              | empty'''
    p[0] = p[1] if p[1] else []

def p_param_list(p):
    '''param_list : param_list COMMA param
                  | param'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_param(p):
    '''param : INT ID'''
    p[0] = f"param {p[2]}"

def p_declarations(p):
    '''declarations : declarations declaration
                    | empty'''
    p[0] = p[1] if p[1] else []

def p_declaration(p):
    '''declaration : INT ID ASSIGN expression SEMI
                   | INT ID SEMI'''
    if len(p) == 6:
        tac_code.append(f"{p[2]} = {p[4]}")
    else:
        tac_code.append(f"{p[2]} = 0")  # Default initialization to 0

def p_statements(p):
    '''statements : statements statement
                  | empty'''
    p[0] = p[1] if p[1] else []

def p_statement_expr(p):
    '''statement : ID ASSIGN expression SEMI
                | PRINT LPAREN expression RPAREN SEMI'''
    if p[1] == 'printf':
        tac_code.append(f"param {p[3]}")
        tac_code.append(f"call printf, 1")
    else:
        tac_code.append(f"{p[1]} = {p[3]}")

def p_statement_return(p):
    '''statement : RETURN expression SEMI'''
    tac_code.append(f"RETURN {p[2]}")

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    temp_left = p[1]
    temp_right = p[3]
    temp = new_temp()
    tac_code.append(f"{temp} = {temp_left} {p[2]} {temp_right}")
    p[0] = temp

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER'''
    temp = new_temp()
    tac_code.append(f"{temp} = {p[1]}")
    p[0] = temp

def p_expression_id(p):
    '''expression : ID'''
    p[0] = p[1]

def p_expression_call(p):
    '''expression : ID LPAREN arguments RPAREN'''
    temp = new_temp()
    for arg in p[3]:
        tac_code.append(f"param {arg}")
    tac_code.append(f"call {p[1]}, {len(p[3])}")
    p[0] = temp

def p_arguments(p):
    '''arguments : arguments COMMA expression
                | expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle code submission and generate TAC
@app.route('/generate', methods=['POST'])
def generate_tac():
    if request.method == 'POST':
        code = request.form['code']
        tac_code.clear()
        parser.parse(code)
        return render_template('result.html', tac_code=tac_code)

if __name__ == '__main__':
    app.run(debug=True)
