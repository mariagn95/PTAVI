#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import calcoo


class CalculadoraHija(calcoo.Calculadora):

    def mult(self):
        return self.num1 * self.num2

    def div(self):
        try:
            return self.num1 / self.num2
        except ZeroDivisionError:
            return("Division by zero is not allowed.")


if __name__ == "__main__":
    try:
        num1 = int(sys.argv[1])
        type_operation = sys.argv[2]
        num2 = int(sys.argv[3])
    except ValueError:
        sys.exit("Error: Non numerical parameters")

    calculo = CalculadoraHija(num1, num2)

    if type_operation == "suma":
        result = calculo.plus()
    elif type_operation == "resta":
        result = calculo.minus()
    elif type_operation == "multiplica":
        result = calculo.mult()
    elif type_operation == "divide":
        result = calculo.div()
    else:
        sys.exit('Error. Try again: python3 calcoohija.py op1 operacion op2')

    print(result)
