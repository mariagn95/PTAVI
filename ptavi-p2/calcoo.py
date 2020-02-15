#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys


class Calculadora:
    def __init__(self, op1, op2):
        self.num1 = op1
        self.num2 = op2

    def plus(self):
        return self.num1 + self.num2

    def minus(self):
        return self.num1 - self.num2


if __name__ == "__main__":

    try:
        num1 = int(sys.argv[1])
        type_operation = sys.argv[2]
        num2 = int(sys.argv[3])
    except ValueError:
        sys.exit("Error: Non numerical parameters")

    calculo = Calculadora(num1, num2)

    if type_operation == "suma":
        result = calculo.plus()
    elif type_operation == "resta":
        result = calculo.minus()
    else:
        sys.exit('Erro: La operación sólo puede ser sumar o restar.')

    print(result)
