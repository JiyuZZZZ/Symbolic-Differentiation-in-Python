#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 15:02:46 2023

@author: zhangjiyu
"""
import math

def symbolic_differentiation(expr):
    def parse_tree(string):
        if string.find('(') == -1:
            return string
        
        elif string[0] == '(' and string[-1] == ')':
            string = string[1:-1]
        
        elif string[0:3] in ['sin', 'cos', 'exp', 'log']:
            left = string[0:3]
            right = parse_tree(string[3:])
            return [left, right]

        level = 0
        operators = []
        for i, char in enumerate(string):
            if char == '(':
                level += 1
            elif char == ')':
                level -= 1
            elif level == 0 and char in "+-*/^":
                operators.append((i, char))

        if not operators:
            return parse_tree(string)

        first_index, first = operators[0]
        left = parse_tree(string[:first_index])
        right = parse_tree(string[first_index + 1:])

        if len(operators) > 1:
            right = [first, right, parse_tree(string[operators[1][0] + 1:])]

        return [first, left, right]


    def differentiate_tree(parsed_expr):
        if isinstance(parsed_expr, str):
            return '1' if parsed_expr == 'x' else '0'
        
        op = parsed_expr[0]

        if op in ['+', '-']:
            left_diff = differentiate_tree(parsed_expr[1])
            right_diff = differentiate_tree(parsed_expr[2])
            return [op, left_diff, right_diff]
        elif op == '*':
            # 乘法规则（乘积法则）
            u = parsed_expr[1]
            v = parsed_expr[2]
            u_diff = differentiate_tree(u)
            v_diff = differentiate_tree(v)
            return ['+', ['*', u_diff, v], ['*', u, v_diff]]
        elif op == '/':
            # 除法规则（商法则）
            u = parsed_expr[1]
            v = parsed_expr[2]
            u_diff = differentiate_tree(u)
            v_diff = differentiate_tree(v)
            return ['/', ['-', ['*', u_diff, v], \
                          ['*', u, v_diff]], ['^', v, '2']]
        elif op == '^':
            # 幂运算规则（链式法则）
            base = parsed_expr[1]
            exponent = parsed_expr[2]
            a_diff = differentiate_tree(base)
            if isinstance(exponent, list):
                return ['*', ['*', exponent, \
                              ['^', base, ['-', exponent, '1']]],
                        a_diff]
            elif exponent.isdigit():
                b = str(int(exponent)-1)
                return ['*', exponent, ['^', base, b]]

        elif op == 'sin':
            # sin函数的微分
            a = differentiate_tree(parsed_expr[1])
            return ['*', a, ['cos', parsed_expr[1]]]
        elif op == 'cos':
            # cos函数的微分
            a = differentiate_tree(parsed_expr[1])
            return ['*', a, ['-', '0', ['sin', parsed_expr[1]]]]
        elif op == 'exp':
            # exp函数的微分
            a = differentiate_tree(parsed_expr[1])
            return ['*', a, ['exp', parsed_expr[1]]]
        elif op == 'log':
            # log函数的微分
            a = differentiate_tree(parsed_expr[1])
            return ['/', a, parsed_expr[1]]

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def calculate_simple_expression(lhs, operator, rhs=None):
        if rhs is None:  # 单参数数学函数
            if operator == 'exp':
                return str(math.exp(float(lhs)))
            elif operator == 'log':
                return str(math.log(float(lhs)))
            elif operator == 'sin':
                return str(math.sin(float(lhs)))
            elif operator == 'cos':
                return str(math.cos(float(lhs)))
        else:  # 常规二元运算
            if operator == '+':
                return str(float(lhs) + float(rhs))
            elif operator == '-':
                return str(float(lhs) - float(rhs))
            elif operator == '*':
                return str(float(lhs) * float(rhs))
            elif operator == '/':
                return str(float(lhs) / float(rhs))
            elif operator == '^':
                return str(float(lhs) ** float(rhs))

    def build_and_simplify_expression(node):
        if isinstance(node, list):
            operator = node[0]
            operands = [build_and_simplify_expression(child) for child in node[1:]]

            if all(is_number(op) for op in operands):
                if len(operands) == 1:  # 单参数数学函数
                    return calculate_simple_expression(operands[0], operator)
                else:  # 常规二元运算
                    return calculate_simple_expression(operands[0], operator, operands[1])
            
            if operator == '*':
                if '0' in operands:
                    return '0'
                elif '1' in operands:
                    operands = [op for op in operands if op != '1']
            elif operator == '+':
                operands = [op for op in operands if op != '0']
            elif operator == '-':
                if operands[0] == '0':
                    result = '(' + '-' + operands[1] + ')'
                    return result
                if operands[1] == '0':
                    return operands[0]
            elif operator == '/':
                if operands[1] == '1':
                    return operands[0]
                if operands[0] == '0':
                    return str(float('0'))
            elif operator == '^':
                if operands[0] == '1':
                    return str(float('1'))
                if operands[0] == '0':
                    return str(float('0'))
                if operands[1] == '0':
                    return str(float('1'))
                if operands[1] == '1':
                    return operands[0]
            elif operator == 'exp':
                if operands[0] == '0':
                    return str(float('1'))
            elif operator == 'log':
                if operands[0] == '1':
                    return str(float('0'))

            if len(operands) == 1:
                if operator in '+-*/^':
                    return operands[0]
                else:
                    if operands[0].isdigit() or operands[0].isalpha():
                        return f"({operator}({operands[0]}))"
                    else:
                        return f"({operator}{operands[0]})"
            else:
                return f"({' '.join([operator.join(operands)])})"
        else:
            return node

    def brackets_delete(expression):
        if expression[1:4] in ['sin', 'cos', 'exp', 'log']:
            expression_new = expression[1:-1]
            return expression_new
        else:
            return expression
        
    parsed_expr = parse_tree(expr)
    diff_tree = differentiate_tree(parsed_expr)
    expression = build_and_simplify_expression(diff_tree)
    new_expression = brackets_delete(expression)
    return new_expression

expr = "cos(((x^2)*(x^2))+x*exp(x))"
expr = "((2*x)-(x^2)/2)"
result = symbolic_differentiation(expr)
print(result)