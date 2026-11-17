"""
Daily Writing Companion - v8
Added: export all entries to a readable .txt file.

Just run: python daily_prompt.py
"""

import random
import json
import os
import sys
from datetime import date, datetime, timedelta

# --- Setup ------------------------------------------------------------------

DATA_FILE = "data.json"

PROMPTS = {
    "story": [
        "Write about a door that only opens once a year.",
        "A character finds a letter addressed to them from ten years in the future.",
        "Someone discovers their reflection is one second behind them.",
        "Write the last five minutes before a goodbye that matters.",
        "A stranger sits down and says, 'You probably don't remember me.'",
    ],
    "poem": [
        "Write a poem about the sound a house makes when it's empty.",
        "Describe a color that doesn't exist using only things that do.",
        "Write about waiting, without using the word 'wait'.",
        "A poem made entirely of questions.",
        "Write about something small that outlived someone.",
    ],
    "journal": [
        "What did you almost say today, but didn't?",
        "Describe today as weather.",
        "What's a small thing you're avoiding right now?",
        "Write a letter to yourself from one year ago.",
        "What did you notice today that no one else seemed to?",
    ],
}


# --- Data Handling --------------------------------------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "entries": [],
        "streak": 0,
        "last_entry_date": None,
        "goal": None,
        "goal_hit_dates": [],
    }


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    

def update_streak(data):
    today = date.today().isoformat()
    last = data.get("last_entry_date")

    if last == today:
        return data["streak"]
    
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    if last == yesterday:
        data["streak"] += 1
    else:
        data["streak"] = 1
        
    data["last_entry_date"] = today
    return data["streak"]


# --- Goal (v4) ----------------------------------------------

def setup_goal(data):
    print("\n--- Set your daily writing goal ---")
    print("How many words do you want to write each day?")
    print("(Suggested: 50 for beginners, 100-200 for more challenge)")

    while True:
        try:
            goal = int(input("> ").strip())
            if goal > 0:
                data["goal"] = goal
                print(f"\nGoal set: {goal} words per day. Let's go!")
                return goal
            else:
                print("Please enter a number greater than 0.")
        except ValueError:
            print("Please enter a whole number.")


def check_goal(data, word_count):
    goal = data.get("goal")
    if goal is None:
        return

    today = date.today().isoformat()

    if word_count >= goal:
        if today not in data.get("goal_hit_dates", []):
            data.setdefault("goal_hit_dates", []).append(today)
        print(f"Goal reached! {word_count}/{goal} words.")
    else:
        remaining = goal - word_count
        print(f"Goal: {word_count}/{goal} words. {remaining} more to hit it today.")


# --- Stats (v2, updated in v4) ----------------------------------------------------

def show_stats():
    data = load_data()
    entries = data.get("entries", [])

    print("=" * 50)
    print("YOUR WRITNG STATS")
    print("=" * 50)

    if not entries:
        print("\nNo entries yet. Write something first!")
        return
    
    total_entries = len(entries)
    total_words = sum(e["word_count"] for e in entries)
    avg_words = total_words // total_entries

    print(f"\nTotal entries    : {total_entries}")
    print(f"Total words      : {total_words}")
    print(f"Average words    : {avg_words} per entry")
    print(f"Current streak  : {data.get('streak', 0)} day(s)")

    goal = data.get("goal")
    if goal:
        hit_dates = data.get("goal_hit_dates", [])
        hit_count = len(hit_dates)
        print(f"\n--- Daily goal: {goal} words ---")
        print(f" Days goal hit  : {hit_count}")
        if total_entries > 0:
            hit_rate = (hit_count * 100) // total_entries
            bar_hit = "█" * hit_count
            bar_miss = "░" * (total_entries - hit_count)
            print(f" Hit rate         : {hit_rate}%")
            print(f" Progress         : {bar_hit}{bar_miss}")

    print("\n--- By category ---")
    categories = {"story": 0, "poem": 0, "journal": 0}
    words_by_category = {"story": 0, "poem": 0, "journal": 0}

    for e in entries:
        cat = e.get("category", "unknown")
        if cat in categories:
            categories[cat] += 1
            words_by_category[cat] += e["word_count"]

    for cat in categories:
        count = categories[cat]
        words = words_by_category[cat]
        bar = "█" * count
        print(f" {cat:<8} {bar} {count} entries, {words} words")

    best = max(entries, key=lambda e: e["word_count"])
    print(f"\n--- Best entry ---")
    print(f"  Date   : {best['date']}")
    print(f"  Type   : {best['category']}")
    print(f"  Words  : {best['word_count']}")
    print(f"  Prompt : {best['prompt']}")

    print("=" * 50)


# --- Search (new in v3) --------------------------------------------

def search_entries(keyword):
    data = load_data()
    entries = data.get("entries", [])

    print("=" * 50)
    print(f'SEARCH: "{keyword}"')
    print("=" * 50)

    if not entries:
        print("\nNo entries yet. Write something first!")
        return

    keyword_lower = keyword.lower()
    matches = [
        e for e in entries
        if keyword_lower in e.get("text", "").lower()
        or keyword_lower in e.get("prompt", "").lower()
    ]

    if not matches:
        print(f"\nNo entries found containing \"{keyword}\".")
        print("Try a different word.")
        return

    print(f"\nFound {len(matches)} entry/entries:\n")

    for i, entry in enumerate(matches, start=1):
        print(f"--- Result {i} ---")
        print(f"  Date     : {entry['date']}")
        print(f"  Type     : {entry['category']}")
        print(f"  Words    : {entry['word_count']}")
        print(f"  Prompt   : {entry['prompt']}")
        print(f" Your writing:")
        text = entry.get("text", "")
        highlighted = text.replace(keyword.lower(), f"[{keyword.lower()}]")
        print(f"\n    {highlighted}\n")

    print("=" * 50)
    print(f"Total matches: {len(matches)} of {len(entries)} entries")
    print("=" * 50)


# --- Writing session ---------------------------------------------------------

def choose_category():
    print("\nWhat do you want to write today?")
    print(" 1. Story")
    print(" 2. Poem")
    print(" 3. Journal")
    print(" 4. Surprise me")
    choice = input("> ").strip()

    mapping = {"1": "story", "2": "poem", "3": "journal"}
    if choice in mapping:
        return mapping[choice]
    return random.choice(list(PROMPTS.keys()))


def write_session():
    data = load_data()

    if data.get("goal") is None:
        setup_goal(data)
        save_data(data)

    goal = data.get("goal")
    if goal:
        print(f"\nDaily: {goal} words")

    category = choose_category()
    prompt = random.choice(PROMPTS[category])

    print(f"\nYour prompt ({category}):")
    print(f'  "{prompt}"')
    print("\nWrite below. Press Enter on an empty line when you're done.\n")

    start_time = datetime.now()
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    end_time = datetime.now()
    text = "\n".join(lines)
    word_count = len(text.split())
    duration = (end_time - start_time).seconds

    if word_count == 0:
        print("\nNo words written — that's okay. Come back tomorrow.")
        return

    entry = {
        "date": date.today().isoformat(),
        "category": category,
        "prompt": prompt,
        "text": text,
        "word_count": word_count,
        "duration_seconds": duration,
    }
    data["entries"].append(entry)
    streak = update_streak(data)
    check_goal(data, word_count)

    # Ask for mood rating (new in v8)
    mood = ask_mood()
    if mood:
        data["entries"][-1]["mood"] = mood
    
    save_data(data)

    print("\n" + "-" * 50)
    print(f"Saved! {word_count} words in {duration // 60}m {duration % 60}s")
    print(f"Current streak: {streak} day{'s' if streak != 1 else ''}")
    print(f"Total words so far: {sum(e['word_count'] for e in data['entries'])}")
    if mood:
        print(f"Mood logged: {mood}")
    print("-" * 50)


# --- Mood tracking (new in v8) -------------------------------------

MOODS = {
    "1": "😔 Struggling",
    "2": "😐 Neutral",
    "3": "🙂 Good",
    "4": "😊 Great",
    "5": "🌟 Amazing",
}


def ask_mood():
    """ Ask the user to rate their mood after writing. Returns mood string or None."""
    print("\nHow are you feeling after writing?")
    print(" 1. 😔 Struggling")
    print(" 2. 😐 Neutral")
    print(" 3. 🙂 Good")
    print(" 4. 😊 Great")
    print(" 5. 🌟 Amazing")
    print(" 0. Skip")

    choice = input("> ").strip()
    if choice in MOODS:
        return MOODS[choice]
    return None


def show_mood_stats():
    """Show a breakdown of moods across all entries"""
    data = load_data()
    entries = data.get("entries", [])

    # Filter only entries that have a mood logged
    mood_entries = [e for e in entries if "mood" in e]

    print("\n" + "=" * 50)
    print("MOOD STATS")
    print("=" * 50)

    if not mood_entries:
        print("\nNo mood data yet.")
        print("Rate your mood after writing to see stats here.")
        input("\nPress Enter to go back to the menu...")
        return

    print(f"\nEntries with mood logged: {len(mood_entries)} of {len(entries)}")
    print("\n--- Mood breakdown ---")

    # Count how many times each mood appears
    mood_counts = {}
    for e in mood_entries:
        mood = e["mood"]
        mood_counts[mood] = mood_counts.get(mood, 0) + 1

    # Show each mood with a bar
    for mood_label in MOODS.values():
        count = mood_counts.get(mood_label, 0)
        bar = "█" * count
        print(f" {mood_label:<20} {bar} {count}")

    # Find most common mood
    best_mood = max(mood_counts, key=lambda m: mood_counts[m])
    print(f"\nMost common mood: {best_mood}")

    # Show last 5 mood entries
    print("\n--- Recent moods ---")
    recent = mood_entries[-5:]
    for e in reversed(recent):
        print(f" :{e['date']} - {e['category']} - {e['mood']}")

    print("=" * 50)
    input("\n Press Enter to go back to the menu...")


# --- Export (new in v6) --------------------------------------------

def export_entries():
    data = load_data()
    entries = data.get("entries", [])
    
    if not entries:
        print("\nNo entries to export yet. Write something first!")
        return
    
    # Build the filename using today's date
    filename = f"Elektra's Lovely Data  {date.today().isoformat()}.txt"

    # Count totals for the header
    total_words = sum(e["word_count"] for e in entries)
    streak = data.get("streak", 0)
    goal = data.get("goal")

    try:
        # Open the file for writing - "w" means write, creates it if it doesn't exist
        with open(filename, "w", encoding="utf-8") as f:

            # Write a header
            f.write("=" * 60 + "\n")
            f.write(" MY WRITING JOURNAL\n")
            f.write(f" Exported : {date.today().isoformat()}\n")
            f.write(f" Entries  : {len(entries)}\n")
            f.write(f" Total    : {total_words} words\n")
            f.write(f" Streak   : {streak} day{'s' if streak != 1 else ''}\n")
            if goal:
                f.write(f" Goal     : {goal} words/day\n")
            f.write("=" * 60 + "\n\n")

            #Write each entry
            for i, entry in enumerate(entries, start=1):
                f.write(f"--- Entry {i} ---\n")
                f.write(f"Date     : {entry['date']}\n")
                f.write(f"Type     : {entry['category']}\n")
                f.write(f"Words    : {entry['word_count']}\n")
                f.write(f"Prompt   : {entry['prompt']}\n")
                f.write("\n")
                f.write(entry.get("text", "") + "\n")
                f.write("\n" + "-" * 60 + "\n\n") 

        print(f"\nExported {len(entries)} entries to: {filename}")
        print("Look for it in your Python Practice folder.")
        print("You can open it in Notepad or VS Code.")

    except Exception as e:
        print(f"\nExport failed: {e}")

    input("\nPress Enter to go back to the menu...")


# --- Edit or delete entry (new in v7) --------------------------------------------

def edit_or_delete_entry():
    data = load_data()
    entries = data.get("entries", [])

    if not entries:
        print("\nNo entries yet. Write something first")
        input("\nPress Enter to go back to the menu...")
        return
    
    # Show all entries so user can pick one
    print("\n" + "=" * 50)
    print("YOUR ENTRIES")
    print("=" * 50)

    for i, entry in enumerate(entries, start=1):
        preview = entry.get("text", "")[:40]
        if len(entry.get("text", "")) > 40:
            preview += "..."
        print(f"  {i}. [{entry['date']}] {entry['category']} - {preview}")

    print("=" * 50)

    # Ask which entry to work on
    while True:
        try:
            choice =input(f"\nEnter entry number (1-{len(entries)}) or 0 to cancel: ").strip()
            index = int(choice)
            if index == 0:
                return
            if 1 <= index <= len(entries):
                break
            else:
                print(f"Please enter a number between 1 and {len(entries)}.")
        except ValueError:
            print("Please enter a whole number.")

    # Show the selected entry in full
    selected = entries[index - 1]
    print("\n" + "-" * 50)
    print(f"Date   : {selected['date']}")
    print(f"Type   : {selected['category']}")
    print(f"Prompt : {selected['prompt']}")
    print(f"Words  : {selected['word_count']}")
    print(f"\nYour writing:\n {selected.get('text', '')}")
    print("-" * 50)

    # Ask what to do with it
    print("\nWhat do you want to do?")
    print("  1. Edit the text")
    print("  2. Delete this entry")
    print("  3. Cancel")
    action = input("> "). strip()

    if action == "1":
        print("\nType your new text below.")
        print("Press Enter on an empty line when done.\n")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)

        new_text = "\n".join(lines)
        if new_text.strip() == "":
            print("\nNo changes made — text was empty.")
        else:
            entries[index - 1]["text"] = new_text
            entries[index - 1]["word_count"] = len(new_text.split())
            data["entries"] = entries
            save_data(data)
            print(f"\nEntry updated. New word count: {len(new_text.split())}")

    elif action == "2":
        confirm = input (f"\nAre you sure you want to delete entry {index}? (yes/no):").strip().lower()
        if confirm == "yes":
            deleted = entries.pop(index - 1)
            data["entries"] = entries
            save_data(data)
            print(f"\nDeleted: ]{deleted['date']}] {deleted['category']}")
        else:
            print("\nDeletetion cancelled.")
        
    else:
        print("\nCancelled.")

    input("\nPress Enter to go back to the menu...")


# --- Change goal from menu --------------------------------------------

def change_goal_menu():
    print("\n--- Change your daily goal ---")
    print("Enter a new word count goal:")

    while True:
        try:
            number = int(input("> ").strip())
            if number > 0:
                data = load_data()
                data["goal"] = number
                save_data(data)
                print(f"\nGoal updated: {number} words per day.")
                return
            else:
                print("Please enter a number greater than 0.")
        except ValueError:
            print("Please enter a whole number.")
           

# --- Main menu (new in v5) -------------------------------------------------------------------------

def show_menu(data):
    """Display the main menu with current streak and goal."""
    streak = data.get("streak", 0)
    goal = data.get("goal")
    entries = data.get("entries", [])
    total_words = sum(e["word_count"] for e in entries)

    print("\n" + "=" * 50)
    print("  DAILY WRITING COMPANION")
    print(f"  Streak : {streak} day{'s' if streak != 1 else ''}")
    if goal:
        print(f"  Goal  : {goal} words/day")
    print(f"  Total  : {total_words} words written")
    print("=" * 50)
    print("  1. Write today's entry")
    print("  2. View my stats")
    print("  3. Search my entries")
    print("  4. Edit or delete an entry")
    print("  5. Mood stats")
    print("  6. Change my goal")
    print("  7. Export to .txt file")
    print("  8. Quit")
    print("=" * 50)


def run_menu():
    """The main application loop — keeps running until user quits"""
    while True:
        data = load_data()
        show_menu(data)

        choice = input("\nChoose an option (1-6): ").strip()
        
        if choice == "1":
            write_session()

        elif choice == "2":
            show_stats()

        elif choice == "3":
            keyword = input("\nSearch for: ").strip()
            if keyword:
                search_entries(keyword)
            else:
                print("Please enter a keyword")

        elif choice == "4":
            change_goal_menu()

        elif choice == "5":
            show_mood_stats()

        elif choice == "6":
            change_goal_menu()

        elif choice == "7":
            export_entries()

        elif choice =="8":
            print("\nSee you tomorrow. Keep writing.")
            break

        else:
            print("\nInvalid option. Please choose 1-8.")


# --- Entry point ------------------------------------------------------------

if __name__ == "__main__":
    run_menu()
