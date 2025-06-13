from voice_input import get_input

def handle_house_assistance(user_name, memory_logger):
    print("\n=== 🏡 House Assistance ===")
    print("Available topics: cleaning, energy, security, organization, automation")

    while True:
        topic = get_input("Please say or type a house tidying topic (or say 'back' to exit): ").strip().lower()

        if topic == 'back':
            print("🔙 Returning to previous menu...\n")
            break

        if topic not in ["cleaning", "energy", "security", "organization", "automation"]:
            print("❌ Invalid topic. Please choose from: cleaning, energy, security, organization, automation.")
            continue

        memory_logger.log_interaction(f"House topic selected: {topic}", "")
        advice = house_tidying(topic)
        print(f"💡 Advice: {advice}")
        memory_logger.log_interaction(f"Advice given for: {topic}", advice)



def house_tidying(topic):
    tips = {
        "cleaning": [
            "Start with a 10-minute tidy-up: Set a timer and focus on one room.",
            "Break cleaning into zones: kitchen, bathroom, living areas, bedroom.",
            "Keep a caddy with basic supplies (spray, cloths, gloves) in each bathroom.",
            "Do one laundry load a day to avoid overwhelming piles.",
            "Always clean as you go — especially in the kitchen to stay ahead of messes."
        ],
        "energy": [
            "Unplug unused electronics — they still draw power in standby mode.",
            "Switch to LED bulbs to reduce energy consumption.",
            "Set your thermostat 1–2 degrees lower in winter and higher in summer to save energy.",
            "Use natural light during the day whenever possible.",
            "Install a smart power strip to manage multiple devices efficiently."
        ],
        "security": [
            "Install motion-sensor lights at entrances and around the backyard.",
            "Use a smart doorbell to monitor activity at your front door.",
            "Keep bushes and trees trimmed to remove hiding spots near windows.",
            "Lock windows and sliding doors at night and when away.",
            "Create a daily routine to check locks and lights before bed."
        ],
        "organization": [
            "Declutter one drawer or shelf a day — small steps build momentum.",
            "Use clear bins so you can see what’s stored inside without opening everything.",
            "Add hooks by the front door for keys, bags, and coats.",
            "Label everything — it helps everyone in the household stay organized.",
            "Use the ‘one in, one out’ rule: for every new item, donate or toss an old one."
        ],
        "automation": [
            "Set routines with your smart assistant (e.g., ‘Good Morning’ to start lights and coffee).",
            "Use smart plugs to schedule appliances like humidifiers or lamps.",
            "Automate vacuuming with a robot vacuum — it saves time every day.",
            "Enable geofencing so lights and thermostats adjust when you leave/arrive.",
            "Use sensors to turn off lights in empty rooms automatically."
        ]
    }

    topic_key = topic.lower()
    if topic_key in tips:
        formatted = f"\n=== {topic.capitalize()} Tips ===\n"
        formatted += '\n'.join([f"{i + 1}. {tip}" for i, tip in enumerate(tips[topic_key])])
        return formatted
    else:
        return (
            "\nI happen to be very knowledgeable in these specific styles, so please ask away! \n"
            "- Cleaning\n- Energy\n- Security\n- Organization\n- Automation"
        )



    