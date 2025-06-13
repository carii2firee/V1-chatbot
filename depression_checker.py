
from voice_input import get_input

def handle_depression_screening(user_name, memory_logger):
    print("\n=== PHQ-9 Depression Screening ===")
    questions = [
        "Little interest or pleasure in doing things?",
        "Feeling down, depressed, or hopeless?",
        "Trouble falling or staying asleep, or sleeping too much?",
        "Feeling tired or having little energy?",
        "Poor appetite or overeating?",
        "Feeling bad about yourself — or that you are a failure or have let yourself or your family down?",
        "Trouble concentrating on things, such as reading the newspaper or watching television?",
        "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving a lot more than usual?",
        "Thoughts that you would be better off dead or of hurting yourself in some way?"
    ]
    print(
        "\nPlease answer each question based on the past 2 weeks:\n"
        "0 = Not at all\n1 = Several days\n2 = More than half the days\n3 = Nearly every day"
    )

    total_score = 0
    responses = []

    valid_answers = {'zero': '0', 'one': '1', 'two': '2', 'three': '3'}

    for idx, question in enumerate(questions, 1):
        while True:
            print(f"\n{idx}. {question}")
            answer = get_input("Your answer (0-3): ")

            # Normalize spoken responses like "one", "two"
            answer = valid_answers.get(answer, answer)

            if answer in ('0', '1', '2', '3'):
                score = int(answer)
                responses.append(score)
                total_score += score
                memory_logger.log_interaction(question, score)
                break
            else:
                print("❌ Invalid input. Please say or type a number from 0 to 3.")

    print("\n=== Screening Results ===")
    print(f"Total Score: {total_score} out of 27")

    if total_score <= 4:
        severity = "Minimal depression"
    elif 5 <= total_score <= 9:
        severity = "Mild depression"
    elif 10 <= total_score <= 14:
        severity = "Moderate depression"
    elif 15 <= total_score <= 19:
        severity = "Moderately severe depression"
    else:
        severity = "Severe depression"

    print(f"🧠 Depression Severity: {severity}")

    if responses[8] > 0:
        print("\n‼️ Your response indicates thoughts of self-harm or suicide.")
        print("Please consider talking to a mental health professional immediately or calling a helpline.")

    print("\n📋 This screening is not a diagnosis. Please consult a professional for a full evaluation.")