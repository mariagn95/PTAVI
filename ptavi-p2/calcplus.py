#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import csv
import calcoohija


if len(sys.argv) <= 2:

    fichero = open(sys.argv[1], 'r')

    for linea in fichero:
        type_operation = linea.split(",")[0]
        operandos = linea.split(",")[1:]
        result = int(operandos[0])

        for num in operandos[1:]:
            calculo = int(num)
            cuenta = calcoohija.CalculadoraHija(result, calculo)

            if type_operation == "suma":
                result = cuenta.plus()
            elif type_operation == "resta":
                result = cuenta.minus()
            elif type_operation == "multiplica":
                result = cuenta.mult()
            elif type_operation == "divide":
                result = cuenta.div()
            else:
                sys.exit('Error. Non numerical parameters')

        print(result)


else:
    print("Only supports one argument")
    print("Error. Try again: python3 calcplus.py fichero.txt")
