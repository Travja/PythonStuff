# calculator
from math import *
import parser
import time

def evaluate(expr):
    expression = parser.expr(expr).compile()
    return eval(expression)

switch = {
    0: lambda: print("Good-bye"), # This won't actually be called.
    1: lambda: print(evaluate(input("Enter an expression: "))),
    2: lambda: print("This is still a work in progress.")
}

def do_menu():
    print(" ---------------" )
    print("How do you want to use this calculator?")
    print("1) Evaluate an expression")
    print("2) Solve a matrix")
    print("\n0) Exit")
    
    selection = -1
    while (selection == -1):
        try:
            selection = int(input("Enter your selection: "))
        except ValueError:
            selection = -1
            
        if not switch.get(selection, False):
            selection = -1

    print()
    return selection

def main_loop():
    while True:
        sel = do_menu()
        if sel == 0:
            break
        else:
            switch.get(sel)()
            time.sleep(1.5)
            
main_loop()
            
