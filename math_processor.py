from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
from sympy import symbols, Eq, solve, diff, integrate, limit
from voice_input import get_input
import os
from dotenv import load_dotenv
import wolframalpha
load_dotenv()

wolfram_api_key = os.getenv("WOLF_IFYKYK")

if not wolfram_api_key:
    raise ValueError("⚠️ Missing WOLF_IFYKYK in .env file!")

wolfram_client = wolframalpha.Client(wolfram_api_key)



WOLFRAM_KEYWORDS = {
    "biology": {
        "cell", "mitochondria", "nucleus", "photosynthesis", "heart", "dna", "protein", "respiration",
        "enzyme", "organism", "reproduction", "genetics", "ecosystem", "muscle", "neuron"
    },
    "chemistry": {
        "atom", "molecule", "reaction", "bond", "acid", "base", "ph", "chemical", "periodic",
        "electrons", "ions", "compound", "solution", "organic", "inorganic"
    },
    "physics": {
        "force", "energy", "velocity", "acceleration", "gravity", "mass", "motion", "quantum",
        "wave", "light", "current", "voltage", "resistance", "thermodynamics"
    },
    "history": {
        "war", "revolution", "president", "empire", "battle", "civilization", "treaty", "monarch",
        "dynasty", "event", "leader", "colony", "constitution", "movement"
    },
    "programming": {
        "python", "java", "loop", "function", "variable", "algorithm", "code", "compile",
        "syntax", "bug", "array", "object", "class", "recursion"
    }
}

def contains_keywords(text, mode):
    text = text.lower()
    keywords = WOLFRAM_KEYWORDS.get(mode, set())
    return any(keyword in text.lower() for keyword in keywords)

def suggest_keywords(mode):
    keywords = WOLFRAM_KEYWORDS.get(mode, set())
    if keywords:
        examples = ', '.join(sorted(list(keywords))[:6])
        return f"🧪 Try including terms like: {examples}..."
    return "❓ No suggestions available."

def display_available_words():
    print("/n 📚 Available keywords for your desired mode.")
    for mode, keywords in WOLFRAM_KEYWORDS.items():
        sample = ', '.join(soreted(keywords)[:8])
        print(f"  🔹 {mode.capitalize()}: {sample}")


# ============ Handler functions =======
def query_wolframalpha(question):
    try:
        res = wolfram_client.query(question)

        if not res.results:
            return "❓ Couldn't understand the input. Please try again."

        results = list(res.results)
        if not results or not results[0].text:
            return "❓ No readable output found. Try something simpler."

        return results[0].text

    except Exception as e:
        return f"⚠️ WolframAlpha error: {e}"

def handle_biology_question(question):
    if contains_keywords(question, "biology"):
        return query_wolframalpha(question)
    return "❓ I dont understand please be more specific." + suggest_keywords("biology")

def handle_chemistry_question(question):
    if contains_keywords(question, "chemistry"):
        return query_wolframalpha(question)
    return "❓ I dont understand please be more specific." + suggest_keywords("chemistry")

def handle_physics_question(question):
    if contains_keywords(question, "physics"):
        return query_wolframalpha(question)
    return "❓ I dont understand please be more specific." + suggest_keywords("physics")

def handle_history_question(question):
    if contains_keywords(question, "history"):
        return query_wolframalpha(question)
    return "❓ I dont understand please be more specific." + suggest_keywords("history")

def handle_programming_question(question):
    if contains_keywords(question, "programming"):
        return query_wolframalpha(question)
    return "❓ I dont understand please be more specific." + suggest_keywords("programming")

def handle_math_question_simple(question):
    return query_wolframalpha(question)

def handle_math_question_advanced(question):
    try:
        question = question.replace('^', '**')


        if '=' in question:
            left_side, right_side = question.split('=', 1)
            left_expr = parse_expr(left_side.strip(), transformations=transformations)
            right_expr = parse_expr(right_side.strip(), transformations=transformations)
            equation = Eq(left_expr, right_expr)

            vars_in_eq = list(equation.free_symbols)
            if not vars_in_eq:
                return "⚠️ No variables found to solve for."

            sol = solve(equation, vars_in_eq[0])
            var_name = str(vars_in_eq[0])
            return f"solve({question}) for {var_name} -> {sol}"


        q_lower = question.lower()

        if q_lower.startswith('diff'):
            inside = question[question.find('(') + 1:question.rfind(')')]
            parts = inside.split(',')
            if len(parts) == 2:
                func = parse_expr(parts[0].strip(), transformations=transformations)
                var = symbols(parts[1].strip())
                result = diff(func, var)
                return f"diff({func}, {var}) -> {result}"
            else:
                return "⚠️ Provide diff as diff(expression, variable)."

        elif q_lower.startswith('integrate'):
            inside = question[question.find('(') + 1:question.rfind(')')]
            parts = inside.split(',')
            if len(parts) == 2:
                func = parse_expr(parts[0].strip(), transformations=transformations)
                var = symbols(parts[1].strip())
                result = integrate(func, var)
                return f"integrate({func}, {var}) -> {result}"
            else:
                return "⚠️ Provide integrate as integrate(expression, variable)."

        elif q_lower.startswith('limit'):
            inside = question[question.find('(') + 1:question.rfind(')')]
            parts = inside.split(',')
            if len(parts) == 3:
                func = parse_expr(parts[0].strip(), transformations=transformations)
                var = symbols(parts[1].strip())
                point = parse_expr(parts[2].strip(), transformations=transformations)
                result = limit(func, var, point)
                return f"limit({func}, {var}, {point}) -> {result}"
            else:
                return "⚠️ Provide limit as limit(expression, variable, point)."


        expr = parse_expr(question, transformations=transformations)
        simplified = expr.simplify()
        return f"Simplified: {simplified}"

    except Exception as e:
        return f"⚠️ Sympy error: {e}"


def handle_math_and_science_mode(user_name, memory_logger):
    print("=== Math & Science Assistant ===")
    print("Please select a mode!:")
    print("  - 'math' : math questions (simple or advanced)")
    print("  - 'subject' : biology, chemistry, physics, history, programming")
    print("Say or type 'exit' anytime to leave.\n")

    while True:
        mode = get_input("Select mode ('math'/'subject') or 'exit': ")

        if mode == "exit":
            print("📤 Exiting Math & Science Assistant...")
            break

        if mode not in ['math', 'subject']:
            print("⚠️ I can't understand you, please enter 'math' or 'subject'.")
            continue

        if mode == 'math':
            handle_math_mode(memory_logger)

        elif mode == 'subject':
            handle_subject_mode(memory_logger)


def handle_math_mode(memory_logger):
    while True:
        math_mode = get_input("Please select math mode ('simple'/'advanced') or 'back': ")

        if math_mode == 'back':
            print("🔁 Returning to main mode selection...\n")
            break
        if math_mode not in ['simple', 'advanced']:
            print("⚠️ Invalid math mode. Please enter 'simple' or 'advanced'.")
            continue

        while True:
            question = get_input(f"➗ {math_mode.capitalize()} Math Input: ")

            if question.lower() == 'back':
                print("🔁 Switching math mode...\n")
                break
            if question.lower() == 'exit':
                print("📤 Exiting Math & Science Assistant...")
                return

            if math_mode == 'simple':
                result = handle_math_question_simple(question)
            else:
                result = handle_math_question_advanced(question)

            print(f"\n🧠 Result:\n{result}\n")
            memory_logger.log_interaction(
                f"{math_mode.capitalize()} Math Q: {question}",
                f"{math_mode.capitalize()} Math A: {result}"
            )


def handle_subject_mode(memory_logger):
    print("✅ Subject help mode activated.")
    print("Available subjects: biology, chemistry, physics, history, programming")

    while True:
        question = get_input(
            "Ask your question starting with subject name (or say 'back' to main menu, 'exit' to quit): ")

        if question.lower() == 'back':
            print("🔁 Returning to main mode selection...\n")
            break
        if question.lower() == 'exit':
            print("📤 Exiting Math & Science Assistant...")
            return

        # Detect subject prefix
        subject = None
        question_clean = question
        for sub in ["biology", "chemistry", "physics", "history", "programming"]:
            if question.lower().startswith(sub):
                subject = sub
                question_clean = question[len(sub):].strip()
                break

        if not subject:
            print(
                "⚠️ Please start your question with one of the subjects: biology, chemistry, physics, history, programming.")
            continue

        # Call appropriate handler
        if subject == "biology":
            result = handle_biology_question(question_clean)
        elif subject == "chemistry":
            result = handle_chemistry_question(question_clean)
        elif subject == "physics":
            result = handle_physics_question(question_clean)
        elif subject == "history":
            result = handle_history_question(question_clean)
        elif subject == "programming":
            result = handle_programming_question(question_clean)
        else:
            result = "⚠️ Cannot understand the subject you are trying to reach."

        print(f"\n🧠 Result:\n{result}\n")
        memory_logger.log_interaction(
            f"{subject.capitalize()} Q: {question_clean}",
            f"{subject.capitalize()} A: {result}"
        )