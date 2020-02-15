#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import csv
import calcoohija


if len(sys.argv) <= 2:

    with open(sys.argv[1], 'r') as csvfile:
        operationreader = csv.reader(csvfile)
        for operation in operationreader:
            type_operation = operation[0]
            result = int(operation[1])

            for num in operation[2:]:
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
    print("Error. Try again: python3 calcplusplus.py fichero.txt")
