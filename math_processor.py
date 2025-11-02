import os
import xml.etree.ElementTree as ET
import re
import requests
from sympy import Rational
from fallback_explanations import FALLBACK_EXPLANATIONS, handle_science_question_advanced

from dotenv import load_dotenv
from sympy import (
    symbols, Eq, solve, diff, integrate, limit, simplify, pretty
)
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

# --- Setup ---
load_dotenv()
WOLFRAM_APP_ID = os.getenv("WOLF_IFYKYK")
print(f"[INIT] WOLFRAM_APP_ID Loaded: {bool(WOLFRAM_APP_ID)}")

transformations = standard_transformations + (
    implicit_multiplication_application, convert_xor
)

# --- WolframAlpha Query ---
def query_wolframalpha(question: str) -> str:
    if not WOLFRAM_APP_ID:
        return "⚠️ WolframAlpha API key not found."

    url = "https://api.wolframalpha.com/v2/query"
    params = {
        "input": question,
        "appid": WOLFRAM_APP_ID,
        "format": "plaintext",
        "output": "XML"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        if root.find(".//error") is not None:
            return "❌ WolframAlpha returned an error for this query."

        # Prefer pods with useful info
        for pod in root.findall(".//pod"):
            title = pod.attrib.get("title", "").lower()
            if title in ["result", "definition", "value", "decimal approximation", "indefinite integral"]:
                plaintext = pod.find(".//plaintext")
                if plaintext is not None and plaintext.text:
                    return plaintext.text.strip()

        # fallback to first plaintext pod
        fallback = root.find(".//pod/subpod/plaintext")
        if fallback is not None and fallback.text:
            return fallback.text.strip()

        return "❓ Couldn't find a readable answer from WolframAlpha."
    except Exception as e:
        return f"⚠️ Error querying WolframAlpha: {e}"




    # =================== parse various fractions ==========
def parse_fraction_input(expr_str: str):
    """
    Converts mixed numbers (like '1 1/6') into proper fractions for calculation.
    """
    import re

    # Find all mixed numbers (digit space fraction)
    def convert_mixed(match):
        whole = int(match.group(1))
        numerator = int(match.group(2))
        denominator = int(match.group(3))
        return str(Rational(whole * denominator + numerator, denominator))

    pattern = re.compile(r'(\d+)\s+(\d+)/(\d+)')
    converted_expr = pattern.sub(convert_mixed, expr_str)
    return converted_expr

# --- Step-by-step Solver for math equations ---
def step_by_step_solve(equation_str: str) -> str:
    try:
        # Convert mixed numbers in the equation
        equation_str = parse_fraction_input(equation_str)

        left, right = equation_str.split('=')
        left_expr = parse_expr(left.strip(), transformations=transformations)
        right_expr = parse_expr(right.strip(), transformations=transformations)
        equation = Eq(left_expr, right_expr)

        variables = list(equation.free_symbols)
        var = variables[0] if variables else symbols('x')

        rearranged = left_expr - right_expr
        simplified = simplify(rearranged)
        solutions = solve(simplified, var)

        steps = [
            f"🟢 **Step 1: Original Equation**\n   {pretty(equation)}",
            f"🔄 **Step 2: Move all terms to one side**\n   {pretty(rearranged)} = 0",
            f"🧹 **Step 3: Simplify the expression**\n   {pretty(simplified)} = 0",
            f"✅ **Step 4: Solve for {var}**\n   {', '.join(map(str, solutions))}",
            f"🎯 **Final Answer:**\n   {var} = {', '.join(map(str, solutions))}"
        ]

        return "\n\n".join(steps)

    except Exception as e:
        return f"⚠️ Couldn't solve step-by-step: {e}"


def step_by_step_arithmetic(expr_str: str) -> str:
    try:
        original_expr_str = expr_str.strip()

        # --- Convert mixed numbers like '1 1/6' into proper fractions ---
        expr_str = parse_fraction_input(original_expr_str)

        # Parse the expression after conversion
        expr = parse_expr(expr_str, transformations=transformations)
        result = simplify(expr)

        steps = [
            f"🟢 **Step 1: Original expression**\n   {original_expr_str}",
            f"➕ **Step 2: Convert mixed numbers**\n   {expr_str}",
            f"🧮 **Step 3: Evaluate**\n   {expr_str} = {result}",
            f"🎯 **Final Answer:**\n   {result}"
        ]
        return "\n\n".join(steps)

    except Exception as e:
        return f"⚠️ Unable to process simple arithmetic: {e}"

# --- Advanced math processing ---
def handle_math_question_advanced(question: str) -> str:
    """
    Advanced math processor for AI companion.
    Supports algebra, calculus (derivatives, integrals, limits), and systems of equations.
    Provides step-by-step reasoning.
    """
    original_input = question.strip()
    q = original_input.lower().replace('^', '**')

    try:
        # --- Derivatives ---
        if q.startswith('diff '):
            expr_str = original_input[5:].strip()  # remove 'diff '
            expr = parse_expr(expr_str, transformations=transformations)
            variables = list(expr.free_symbols)
            var = variables[0] if variables else symbols('x')
            derivative = diff(expr, var)
            steps = [
                f"🟢 **Step 1: Original expression**\n   {pretty(expr)}",
                f"🧮 **Step 2: Differentiate w.r.t {var}**\n   d/d{var} {pretty(expr)} = {pretty(derivative)}",
                f"🎯 **Final Answer:**\n   {pretty(derivative)}"
            ]
            return "\n\n".join(steps)

        # --- Integrals ---
        if q.startswith('integrate '):
            expr_str = original_input[9:].strip()  # remove 'integrate '
            expr = parse_expr(expr_str, transformations=transformations)
            variables = list(expr.free_symbols)
            var = variables[0] if variables else symbols('x')
            integral = integrate(expr, var)
            steps = [
                f"🟢 **Step 1: Original expression**\n   {pretty(expr)}",
                f"🧮 **Step 2: Integrate w.r.t {var}**\n   ∫ {pretty(expr)} d{var} = {pretty(integral)}",
                f"🎯 **Final Answer:**\n   {pretty(integral)} + C"
            ]
            return "\n\n".join(steps)

        # --- Limits ---
        if q.startswith('limit '):
            # Expect format: limit f(x) as x->a
            import re
            match = re.search(r'limit (.+) as (.+)->(.+)', q)
            if match:
                expr_str, var_str, point_str = match.groups()
                expr = parse_expr(expr_str, transformations=transformations)
                var = symbols(var_str.strip())
                point = parse_expr(point_str.strip(), transformations=transformations)
                lim = limit(expr, var, point)
                steps = [
                    f"🟢 **Step 1: Original expression**\n   {pretty(expr)}",
                    f"🧮 **Step 2: Evaluate limit as {var} -> {point}**\n   {pretty(lim)}",
                    f"🎯 **Final Answer:**\n   {lim}"
                ]
                return "\n\n".join(steps)
            else:
                return "⚠️ Limit query not understood. Use format: 'limit f(x) as x->a'"

        # --- Equations ---
        if '=' in q:
            return step_by_step_solve(original_input)

        # --- Systems of equations (comma-separated) ---
        if ',' in q:
            eqs = [parse_expr(eq.strip(), transformations=transformations) for eq in q.split(',')]
            vars_set = set().union(*[eq.free_symbols for eq in eqs])
            solutions = solve(eqs, vars_set)
            return f"🧮 **System of Equations Solution:**\n   {solutions}"

        # --- Simple arithmetic / simplification ---
        expr = parse_expr(q, transformations=transformations)
        if expr.free_symbols == set():
            return step_by_step_arithmetic(original_input)
        simplified = simplify(expr)
        return f"🧮 Simplified Expression:\n  {pretty(expr)} = {simplified}"

    except Exception as e:
        return f"⚠️ Unable to process expression: {e}"

# --- Science keywords for subject detection ---
WOLFRAM_KEYWORDS = {
    "biology": ["cell", "dna", "rna", "photosynthesis", "organism", "evolution", "genetics", "enzyme", "protein", "neuron"],
    "chemistry": ["atom", "molecule", "compound", "acid", "base", "reaction", "bond", "ion", "periodic", "solution"],
    "physics": ["force", "mass", "velocity", "energy", "acceleration", "momentum", "gravity", "friction", "work", "wave", "light", "electricity", "thermodynamics"],
    "astronomy": ["planet", "star", "galaxy", "universe", "black hole", "comet", "asteroid", "orbit", "light year"],
    "earth_science": ["rock", "volcano", "earthquake", "climate", "weather", "atmosphere", "ocean", "ecosystem", "pollution"],
}

def handle_science_question(question: str, memory_logger=None) -> str:
    lower = question.lower().strip()
    print(f"[DEBUG] Received science question: {lower}")

    # --- Normalize question ---
    cleaned = re.sub(r'[^a-z0-9\s]', '', lower)

    # --- Detect subject by keyword presence ---
    subject_scores = {
        subject: sum(1 for kw in kws if re.search(rf'\b{re.escape(kw)}s?\b', cleaned))
        for subject, kws in WOLFRAM_KEYWORDS.items()
    }
    subject_scores = {k: v for k, v in subject_scores.items() if v > 0}

    if not subject_scores:
        return "🤖 Try a more specific science question — for example, mention terms like *photosynthesis*, *atom*, or *gravity*."

    subject = max(subject_scores, key=subject_scores.get)

    # --- Query WolframAlpha ---
    result = query_wolframalpha(question)

    fallback_hit = None
    # --- Level 7 fallback if WolframAlpha fails ---
    if not result or any(err in result.lower() for err in ["no result", "error", "unknown", "not found"]):
        # Delegate entirely to the Level 7 advanced handler
        result = handle_science_question_advanced(question, memory_logger=memory_logger)
        return result

    # --- Log interaction (if applicable) ---
    if memory_logger:
        memory_logger.log_interaction(
            question=f"[Science/{subject.capitalize()}] Q: {question}",
            response=f"A: {result}",
            tags=["science_mode", subject]
        )

    # --- Generic message if still no result ---
    if not result:
        result = "🤖 I couldn’t find a detailed explanation, but try rephrasing your question or including more context."

    # --- Add context line if fallback was used ---
    if fallback_hit:
        result += f"\n\n🔍 (Matched fallback topic: **{fallback_hit}**)"

    return result

# --- Unified handler for math or science queries ---

def process_query(user_input: str, mode: str = None, memory_logger=None) -> str:
    print(f"[DEBUG] memory_logger type: {type(memory_logger)}")
    user_input = user_input.strip()

    if not user_input:
        return "⚠️ Please enter a valid question or expression."

    try:
        if mode == 'science':
            return handle_science_question(user_input, memory_logger)

        elif mode == 'math':
            return handle_math_question_advanced(user_input)

        else:
            return "⚠️ Unknown mode specified. Please use 'math' or 'science'."

    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"
