import re
import requests
import matplotlib.pyplot as plt
import numpy as np
import uuid
import os
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from sympy import Expr, Rational
from sympy import (
    symbols, Eq, solve, diff, integrate, limit, simplify,
    pretty, sympify, Rational
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor
)
from sympy.core.expr import Expr
from dotenv import load_dotenv
from fallback_explanations import handle_science_question_advanced

# === Setup ===
load_dotenv()
WOLFRAM_APP_ID = os.getenv("WOLF_IFYKYK")

GRAPH_DIR = "static/graphs"
os.makedirs(GRAPH_DIR, exist_ok=True)

transformations = standard_transformations + (implicit_multiplication_application, convert_xor)

# === Helpers ===
def format_number(val, fraction_mode=False):
    if fraction_mode:
        if isinstance(val, Rational):
            return str(val)
        return str(Rational(val).limit_denominator())
    else:
        if val == int(val):
            return str(int(val))
        return f"{val:.6f}".rstrip("0").rstrip(".")


# Math multiplication helper
def fix_implicit_multiplication(expr_str: str) -> str:
    """
    Replace 'number space number' with 'number*number'
    Example: '23 7' -> '23*7'
    """
    import re
    return re.sub(r'(\d)\s+(\d)', r'\1*\2', expr_str)

def parse_fraction_input(expr_str: str):
    """Convert mixed numbers (like 2 3/4) to Rational"""
    mixed_number_re = re.compile(r'(\d+)\s+(\d+)/(\d+)')


    def convert_mixed(match):
        whole, num, den = map(int, match.groups())
        return str(Rational(whole * den + num, den))
    return mixed_number_re.sub(convert_mixed, expr_str)

# === Wolfram Alpha Query ===
def query_wolframalpha(question: str) -> str:
    """Fallback for complex queries using Wolfram Alpha"""
    url = "http://api.wolframalpha.com/v2/query"
    params = {"input": question, "appid": WOLFRAM_APP_ID, "format": "plaintext"}
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.text
    except Exception as e:
        return f"⚠️ Wolfram Alpha error: {e}"

# === Step-by-step arithmetic solver  ===
def step_by_step_arithmetic_full(expr_str: str, fraction_mode=False) -> str:
    """
    True step-by-step arithmetic solver.
    Handles addition, subtraction, multiplication, division, powers, and fractions.
    """
    try:
        # 1️⃣ Fix implicit multiplication
        expr_str = fix_implicit_multiplication(expr_str)
        # 2️⃣ Convert mixed fractions (like 2 3/4 -> Rational)
        expr_str = parse_fraction_input(expr_str)
        # 3️⃣ Parse into SymPy expression WITHOUT auto-evaluation
        expr = parse_expr(expr_str, transformations=transformations, evaluate=False)

        steps = [f"🟢 Step 1: Original expression\n   {expr_str}"]

        def walk(e: Expr) -> str:
            # Rational
            if isinstance(e, Rational):
                return format_number(e, fraction_mode)
            # Atomic numbers
            if e.is_Number:
                return format_number(e, fraction_mode)
            # Addition/Subtraction
            if e.is_Add:
                values = [walk(arg) for arg in e.args]
                result = format_number(e.evalf(), fraction_mode)
                steps.append(f"➕ Add/Subtract: {' + '.join(values)} = {result}")
                return result
            # Multiplication
            if e.is_Mul:
                if any(arg.is_Add for arg in e.args):
                    steps.append(f"🔹 Distributive property might apply: {e}")
                values = [walk(arg) for arg in e.args]
                result = format_number(e.evalf(), fraction_mode)
                steps.append(f"✖️ Multiply: {' × '.join(values)} = {result}")
                return result
            # Power
            if e.is_Pow:
                base_v = walk(e.base)
                exp_v = walk(e.exp)
                result = format_number(e.evalf(), fraction_mode)
                if e.exp == Rational(1, 2):
                    steps.append(f"🟢 Square root: √{base_v} = {result}")
                else:
                    steps.append(f"🧮 Power: {base_v}^{exp_v} = {result}")
                return result
            # Division
            num, denom = e.as_numer_denom()
            if denom != 1:
                num_v = walk(num)
                denom_v = walk(denom)
                result = format_number(e.evalf(), fraction_mode)
                steps.append(f"➗ Divide: {num_v} ÷ {denom_v} = {result}")
                return result
            # Fallback
            result = format_number(e.evalf(), fraction_mode)
            steps.append(f"🔹 Simplified: {result}")
            return result

        final_result = walk(expr)
        steps.append(f"🎯 Final Answer:\n   {final_result}")
        return "\n\n".join(steps)

    except Exception as e:
        return f"⚠️ Unable to process arithmetic: {e}"



# === Equation solver ===
def step_by_step_solve(equation_str: str) -> str:
    try:
        equation_str = parse_fraction_input(equation_str)
        left, right = equation_str.split('=')
        left_expr = parse_expr(left, transformations=transformations)
        right_expr = parse_expr(right, transformations=transformations)
        equation = Eq(left_expr, right_expr)
        var = list(equation.free_symbols)[0]

        rearranged = left_expr - right_expr
        simplified = simplify(rearranged)
        solutions = solve(simplified, var)
        formatted = [format_number(s.evalf()) for s in solutions]

        return "\n\n".join([
            f"🟢 Step 1: Original Equation\n   {pretty(equation)}",
            f"🔄 Step 2: Move all terms to one side\n   {pretty(rearranged)} = 0",
            f"🧹 Step 3: Simplify\n   {pretty(simplified)} = 0",
            f"🎯 Final Answer:\n   {var} = {', '.join(formatted)}"
        ])
    except Exception as e:
        return f"⚠️ Couldn't solve equation: {e}"

# === Graphing with Matplotlib + SymPy ===
def plot_expression(expr_str: str) -> str:
    try:
        expr_str = expr_str.lower().replace('plot', '').replace('^', '**').strip()
        x = symbols('x')
        expr = parse_expr(expr_str, transformations=transformations)
        x_vals = np.linspace(-10, 10, 400)
        y_vals = [float(expr.subs(x, v)) for v in x_vals]

        filename = f"{uuid.uuid4().hex}.png"
        path = os.path.join(GRAPH_DIR, filename)
        plt.plot(x_vals, y_vals)
        plt.grid(True)
        plt.savefig(path)
        plt.close()
        return f"🖼 [View graph]({path})"
    except Exception as e:
        return f"⚠️ Graph error: {e}"

# === Unified math handler ===
def handle_math_question_advanced(question: str) -> str:
    q = question.strip().replace("^", "**")  # normalize powers

    # Detect simple arithmetic (numbers, operators, parentheses only)
    if re.fullmatch(r'[\d\s\+\-\*\/\(\)]+', q):
        return step_by_step_arithmetic_full(q)

    try:
        # Derivative
        if q.lower().startswith("diff "):
            expr = parse_expr(question[5:], transformations=transformations)
            var = list(expr.free_symbols)[0]
            return pretty(diff(expr, var))

        # Integral
        if q.lower().startswith("integrate "):
            expr = parse_expr(question[9:], transformations=transformations)
            var = list(expr.free_symbols)[0]
            return pretty(integrate(expr, var)) + " + C"

        # Limit
        if q.lower().startswith("limit "):
            match = re.search(r'limit (.+) as (.+)->(.+)', q.lower())
            if match:
                expr, var, pt = match.groups()
                return str(limit(parse_expr(expr), symbols(var), sympify(pt)))

        # Equation solving
        if "=" in q:
            return step_by_step_solve(question)

        # Graphing
        if "plot" in q.lower():
            return plot_expression(question)

        # Complex arithmetic that slipped through
        expr = parse_expr(q, transformations=transformations)
        if not expr.free_symbols:
            return step_by_step_arithmetic_full(question)

        # Algebraic simplification
        return f"🧮 Simplified:\n   {pretty(simplify(expr))}"

    except Exception:
        # Wolfram Alpha fallback for anything SymPy can't handle
        return query_wolframalpha(question)


# === Science handler ===
def handle_science_question(question: str, memory_logger=None) -> str:
    return handle_science_question_advanced(question, memory_logger)

# === Unified query processor ===
def process_query(user_input: str, mode: str = None, memory_logger=None) -> str:
    if mode == "math":
        return handle_math_question_advanced(user_input)
    if mode == "science":
        return handle_science_question(user_input, memory_logger)
    return "⚠️ Unknown mode."
