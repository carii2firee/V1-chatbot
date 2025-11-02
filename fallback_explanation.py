import re
from sympy import symbols, Eq, solve, diff, integrate, limit, simplify, pretty
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, \
    convert_xor


# --- Transformations for sympy parsing ---
transformations = standard_transformations + (implicit_multiplication_application, convert_xor)

# --- Expanded keyword sets for semantic matching ---
WOLFRAM_KEYWORDS = {
    "biology": ["cell", "cells", "dna", "rna", "photosynthesis", "organism", "evolution", "genetics", "enzyme",
                "protein", "neuron", "nucleus", "mitochondria"],
    "chemistry": ["atom", "molecule", "compound", "acid", "base", "reaction", "bond", "ion", "periodic", "solution",
                  "electron", "proton", "valence"],
    "physics": ["force", "mass", "velocity", "energy", "acceleration", "momentum", "gravity", "friction", "work",
                "wave", "light", "electricity", "thermodynamics", "magnetism"],
    "astronomy": ["planet", "star", "galaxy", "universe", "black hole", "comet", "asteroid", "orbit", "light year",
                  "nebula", "exoplanet"],
    "earth_science": ["rock", "volcano", "earthquake", "climate", "weather", "atmosphere", "ocean", "ecosystem",
                      "pollution", "river", "glacier"],
}

# ====== Fallback explanations =====
# --- Expanded Fallback Explanations for Science ---

FALLBACK_EXPLANATIONS = {
    # Biology
    "cell": "A cell is the basic structural and functional unit of all living organisms.",
    "dna": "DNA (deoxyribonucleic acid) carries genetic instructions for growth, development, and reproduction.",
    "rna": "RNA is a single-stranded molecule involved in coding, decoding, and expression of genes.",
    "photosynthesis": "Photosynthesis converts sunlight, carbon dioxide, and water into glucose and oxygen in plants.",
    "chlorophyll": "Chlorophyll is the green pigment in plants that absorbs light for photosynthesis.",
    "mitosis": "Mitosis is the process of cell division that produces two genetically identical daughter cells.",
    "meiosis": "Meiosis produces gametes (sperm and eggs) with half the number of chromosomes.",
    "enzyme": "An enzyme is a biological catalyst that speeds up chemical reactions in cells.",
    "protein": "Proteins are large biomolecules made of amino acids that perform most cellular functions.",
    "gene": "A gene is a sequence of DNA that contains instructions for making a specific protein.",
    "chromosome": "A chromosome is a thread-like structure of DNA that carries genetic information.",
    "evolution": "Evolution is the process by which species change over generations through natural selection.",
    "homeostasis": "Homeostasis is the maintenance of a stable internal environment in living organisms.",
    "neuron": "A neuron is a nerve cell that transmits electrical and chemical signals in the body.",
    "immune system": "The immune system defends the body against infections and foreign substances.",
    "bacteria": "Bacteria are single-celled microorganisms that can be beneficial or cause disease.",
    "virus": "A virus is a microscopic infectious agent that replicates only inside living host cells.",

    # Chemistry
    "atom": "An atom is the smallest unit of matter that retains the properties of an element.",
    "element": "An element is a pure substance made of only one type of atom.",
    "molecule": "A molecule is two or more atoms bonded together chemically.",
    "compound": "A compound is a substance formed when atoms of different elements bond in fixed ratios.",
    "ion": "An ion is an atom or molecule with an electric charge due to gain or loss of electrons.",
    "acid": "An acid is a substance that donates hydrogen ions (H+) in a solution.",
    "base": "A base is a substance that accepts hydrogen ions or releases hydroxide ions (OH−).",
    "ph": "pH measures how acidic or basic a solution is on a scale of 0 to 14.",
    "reaction": "A chemical reaction involves breaking and forming bonds to create new substances.",
    "catalyst": "A catalyst speeds up a chemical reaction without being consumed by it.",
    "periodic table": "The periodic table arranges chemical elements by atomic number and properties.",
    "bond": "A chemical bond is the force that holds atoms together in molecules and compounds.",
    "oxidation": "Oxidation is a reaction where an atom loses electrons, often involving oxygen.",
    "reduction": "Reduction is a reaction where an atom gains electrons.",
    "solution": "A solution is a homogeneous mixture of a solute dissolved in a solvent.",

    # Physics
    "force": "A force is a push or pull on an object that can change its motion.",
    "energy": "Energy is the capacity to do work or produce change, existing in many forms.",
    "mass": "Mass is the amount of matter in an object, measured in kilograms.",
    "velocity": "Velocity is the speed of something in a given direction.",
    "acceleration": "Acceleration is the rate at which velocity changes over time.",
    "momentum": "Momentum is the product of an object's mass and velocity.",
    "gravity": "Gravity is the force of attraction between all masses.",
    "friction": "Friction is the resistance that one surface encounters when moving over another.",
    "work": "In physics, work is done when a force moves an object through a distance.",
    "power": "Power is the rate at which work is done or energy is transferred.",
    "wave": "A wave is a disturbance that transfers energy through space or matter.",
    "sound": "Sound is a mechanical wave produced by vibrating objects and transmitted through a medium.",
    "light": "Light is electromagnetic radiation visible to the human eye.",
    "electricity": "Electricity is the flow of electric charge through a conductor.",
    "magnetism": "Magnetism is the force exerted by magnets when they attract or repel each other.",
    "quantum": "Quantum physics studies the behavior of matter and energy at the smallest scales.",
    "thermodynamics": "Thermodynamics deals with heat, work, temperature, and energy transformations.",

    # Astronomy
    "planet": "A planet is a celestial body that orbits a star and is massive enough to be nearly spherical.",
    "star": "A star is a massive, luminous ball of gas held together by gravity and powered by nuclear fusion.",
    "galaxy": "A galaxy is a huge collection of stars, gas, dust, and dark matter bound by gravity.",
    "universe": "The universe is all of space, time, matter, and energy that exists.",
    "black hole": "A black hole is a region in space where gravity is so strong that nothing, not even light, can escape.",
    "supernova": "A supernova is a powerful explosion that occurs when a massive star dies.",
    "light year": "A light-year is the distance that light travels in one year, about 9.46 trillion kilometers.",
    "orbit": "An orbit is the curved path an object takes around a star, planet, or moon due to gravity.",
    "comet": "A comet is an icy body that releases gas and dust, forming a glowing tail as it approaches the sun.",
    "asteroid": "An asteroid is a small rocky object orbiting the sun, mainly found in the asteroid belt.",

    # Earth & Environmental Science
    "rock": "A rock is a naturally occurring solid composed of minerals or mineraloids.",
    "mineral": "A mineral is a naturally occurring, inorganic solid with a specific chemical composition.",
    "volcano": "A volcano is an opening in Earth's crust through which molten rock and gases erupt.",
    "earthquake": "An earthquake is the shaking of Earth's surface caused by sudden movement of tectonic plates.",
    "plate tectonics": "Plate tectonics is the theory that Earth's outer shell is divided into plates that move over the mantle.",
    "climate": "Climate is the long-term pattern of temperature and precipitation in a region.",
    "weather": "Weather describes short-term atmospheric conditions like temperature, humidity, and precipitation.",
    "atmosphere": "The atmosphere is the layer of gases surrounding Earth.",
    "ocean": "An ocean is a large body of saltwater that covers most of Earth's surface.",
    "ecosystem": "An ecosystem is a community of living organisms interacting with their environment.",
    "pollution": "Pollution is the introduction of harmful substances or energy into the environment.",
    "greenhouse effect": "The greenhouse effect is the trapping of heat in Earth's atmosphere by greenhouse gases.",
    "renewable energy": "Renewable energy comes from sources that are naturally replenished, such as sunlight, wind, and water.",
    "carbon footprint": "A carbon footprint measures the total greenhouse gas emissions caused by an individual or organization.",
    "sustainability": "Sustainability means meeting present needs without compromising future generations' ability to meet theirs."
}


# --- Level 7: step-by-step multi-layer fallback explanation ----
def generate_science_explanation(keyword: str) -> str:
    """
    Return a rich, multi-step scientific explanation for a keyword.
    Splits explanation into logical steps and adds extra context.
    """
    explanation = FALLBACK_EXPLANATIONS.get(keyword.lower())
    if not explanation:
        return f"🔍 I know about '{keyword}' in general, but try specifying a more detailed concept."


    steps = [f"**Step 1: Definition** – {explanation}",
             f"**Step 2: Role / Function** – {keyword.capitalize()} plays an important role in science and everyday life.",
             f"**Step 3: Fun Fact / Context** – Did you know? {keyword.capitalize()} has interesting implications in biology, chemistry, or physics!"]

    # Step 1: Core definition

    # Step 2: Function / role in real world (if applicable)

    # Step 3: Fun fact or additional context

    return "\n".join(steps)


def detect_science_subject(question: str):
    """
    Detects science subject based on keywords in the question.
    Works with multi-word keywords.
    """
    cleaned = re.sub(r'[^a-z0-9\s]', '', question.lower())
    subject_scores = {}
    for subject, kws in WOLFRAM_KEYWORDS.items():
        count = 0
        for kw in kws:
            # Match multi-word keywords by simple substring check
            if kw.lower() in cleaned:
                count += 1
        if count > 0:
            subject_scores[subject] = count

    subject = max(subject_scores, key=subject_scores.get) if subject_scores else None
    return subject, cleaned


def handle_science_question_advanced(question: str, memory_logger=None) -> str:
    """
    Level 7 science question handler with multi-step fallback explanations.
    """
    subject, cleaned = detect_science_subject(question)

    # No keyword match
    if not subject:
        return "🤖 Try asking with more scientific terms like *photosynthesis*, *atom*, or *gravity*."

    # Placeholder for WolframAlpha query
    result = None  # query_wolframalpha(question)

    # Fallback if WolframAlpha fails
    fallback_hit = None
    if not result or any(err in result.lower() for err in ["no result", "error", "unknown", "not found"]):
        for keyword in sorted(FALLBACK_EXPLANATIONS.keys(), key=lambda x: -len(x)):
            # Match multi-word keywords by substring
            if keyword.lower() in cleaned:
                fallback_hit = keyword
                result = generate_science_explanation(keyword)
                break

    # Log interaction if applicable
    if memory_logger:
        memory_logger.log_interaction(
            question=f"[Science/{subject.capitalize()}] Q: {question}",
            response=f"A: {result}",
            tags=["science_level7", subject]
        )

    # If still nothing, gentle generic response
    if not result:
        result = "🤖 I couldn’t find a detailed answer, try rephrasing or giving more context."

    # Add fallback context
    if fallback_hit:
        result += f"\n\n🔎 (Matched fallback topic: **{fallback_hit}**)"

    return result




def handle_math_question_level7(expr_str: str) -> str:
    """
    Parse, simplify, differentiate, integrate, or solve math queries with steps.
    """
    expr_str = expr_str.strip().replace("^", "**")
    try:
        # Derivative
        if expr_str.lower().startswith("diff "):
            expr = parse_expr(expr_str[5:], transformations=transformations)
            var = list(expr.free_symbols)[0] if expr.free_symbols else symbols('x')
            derivative = diff(expr, var)
            return f"🟢 **Original:** {pretty(expr)}\n🧮 **Derivative w.r.t {var}:** {pretty(derivative)}"

        # Integral
        if expr_str.lower().startswith("integrate "):
            expr = parse_expr(expr_str[9:], transformations=transformations)
            var = list(expr.free_symbols)[0] if expr.free_symbols else symbols('x')
            integral = integrate(expr, var)
            return f"🟢 **Original:** {pretty(expr)}\n🧮 **Integral w.r.t {var}:** {pretty(integral)} + C"

        # Solve equations
        if "=" in expr_str:
            left, right = expr_str.split("=")
            equation = Eq(parse_expr(left, transformations=transformations),
                          parse_expr(right, transformations=transformations))
            var = list(equation.free_symbols)[0] if equation.free_symbols else symbols('x')
            sol = solve(equation, var)
            return f"🟢 **Equation:** {pretty(equation)}\n✅ **Solution:** {var} = {sol}"

        # Simplify arithmetic
        expr = parse_expr(expr_str, transformations=transformations)
        simplified = simplify(expr)
        return f"🧮 **Simplified:** {pretty(expr)} = {simplified}"

    except Exception as e:
        return f"⚠️ Could not process the expression: {e}"


# --- Unified Level 7 handler ---
def process_query_level7(user_input: str, mode: str = None, memory_logger=None) -> str:
    if not user_input.strip():
        return "⚠️ Please enter a valid question or expression."

    if mode == "science":
        return handle_science_question_advanced(user_input, memory_logger)
    elif mode == "math":
        return handle_math_question_level7(user_input)
    else:
        return "⚠️ Unknown mode. Use 'science' or 'math'."




