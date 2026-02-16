import re
import requests
import matplotlib.pyplot as plt
import numpy as np
import uuid
import os

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
    Conversational, scaffolded arithmetic tutor with reflective thought bubbles.
    """

    try:
        expr_str = fix_implicit_multiplication(expr_str)
        expr_str = parse_fraction_input(expr_str)
        expr = parse_expr(expr_str, transformations=transformations, evaluate=False)

        steps = []

        # -----------------------------------------
        # Messaging Helpers
        # -----------------------------------------
        def add_step(msg):
            steps.append(msg)

        def thought(msg):
            steps.append(f"💭 Pause & Think: {msg}")

        def coach(msg):
            steps.append(f"🧠 Strategy: {msg}")

        # -----------------------------------------
        # Intro
        # -----------------------------------------
        add_step(f"🟢 Let's solve this together:\n   {expr_str}")
        add_step("We’ll move slowly and make sure each idea actually makes sense.")

        # -----------------------------------------
        # Utility: Place-Value Decomposition
        # -----------------------------------------
        def decompose_number(n):
            parts = []
            place = 1
            while n > 0:
                digit = n % 10
                if digit != 0:
                    parts.append(digit * place)
                n //= 10
                place *= 10
            return list(reversed(parts))

        # -----------------------------------------
        # Multiplication Handler
        # -----------------------------------------
        def handle_multiplication(e):
            add_step(f"\n🔎 We see multiplication → {e}")
            thought("Can any of these numbers be broken into easier parts?")

            # Distribution case
            if any(arg.is_Add for arg in e.args):
                coach("When multiplication touches parentheses, we distribute.")

                thought("What does multiplying across a sum remind you of?")

                distributed_terms = []
                for arg in e.args:
                    if arg.is_Add:
                        other_factors = [a for a in e.args if a != arg]
                        for term in arg.args:
                            new_expr = term
                            for factor in other_factors:
                                new_expr *= factor
                            distributed_terms.append(new_expr)

                expanded = sum(distributed_terms)

                add_step(f"🪜 After distributing:\n   {expanded}")
                thought("Why does distributing preserve the total value?")
                return walk(expanded)

            # Pure numbers
            if all(arg.is_Number for arg in e.args):
                nums = [int(a) for a in e.args]

                # Exactly 2 numbers
                if len(nums) == 2:
                    a, b = nums
                    digits_a = len(str(abs(a)))
                    digits_b = len(str(abs(b)))

                    # Single-digit × single-digit
                    if digits_a == 1 and digits_b == 1:
                        coach("Both are single digits — direct multiplication.")
                        result = a * b
                        add_step(f"   {a} × {b} = {result}")
                        thought("Does that match any ideas that you already know?")
                        return format_number(result, fraction_mode)

                    # Multi-digit × single-digit
                    if digits_a > 1 and digits_b == 1:
                        coach("Break the larger number using place value.")

                        parts = decompose_number(a)
                        add_step(f"   {a} = {' + '.join(map(str, parts))}")

                        thought("Why is breaking by place value helpful here?")

                        partials = []
                        for p in parts:
                            val = p * b
                            partials.append(val)
                            add_step(f"   {p} × {b} = {val}")

                        total = sum(partials)
                        add_step(f"➕ Add partial products:")
                        add_step(f"   {' + '.join(map(str, partials))} = {total}")

                        thought("Why does adding these give the answer we want?")
                        return format_number(total, fraction_mode)

                    # Multi-digit × multi-digit
                    coach("Break BOTH numbers (area model thinking).")

                    parts_a = decompose_number(a)
                    parts_b = decompose_number(b)

                    add_step(f"   {a} = {' + '.join(map(str, parts_a))}")
                    add_step(f"   {b} = {' + '.join(map(str, parts_b))}")

                    thought("How many smaller multiplications will we create?")

                    partials = []
                    for pa in parts_a:
                        for pb in parts_b:
                            val = pa * pb
                            partials.append(val)
                            add_step(f"   {pa} × {pb} = {val}")

                    total = sum(partials)
                    add_step("➕ Add all partial products:")
                    add_step(f"   {' + '.join(map(str, partials))} = {total}")

                    thought("Does this result seem reasonable compared to jus estimating it")
                    return format_number(total, fraction_mode)

                # More than 2 numbers
                coach("Multiply step-by-step from left to right.")
                current = nums[0]

                for n in nums[1:]:
                    thought(f"What happens when we multiply {current} by {n}?")
                    add_step(f"   {current} × {n}")
                    current *= n

                add_step(f"✖️ Final result = {current}")
                return format_number(current, fraction_mode)

            # Mixed symbolic
            coach("Evaluate each factor first, then combine.")
            values = [walk(arg) for arg in e.args]
            result = format_number(e.evalf(), fraction_mode)
            add_step(f"✖️ Combine → {' × '.join(values)} = {result}")
            return result

        # -----------------------------------------
        # Addition Handler
        # -----------------------------------------
        def handle_addition(e):
            add_step(f"\n🔎 I see addition/subtraction → {e}")
            thought("Should we evaluate any parts first before combining?")

            values = [walk(arg) for arg in e.args]
            result = format_number(e.evalf(), fraction_mode)

            add_step(f"➕ Combine:")
            add_step(f"   {' + '.join(values)} = {result}")

            thought("Is the final number larger or smaller than the biggest addend?")
            return result

        # -----------------------------------------
        # Power Handler
        # -----------------------------------------
        def handle_power(e):
            base_v = walk(e.base)
            exp_v = walk(e.exp)

            add_step(f"\n🔎 Exponent detected → {base_v}^{exp_v}")
            thought("What does an exponent represent conceptually?")

            if e.exp.is_Integer and e.exp > 1:
                coach(f"Multiply {base_v} by itself {e.exp} times.")
                result = format_number(e.evalf(), fraction_mode)
                add_step(f"   Result = {result}")
                return result

            if e.exp.is_Number and e.exp < 0:
                coach("Negative exponent → take reciprocal.")
                result = format_number(e.evalf(), fraction_mode)
                add_step(f"   Result = {result}")
                return result

            if e.exp == Rational(1, 2):
                coach("Exponent of 1/2 means square root.")
                result = format_number(e.evalf(), fraction_mode)
                add_step(f"   √{base_v} = {result}")
                return result

            result = format_number(e.evalf(), fraction_mode)
            add_step(f"   Result = {result}")
            return result

        # -----------------------------------------
        # Recursive Walker
        # -----------------------------------------
        def walk(e: Expr) -> str:

            if isinstance(e, Rational):
                return format_number(e, fraction_mode)

            if e.is_Number:
                return format_number(e, fraction_mode)

            if e.is_Add:
                return handle_addition(e)

            if e.is_Mul:
                return handle_multiplication(e)

            if e.is_Pow:
                return handle_power(e)

            num, denom = e.as_numer_denom()
            if denom != 1:
                add_step("\n🔎 Division detected.")
                thought("Division can be thought of as splitting or fractions.")

                num_v = walk(num)
                denom_v = walk(denom)

                result = format_number(e.evalf(), fraction_mode)
                add_step(f"➗ {num_v} ÷ {denom_v} = {result}")

                thought("Does this quotient make sense in size?")
                return result

            result = format_number(e.evalf(), fraction_mode)
            add_step(f"🔹 Simplified result = {result}")
            return result

        final_result = walk(expr)

        add_step("\n🎯 Final Answer:")
        add_step(f"   {final_result}")

        thought("Could you explain one of the steps in your own words?")
        add_step("That’s how you lock understanding in.")

        return "\n".join(steps)

    except Exception as e:
        return f"⚠️ Unable to process your math problem: {e}"


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
            f"🟢 Step 1: Original Equation\n   {pretty(equation)} which we want to evaluate is {formatted[0]}",
            f"🔄 Step 2: Move all terms to one side\n   {pretty(rearranged)} = 0",
            f"🧹 Step 3: Simplify\n   {pretty(simplified)} = 0",
            f"🎯 Final Answer:\n   {var} = {', '.join(formatted)} Now I want you to give it a try! "
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
