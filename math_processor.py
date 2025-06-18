from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))
from sympy import symbols, Eq, solve, diff, integrate, limit
from voice_input import get_input
import os
from dotenv import load_dotenv
import wolframalpha
import requests
import traceback
import xml.etree.ElementTree as ET


load_dotenv()

# ====== Speak function =====
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

WOLFRAM_APP_ID = os.getenv("WOLF_IFYKYK")

# Initialize client if key is found
if WOLFRAM_APP_ID:
    wolfram_client = wolframalpha.Client(WOLFRAM_APP_ID)
else:
    print("⚠️ WolframAlpha API key not found. Some advanced queries may not work.")
    wolfram_client = None

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


# ======  explanation fallback =========

FALLBACK_EXPLANATIONS = {
    # Basic Science & Biology
    "dna": "DNA, or deoxyribonucleic acid, is a molecule that contains the genetic instructions used in the development and function of all living organisms.",
    "nucleus": "The nucleus is the central part of a cell that contains the cell's DNA and controls its activities, acting like the cell's command center.",
    "atom": "An atom is the smallest unit of matter that retains all of the chemical properties of an element. It's made of protons, neutrons, and electrons.",
    "chromosome": "A chromosome is a thread-like structure made of DNA and proteins that contains genetic information.",
    "mutation": "A mutation is a change in the DNA sequence that can affect how genes function.",
    "enzyme": "An enzyme is a protein that speeds up chemical reactions without being consumed.",
    "photosynthesis": "Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into oxygen and glucose.",
    "respiration": "Cellular respiration is the process cells use to convert glucose and oxygen into energy (ATP), carbon dioxide, and water.",
    "hormone": "A hormone is a chemical messenger produced by glands that regulate physiology and behavior.",
    "virus": "A virus is a microscopic infectious agent that replicates only inside the living cells of organisms.",
    "bacteria": "Bacteria are single-celled microorganisms that can exist independently or as parasites.",
    "ecosystem": "An ecosystem is a community of living organisms interacting with each other and their physical environment.",
    "acid": "An acid is a substance that releases hydrogen ions (H+) when dissolved in water.",
    "base": "A base is a substance that can accept hydrogen ions or release hydroxide ions (OH-) in solution.",
    "ph scale": "The pH scale measures how acidic or basic a solution is, ranging from 0 (acidic) to 14 (basic).",
    "chemical bond": "A chemical bond is the attraction between atoms that allows the formation of chemical substances.",
    "ionic bond": "An ionic bond forms when one atom donates an electron to another, creating positively and negatively charged ions.",
    "covalent bond": "A covalent bond forms when atoms share pairs of electrons.",
    "periodic table": "The periodic table organizes all known chemical elements by increasing atomic number and similar properties.",
    "element": "An element is a pure chemical substance consisting of one type of atom.",
    "compound": "A compound is a chemical substance formed from two or more elements chemically bonded.",
    "osmosis": "Osmosis is the movement of water across a semipermeable membrane from low to high solute concentration.",
    "antibody": "An antibody is a protein produced by the immune system to neutralize pathogens like bacteria and viruses.",
    "vaccine": "A vaccine stimulates the body's immune response to prepare it to fight specific infections.",

    # Mathematics & Physics
    "function": "In mathematics, a function is a relation that uniquely associates members of one set with members of another set. Think of it like a machine: you input a value, and the function gives you exactly one output.",
    "matrix": "A matrix is a rectangular array of numbers or expressions arranged in rows and columns, used in linear algebra to solve systems of equations and transform data.",
    "vector": "A vector is a quantity that has both magnitude and direction, commonly used in physics and math to represent forces or velocities.",
    "scalar": "A scalar is a quantity that only has magnitude, like temperature or mass, without any direction.",
    "equation": "An equation is a mathematical statement that asserts the equality of two expressions.",
    "theorem": "A theorem is a mathematical statement that has been proven to be true based on previously established statements.",
    "proof": "A proof is a logical argument demonstrating the truth of a theorem or statement.",
    "probability": "Probability measures how likely an event is to occur, expressed as a number between 0 (impossible) and 1 (certain).",
    "statistics": "Statistics is the study of data collection, analysis, interpretation, and presentation.",
    "momentum": "Momentum is the quantity of motion an object has, calculated as mass times velocity.",
    "inertia": "Inertia is the resistance of any physical object to any change in its velocity.",
    "work": "Work is done when a force causes an object to move in the direction of the force.",
    "power": "Power is the rate at which work is performed or energy is transferred.",
    "wave-particle duality": "Wave-particle duality is a concept in quantum physics stating particles can exhibit both wave-like and particle-like properties.",
    "entropy": "Entropy measures the disorder or randomness in a system; in thermodynamics, it tends to increase over time.",
    "coulomb": "A coulomb is the standard unit of electric charge in the International System of Units (SI).",
    "ohm": "An ohm is the unit of electrical resistance, symbolized by Ω.",
    "newton": "A newton is the SI unit of force, equivalent to the force required to accelerate one kilogram of mass by one meter per second squared.",
    "joule": "A joule is the unit of energy in the SI system, equal to the work done when a force of one newton moves an object one meter.",
    "acceleration due to gravity": "The acceleration due to gravity on Earth is approximately 9.8 meters per second squared, representing the rate objects fall near the surface.",

    # Programming & Computer Science
    "api": "An API (Application Programming Interface) is a set of rules that allows software applications to communicate with each other.",
    "variable": "A variable is a storage location identified by a name that holds a value which can be changed during program execution.",
    "class": "A class is a blueprint for creating objects, encapsulating data and behavior in object-oriented programming.",
    "object": "An object is an instance of a class containing data and methods that operate on that data.",
    "loop": "A loop is a programming construct that repeats a block of code while a condition is true.",
    "conditional": "A conditional statement executes different blocks of code based on whether a condition is true or false.",
    "recursion": "Recursion is a process where a function calls itself to solve smaller instances of a problem.",
    "algorithm": "An algorithm is a defined sequence of steps to solve a problem or perform a task.",
    "data structure": "A data structure is a way of organizing and storing data for efficient access and modification.",
    "array": "An array is a collection of elements identified by index or key, stored in contiguous memory.",
    "linked list": "A linked list is a data structure where each element points to the next, allowing efficient insertions and deletions.",
    "stack": "A stack is a data structure that follows Last In First Out (LIFO) principle.",
    "queue": "A queue is a data structure that follows First In First Out (FIFO) principle.",
    "hash table": "A hash table stores key-value pairs and allows for fast data retrieval based on the key.",
    "binary tree": "A binary tree is a hierarchical data structure in which each node has at most two children.",
    "compiler": "A compiler translates source code written in one programming language into another language, often machine code.",
    "interpreter": "An interpreter executes code line-by-line, translating it into machine instructions during runtime.",
    "syntax": "Syntax is the set of rules defining how code must be written to be correctly interpreted by a compiler or interpreter.",
    "debugging": "Debugging is the process of identifying, analyzing, and fixing errors in software code.",
    "framework": "A framework is a reusable set of libraries or tools that help build software applications more efficiently.",
    "library": "A library is a collection of pre-written code that developers can use to perform common tasks.",
    "api key": "An API key is a code passed in by computer programs to identify the calling program, user, or developer.",
    "cloud computing": "Cloud computing refers to storing and accessing data and programs over the internet instead of a local computer.",
    "machine learning": "Machine learning is a type of artificial intelligence where algorithms improve automatically through experience.",
    "neural network": "A neural network is a computing system inspired by biological neural networks, used in machine learning.",
    "database": "A database is an organized collection of data, generally stored and accessed electronically.",
    "sql": "SQL (Structured Query Language) is a programming language used to manage and manipulate databases.",
    "no sql": "NoSQL databases store data in formats other than traditional relational tables, useful for large-scale or flexible data.",

    # History & Culture
    "renaissance": "The Renaissance was a cultural movement spanning the 14th to 17th centuries, marked by a revival of art, science, and literature.",
    "industrial revolution": "The Industrial Revolution was the transition to new manufacturing processes from about 1760 to 1840, transforming economies and societies.",
    "cold war": "The Cold War was a period of political tension between the Soviet Union and the United States after World War II.",
    "world war i": "World War I was a global war centered in Europe from 1914 to 1918, involving many of the world's great powers.",
    "world war ii": "World War II was a global conflict from 1939 to 1945, involving most of the world's countries in two opposing military alliances.",
    "democracy": "Democracy is a system of government where citizens exercise power by voting.",
    "dictatorship": "A dictatorship is a government ruled by one person or a small group with absolute power.",
    "revolution": "A revolution is a rapid and fundamental change in political power or organizational structure.",
    "constitution": "A constitution is a set of fundamental principles or established precedents according to which a state or organization is governed.",
    "civil rights": "Civil rights are the rights of citizens to political and social freedom and equality.",
    "capitalism": "Capitalism is an economic system based on private ownership and free markets.",
    "socialism": "Socialism is an economic and political system where the means of production are owned and regulated by the community.",
    "feudalism": "Feudalism was a medieval European social system where land was held in exchange for service or labor.",
    "empire": "An empire is a large political unit or state, usually under a single leader, that controls many territories or peoples.",

    # Philosophy & General Concepts
    "ethics": "Ethics is the branch of philosophy dealing with moral principles that govern a person's behavior.",
    "logic": "Logic is the study of reasoning, including the rules of valid inference and argument.",
    "existentialism": "Existentialism is a philosophical movement focusing on individual freedom, choice, and the meaning of life.",
    "metaphysics": "Metaphysics is the branch of philosophy concerned with the nature of existence and reality.",
    "epistemology": "Epistemology studies the nature and scope of knowledge and belief.",
    "free will": "Free will is the ability to choose between different possible courses of action unimpeded.",
    "determinism": "Determinism is the philosophical idea that all events are determined completely by previously existing causes.",
    "consciousness": "Consciousness is the state of being aware of and able to think and perceive.",
    "happiness": "Happiness is a state of well-being and contentment.",
    "justice": "Justice is the concept of moral rightness based on ethics, law, fairness, and equity.",

    # Technology & Everyday Concepts
    "internet": "The internet is a global network connecting millions of private, public, academic, business, and government networks.",
    "wifi": "WiFi is a technology that allows devices to connect to the internet wirelessly using radio waves.",
    "smartphone": "A smartphone is a mobile phone with advanced computing capabilities and internet connectivity.",
    "software": "Software is a collection of instructions or programs that tell a computer what to do.",
    "hardware": "Hardware refers to the physical components of a computer or electronic system.",
    "battery": "A battery stores chemical energy and converts it into electrical energy to power devices.",
    "gps": "GPS is a satellite-based system that provides location and time information anywhere on Earth.",
    "encryption": "Encryption is the process of encoding information to prevent unauthorized access.",
    "password": "A password is a secret word or phrase used to authenticate a user’s identity.",
    "cloud": "Cloud computing provides computing services over the internet, such as storage and processing power.",
    "email": "Email is a method of exchanging digital messages over the internet.",
    "social media": "Social media are platforms that enable users to create and share content or participate in social networking.",
    "ai": "Artificial Intelligence is the simulation of human intelligence processes by machines, especially computer systems.",
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
    if not WOLFRAM_APP_ID:
        return "⚠️ WolframAlpha API key not found."

    url = "http://api.wolframalpha.com/v2/query"
    params = {
        "input": question,
        "appid": WOLFRAM_APP_ID,
        "format": "plaintext",
        "output": "XML"
    }

    try:
        print(f"🔍 Querying WolframAlpha with: {question}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        # Check for error in response
        error = root.find(".//error")
        if error is not None:
            return "❌ WolframAlpha returned an error for this query."

        # Extract plaintext results from pods
        for pod in root.findall(".//pod"):
            title = pod.attrib.get("title", "").lower()
            if title in ["result", "definition", "value", "decimal approximation"]:
                plaintext = pod.find(".//plaintext")
                if plaintext is not None and plaintext.text:
                    return plaintext.text.strip()

        # If no "result" pod found, return first pod's plaintext
        first_plaintext = root.find(".//pod/subpod/plaintext")
        if first_plaintext is not None and first_plaintext.text:
            return first_plaintext.text.strip()

        return "❓ Couldn't find a readable answer from WolframAlpha."

    except requests.exceptions.RequestException as e:
        return f"⚠️ Network or API error: {e}"
    except ET.ParseError:
        return "⚠️ Failed to parse WolframAlpha response."


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


def handle_math_and_science_mode(memory_logger):
    print("=== Math & Subject Assistant ===")
    print("Please select a mode!:")
    print("  - 'math' : math questions (simple or advanced) :Note use solve, simplify when solving for x")
    print("  - 'subject' : biology, chemistry, physics, history, programming")
    print("Say or 'exit' anytime to leave.\n")

    while True:
        mode = get_input("Select mode ('math'/'subject') or 'exit': ")

        if mode == "exit":
            speak("📤 Exiting Math & Science Assistant...")
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

    fallback_trigger_phrases = [
        "no results",
        "couldn't find",
        "did not understand",
        "error",
        "didn't catch",
        "no information",
        "not found",
        "unknown"
    ]

    while True:
        question = get_input(
            "Ask your question about any subject (or say 'back' to main menu, 'exit' to quit): "
        ).strip()

        if question.lower() == 'back':
            print("🔁 Returning to main mode selection...\n")
            break
        if question.lower() == 'exit':
            print("📤 Exiting Math & Science Assistant...")
            return

        # Try to match subject by scanning for known keywords
        subject_matches = {}
        for subject, keywords in WOLFRAM_KEYWORDS.items():
            match_count = sum(1 for keyword in keywords if keyword in question.lower())
            if match_count > 0:
                subject_matches[subject] = match_count

        if not subject_matches:
            print("🤖 Hmm, I'm not sure what subject you're referring to.")
            print("👉 Try asking more clearly, like 'What is DNA?' or 'Explain Newton's laws.'")
            print("📘 Tip: Mention words like 'cell', 'loop', 'war', 'force', etc.\n")
            continue

        # Choose subject with the most matched keywords
        subject = max(subject_matches, key=subject_matches.get)

        if subject == "biology":
            result = handle_biology_question(question)
        elif subject == "chemistry":
            result = handle_chemistry_question(question)
        elif subject == "physics":
            result = handle_physics_question(question)
        elif subject == "history":
            result = handle_history_question(question)
        elif subject == "programming":
            result = handle_programming_question(question)
        else:
            result = "⚠️ Cannot understand the subject you are trying to reach."

        # Improved fallback logic
        result_lower = result.lower()

        # Check if fallback should trigger: only if result contains fallback triggers AND does NOT have good keywords
        if any(trigger in result_lower for trigger in fallback_trigger_phrases) and not (
            "noun" in result_lower or "definition" in result_lower or "result" in result_lower
        ):
            # Try to find an educational fallback explanation matching keywords in the question
            for keyword, explanation in FALLBACK_EXPLANATIONS.items():
                if keyword in question.lower():
                    result = f"📘 Educational Insight:\n{explanation}"
                    break

        print(f"\n🧠 Result:\n{result}\n")
        memory_logger.log_interaction(
            f"{subject.capitalize()} Q: {question}",
            f"{subject.capitalize()} A: {result}"
        )
