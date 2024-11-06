# Address Code Generator

This is a simple Flask-based web application that generates Three Address Code (TAC) from C-like source code. The application uses **PLY (Python Lex-Yacc)** to perform lexical analysis and parsing, generating TAC for basic arithmetic and control flow expressions.

## Features

- Lexical analysis of source code
- Generation of Three Address Code (TAC) for arithmetic and control flow operations
- Web interface to input code and view the generated TAC

## Technologies Used

- **Flask**: Web framework to create the application.
- **PLY (Python Lex-Yacc)**: Used for lexical analysis and parsing to generate TAC.
- **HTML/CSS**: For creating the frontend interface.


## Sample Input 

int main() {
    int a = 5;
    int b = 10;
    int result = a + b;
    printf(result);
    return 0;
}



