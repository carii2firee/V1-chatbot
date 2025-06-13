import random
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from chat_data import questions, followups, transition_comments

# Optional: wrap input for easy swapping with GUI/voice
def get_input(prompt):
    return input(prompt)

# ============= Sentiment Detection =============
sid = SentimentIntensityAnalyzer()

def detect_emotion(text):
    scores = sid.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.1:
        return "positive"
    elif compound <= -0.1:
        return "negative"
    else:
        return "neutral"

# ============= Casual Chat Launcher =============
def handle_casual_chat(user_name, memory_logger):
    print("\n=== Casual Chat ===")
    memory_logger.log_interaction("Entered casual chat mode", "")
    casual_chat(user_name, memory_logger)
    memory_logger.log_interaction("Exited casual chat mode", "")

# ============= Casual Chat Engine =============
def casual_chat(user_name, memory_logger=None):
    print(f"Friend: Hey {user_name}! I'm excited to chat today. Mind if I ask you a few things?")

    chat_round = 0

    while True:
        if chat_round >= len(questions):
            print("Friend: I love these conversations. Is there anything you want to ask me now?")
        else:
            print(f"Friend: {questions[chat_round]}")

        user_input = get_input(f"{user_name}: ").strip()

        if memory_logger:
            memory_logger.log_interaction(f"Chat question {chat_round + 1}", user_input)

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Friend: It’s always a pleasure chatting with you. Let’s catch up again soon!")
            if memory_logger:
                memory_logger.log_interaction("Chat ended", "")
            break

        mood = detect_emotion(user_input)
        response = random.choice(followups.get(mood, followups["neutral"]))

        print("Friend:", response)
        if memory_logger:
            memory_logger.log_interaction(f"Chat response {chat_round + 1}", response)

        # Optional personality comment
        if chat_round % 2 == 1 and chat_round != 0:
            print("Friend:", random.choice(transition_comments))

        chat_round += 1