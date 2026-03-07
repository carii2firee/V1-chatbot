import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

user_budget_data = {}

AUDIOBOOKS = {
    "investing": [
        {"title": "Investing Basics for Beginners", "url": "https://www.youtube.com/watch?v=4j46AjyuyeU"},
        {"title": "How to Build Your Investment Portfolio", "url": "https://www.youtube.com/watch?v=478KIty5AkU"},
    ],
    "saving": [
        {"title": "Smart Saving Strategies", "url": "https://www.youtube.com/watch?v=uwHUwP1TrhY"},
    ],
    "budgeting": [
        {"title": "Budgeting 101: The Basics", "url": "https://www.youtube.com/watch?v=stGEED_Z3vo"},
        {"title": "Master Your Budget: Tips and Tricks", "url": "https://www.youtube.com/watch?v=uxaNpwgCn8A"},
    ],
    "debt": [
        {"title": "How to Get Out of Debt Fast", "url": "https://www.youtube.com/watch?v=dcTRONAbO48"},
        {"title": "Financial Freedom, Live on Your Own Terms", "url": "https://www.youtube.com/watch?v=9DvVothk6rY&t=816s"},
    ],
    "emergency": [
        {"title": "How to Build an Emergency Fund", "url": "https://www.youtube.com/watch?v=UE6PapZxYIs"},
    ],
    "general": [
        {"title": "Personal Finance Basics", "url": "https://www.youtube.com/watch?v=HQzoZfc3GwQ"},
    ],
}

def get_sp500_data():
    api_key = os.getenv("ALPHA_VANTAGE_KEY")
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        quote = data.get("Global Quote", {})
        return {
            "price": quote.get("05. price", "N/A"),
            "change": quote.get("09. change", "N/A"),
            "change_pct": quote.get("10. change percent", "N/A"),
            "high": quote.get("03. high", "N/A"),
            "low": quote.get("04. low", "N/A"),
        }
    except:
        return None

def list_audiobooks(topic):
    topic = topic.lower()
    if topic not in AUDIOBOOKS:
        return {"error": f"Sorry, no audiobooks found for '{topic}'. Try: {', '.join(AUDIOBOOKS.keys())}"}
    return AUDIOBOOKS[topic]

def simulate_growth(starting, monthly, annual_return, years):
    months = years * 12
    r = annual_return / 12
    total = starting
    for _ in range(months):
        total = total * (1 + r) + monthly
    invested_total = (monthly * months) + starting
    growth = total - invested_total
    return {
        "future_value": round(total, 2),
        "invested_total": round(invested_total, 2),
        "growth": round(growth, 2)
    }

def generate_custom_response(question):
    question = question.lower().strip()

    if any(w in question for w in ["hello", "hey", "hi", "what's up", "wassup", "sup", "good morning", "good evening", "howdy"]):
        return {
            "response": (
                "Hey scholar! 👋 Good to have you here.\n\n"
                "I'm WRIN — think of me as the financial coach nobody gave you growing up.\n\n"
                "Most people learn about money the hard way. You don't have to.\n\n"
                "Ask me anything on your mind, or just start typing what's been stressing you out financially."
            ),
            "suggest": None
        }

    elif any(w in question for w in ["invest", "investment", "stocks", "portfolio", "rich", "wealthy", "grow my money", "make money", "passive income"]):
        return {
            "response": (
                "Investing early isn't about having money, it's about buying time.\n\n"
                "Most people wait until they feel ready. But every year you wait, compound interest works against you instead of for you. "
                "A dollar invested at 18 is worth 4x more than a dollar invested at 30. That's not motivation, that's math.\n\n"
                "The move: emergency fund first, then Roth IRA, then VOO or SPY on autopilot. "
                "You're not picking stocks. You're buying a piece of every major US company and letting time do the heavy lifting.\n\n"
                "Want to see how the numbers can shift your wallet balance, even with little growth over time? 👇"
            ),
            "suggest": {"label": "📊 Run a Wealth Simulation", "action": "5", "nudge": "See how investing in the long term can change your trajectory."}
        }

    elif any(w in question for w in ["save", "goal", "savings", "set aside", "saving up", "put money away", "stash", "money", "save money", "how do i save"]):
        return {
            "response": (
                "Saving isn't about restriction, it's about building options.\n\n"
                "Every dollar saved is a future version of you with more choices. "
                "The reason most people never save isn't income, it's that they pay everyone else first and leave themselves with whatever's left.\n\n"
                "Flip that. The moment money hits your account, move 10-20% out before you touch anything else. "
                "Out of sight, out of mind, and quietly becoming the foundation you never had.\n\n"
                "Even watching $5 a week grow will change how you think about money. 👇"
            ),
            "suggest": {"label": "🎯 Track Savings Progress", "action": "1", "nudge": "Watch what consistency does over time."}
        }

    elif any(w in question for w in ["broke", "no money", "cant afford", "can't afford", "struggling", "nothing left", "empty", "zero", "flat broke"]):
        return {
            "response": (
                "Being broke is a position. Not a personality. Not a life sentence.\n\n"
                "The reason it feels permanent is because nobody shows you the first step out. "
                "It's not earning more, it's seeing clearly. Most people have no idea where their money actually goes. "
                "That unawareness is what keeps the cycle going.\n\n"
                "Start here: track every dollar for 7 days. No judgment. Just data. "
                "What you find will surprise you, and surprise is the beginning of change.\n\n"
                "The shift from 'I have no money' to 'I control where it goes' is closer than you think. 👇"
            ),
            "suggest": {"label": "🎯 Track Savings Progress", "action": "1", "nudge": "See what small consistency builds into."}
        }

    elif any(w in question for w in ["track", "habit", "monitor", "routine", "progress", "consistent", "discipline"]):
        return {
            "response": (
                "You can't improve what you can't see.\n\n"
                "That's the whole reason tracking works. Not because it's exciting, because it makes the invisible visible. "
                "Most people guess where their money goes. The ones who track it know. And knowing is where control starts.\n\n"
                "One week of logging every purchase will show you patterns you didn't know existed. "
                "That awareness alone shifts behavior, not because you forced it, but because you can't unsee it.\n\n"
                "Consistency over intensity. Every time. 👇"
            ),
            "suggest": {"label": "📊 Check My Progress", "action": "2", "nudge": "See the difference a habit makes in real numbers."}
        }

    elif any(w in question for w in ["spending", "expenses", "bills", "cost", "overspending", "spend too much", "impulse", "waste", "unnecessary"]):
        return {
            "response": (
                "Overspending is rarely a willpower problem, it's a system problem.\n\n"
                "The environment around you is designed to make spending easy and saving hard. "
                "One-click checkout, saved card info, marketing emails timed perfectly. "
                "Every friction point removed is money leaving your account faster.\n\n"
                "The fix isn't discipline. It's building your own friction. "
                "24-hour rule on non-essentials. Cash for discretionary spending. Subscriptions audited monthly. "
                "When the system works for you instead of against you, the behavior follows naturally.\n\n"
                "Small intentional shifts compound into a completely different financial life. 👇"
            ),
            "suggest": {"label": "🎧 Browse Audiobooks", "action": "4", "nudge": "Explore what others have learned about spending with intention."}
        }

    elif any(w in question for w in ["debt", "owe", "loan", "credit card", "credit", "interest", "minimum payment"]):
        return {
            "response": (
                "Debt feels heavy because it is, but it's not permanent when you have a strategy.\n\n"
                "Here's why the minimum payment trap destroys people: a $1000 credit card at 20% APR, "
                "paying just the minimum, takes years to clear and costs hundreds extra. "
                "The bank designed it that way. Knowing that changes how you respond to it.\n\n"
                "Two exits: Snowball, smallest balance first, psychological wins keep momentum. "
                "Avalanche, highest interest first, mathematically saves the most. "
                "Either works. Picking one and starting today beats analyzing both forever.\n\n"
                "The day you stop adding to it and start attacking it, the math finally works in your favor. 👇"
            ),
            "suggest": {"label": "🎧 Listen to Debt Audiobooks", "action": "4", "nudge": "Hear from people who've been exactly where you are."}
        }

    elif any(w in question for w in ["budget", "plan", "allocate", "money management", "manage", "paycheck", "50/30/20", "where does my money go"]):
        return {
            "response": (
                "A budget isn't a restriction, it's a decision made in advance.\n\n"
                "Without one, money disappears and you're left guessing. With one, every dollar has a job "
                "before it even hits your account. That shift in control is what separates people who build wealth "
                "from people who wonder where it went.\n\n"
                "Start with 50/30/20: 50% needs, 30% wants, 20% savings and debt. "
                "Can't hit 20% yet? Start at 5% and raise it 1% monthly. "
                "The percentage matters less than the habit of doing it at all.\n\n"
                "The best budget is the one you actually stick to. Build it around your life, not someone else's. 👇"
            ),
            "suggest": {"label": "🎧 Browse Audiobooks", "action": "4", "nudge": "See how others have built systems that actually stick."}
        }

    elif any(w in question for w in ["emergency", "rainy day", "unexpected", "backup", "safety net", "just in case", "cushion"]):
        return {
            "response": (
                "An emergency fund isn't exciting — until the day you need it.\n\n"
                "Without one, every unexpected expense becomes debt. Car breaks down, debt. Medical bill, debt. "
                "Lose a shift at work, debt. The fund doesn't just protect your bank account — "
                "it protects every other financial goal you have from getting derailed.\n\n"
                "Start with $500. That one milestone covers most common emergencies. "
                "Then $1000. Then one month of expenses. Build it in a high-yield savings account "
                "where it earns while it waits — and automate it so you never have to think about it.\n\n"
                "Peace of mind has a price. It's lower than you think. 👇"
            ),
            "suggest": {"label": "🎯 Start an Emergency Fund Goal", "action": "1", "nudge": "See what building a safety net actually looks like in practice."}
        }

    elif any(w in question for w in ["learn", "read", "listen", "audiobook", "book", "financial literacy", "educate", "understand money"]):
        return {
            "response": (
                "Financial literacy is the subject that affects everything — and the one schools almost never teach.\n\n"
                "The gap between people who build wealth and people who don't isn't income. "
                "It's knowledge applied early. The earlier you understand how money works, "
                "the more time you have to let that understanding compound.\n\n"
                "Start at Level 1: budgeting, saving, avoiding debt traps. "
                "Then Level 2: compound interest, index funds, Roth IRAs. "
                "Then Level 3: tax strategy, real estate, multiple income streams. "
                "One concept at a time. Applied immediately. That's the whole strategy.\n\n"
                "The person who reads 10 pages a day on money is unrecognizable in 5 years. 👇"
            ),
            "suggest": {"label": "🎧 Browse Audiobooks", "action": "4", "nudge": "Start where you are. The library is waiting."}
        }

    elif any(w in question for w in ["college", "student", "tuition", "financial aid", "scholarship", "fafsa", "student loan", "borrowed future", "college debt", "university"]):
        return {
            "response": (
                "College is sold as the path to opportunity — but the debt it leaves behind can close more doors than it opens.\n\n"
                "Here's what the brochure doesn't show you: a $50,000 loan at 6.5% over 10 years costs $68,000 total. "
                "You pay $18,000 just in interest. And 4 billion dollars in free aid goes unclaimed every year "
                "because people didn't fill out the FAFSA. That's money that existed and went back unused.\n\n"
                "Before any loan: exhaust grants, scholarships, work-study. Federal loans only if you must borrow. "
                "Borrow for tuition — not lifestyle. And research what your degree earns before you commit to what it costs.\n\n"
                "You deserve to graduate building wealth, not paying off the cost of getting there. 👇"
            ),
            "suggest": {"label": "🎯 Set a College Savings Goal", "action": "1", "nudge": "Every dollar saved now is a dollar you won't owe later."}
        }

    elif any(w in question for w in ["job", "income", "work", "salary", "earn", "side hustle", "freelance"]):
        return {
            "response": (
                "Income is the starting line — not the finish line.\n\n"
                "Most people spend what they earn and save what's left. "
                "The problem is nothing is ever left. The ones who build wealth flip that equation: "
                "save first, spend what remains. That single habit separates two completely different financial futures.\n\n"
                "Automate 10-20% out the moment your paycheck lands. "
                "Negotiate your salary — most people leave money on the table by not asking. "
                "And as income grows, resist lifestyle inflation. Let the raise go to work instead of to spending.\n\n"
                "Your income is the seed. What you do with it determines what grows. 👇"
            ),
            "suggest": {"label": "📊 Run a Wealth Simulation", "action": "5", "nudge": "See what your income could quietly become over time."}
        }

    elif any(w in question for w in ["crypto", "bitcoin", "nft", "dogecoin", "meme stock"]):
        return {
            "response": (
                "The potential in crypto is real. So is the risk of losing everything — and most people find out which one they got too late.\n\n"
                "Here's why: most retail investors don't lose because the asset is worthless. "
                "They lose because emotion drives the decision. They buy when it's trending, sell when it drops, "
                "and repeat the cycle. By the time something hits social media, the smart money already moved.\n\n"
                "If you explore it: never more than 5-10% of your portfolio. Never money you can't afford to lose. "
                "Never without understanding why the asset has value. "
                "Build the foundation first — stable, boring, consistent. Then take calculated risks from a position of strength.\n\n"
                "Boring wins over 20 years. Every time. 👇"
            ),
            "suggest": {"label": "📊 Run a Wealth Simulation", "action": "5", "nudge": "See what steady and consistent actually builds into."}
        }

    else:
        return {
            "response": (
                "That's outside my lane — but I respect the curiosity.\n\n"
                "I'm built specifically to help you win with money. "
                "Saving, investing, debt, budgeting, college finances, building income — that's where I live.\n\n"
                "Bring me something in that world and I'll give you everything I've got. 💪"
            ),
            "suggest": None
        }


def start_budget_tracking(user_name, memory_logger):
    if user_name not in user_budget_data:
        user_budget_data[user_name] = {
            "goal": None,
            "current": 0.0,
            "transactions": []
        }

    # --- Set Savings Goal ---
    if user_budget_data[user_name]["goal"] is None:
        goal_input = yield f"Welcome {user_name}! To get started, enter your savings goal amount in dollars (e.g. $1000):"

        while True:
            if memory_logger:
                memory_logger.log_interaction(f"Savings Goal Input: {goal_input}", goal_input)

            cleaned_input = goal_input.replace("$", "").replace(",", "").strip()

            if any(c.isalpha() for c in cleaned_input) or not cleaned_input:
                result = generate_custom_response(goal_input)
                goal_input = yield {
                    "message": result["response"],
                    "suggest": result["suggest"]
                }
                continue

            try:
                goal = float(cleaned_input)
                if goal <= 0:
                    goal_input = yield "❌ Goal must be a positive number. Enter again:"
                    continue

                user_budget_data[user_name]["goal"] = goal
                yield {
                    "message": f"🎯 Goal set to ${goal:.2f}! I'm here to help with any financial questions you have. Ask me anything or type 'options' for the menu.",
                    "goal_progress": {"current": 0.0, "goal": round(goal, 2), "progress": 0}
                }
                break
            except ValueError:
                goal_input = yield "❌ Invalid number. Please enter a valid savings goal."

    # --- Main Menu Loop ---
    while True:
        choice = yield None

        if not choice:
            continue

        if memory_logger:
            memory_logger.log_interaction(f"Budget Mode Choice: {choice}", choice)

        spoken_map = {"one": "1", "two": "2", "three": "3", "four": "4",
                      "five": "5", "six": "6", "seven": "7"}
        choice = spoken_map.get(choice.lower(), choice.strip())

        if choice == "options":
            yield (
                "\nSelect an option:\n"
                "1. Add saved amount\n"
                "2. Check progress\n"
                "3. View savings history 📝\n"
                "4. Listen to audiobooks 🎧\n"
                "5. Run Wealth Simulation 📊\n"
                "6. Reset your total savings history\n"
            )

        elif choice == "6":
            user_budget_data[user_name] = {"goal": None, "current": 0.0, "transactions": []}
            yield "✅ Savings history reset. Type anything to start fresh!"
            break

        elif choice == "1":
            while True:
                amount_input = yield "How much did you save? Enter in dollars: $"
                if memory_logger:
                    memory_logger.log_interaction(f"Saved Amount Input: {amount_input}", amount_input)
                cleaned = amount_input.replace("$", "").replace(",", "").strip()
                if any(c.isalpha() for c in cleaned) or not cleaned:
                    yield "❌ Invalid number. Try again."
                    continue
                try:
                    amount = float(cleaned)
                    if amount <= 0:
                        yield "❌ Amount must be positive. Try again."
                        continue
                    break
                except ValueError:
                    yield "❌ Enter a valid number."

            note = yield "What's this saving for? (e.g., emergency, trip, gift): "
            if memory_logger:
                memory_logger.log_interaction(f"Saved Amount Note: {note}", note)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            user_budget_data[user_name]["current"] += amount
            user_budget_data[user_name]["transactions"].append({
                "amount": amount, "note": note, "time": timestamp
            })

            current = user_budget_data[user_name]["current"]
            goal = user_budget_data[user_name]["goal"]
            progress = min((current / goal) * 100, 100) if goal else 0

            if current >= goal:
                yield {
                    "message": f"🎉 Congrats {user_name}! You reached your ${goal:.2f} goal. Building habits like this puts you one step towards becoming wealthy!",
                    "goal_progress": {"current": round(current, 2), "goal": round(goal, 2), "progress": 100}
                }
            else:
                yield {
                    "message": f"💰 Added ${amount:.2f}! You're now at ${current:.2f} of ${goal:.2f}, keep striving for excellence scholar!",
                    "goal_progress": {"current": round(current, 2), "goal": round(goal, 2), "progress": round(progress, 1)}
                }

        elif choice == "2":
            goal = user_budget_data[user_name]["goal"]
            current = user_budget_data[user_name]["current"]
            progress = min((current / goal) * 100, 100) if goal else 0
            yield {
                "message": "📊 Here's your current progress:",
                "goal_progress": {"current": round(current, 2), "goal": round(goal, 2), "progress": round(progress, 1)}
            }

        elif choice == "3":
            transactions = user_budget_data[user_name]["transactions"]
            if not transactions:
                yield "📭 No savings recorded yet."
            else:
                history_lines = ["💰 Savings History:"]
                for t in transactions:
                    history_lines.append(f"- ${t['amount']:.2f} for '{t['note']}' on {t['time']}")
                yield "\n".join(history_lines)

        elif choice == "4":
            topic = yield "Which topic? (investing, saving, budgeting, debt): "
            if memory_logger:
                memory_logger.log_interaction(f"Audiobook Topic: {topic}", topic)
            audiobooks_response = list_audiobooks(topic)
            if isinstance(audiobooks_response, dict) and "error" in audiobooks_response:
                yield audiobooks_response["error"]
            else:
                response_lines = [f"📚 Audiobooks on {topic.capitalize()}:"]
                for book in audiobooks_response:
                    response_lines.append(f"- {book['title']}: {book['url']}")
                yield "\n".join(response_lines)

        elif choice == "5":
            sp500 = get_sp500_data()
            if sp500:
                yield {
                    "message": (
                        f"📈 Live S&P 500 (SPY) Data:\n"
                        f"Price: ${float(sp500['price']):.2f} | Change: {sp500['change']} ({sp500['change_pct']})\n"
                        f"High: ${float(sp500['high']):.2f} | Low: ${float(sp500['low']):.2f}\n\n"
                        f"✅ We'll default to S&P 500 returns — best starting point for beginners.\n\n"
                        f" are you ready to to start your wealth journey? 🚀"
                    ),
                    "sp500": sp500
                }
            else:
                yield "🚀 Let's build your wealth projection! (S&P 500 data unavailable right now)"

            while True:
                monthly_input = yield "💵 How much can you invest monthly? ($): "
                cleaned_monthly = monthly_input.replace("$", "").replace(",", "").strip()
                if any(c.isalpha() for c in cleaned_monthly) or not cleaned_monthly:
                    yield "❌ Invalid number. Try again."
                    continue
                try:
                    monthly = float(cleaned_monthly)
                    if monthly < 0:
                        yield "❌ Must be a positive number. Try again."
                        continue
                    break
                except ValueError:
                    yield "❌ Enter a valid number."

            while True:
                years_input = yield "📅 For how many years?: "
                cleaned_years = years_input.strip()
                if not cleaned_years.isdigit() or int(cleaned_years) <= 0:
                    yield "❌ Enter a positive number of years."
                    continue
                years = int(cleaned_years)
                break

            while True:
                start_input = yield "🏦 Starting amount? (0 if none): "
                cleaned_start = start_input.replace("$", "").replace(",", "").strip()
                if any(c.isalpha() for c in cleaned_start) or not cleaned_start:
                    yield "❌ Invalid amount. Try again."
                    continue
                try:
                    starting = float(cleaned_start)
                    if starting < 0:
                        yield "❌ Must be positive."
                        continue
                    break
                except ValueError:
                    yield "❌ Enter a valid number."

            conservative = simulate_growth(starting, monthly, 0.05, years)
            moderate = simulate_growth(starting, monthly, 0.07, years)
            aggressive = simulate_growth(starting, monthly, 0.10, years)

            yield {
                "message": (
                    f"📊 Your Wealth Simulation ({years} yrs)\n\n"
                    f"🟢 Conservative (5%)\nFuture Value: ${conservative['future_value']:,}\nInvested: ${conservative['invested_total']:,}\nGrowth: ${conservative['growth']:,}\n\n"
                    f"🟡 Moderate (7% — S&P 500 avg)\nFuture Value: ${moderate['future_value']:,}\nInvested: ${moderate['invested_total']:,}\nGrowth: ${moderate['growth']:,}\n\n"
                    f"🔴 Aggressive (10%)\nFuture Value: ${aggressive['future_value']:,}\nInvested: ${aggressive['invested_total']:,}\nGrowth: ${aggressive['growth']:,}\n\n"
                    f"💡 Type 'options' to return to the menu."
                ),
                "simulation": {
                    "conservative": conservative,
                    "moderate": moderate,
                    "aggressive": aggressive,
                    "years": years,
                    "monthly": monthly,
                    "starting": starting
                },
                "sp500": sp500
            }

        else:
            result = generate_custom_response(choice)
            yield {
                "message": result["response"],
                "suggest": result["suggest"]
            }
