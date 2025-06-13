# ====== Imports and Global Setup ======
from voice_input import get_input  # Your voice + fallback input

# If you're using this in a dedicated file
user_budget_data = {} 




def start_budget_tracking(user_name):
    if user_name not in user_budget_data:
        print(f"\nWelcome {user_name}! Let's save some money. Remember: dreams without goals are just dreams.")

        while True:
            goal_input = get_input("What is your savings goal? (Enter in dollars): $")
            try:
                goal = float(goal_input)
                break
            except ValueError:
                print("❌ Please enter a valid number.")

        user_budget_data[user_name] = {
            "goal": goal,
            "current": 0.0
        }

        print(f"Great! Your savings goal is ${goal:.2f}. Let's start saving!\n")

    while True:
        print("\nSelect an option:")
        print("1. Add saved amount")
        print("2. Check progress")
        print("3. Offer some budgeting tips!")
        print("4. I want to exit for now")

        choice = get_input("Say or type your choice (1-4): ").strip().lower()

        # Normalize spoken numbers if any
        spoken_map = {"one": "1", "two": "2", "three": "3", "four": "4"}
        choice = spoken_map.get(choice, choice)

        if choice == "1":
            amount_input = get_input("Enter how much you’ve saved to add to your progress: $")
            try:
                amount = float(amount_input)
                user_budget_data[user_name]["current"] += amount

                current = user_budget_data[user_name]["current"]
                goal = user_budget_data[user_name]["goal"]

                if current >= goal:
                    print(f"\n🎉 Congratulations, {user_name}! You’ve reached your goal of ${goal:.2f}!")
                    print(
                        "The discipline you're building will change your future. You're one step closer to financial freedom!\n")
                else:
                    remaining = goal - current
                    print(f"You’ve saved ${current:.2f}. Only ${remaining:.2f} to go! Keep going, you're doing great!")

            except ValueError:
                print("❌ Please enter a valid number.")

        elif choice == "2":
            goal = user_budget_data[user_name]["goal"]
            current = user_budget_data[user_name]["current"]
            progress = (current / goal) * 100 if goal != 0 else 0
            print(f"\nYour Goal: ${goal:.2f}")
            print(f"Current Savings: ${current:.2f}")
            print(f"Progress: {progress:.1f}%\n")

        elif choice == "3":
            question = get_input("What kind of budget help do you need? ")
            advice = generate_custom_response(question)
            print(f"💡 Advice: {advice}")

        elif choice == "4":
            print("Returning to the mode selector...\n")
            break

        else:
            print("❌ Invalid option. Please select 1-4.")

# ============= Budget Advice Sub-System =============
def generate_custom_response(question):
    question = question.lower().strip()

    if any(word in question for word in ["invest", "investment", "stocks", "portfolio"]):
        return (
            "Smart move thinking about investing. Before diving in, ask yourself: "
            "Do I have an emergency fund set aside? Start with index funds or ETFs — they’re low-risk and great for beginners. "
            "Remember, investing is a long-term game, not a get-rich-quick scheme."
        )

    elif any(word in question for word in ["save", "goal", "savings", "set aside"]):
        return (
            "Great! Start with a SMART goal — Specific, Measurable, Achievable, Relevant, Time-bound. "
            "For example, instead of 'I want to save money', try 'I’ll save $50/week for 6 months to build a $1200 emergency fund.' "
            "Clarity fuels discipline."
        )

    elif any(word in question for word in ["track", "habit", "monitor", "routine"]):
        return (
            "Tracking is key. Start small: list your expenses daily for just one week. "
            "Patterns will emerge. Pair that with a visual tracker — like a habit app or spreadsheet. "
            "The goal? Make progress visible and addictive."
        )

    elif any(word in question for word in ["spending", "expenses", "bills", "cost"]):
        return (
            "Challenge yourself: write down your top 3 spending categories. "
            "Then cut back just 10% in one of them this week. No shame — just insight. "
            "Spend with intention, not impulse."
        )

    elif any(word in question for word in ["debt", "owe", "loan", "credit card"]):
        return (
            "Debt can feel heavy, but there’s a path out. Use the snowball method (smallest balance first) for momentum, "
            "or the avalanche method (highest interest first) to save more long term. "
            "Either way — pay *more than the minimum*. Every dollar over counts more than you think."
        )

    elif any(word in question for word in ["budget", "plan", "allocate", "money management"]):
        return (
            "Think of your budget like a map — it tells your money where to go instead of wondering where it went. "
            "Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings/debt. "
            "Tweak it to fit your life — the point is to be *intentional* with every dollar."
        )

    elif any(word in question for word in ["emergency", "rainy day", "unexpected", "backup"]):
        return (
            "Emergencies happen. That’s why even setting aside $500 is powerful. "
            "It gives you breathing room — and peace of mind. Start small: automate $10–$20 weekly into a separate account. "
            "Your future self will thank you."
        )

    else:
        return (
            "Good question. When in doubt, do this: for the next 7 days, write down *every* dollar you spend. "
            "Don’t judge it, just log it. Awareness is the first step to control. "
            "You don’t need more money, you need a stricter mindset with how your money is being spent. 💪"
        )