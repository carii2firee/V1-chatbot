from voice_input import get_input

def handle_name_recognition(user_name, memory_logger):
    print("\n=== Name Recognition System ===")

    name = get_input("Enter a name to check: ")
    memory_logger.log_interaction(name, "")

    check_name(name)
    memory_logger.log_interaction(name, "Checked name recognition")


known_names = ["Shacarion Wrencher", "Juleena Pham", "Win Giang ", "Suri Situmorang"]


def check_name(user_name):
    if user_name in known_names:
        print(
            f"Chatbot: Hello, {user_name}, It's nice to see a familiar face, since you just told me your lovely name...")
    else:
        print(f"Chatbot: Nice to meet you, {user_name}, you look wonderful today!")