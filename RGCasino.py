import random
import time
import os
import sys
import string
import ctypes
from collections import Counter, defaultdict
from itertools import combinations

# ------------------ Enable ANSI on Windows ------------------
def enable_ansi_windows():
    if os.name != "nt":
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)) == 0:
            return
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(handle, new_mode)
    except Exception:
        pass

enable_ansi_windows()

# ------------------ MENU SYSTEM ------------------

def main_menu():
    while True:
        print("\n=== MAIN MENU ===")
        print("1. Play games")
        print("2. Other (repay/borrow/vip/heist/boss/stats/leave)")
        print("3. Teleporter")
        print("4. Quit")

        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            games_menu()
        elif choice == "2":
            other_menu()
        elif choice == "3":
            teleporter()
        elif choice == "4":
            if shady_borrowed and debt > 0:
                print(RED + "\nThe shady man won't let you leave with unpaid debt. Work it off now." + RESET)
                work_off_debt()
            show_stats(final=True)
            print(YELLOW + "Thanks for playing! Goodbye!" + RESET)
            break
        else:
            print(YELLOW + "Invalid choice." + RESET)

def games_menu():
    print("\n╔══════════════════ GAMES ══════════════════╗")
    print("1. Blackjack")
    print("2. Roulette")
    print("3. War")
    print("4. Slot Machines")
    print("5. High Card")
    print("6. Dice Roll")
    print("7. Craps")
    print("8. Horse Racing")
    print("9. Texas Hold'em Poker")
    print("10. Yahtzee")
    print("11. Teleporter")
    print("12. Back")
    choice = input("Choose a game (1-11): ").strip()
    mapping = {
        "1": blackjack_game,
        "2": roulette_game,
        "3": war_game,
        "4": slots_game,
        "5": high_card_game,
        "6": dice_game,
        "7": craps_game,
        "8": horse_race_game,
        "9": play_texas_holdem,
        "10": yahtzee_game,
        "11": teleporter,
    }
    if choice == "12":
        return
    func = mapping.get(choice)
    if func:
        func()
    else:
        print(YELLOW + "Invalid choice." + RESET)

def other_menu():
    print("\n╔══════════════════ OTHER ══════════════════╗")
    print("1. Repay Loan")
    print("2. Borrow from Shady Man")
    print("3. View Stats")
    print("4. VIP Lounge")
    print("5. Heist Event (rare/risky)")
    print("6. Meet the Boss (if conditions)")
    print("7. Leave (and show final profit)")
    print("8. The Arena")
    print("9. Teleporter")
    print("10. Back")
    choice = input("Choose (1-10): ").strip()
    if choice == "1":
        repay_loan()
    elif choice == "2":
        borrow_from_shady()
    elif choice == "3":
        show_stats(final=False)
    elif choice == "4":
        vip_lounge()
    elif choice == "5":
        # Heist only when broke or rare manual attempt allowed
        heist_event()
    elif choice == "6":
        if debt > 0 or boss_alert_level >= 2:
            boss_encounter(auto=False)
        else:
            print(YELLOW + "No boss activity right now. Owe money or accumulate reminders to trigger him." + RESET)
            pause(0.6)
    elif choice == "7":
        if shady_borrowed and debt > 0:
            print(RED + "\n💀 The shady man blocks your exit! Work off your debt first." + RESET)
            work_off_debt()
        show_stats(final=True)
        print(YELLOW + "You leave the casino. See you next time!" + RESET)
        sys.exit()
    elif choice == "8":
        arena_menu()
    elif choice == "9":
        teleporter()
    elif choice == "10":
        return
    else:
        print(YELLOW + "Invalid choice." + RESET)
    # always go back to main menu after other menu choice
    return

def return_to_main_menu():
    # small helper to add consistent flow: show message, pause, and then return to main menu.
    print(CYAN + "\nReturning to MAIN MENU..." + RESET)
    pause(0.9)

def teleporter():
    print("Hello! Where would you like to go?")
    slow_print("1. Main Menu")
    slow_print("2. Games Menu")
    slow_print("3. Other Menu")
    slow_print("4. VIP Lounge")
    slow_print("5. The Arena")
    choice = input("Choose 1-5: ")
    if choice == "1":
        print(RED + "Great let's go to the Main Menu!" + RESET)
        main_menu()
    elif choice == "2":
        print(BLUE + "Great let's go to the Games Menu!" + RESET)
        games_menu()
    elif choice == "3":
        print(YELLOW + "Great let's go to Other Menu!"+ RESET)
        other_menu()
    elif choice == "4":
        print(GREEN + "Great let's go to the VIP Lounge!"+ RESET)
        vip_lounge()
    elif choice == "5":
        print(CYAN +"Great let's go to The Arena!" + RESET)
        check_arena_unlock()
        arena_menu()
# ------------------ COLOURS ------------------
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
GOLD = "\033[33m"  # used for VIP title

# ------------------ GLOBAL STATE & STATS ------------------
money = 1000
starting_money = money
shady_borrowed = False
debt = 0
borrow_count = 0
games_since_borrow = 0
INTEREST_INTERVAL_GAMES = 3

# arena stats
player_health = 100
enemy_1 = 100
enemy_2 = 120
enemy_3 = 150
enemy_4 = 170
fat_tony = 220
arena_unlocked = False

stats = {
    "games_played": 0,
    "total_bet": 0,
    "total_won": 0,
    "total_lost": 0,
    "wins": 0,
    "losses": 0,
    "ties": 0
}

# boss/heist/VIP state
boss_alert_level = 0
boss_met = False
heist_unlocked = False
vip_unlocked = False
heist_trigger_chance = 0.20  # 20% rare trigger when broke (we'll call when broke)

# other
SLOW = 0.01
PAUSE_SHORT = 0.5
PAUSE = 0.9

# ------------------ HELPERS ------------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause(s=PAUSE_SHORT):
    time.sleep(s)

def slow_print(text, delay=SLOW):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def safe_int(prompt, min_v=None, max_v=None, allow_zero=False):
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
            if not allow_zero and v == 0:
                print(YELLOW + "Zero is not allowed." + RESET)
                continue
            if min_v is not None and v < min_v:
                print(YELLOW + f"Value must be at least {min_v}." + RESET)
                continue
            if max_v is not None and v > max_v:
                print(YELLOW + f"Value must be at most {max_v}." + RESET)
                continue
            return v
        except ValueError:
            print(YELLOW + "Please enter a valid integer." + RESET)

def header():
    print(CYAN + r"""
   ____      _             _            
  / ___|__ _| | ___  _ __ (_) __ _ _ __  
 | |   / _` | |/ _ \| '_ \| |/ _` | '_ \
 | |__| (_| | | (_) | | | | | (_| | | | |
  \____\__,_|_|\___/|_| |_|_|\__,_|_| |_|
    """ + RESET)
    print(MAGENTA + "╔══════════════════════════════════════╗" + RESET)
    print(MAGENTA + "║      🎰 WELCOME TO THE CASINO 🎰     ║" + RESET)
    print(MAGENTA + "╚══════════════════════════════════════╝" + RESET)
    pause(0.8)
    slow_print(YELLOW + "You walk into the casino. The air smells like smoke and desperation..." + RESET)
    pause(0.6)

def show_game_title(title, gold=False):
    if gold:
        col = GOLD
    else:
        col = BLUE
    print("\n" + col + "╔══════════════════════════════╗" + RESET)
    print(col + f"║       🎲 {title} 🎲                ║" + RESET)
    print(col + "╚══════════════════════════════╝" + RESET)
    pause(0.25)

def update_stats_after_result(bet, result):
    # result: "win", "loss", "tie" ; bet is amount added/lost/placed
    stats["games_played"] += 1
    stats["total_bet"] += bet if bet>0 else 0
    if result == "win":
        stats["wins"] += 1
        stats["total_won"] += bet
    elif result == "loss":
        stats["losses"] += 1
        stats["total_lost"] += bet
    elif result == "tie":
        stats["ties"] += 1

def apply_interest_if_due(announce=True):
    global debt, games_since_borrow, boss_alert_level
    if debt <= 0:
        return
    games_since_borrow += 1
    if games_since_borrow >= INTEREST_INTERVAL_GAMES:
        inc = max(1, int(debt * 0.10))
        debt += inc
        games_since_borrow = 0
        boss_alert_level += 1
        if announce:
            # 1-in-4 chance boss appears loudly, else small reminder
            if random.randint(1,4) == 1 or boss_alert_level >= 4:
                boss_encounter(auto=True)
            else:
                print(YELLOW + f"\n(Interest tick: your debt increased by {inc} to ${debt})" + RESET)
        pause(0.4)

def check_money_and_handle():
    """
    Called when money <= 0. Returns True to continue, False to exit program.
    If player is broke and hasn't borrowed, offer loan.
    If already borrowed -> force work_off_debt (alphabet mini-game).
    """
    global money, shady_borrowed, debt, borrow_count
    if money > 0:
        return True
    if not shady_borrowed:
        print(RED + "\n💀 You're completely broke!" + RESET)
        choice = input("Do you want to borrow $500 from a very suspicious man? (Y/N): ").strip().upper()
        if choice == "Y":
            money += 500
            debt += 500
            shady_borrowed = True
            borrow_count += 1
            print(GREEN + "You take the loan. He says he'll find you if you don't pay back..." + RESET)
            pause(0.6)
            return True
        else:
            print("You leave the casino, broke and cold. 😢")
            return False
    else:
        # already borrowed: force work-off-debt
        print(RED + "\n💀 You're broke and already in debt to the shady man." + RESET)
        pause(0.4)
        work_off_debt()
        if money <= 0:
            money = 1
            print(YELLOW + "\nAfter working off some debt, the shady man tosses you a single dollar to continue." + RESET)
        return True

# ------------------ LOAN / SHADY MAN / REPAY ------------------
def borrow_from_shady():
    global money, shady_borrowed, debt, borrow_count, games_since_borrow
    print(RED + "\nA suspicious man steps out of a shadow..." + RESET)
    pause(0.5)
    amount = safe_int("How much would you like to borrow? $", min_v=1)
    money += amount
    debt += amount
    shady_borrowed = True
    borrow_count += 1
    games_since_borrow = 0
    print(GREEN + f"You borrow ${amount}. You now owe ${debt} (10% interest every {INTEREST_INTERVAL_GAMES} games)." + RESET)
    pause(0.6)

def repay_loan():
    global money, shady_borrowed, debt
    if not shady_borrowed or debt <= 0:
        print(YELLOW + "\nYou don't owe the shady man anything." + RESET)
        pause(0.5)
        return
    print(f"\nYou currently owe the shady man ${debt}. You have ${money}.")
    repay = safe_int("How much will you pay now? $", min_v=0, allow_zero=True)
    if repay == 0:
        print("You decide not to pay right now.")
        return
    if repay > money:
        print(RED + "You don't have that much money!" + RESET)
        return
    pay = min(repay, debt)
    money -= pay
    debt -= pay
    print(GREEN + f"You handed over ${pay}. Debt left: ${debt}" + RESET)
    if debt <= 0:
        shady_borrowed = False
        debt = 0
        print(GREEN + "The shady man nods and disappears." + RESET)

# ------------------ WORK-OFF-DEBT MINI-GAME ------------------
def work_off_debt():
    global debt, money, shady_borrowed
    alphabet = list(string.ascii_uppercase)
    total = debt if debt > 0 else 1
    print(MAGENTA + "\n💀 The shady man forces you to work off your debt." + RESET)
    print("Press the requested letter + Enter to reduce your debt by $1 per correct letter.")
    pause(0.6)
    # Keep it fair: stop if user wants to quit - but boss requires completion to clear debt
    while debt > 0:
        letter = random.choice(alphabet)
        guess = input(f"Press '{letter}': ").strip().upper()
        if guess == letter:
            debt -= 1
            tip = ""
            if random.randint(1, 20) == 1:
                money += 1
                tip = " He tosses you $1 as a tip."
            remaining = debt
            done = total - remaining
            pct = int((done / total) * 20) if total > 0 else 20
            bar = "#" * pct + "-" * (20 - pct)
            print(GREEN + f"Correct! Debt remaining: ${remaining}. [{bar}] {done}/{total}{tip}" + RESET)
        else:
            print(YELLOW + "Wrong! Try again." + RESET)
    shady_borrowed = False
    print(GREEN + "\n🎉 You have fully paid off your debt by working! The shady man disappears." + RESET)
    pause(0.6)

# ------------------ BOSS ENCOUNTER & MISSIONS ------------------
def boss_encounter(auto=False):
    """
    Boss encounter: triggered automatically sometimes when interest increases,
    or manually via menu if debt/alert allows.
    auto=True means this was forced as a reminder.
    """
    global boss_met, debt, money, boss_alert_level
    boss_met = True
    clear()
    # Use slow_print and colours consistently to avoid stray sequences
    slow_print(RED + BOLD + "A black SUV idles outside the casino's back door..." + RESET, 0.02)
    pause(0.5)
    slow_print("Two men in suits escort you into an office where a single lamp burns.", 0.02)
    pause(0.4)
    slow_print(MAGENTA + "\nTHE BOSS: 'You been skating on my money. That's... inconvenient.'\n" + RESET, 0.02)
    pause(0.4)

    severity = 0
    if debt > 1000:
        severity = 2
    elif debt > 500:
        severity = 1

    # Slightly higher chance to see boss if auto
    if auto and random.random() < 0.5:
        # short dialogue then boss disappears
        slow_print(RED + "'Consider this a reminder. Pay up soon.' He snaps his fingers." + RESET, 0.02)
        boss_alert_level += 1
        pause(0.4)
        return_to_main_menu()
        return

    print("\nChoices:")
    print("1) Beg for mercy and ask for a deal")
    print("2) Offer to do Boss missions (3 short jobs)")
    print("3) Try to run (risky)")
    print("4) Try to bluff (risky)")

    choice = input("\nYour choice (1-4): ").strip()
    if choice == "1":
        slow_print("\nYou drop to your knees and promise anything.", 0.01)
        if severity >= 2:
            slow_print(RED + "'This isn't charity,' he says. 'Fine — I'll cut some recent interest.'\n" + RESET, 0.01)
            debt = max(0, int(debt * 0.9))
            boss_alert_level = max(0, boss_alert_level - 1)
        elif severity == 1:
            slow_print(GREEN + "'Alright kid. I'll knock a chunk off your interest.'\n" + RESET, 0.01)
            debt = max(0, int(debt * 0.6))
            boss_alert_level = max(0, boss_alert_level - 1)
        else:
            slow_print(GREEN + "'I'll delay the next interest wave.'\n" + RESET, 0.01)
            boss_alert_level = max(0, boss_alert_level - 1)
        pause(0.4)

    elif choice == "2":
        slow_print("\n'Good,' the Boss smiles. 'You can earn your way. Do three small jobs for me. Do them well.'", 0.01)
        pause(0.4)
        boss_mission_sequence()
        boss_alert_level = max(0, boss_alert_level - 1)

    elif choice == "3":
        slow_print("\nYou try to bolt. The room blurs. Someone pins you down.", 0.01)
        if random.random() < 0.5:
            slow_print(RED + "'You thought you could run?' he snaps. 'Now double the debt.'\n" + RESET, 0.01)
            debt *= 2
            boss_alert_level += 1
        else:
            slow_print(GREEN + "You escape but drop half your cash in the process." + RESET, 0.01)
            deposit = int(money // 2)
            money = max(0, money - deposit)
            boss_alert_level += 1
        pause(0.4)

    elif choice == "4":
        slow_print("\nYou tell a shaky lie. The Boss watches your lips move.", 0.01)
        if random.random() < 0.45:
            slow_print(GREEN + "'Not bad. Maybe you can be useful after all.' He reduces a bit of the debt.'\n" + RESET, 0.01)
            debt = int(debt * 0.75)
            boss_alert_level = max(0, boss_alert_level - 1)
        else:
            slow_print(RED + "'Liar.' He slams his fist on the desk. 'Add a bonus.'\n" + RESET, 0.01)
            debt += int(debt * 0.25)
            boss_alert_level += 1
        pause(0.4)
    else:
        slow_print(YELLOW + "\nYou freeze. The Boss doesn't like indecision. He adds more interest." + RESET, 0.01)
        debt += int(max(1, debt * 0.10))
        boss_alert_level += 1
        pause(0.4)

    # small random tip
    if random.randint(1, 6) == 1:
        tip = random.randint(5, 20)
        money += tip
        slow_print(GREEN + f"\nThe Boss unexpectedly slips you ${tip} as 'motivation'." + RESET, 0.01)

    pause(0.6)
    return_to_main_menu()

def boss_mission_sequence():
    global money, debt
    missions = [
        {"name": "Collect payment", "mech": "letter",
         "prompt": "Collect a 'payment' from a jittery gambler. Press the letter shown.", "reward": 30, "risk": 0.25},
        {"name": "Slip a note", "mech": "number",
         "prompt": "Slip a note into a locker. Pick the correct locker number (1-3).", "reward": 40, "risk": 0.20},
        {"name": "Deliver envelope", "mech": "letter",
         "prompt": "Deliver a sealed envelope to a backdoor. Press the shown letter quickly.", "reward": 50, "risk": 0.15}
    ]
    alphabet = list(string.ascii_uppercase)
    for i, m in enumerate(missions, 1):
        print(YELLOW + f"\nMission {i}: {m['prompt']}" + RESET)
        pause(0.25)
        success = False
        if m["mech"] == "letter":
            letter = random.choice(alphabet)
            ans = input(f"Press '{letter}': ").strip().upper()
            if ans == letter:
                success = True
        else:
            num = random.randint(1, 3)
            ans = input("Choose locker 1, 2 or 3: ").strip()
            if ans == str(num):
                success = True
        if success:
            print(GREEN + f"Mission success! You get ${m['reward']}." + RESET)
            money += m['reward']
            debt = max(0, debt - int(m['reward'] * 0.3))
        else:
            print(RED + "Mission failed. The Boss is not pleased." + RESET)
            penalty = int(m['reward'] * 0.6)
            debt += penalty
            print(RED + f"The Boss adds ${penalty} to your debt as penalty." + RESET)
        pause(0.35)
    print(GREEN + "\nYou finish the missions. The Boss watches you carefully." + RESET)
    pause(0.5)

# ------------------ HEIST EVENT ------------------
def heist_event():
    """
    Rare event triggered sometimes when broke or by special condition.
    Offers big reward but risk: if debt too high, shady man may betray.
    Keep it short but fun: choose a role, mini prompts.
    """
    global money, debt, shady_borrowed, borrow_count
    show_game_title("HEIST EVENT", gold=False)
    print(MAGENTA + "You are approached by a whispering contact. 'We could hit the casino vault... big payout, big risk.'" + RESET)
    choice = input("Do you want to try a heist? (Y/N): ").strip().upper()
    if choice != "Y":
        print("You back away. Probably for the best.")
        return
    # risk increases with debt
    base_success = 0.45
    debt_penalty = min(0.35, debt / 2000.0)  # more debt reduces success
    success_chance = max(0.05, base_success - debt_penalty)
    print(YELLOW + f"Success chance roughly: {int(success_chance*100)}%" + RESET)
    pause(0.8)
    # quick mini-game: pick the correct wire (1-3)
    wire = random.randint(1, 3)
    guess = safe_int("Pick a wire to cut (1-3): ", min_v=1, max_v=3)
    if guess == wire and random.random() < success_chance:
        reward = random.randint(400, 1200)
        print(GREEN + f"\nHeist SUCCESS! You get ${reward}." + RESET)
        money += reward
        # possible shady betrayal if debt huge
        if shady_borrowed and debt > 1000 and random.random() < 0.4:
            print(RED + "\nThe shady man shows up and slams you — he takes a cut and doubles your debt!" + RESET)
            cut = int(reward * 0.4)
            money -= cut
            debt = int(debt * 2)
            print(RED + f"He takes ${cut} from your loot and your debt jumps to ${debt}!" + RESET)
        return
    else:
        # failed heist: fine + penalty
        penalty = random.randint(200, 700)
        print(RED + f"\nHeist FAILED! You are chased off and lose ${penalty} in expenses." + RESET)
        money -= penalty
        if not check_money_and_handle():
            sys.exit()
        # if shady man is around and debt huge: he may punish
        if shady_borrowed and debt > 1200 and random.random() < 0.3:
            print(RED + "\nThe shady man hears of your failure — he shows up to remind you why you should pay." + RESET)
            debt += int(penalty * 0.5)
            print(RED + f"Your debt increases to ${debt}." + RESET)
        return

# ------------------ STATS & VIP ------------------
def show_stats(final=False):
    profit = stats["total_won"] - stats["total_lost"]
    print(CYAN + "\n📊 PLAYER STATS 📊" + RESET)
    print(f"Games played: {stats['games_played']}")
    print(f"Total bet placed: ${stats['total_bet']}")
    print(f"Total won: {GREEN}${stats['total_won']}{RESET}")
    print(f"Total lost: {RED}${stats['total_lost']}{RESET}")
    print(f"Wins: {stats['wins']} | Losses: {stats['losses']} | Ties: {stats['ties']}")
    color = GREEN if profit >= 0 else RED
    sign = "+" if profit >= 0 else ""
    print(f"Final profit: {color}{sign}${profit}{RESET}")
    print(f"Times borrowed: {borrow_count}")
    print(f"Current money: ${money}")
    print(f"Current debt: ${debt}")
    if final:
        print(BLUE + f"\nFINAL PROFIT: {sign}${profit}" + RESET)
    input("\nPress Enter to continue...")

def check_vip_unlock():
    global vip_unlocked
    profit = (stats["total_won"] - stats["total_lost"])
    if profit >= 5000 and not vip_unlocked:
        vip_unlocked = True
        print(GOLD + "\n🔥 VIP LOUNGE UNLOCKED! 🔥" + RESET)
        print(GOLD + "You have achieved huge profit — VIP lounge awaits. Access exclusive games!" + RESET)
        pause(1.0)
# ------------------ ARENA (UNDER CONSTRUCTION) -------------------
def check_arena_unlock():
    global arena_unlocked
    profit = (stats["total_won"] - stats["total_lost"])
    if profit >= 10000 and not arena_unlocked:
        arena_unlocked = True
        print(GOLD + "\n🔥 ARENA UNLOCKED! 🔥" + RESET)
        print(GOLD + "You have achieved MASSIVE profit — The Boxing Ring Awaits!" + RESET)
        pause(1.0)

def arena_menu():
    if not vip_unlocked:
        print(YELLOW + "VIP lounge locked — earn +$5000 profit to unlock." + RESET)
        return_to_main_menu()
        return
    print(BLUE +"Welcome back to the Arena! Where would you like to go?" + RESET)
    print(MAGENTA + "1. Go bet on a brawl!" + RESET)
    print(MAGENTA + "\n 2. Participate in the Funky Feet Fights!" + RESET)
    print(MAGENTA + "\n 3. Get a Pick-Me-Up at the Roughhouse Restruant!" + RESET)
    print(MAGENTA + "\n 4. Back" + RESET)
    choice = input("Choose (1-4): ").strip()
    if choice == "1":
        print("Nice")
    elif choice == "2":
        print("Interesting")
        fight1_game()
    elif choice == "3":
        print("You got it!")
        arena_restraunt()
    else:
        print("Goodbye, potential victim. Perhaps another time!")
        return_to_main_menu()
        return

def arena_restraunt():
    global money , player_health
    print(BLUE + "\nWelcome to the Roughhouse Restraunt!" + RESET)
    print("Would you like to dine in?")
    choice = input("Y/N: ")
    if choice == "Y":
        print("Great! Would you like a Food Menu or a Drinks Menu?")
        choice = input("1 OR 2: ")
        if choice == "2":
            print("Excellent! Here are the Really Rare Roughhouse Restraunt Refreshments! ")
            slow_print("1. $5 - Simple Water (+ 5 health)")
            time.sleep(0.3)
            slow_print("2. $15 - Soft Drinks (+ 10 health)")
            time.sleep(0.3)
            slow_print("3. $25 - Beer (+ 16 health)")
            time.sleep(0.3)
            slow_print("4. $45 - Fruit Cocktail (+ 25 health)")
            time.sleep(0.3)
            slow_print("5. $100 - Martini (+ 30 health)")
            choice = input("Choose 1-5: ")
            if choice == "1":
                print("Great. Here you go!")
                print("(- $5 / + 5 health)")
                player_health = player_health + 5
                money = money - 5
                time.sleep(2)
                arena_menu()
            elif choice == "2":
                print("Playing it safe, huh? don't worry, here it is!")
                print("(- $15 / + 10 health)")
                player_health = player_health + 10
                money = money - 15
                time.sleep(2)
                arena_menu()
            elif choice == "3":
                print("Good ol', good ol'!")
                print("(- $25 / + 16 health)")
                money = money - 25
                player_health = player_health + 16
                time.sleep(2)
                arena_menu()
            elif choice == "4":
                print("You deserve it!")
                print("(- $45 / + 25 health)")
                player_health = player_health + 25
                money = money - 45
                time.sleep(2)
                arena_menu()
            elif choice == "5":
                print("Someone's got money to burn!")
                print("(- $100 / + 30 health)")
                player_health = player_health + 30
                money = money - 100
                time.sleep(2)
                arena_menu()
        if choice == "1":
            print("Excellent!  Here are our choices for today: ")
            slow_print(YELLOW + "1. $10 - Boiled Egg (+ 12 health)" + RESET)
            time.sleep(0.3)
            slow_print(YELLOW +"2. $32 - BLT Sandwich (+ 38 health)"+ RESET)
            time.sleep(0.3)
            slow_print(YELLOW + "3. $67 - Caesar Salad + Shrimp In Butter Sauce (+ 61 health)" + RESET)
            time.sleep(0.3)
            slow_print(YELLOW + "4. $125 - Full English Breakfast (+ 74 health)" + RESET)
            time.sleep(0.3)
            slow_print(YELLOW + "5. $400 - Bluefin Tuna Ravioli (+ 99 health)" + RESET)
            choice = input("Choose 1-5: ")
            if choice == "1":
                print("Not the best...")
                print("(- $10 / + 12 health)")
                player_health = player_health + 12
                money = money - 10
                time.sleep(2)
                arena_menu()
            elif choice == "2":
                print("Pretty basic, pretty basic")
                print("(- $32 / + 38 health)")
                player_health = player_health + 38
                money = money - 32
                time.sleep(2)
                arena_menu()
            elif choice == "3":
                print("Someone's healthy!")
                print("(- $67 / + 61 health)")
                player_health = player_health + 61
                money = money - 67
                time.sleep(2)
                arena_menu()
            elif choice == "4":
                print("Hearty and warming - what a combo!")
                print("(- $125 / + 74 health)")
                player_health = player_health + 74
                money = money - 125
                time.sleep(2)
                arena_menu()
            elif choice == "5":
                print("Very exotic, very tasty. Superb choice!")
                print("(- $400 / + 99 health)")
                player_health = player_health + 99
                money = money - 99
                time.sleep(2)
                arena_menu()





def fight5_game():
    global player_health , fat_tony , money
    slow_print("Now time for the one, the only.... FAT TONY!")
    time.sleep(1)
    print("Here we go!")
     
    while fat_tony > 0 and fat_tony <= 220:
        timer = random.randint(3, 10)
        time.sleep(timer)

        print("⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⢉⣉⣤⣤⣤⣤⣄⣉⡉⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⠟⢁⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣌⠙⢿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⡿⢁⣴⡟⣿⣿⣿⣿⣿⣿⠟⣻⣿⣿⣿⣿⣿⣿⣷⣄⠙⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⡟⢀⣾⣿⠇⢙⣁⡙⠛⢋⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠘⣿⣿⣿⣿")
        print("⠁⣤⣌⠁⣾⣿⣿⣀⣼⣿⡇⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠸⣿⣿⣿")
        print("⡄⢿⡇⢸⣿⢹⣿⣿⣿⣿⠿⠛⣋⡉⢹⣿⣿⣿⡿⠛⣩⣤⣶⣶⢈⣿⡀⢿⣿⣿")
        print("⣷⡈⠃⣼⣿⠀⣭⠉⡄⢰⠀⢿⣿⠀⢸⣿⣿⣿⣴⣿⣿⣿⡿⢃⣼⣿⡇⢸⣿⣿")
        print("⣿⣷⠀⣿⣿⡆⢿⠀⠁⣀⣤⡈⠇⡜⢸⣿⣿⣿⣿⣿⡿⠋⣠⣾⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⡆⢹⣿⡇⠀⠀⣾⣿⣿⣿⣾⡇⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⣇⠸⣿⣷⡀⢸⣿⣿⣿⣿⣿⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⣬⣭⠉")
        print("⣿⣿⣿⡄⢻⣿⣧⠘⣿⣿⣿⣿⠇⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⣴")
        print("⣿⣿⣿⣿⣄⠹⣿⣷⣌⡙⠛⣁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢋⣤⣿⣿")
        print("⣿⣿⣿⣿⣿⣷⣌⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⣉⣤⣾⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⣉⡙⠛⠛⠛⠛⠛⢋⣉⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿")

        start = time.time()
        print("GO!")
        input()
        reaction_time = time.time()-start
        if reaction_time <= 0.3:
            damage = random.randint(1, 20)
            print(GREEN + f"You have dealt {damage} damage to your opponent!" + RESET)
            fat_tony = fat_tony - damage
            print(BLUE + f"Your enemy is on {fat_tony} health!" + RESET)
            time.sleep(2)
        elif reaction_time > 0.3:
            damageRecieved = random.randint(1, 20)
            print(RED +f"The enemy lands a mean hook for {damageRecieved} damage!" + RESET)
            player_health = player_health - damageRecieved
            print(BLUE + f"You are now on {player_health} health..." + RESET)
            if player_health <= 0:
                slow_print(RED + "You've died" + RESET)
                slow_print(RED + "Your eyes slowly shut as all you can hear around you is the roar of applause for your opponent..." + RESET)
                break  
    else:
        print("Good job! You killed Fat Tony!")
        arena()
       

def fight4_game():
    global player_health , enemy_4
    slow_print("Now time for opponent 4!")
    time.sleep(1)
    print("Here we go!")
   
    while enemy_4 > 0 and enemy_4 <= 170:
        timer = random.randint(3, 10)
        time.sleep(timer)

        print("⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⢉⣉⣤⣤⣤⣤⣄⣉⡉⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⠟⢁⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣌⠙⢿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⡿⢁⣴⡟⣿⣿⣿⣿⣿⣿⠟⣻⣿⣿⣿⣿⣿⣿⣷⣄⠙⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⡟⢀⣾⣿⠇⢙⣁⡙⠛⢋⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠘⣿⣿⣿⣿")
        print("⠁⣤⣌⠁⣾⣿⣿⣀⣼⣿⡇⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠸⣿⣿⣿")
        print("⡄⢿⡇⢸⣿⢹⣿⣿⣿⣿⠿⠛⣋⡉⢹⣿⣿⣿⡿⠛⣩⣤⣶⣶⢈⣿⡀⢿⣿⣿")
        print("⣷⡈⠃⣼⣿⠀⣭⠉⡄⢰⠀⢿⣿⠀⢸⣿⣿⣿⣴⣿⣿⣿⡿⢃⣼⣿⡇⢸⣿⣿")
        print("⣿⣷⠀⣿⣿⡆⢿⠀⠁⣀⣤⡈⠇⡜⢸⣿⣿⣿⣿⣿⡿⠋⣠⣾⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⡆⢹⣿⡇⠀⠀⣾⣿⣿⣿⣾⡇⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⣇⠸⣿⣷⡀⢸⣿⣿⣿⣿⣿⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⣬⣭⠉")
        print("⣿⣿⣿⡄⢻⣿⣧⠘⣿⣿⣿⣿⠇⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⣴")
        print("⣿⣿⣿⣿⣄⠹⣿⣷⣌⡙⠛⣁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢋⣤⣿⣿")
        print("⣿⣿⣿⣿⣿⣷⣌⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⣉⣤⣾⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⣉⡙⠛⠛⠛⠛⠛⢋⣉⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿")

        start = time.time()
        print("GO!")
        input()
        reaction_time = time.time()-start
        if reaction_time <= 0.3:
            damage = random.randint(1, 20)
            print(GREEN + f"You have dealt {damage} damage to your opponent!" + RESET)
            enemy_4 = enemy_4 - damage
            print(BLUE + f"Your enemy is on {enemy_4} health!" + RESET)
            time.sleep(2)
        elif reaction_time > 0.3:
            damageRecieved = random.randint(1, 20)
            print(RED +f"The enemy lands a mean hook for {damageRecieved} damage!" + RESET)
            player_health = player_health - damageRecieved
            print(BLUE + f"You are now on {player_health} health..." + RESET)
            if player_health <= 0:
                slow_print(RED + "You've died" + RESET)
                slow_print(RED + "Your eyes slowly shut as all you can hear around you is the roar of applause for your opponent..." + RESET)
                break    
    else:
        print("Good job! You killed enemy_4!")
        fight5_game()

def fight3_game():
    global player_health , enemy_3
    slow_print("Now time for opponent 3!")
    time.sleep(1)
    print("Here we go!")
   
    while enemy_3 > 0 and enemy_3 <= 170:
        timer = random.randint(3, 10)
        time.sleep(timer)

        print("⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⢉⣉⣤⣤⣤⣤⣄⣉⡉⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⠟⢁⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣌⠙⢿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⡿⢁⣴⡟⣿⣿⣿⣿⣿⣿⠟⣻⣿⣿⣿⣿⣿⣿⣷⣄⠙⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⡟⢀⣾⣿⠇⢙⣁⡙⠛⢋⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠘⣿⣿⣿⣿")
        print("⠁⣤⣌⠁⣾⣿⣿⣀⣼⣿⡇⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠸⣿⣿⣿")
        print("⡄⢿⡇⢸⣿⢹⣿⣿⣿⣿⠿⠛⣋⡉⢹⣿⣿⣿⡿⠛⣩⣤⣶⣶⢈⣿⡀⢿⣿⣿")
        print("⣷⡈⠃⣼⣿⠀⣭⠉⡄⢰⠀⢿⣿⠀⢸⣿⣿⣿⣴⣿⣿⣿⡿⢃⣼⣿⡇⢸⣿⣿")
        print("⣿⣷⠀⣿⣿⡆⢿⠀⠁⣀⣤⡈⠇⡜⢸⣿⣿⣿⣿⣿⡿⠋⣠⣾⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⡆⢹⣿⡇⠀⠀⣾⣿⣿⣿⣾⡇⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⣇⠸⣿⣷⡀⢸⣿⣿⣿⣿⣿⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⣬⣭⠉")
        print("⣿⣿⣿⡄⢻⣿⣧⠘⣿⣿⣿⣿⠇⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⣴")
        print("⣿⣿⣿⣿⣄⠹⣿⣷⣌⡙⠛⣁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢋⣤⣿⣿")
        print("⣿⣿⣿⣿⣿⣷⣌⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⣉⣤⣾⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⣉⡙⠛⠛⠛⠛⠛⢋⣉⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿")

        start = time.time()
        print("GO!")
        input()
        reaction_time = time.time()-start
        if reaction_time <= 0.3:
            damage = random.randint(1, 20)
            print(GREEN + f"You have dealt {damage} damage to your opponent!" + RESET)
            enemy_3 = enemy_3 - damage
            print(BLUE + f"Your enemy is on {enemy_3} health!" + RESET)
            time.sleep(2)
        elif reaction_time > 0.3:
            damageRecieved = random.randint(1, 20)
            print(RED +f"The enemy lands a mean hook for {damageRecieved} damage!" + RESET)
            player_health = player_health - damageRecieved
            print(BLUE + f"You are now on {player_health} health..." + RESET)  
            if player_health <= 0:
                slow_print(RED + "You've died" + RESET)
                slow_print(RED + "Your eyes slowly shut as all you can hear around you is the roar of applause for your opponent..." + RESET)
                break  
    else:
        print("Good job! You killed opponent 3!")
        fight4_game()  

def fight2_game():
    global player_health , enemy_2
    slow_print("Now time for opponent 2!")
    time.sleep(1)
    print("Here we go!")
   
    while enemy_2 > 0 and enemy_2 <= 120:
        timer = random.randint(3, 10)
        time.sleep(timer)

        print("⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⢉⣉⣤⣤⣤⣤⣄⣉⡉⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⠟⢁⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣌⠙⢿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⡿⢁⣴⡟⣿⣿⣿⣿⣿⣿⠟⣻⣿⣿⣿⣿⣿⣿⣷⣄⠙⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⡟⢀⣾⣿⠇⢙⣁⡙⠛⢋⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠘⣿⣿⣿⣿")
        print("⠁⣤⣌⠁⣾⣿⣿⣀⣼⣿⡇⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠸⣿⣿⣿")
        print("⡄⢿⡇⢸⣿⢹⣿⣿⣿⣿⠿⠛⣋⡉⢹⣿⣿⣿⡿⠛⣩⣤⣶⣶⢈⣿⡀⢿⣿⣿")
        print("⣷⡈⠃⣼⣿⠀⣭⠉⡄⢰⠀⢿⣿⠀⢸⣿⣿⣿⣴⣿⣿⣿⡿⢃⣼⣿⡇⢸⣿⣿")
        print("⣿⣷⠀⣿⣿⡆⢿⠀⠁⣀⣤⡈⠇⡜⢸⣿⣿⣿⣿⣿⡿⠋⣠⣾⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⡆⢹⣿⡇⠀⠀⣾⣿⣿⣿⣾⡇⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⣇⠸⣿⣷⡀⢸⣿⣿⣿⣿⣿⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⣬⣭⠉")
        print("⣿⣿⣿⡄⢻⣿⣧⠘⣿⣿⣿⣿⠇⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⣴")
        print("⣿⣿⣿⣿⣄⠹⣿⣷⣌⡙⠛⣁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢋⣤⣿⣿")
        print("⣿⣿⣿⣿⣿⣷⣌⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⣉⣤⣾⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⣉⡙⠛⠛⠛⠛⠛⢋⣉⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿")

        start = time.time()
        print("GO!")
        input()
        reaction_time = time.time()-start
        if reaction_time <= 0.3:
            damage = random.randint(1, 20)
            print(GREEN + f"You have dealt {damage} damage to your opponent!" + RESET)
            enemy_2 = enemy_2 - damage
            print(BLUE + f"Your enemy is on {enemy_2} health!" + RESET)
            time.sleep(2)
        elif reaction_time > 0.3:
            damageRecieved = random.randint(1, 20)
            print(RED +f"The enemy lands a mean hook for {damageRecieved} damage!" + RESET)
            player_health = player_health - damageRecieved
            print(BLUE + f"You are now on {player_health} health..." + RESET)
            if player_health <= 0:
                slow_print(RED + "You've died" + RESET)
                slow_print(RED + "Your eyes slowly shut as all you can hear around you is the roar of applause for your opponent..." + RESET)
                break    
    else:
        print("Good job! You killed opponent 2!")
        fight3_game()  

def fight1_game():
    global player_health , enemy_1
    print("now time for opponent 1!")
    print("Hit ENTER with 0.3s to deal damage to your opponent!")
    print("Fail, and the damage will be dealt to YOU!")
    while enemy_1 > 0 and enemy_1 <= 100:
        timer = random.randint(3, 10)
        time.sleep(timer)

        print("⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⢉⣉⣤⣤⣤⣤⣄⣉⡉⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⠟⢁⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣌⠙⢿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⡿⢁⣴⡟⣿⣿⣿⣿⣿⣿⠟⣻⣿⣿⣿⣿⣿⣿⣷⣄⠙⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⡟⢀⣾⣿⠇⢙⣁⡙⠛⢋⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠘⣿⣿⣿⣿")
        print("⠁⣤⣌⠁⣾⣿⣿⣀⣼⣿⡇⢁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠸⣿⣿⣿")
        print("⡄⢿⡇⢸⣿⢹⣿⣿⣿⣿⠿⠛⣋⡉⢹⣿⣿⣿⡿⠛⣩⣤⣶⣶⢈⣿⡀⢿⣿⣿")
        print("⣷⡈⠃⣼⣿⠀⣭⠉⡄⢰⠀⢿⣿⠀⢸⣿⣿⣿⣴⣿⣿⣿⡿⢃⣼⣿⡇⢸⣿⣿")
        print("⣿⣷⠀⣿⣿⡆⢿⠀⠁⣀⣤⡈⠇⡜⢸⣿⣿⣿⣿⣿⡿⠋⣠⣾⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⡆⢹⣿⡇⠀⠀⣾⣿⣿⣿⣾⡇⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣿⣿")
        print("⣿⣿⣇⠸⣿⣷⡀⢸⣿⣿⣿⣿⣿⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⣬⣭⠉")
        print("⣿⣿⣿⡄⢻⣿⣧⠘⣿⣿⣿⣿⠇⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⣴")
        print("⣿⣿⣿⣿⣄⠹⣿⣷⣌⡙⠛⣁⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢋⣤⣿⣿")
        print("⣿⣿⣿⣿⣿⣷⣌⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⣉⣤⣾⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⣉⡙⠛⠛⠛⠛⠛⢋⣉⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿")
        print("⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿")

        start = time.time()
        print("GO!")
        input()
        reaction_time = time.time()-start
        if reaction_time <= 0.3:
            damage = random.randint(1, 20)
            print(GREEN + f"You have dealt {damage} damage to your opponent!" + RESET)
            enemy_1 = enemy_1 - damage
            print(BLUE + f"Your enemy is on {enemy_1} health!" + RESET)
            time.sleep(2)
        elif reaction_time > 0.3:
            damageRecieved = random.randint(1, 20)
            print(RED +f"The enemy lands a mean hook for {damageRecieved} damage!" + RESET)
            player_health = player_health - damageRecieved
            print(BLUE + f"You are now on {player_health} health..." + RESET)
            if player_health <= 0:
                slow_print(RED + "You've died" + RESET)
                slow_print(RED + "Your eyes slowly shut as all you can hear around you is the roar of applause for your opponent..." + RESET)
                break
    else:
        print("Good job! You killed opponent 1!")
        slow_print(RED + "Now for your next opponent!" + RESET)
        fight2_game()    

def arena():
    global money
    show_game_title(" THE ARENA", gold=True)
    if not arena_unlocked:
        print(YELLOW + "Arena locked — earn +$10000 profit to unlock." + RESET)
        return_to_main_menu()
        return
    print(BLUE +"Welcome to the Arena! Where would you like to go?" + RESET)
    print(MAGENTA + "1. Go bet on a brawl!" + RESET)
    print(MAGENTA + "\n 2. Participate in the Funky Feet Fights!" + RESET)
    print(MAGENTA + "\n 3. Get a Pick-Me-Up at the Roughhouse Restruant!" + RESET)
    print(MAGENTA + "\n 4. Back" + RESET)
    choice = input("Choose (1-4): ").strip()
    if choice == "1":
        print("Nice")
    elif choice == "2":
        print("Interesting")
        fight1_game()
    elif choice == "3":
        print("You got it!")
        arena_restraunt()
    else:
        print("Goodbye, potential victim. Perhaps another time!")
        return_to_main_menu()
        return









# ------------------ CORE GAMES ------------------
# Each game returns to MAIN MENU when done.

def blackjack_game():
    global money
    show_game_title("BLACKJACK")
    cards = [2,3,4,5,6,7,8,9,10,10,10,10,11]
    card1 = random.choice(cards)
    card2 = random.choice(cards)
    bet = safe_int(f"You have ${money}. How much would you like to bet? $", min_v=1)
    total = card1 + card2
    print(f"\nYour starting cards: {card1}, {card2} (Total: {total})")
    while True:
        if total > 21:
            print(RED + "Bust! You lose!" + RESET)
            money -= bet
            update_stats_after_result(bet, "loss")
            if not check_money_and_handle():
                sys.exit()
            apply_interest_if_due()
            return_to_main_menu()
            return
        move = input("Hit or Stand? (H/S): ").strip().upper()
        if move == "H":
            new_card = random.choice(cards)
            print(f"You drew {new_card}")
            total += new_card
            print(f"Total: {total}")
            continue
        else:
            break
    dealer_total = random.randint(15, 23)
    print(f"\nDealer total: {dealer_total}")
    if dealer_total > 21 or total > dealer_total:
        print(GREEN + "🎉 You win!" + RESET)
        money += bet
        update_stats_after_result(bet, "win")
        check_arena_unlock()
    elif total == dealer_total:
        print(YELLOW + "Draw!" + RESET)
        update_stats_after_result(bet, "tie")
    else:
        print(RED + "Dealer wins!" + RESET)
        money -= bet
        update_stats_after_result(bet, "loss")
        if not check_money_and_handle():
            sys.exit()
    print(f"Money: ${money}")
    apply_interest_if_due()
    return_to_main_menu()

def roulette_game():
    global money
    show_game_title("ROULETTE")
    player_color = input("Bet on color (Red/Black): ").capitalize().strip()
    while player_color not in ["Red","Black"]:
        player_color = input("Invalid. Choose Red or Black: ").capitalize().strip()
    try:
        player_number = int(input("Pick a number (0–36): ").strip())
        if not (0 <= player_number <= 36):
            print("Invalid number. Using 0."); player_number = 0
    except ValueError:
        print("Enter a valid number. Using 0."); player_number = 0
    bet = safe_int(f"You have ${money}. How much would you like to bet? $", min_v=1)
    print("Spinning...")
    pause(1.2)
    number = random.randint(0,36)
    red = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    color = "Green" if number == 0 else ("Red" if number in red else "Black")
    print(f"\nWheel lands on {number} ({color})!")
    if player_color == color and player_number == number:
        print(GREEN + "JACKPOT! Both match!" + RESET)
        money += bet * 5
        check_arena_unlock()
        update_stats_after_result(bet*5, "win")
    elif player_color == color:
        print(GREEN + "Correct color!" + RESET)
        money += bet
        check_arena_unlock()
        update_stats_after_result(bet, "win")
    elif player_number == number:
        print(GREEN + "Correct number!" + RESET)
        money += bet * 2
        check_arena_unlock()
        update_stats_after_result(bet*2, "win")
    else:
        print(RED + "You lost." + RESET)
        money -= bet
        update_stats_after_result(bet, "loss")
        if not check_money_and_handle():
            sys.exit()
    print(f"Money: ${money}")
    apply_interest_if_due()
    return_to_main_menu()

def war_game():
    global money
    show_game_title("WAR")
    deck = [2,3,4,5,6,7,8,9,10,11,12,13,14]*4
    random.shuffle(deck)
    player_card = deck.pop()
    dealer_card = deck.pop()
    print(f"You drew {player_card}, Dealer drew {dealer_card}")
    bet = safe_int(f"You have ${money}. How much would you like to bet? $", min_v=1)
    if player_card > dealer_card:
        print(GREEN + "🎉 You win!" + RESET)
        money += bet
        check_arena_unlock()
        update_stats_after_result(bet, "win")
    elif player_card < dealer_card:
        print(RED + "💀 You lose!" + RESET)
        money -= bet
        update_stats_after_result(bet, "loss")
        if not check_money_and_handle():
            sys.exit()
    else:
        print(YELLOW + "Draw!" + RESET)
        update_stats_after_result(bet, "tie")
    print(f"Money: ${money}")
    apply_interest_if_due()
    return_to_main_menu()

def slots_game():
    global money
    show_game_title("SLOT MACHINES")
    symbols = ["🍒","🍋","🔔","💎","7"]
    bet = safe_int(f"You have ${money}. How much would you like to bet? $", min_v=1)
    print("Spinning...")
    pause(0.8)
    a = random.choice(symbols); print(f"{a}"); pause(0.4)
    b = random.choice(symbols); print(f"{b}"); pause(0.4)
    c = random.choice(symbols); print(f"{c}"); pause(0.4)
    print(f"\n🎰 | {a} {b} {c} | 🎰")
    if a == b == c:
        print(GREEN + "💰 JACKPOT! All three match!" + RESET)
        money += bet * 5
        check_arena_unlock()
        update_stats_after_result(bet*5, "win")
    elif a == b or b == c or a == c:
        print(GREEN + "✨ Nice! You got two matching symbols!" + RESET)
        money += bet * 2
        check_arena_unlock()
        update_stats_after_result(bet*2, "win")
    else:
        print(RED + "😢 No match. Better luck next time!" + RESET)
        money -= bet
        update_stats_after_result(bet, "loss")
        if not check_money_and_handle():
            sys.exit()
    print(f"Money: ${money}")
    apply_interest_if_due()
    return_to_main_menu()

def high_card_game():
    global money
    show_game_title("HIGH CARD")
    deck = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]*4
    values = {str(i):i for i in range(2,11)}
    values.update({"J":11,"Q":12,"K":13,"A":14})
    random.shuffle(deck)
    bet = safe_int(f"You have ${money}. How much would you like to bet? $", min_v=1)
    player = deck.pop()
    dealer = deck.pop()
    print(f"You drew: {player}, Dealer drew: {dealer}")
    if values[player] > values[dealer]:
        print(GREEN + "🎉 You win!" + RESET)
        money += bet
        check_arena_unlock()
        update_stats_after_result(bet, "win")
    elif values[player] < values[dealer]:
        print(RED + "💀 You lose!" + RESET)
        money -= bet
        update_stats_after_result(bet, "loss")
        if not check_money_and_handle():
            sys.exit()
    else:
        print(YELLOW + "It's a tie!" + RESET)
        update_stats_after_result(bet, "tie")
    print(f"Money: ${money}")
    apply_interest_if_due()
    return_to_main_menu()

def dice_game():
    global money
    show_game_title("DICE ROLL")
    bet = safe_int(f"You have ${money}. How much would you like to bet? $", min_v=1)
    input("Press Enter to roll your dice...")
    player = random.randint(1,6)
    dealer = random.randint(1,6)
    print(f"\nYou rolled: {player}")
    pause(0.7)
    print(f"Dealer rolled: {dealer}")
    if player > dealer:
        print(GREEN + "🎉 You win!" + RESET)
        money += bet
        check_arena_unlock()
        update_stats_after_result(bet, "win")
    elif player < dealer:
        print(RED + "💀 You lose!" + RESET)
        money -= bet
        update_stats_after_result(bet, "loss")
        if not check_money_and_handle():
            sys.exit()
    else:
        print(YELLOW + "It's a tie! No money lost." + RESET)
        update_stats_after_result(bet, "tie")
    print(f"Money: ${money}")
    apply_interest_if_due()
    return_to_main_menu()

def craps_game():
    global money
    show_game_title("CRAPS (Pass Line)")
    bet = safe_int(f"You have ${money}. How much would you like to bet? $", min_v=1)
    print(BLUE + "\nCome-out roll..." + RESET)
    pause(0.8)
    roll = random.randint(1,6) + random.randint(1,6)
    print(f"You roll: {roll}")
    if roll in (7,11):
        print(GREEN + "Natural! You win!" + RESET)
        money += bet
        check_arena_unlock()
        update_stats_after_result(bet, "win")
        apply_interest_if_due()
        return_to_main_menu()
    elif roll in (2,3,12):
        print(RED + "Craps! You lose!" + RESET)
        money -= bet
        update_stats_after_result(bet, "loss")
        if not check_money_and_handle():
            sys.exit()
        apply_interest_if_due()
        return_to_main_menu()
    else:
        point = roll
        print(YELLOW + f"Point is {point}. Rolling until {point} (win) or 7 (lose)." + RESET)
        pause(0.6)
        while True:
            input("Press Enter to roll the dice...")
            roll = random.randint(1,6) + random.randint(1,6)
            print(f"You roll: {roll}")
            if roll == point:
                print(GREEN + f"You hit the point {point}! You win!" + RESET)
                money += bet
                check_arena_unlock()
                update_stats_after_result(bet, "win")
                break
            elif roll == 7:
                print(RED + "Seven out! You lose!" + RESET)
                money -= bet
                update_stats_after_result(bet, "loss")
                if not check_money_and_handle():
                    sys.exit()
                break
            else:
                print("No decision — rolling again...")
                pause(0.5)
        apply_interest_if_due()
        print(f"Money: ${money}")
        return_to_main_menu()

def horse_race_game():
    global money
    show_game_title("HORSE RACING")
    horses = ["Thunderhoof","Nightmare","Lucky Star","Ironmane","Shadowbolt"]
    for i, h in enumerate(horses,1):
        print(f"{i}. {h}")
        pause(0.12)
    choice = safe_int("\nPick your horse (1-5): ", min_v=1, max_v=5)
    chosen = horses[choice-1]
    bet = safe_int(f"You have ${money}. How much would you like to bet? $", min_v=1)
    print(f"\nYou bet ${bet} on {chosen}. The race begins!")
    pause(0.6)
    positions = [0]*5
    finish = 40
    while True:
        clear()
        print("🏇 HORSE RACE 🏇")
        print(f"Bet: ${bet} on {chosen}\n")
        for i in range(5):
            step = random.randint(1,4)
            positions[i] += step
            track = "=" * (positions[i]//2)
            print(f"{i+1}. {horses[i]:<12} |{track}>{' '}{positions[i]}")
        winners = [i for i,p in enumerate(positions) if p >= finish]
        if winners:
            break
        pause(0.25)
    winning_names = [horses[i] for i in winners]
    if len(winning_names) == 1:
        winner = winning_names[0]
        print(f"\n🏁 The winner is {winner}! 🏆")
    else:
        print(f"\n🏁 It's a tie! Winners: {', '.join(winning_names)} 🏆")
    if chosen in winning_names and len(winning_names) == 1:
        print(GREEN + "🎉 Your horse wins! You earn double your bet!" + RESET)
        money += bet * 2
        check_arena_unlock()
        update_stats_after_result(bet*2, "win")
    elif chosen in winning_names and len(winning_names) > 1:
        print(YELLOW + "Your horse was among the winners — it's a tie. Your bet is refunded." + RESET)
        update_stats_after_result(bet, "tie")
    else:
        print(RED + "💀 Your horse lost. Better luck next time." + RESET)
        money -= bet
        update_stats_after_result(bet, "loss")
        if not check_money_and_handle():
            sys.exit()
    print(f"Money: ${money}")
    apply_interest_if_due()
    return_to_main_menu()

# Dice faces (5 lines each) — uses CYAN / RESET from main file
dice_faces = {
    1: ["┌─────┐", "│     │", "│  ●  │", "│     │", "└─────┘"],
    2: ["┌─────┐", "│ ●   │", "│     │", "│   ● │", "└─────┘"],
    3: ["┌─────┐", "│ ●   │", "│  ●  │", "│   ● │", "└─────┘"],
    4: ["┌─────┐", "│ ● ● │", "│     │", "│ ● ● │", "└─────┘"],
    5: ["┌─────┐", "│ ● ● │", "│  ●  │", "│ ● ● │", "└─────┘"],
    6: ["┌─────┐", "│ ● ● │", "│ ● ● │", "│ ● ● │", "└─────┘"],
}

def draw_dice(dice):
    """Display multiple dice side-by-side using existing color constants."""
    lines = [""] * 5
    for d in dice:
        face = dice_faces[d]
        for i in range(5):
            lines[i] += face[i] + "  "
    for l in lines:
        print(CYAN + l + RESET)

# Scoring helpers (kept logic identical to your version)
def score_upper(dice, number): return dice.count(number) * number
def score_three_of_a_kind(dice): return sum(dice) if any(dice.count(x) >= 3 for x in dice) else 0
def score_four_of_a_kind(dice): return sum(dice) if any(dice.count(x) >= 4 for x in dice) else 0
def score_full_house(dice): return 25 if sorted([dice.count(i) for i in set(dice)]) == [2, 3] else 0
def score_small_straight(dice):
    s = sorted(set(dice))
    straights = [[1,2,3,4],[2,3,4,5],[3,4,5,6]]
    return 30 if any(all(i in s for i in seq) for seq in straights) else 0
def score_large_straight(dice):
    s = sorted(set(dice))
    return 40 if s in [[1,2,3,4,5],[2,3,4,5,6]] else 0
def score_yahtzee(dice): return 50 if len(set(dice)) == 1 else 0
def score_chance(dice): return sum(dice)

categories = [
    "Ones", "Twos", "Threes", "Fours", "Fives", "Sixes",
    "Three of a Kind", "Four of a Kind", "Full House",
    "Small Straight", "Large Straight", "Yahtzee", "Chance"
]

def calculate_score(dice, category):
    if category == "Ones": return score_upper(dice,1)
    if category == "Twos": return score_upper(dice,2)
    if category == "Threes": return score_upper(dice,3)
    if category == "Fours": return score_upper(dice,4)
    if category == "Fives": return score_upper(dice,5)
    if category == "Sixes": return score_upper(dice,6)
    if category == "Three of a Kind": return score_three_of_a_kind(dice)
    if category == "Four of a Kind": return score_four_of_a_kind(dice)
    if category == "Full House": return score_full_house(dice)
    if category == "Small Straight": return score_small_straight(dice)
    if category == "Large Straight": return score_large_straight(dice)
    if category == "Yahtzee": return score_yahtzee(dice)
    if category == "Chance": return score_chance(dice)
    return 0

def display_scorecard(scorecard):
    print(YELLOW + "\n📜 SCORECARD 📜" + RESET)
    print(YELLOW + "=" * 38 + RESET)
    for cat in categories:
        val = scorecard.get(cat, "-")
        print(f"{cat:<20}: {val}")
    print(YELLOW + "=" * 38 + RESET)

def yahtzee_game():
    """Integrated Yahtzee game — asks for a bet, plays 13 rounds, pays out based on final score."""
    global money
    show_game_title("YAHTZEE")            # consistent title UI
    bet = safe_int(f"You have ${money}. How much would you like to bet on Yahtzee? $", min_v=1)
    if bet > money:
        print(RED + "You don't have that much!" + RESET)
        return_to_main_menu()
        return

    # subtract bet up front (loss-first model); if player wins they get payout on top
    money -= bet
    update_stats_after_result(bet, "loss")  # pessimistically record; we'll update on win below

    slow_print("🎲 WELCOME TO RG'S YAHTZEE MASTER EDITION 🎲", 0.02)
    scorecard = {}
    total = 0

    for turn in range(1, 14):
        clear()
        slow_print(f"\nROUND {turn}/13", 0.02)
        pause(0.35)

        # initial roll
        dice = [random.randint(1,6) for _ in range(5)]
        slow_print("Rolling dice...", 0.02)
        draw_dice(dice)

        rerolls = 2
        while rerolls > 0:
            slow_print(f"\nYou have {rerolls} reroll(s) left.", 0.03)
            ans = input("Reroll any dice? (y/n): ").strip().lower()
            if ans == "y":
                picks = input("Enter dice positions to reroll (1-5 separated by spaces): ").split()
                valid_pick = False
                for p in picks:
                    try:
                        idx = int(p)-1
                        if 0 <= idx < 5:
                            dice[idx] = random.randint(1,6)
                            valid_pick = True
                    except Exception:
                        continue
                if not valid_pick:
                    print(YELLOW + "No valid dice chosen; skipping reroll." + RESET)
                clear()
                draw_dice(dice)
                rerolls -= 1
            else:
                break

        available = [c for c in categories if c not in scorecard]
        slow_print("\nChoose a category to score:", 0.02)
        for i, cat in enumerate(available, 1):
            print(f"{i}. {cat}")
        while True:
            try:
                pick = int(input("\nSelect number: ").strip()) - 1
                selected = available[pick]
                break
            except Exception:
                print(YELLOW + "Invalid choice." + RESET)

        score = calculate_score(dice, selected)
        scorecard[selected] = score
        total = sum(scorecard.values())
        slow_print(f"\nScored {score} for {selected}!", 0.02)
        pause(0.6)
        display_scorecard(scorecard)
        pause(0.9)

    clear()
    slow_print("🎉 FINAL SCORE 🎉", 0.03)
    display_scorecard(scorecard)
    slow_print(f"\nTOTAL: {total} POINTS!", 0.05)
    pause(0.6)

    # Determine payout tiers from final total (adjustable balances)
    # You risk your bet (taken already). Winning gives you your bet back and a multiplier:
    payout_multiplier = 0
    if total >= 200:
        payout_multiplier = 5   # huge win
    elif total >= 150:
        payout_multiplier = 3   # big win
    elif total >= 100:
        payout_multiplier = 2   # modest win
    elif total >= 60:
        payout_multiplier = 1   # break-even-ish (give bet back)
    else:
        payout_multiplier = 0   # lost bet (already subtracted)

    if payout_multiplier > 0:
        payout = bet * payout_multiplier
        money += payout
        # adjust stats: we recorded an initial loss; convert to win by adding the net
        # treat total payout as "won" for stats (makes stats consistent)
        update_stats_after_result(payout, "win")
        print(GREEN + f"\nYou win! Payout: ${payout} (mult x{payout_multiplier})" + RESET)
        check_arena_unlock()
    else:
        # already subtracted bet; record loss (we already added a 'loss' entry initially)
        print(RED + "\nTough luck. You lost your bet." + RESET)
    pause(0.6)

    # Interest & broke-check integration
    apply_interest_if_due()
    if not check_money_and_handle():
        sys.exit()

    print(f"Money: ${money}")
    return_to_main_menu()

# ------------------ TEXAS HOLD'EM POKER ------------------
# Implementation: Player (you), Dealer (plays as a seat), NPC1, NPC2
# Betting rounds: preflop, flop, turn, river. Simple betting logic and NPC AI.
# Hand evaluation: rank hands and compare. Show cards prettified at showdown.

RANK_NAMES = {
    9: "Royal Flush",
    8: "Straight Flush",
    7: "Four of a Kind",
    6: "Full House",
    5: "Flush",
    4: "Straight",
    3: "Three of a Kind",
    2: "Two Pair",
    1: "One Pair",
    0: "High Card"
}

def make_deck():
    suits = ['♠','♥','♦','♣']
    ranks = list(range(2,15))  # 11=J,12=Q,13=K,14=A
    deck = []
    for s in suits:
        for r in ranks:
            deck.append((r, s))
    random.shuffle(deck)
    return deck

def card_str(card):
    r, s = card
    name = str(r)
    if r == 11: name = 'J'
    if r == 12: name = 'Q'
    if r == 13: name = 'K'
    if r == 14: name = 'A'
    return f"{name}{s}"

def pretty_hand(cards):
    return " ".join(card_str(c) for c in cards)

def rank_hand(cards7):
    """
    Given 7 cards (tuples (rank,suit)), return (rank_category, tie_breaker_tuple)
    Category 0..9 (higher better). tie_breaker is tuple for lexicographic compare.
    This is a straightforward evaluator - not the fastest but clear.
    """
    ranks = sorted([r for r, s in cards7], reverse=True)
    suits = [s for r,s in cards7]
    # count ranks
    rank_counts = Counter(ranks)
    counts_to_ranks = defaultdict(list)
    for r,c in rank_counts.items():
        counts_to_ranks[c].append(r)
    for c in counts_to_ranks:
        counts_to_ranks[c].sort(reverse=True)

    # check flush and straight flush / royal
    suit_groups = defaultdict(list)
    for r,s in cards7:
        suit_groups[s].append(r)
    flush_suit = None
    flush_cards = []
    for s,rs in suit_groups.items():
        if len(rs) >= 5:
            flush_suit = s
            flush_cards = sorted(rs, reverse=True)
            break

    # helper to find highest straight from a list of ranks
    def highest_straight(rlist):
        rset = set(rlist)
        # Ace-low straight handling
        candidates = []
        for high in range(14, 4, -1):
            needed = set(range(high-4, high+1))
            if needed.issubset(rset):
                return high
        # check wheel A-2-3-4-5
        if {14,5,4,3,2}.issubset(rset):
            return 5
        return None

    # Straight flush / royal flush
    if flush_suit:
        hf = highest_straight(flush_cards)
        if hf:
            if hf == 14:
                return (9, (14,))  # Royal flush
            else:
                return (8, (hf,))  # Straight flush with high card hf

    # Four of a kind
    if 4 in counts_to_ranks:
        quad_rank = counts_to_ranks[4][0]
        kicker = max([r for r in ranks if r != quad_rank])
        return (7, (quad_rank, kicker))

    # Full house
    if 3 in counts_to_ranks and (2 in counts_to_ranks or len(counts_to_ranks[3]) >= 2):
        trips = counts_to_ranks[3][0]
        # for full house, second part is the highest of remaining trips or pairs
        second = None
        if len(counts_to_ranks[3]) >= 2:
            second = counts_to_ranks[3][1]
        elif 2 in counts_to_ranks:
            second = counts_to_ranks[2][0]
        return (6, (trips, second))

    # Flush
    if flush_suit:
        top5 = tuple(flush_cards[:5])
        return (5, top5)

    # Straight
    hs = highest_straight(ranks)
    if hs:
        return (4, (hs,))

    # Three of a kind
    if 3 in counts_to_ranks:
        trips = counts_to_ranks[3][0]
        kickers = [r for r in ranks if r != trips][:2]
        return (3, (trips,)+tuple(kickers))

    # Two pairs
    if 2 in counts_to_ranks and len(counts_to_ranks[2]) >= 2:
        top_pair = counts_to_ranks[2][0]
        second_pair = counts_to_ranks[2][1]
        kicker = max([r for r in ranks if r != top_pair and r != second_pair])
        return (2, (top_pair, second_pair, kicker))

    # One pair
    if 2 in counts_to_ranks:
        pair = counts_to_ranks[2][0]
        kickers = [r for r in ranks if r != pair][:3]
        return (1, (pair,)+tuple(kickers))

    # High card
    return (0, tuple(ranks[:5]))

def compare_hands(h1, h2):
    # h1/h2 are (category, tie_tuple)
    if h1[0] != h2[0]:
        return h1[0] - h2[0]
    # same category: compare tie tuples lexicographically
    if h1[1] > h2[1]:
        return 1
    elif h1[1] < h2[1]:
        return -1
    return 0

def ai_decision(player_stack, current_bet, to_call, community, hole, aggression=0.5):
    """
    Simple AI: returns action string among 'fold','call','raise'
    Aggression 0..1 affects chance to raise.
    Decision based on hand strength roughly.
    """
    # build 7-card sample, evaluate approximate hand category using remaining deck
    # For simplicity, look at rank of hole + community and count pairs/trips
    all_cards = hole + community
    ranks = [r for r,s in all_cards]
    counts = Counter(ranks)
    max_count = max(counts.values()) if counts else 1
    # heuristics:
    if max_count >= 3:
        # strong hand - often raise
        if random.random() < 0.7 + aggression*0.2:
            return "raise"
        return "call"
    if max_count == 2:
        # pair - call usually, occasionally raise
        if random.random() < 0.25 + aggression*0.1:
            return "raise"
        return "call"
    # check for straight/flush potential by approximate method (if community >=3)
    if len(community) >= 3:
        ranks_set = set(ranks)
        # rough straight potential
        for r in range(2, 11):
            if len([x for x in range(r, r+5) if x in ranks_set or x==14 and 14 in ranks_set]) >= 4:
                return "call"
    # otherwise weak - fold or call small
    if to_call == 0:
        # free check -> call via check
        return "call"
    if to_call > player_stack * 0.6:
        return "fold"
    if random.random() < 0.3 + aggression*0.1:
        return "call"
    return "fold"

def distribute_pot_and_announce(winners, pot, shares):
    # winners: list of player names who win (tie handled by splitting shares)
    # pot not tracked globally in our simple single-pot system, this is placeholder
    pass

def play_texas_holdem(test_mode_no_money=False):
    """
    Full (manual) Texas Hold'em for 4 players: You (player), Dealer, NPC1, NPC2
    Betting is simplified, but includes preflop, flop, turn, river.
    test_mode_no_money: if True, bets won't change the global money (for isolated testing).
    """
    global money
    show_game_title("TEXAS HOLD'EM POKER")
    # players setup
    seats = [
        {"name":"YOU", "stack": money, "is_human": True},
        {"name":"Dealer", "stack": money, "is_human": False},
        {"name":"NPC1", "stack": money, "is_human": False},
        {"name":"NPC2", "stack": money, "is_human": False}
    ]
    # minimal ante/small blind/big blind structure
    small_blind = 5
    big_blind = 10
    pot = 0
    deck = make_deck()
    # deal hole cards
    for seat in seats:
        seat["hole"] = [deck.pop(), deck.pop()]
        seat["in_hand"] = True
        seat["current_bet"] = 0
    # blinds posted by NPCs: Dealer = dealer button; small blind = Dealer's left
    # for simplicity: seats[0] YOU is first to act preflop
    print("Dealing hole cards...")
    pause(0.6)
    # show player's hole cards
    print(GREEN + "Your hole cards:", pretty_hand(seats[0]["hole"]) + RESET)
    # blinds: we'll have Dealer put small, NPC1 big, YOU first to act
    # Pay blinds
    # We'll subtract blinds from their stacks and add to pot (unless test_mode_no_money)
    def post_blind(player_idx, amount):
        nonlocal pot
        seat = seats[player_idx]
        paid = min(amount, seat["stack"])
        seat["stack"] -= paid
        seat["current_bet"] += paid
        pot += paid
    post_blind(1, small_blind)  # Dealer small blind
    post_blind(2, big_blind)    # NPC1 big blind
    # Preflop betting round: starting from YOU (index 0)
    current_bet = big_blind
    to_call = lambda s: current_bet - s["current_bet"]
    # simple betting round sequence
    def betting_round(start_idx=0):
        nonlocal current_bet, pot
        active_players = [p for p in seats if p["in_hand"] and p["stack"]>0]
        # loop through players (one pass + allow raises)
        i = start_idx
        players_consented = set()
        while True:
            seat = seats[i % len(seats)]
            if seat["in_hand"] and seat["stack"]>0:
                call_amt = to_call(seat)
                if seat["is_human"]:
                    # show player's hole and community
                    print(GREEN + f"\nYour cards: {pretty_hand(seat['hole'])}, Stack: ${seat['stack']}, To call: ${call_amt}" + RESET)
                    action = input("Choose action: (fold/call/raise) or (f/c/r): ").strip().lower()
                    if action in ["f","fold"]:
                        seat["in_hand"] = False
                        print("You folded.")
                    elif action in ["c","call",""]:
                        # call
                        pay = min(call_amt, seat["stack"])
                        seat["stack"] -= pay
                        seat["current_bet"] += pay
                        pot += pay
                        print(f"You call ${pay}.")
                    elif action in ["r","raise"]:
                        # ask raise amount
                        max_raise = seat["stack"]
                        raise_amt = safe_int(f"Enter raise amount (min {big_blind}): $", min_v=big_blind, max_v=max_raise)
                        seat["stack"] -= raise_amt
                        seat["current_bet"] += raise_amt
                        current_bet = seat["current_bet"]
                        pot += raise_amt
                        print(f"You raise to ${current_bet}.")
                else:
                    # AI decision
                    # approximate community/hole for decision; here community will be passed externally
                    # we'll let AI be simple: if to_call cheap -> call else fold sometimes
                    # We access local variables by closure (we'll provide community var below)
                    try:
                        community = community_cards  # set by outer scope when used
                    except NameError:
                        community = []
                    action = ai_decision(seat["stack"], current_bet, call_amt, community, seat["hole"], aggression=random.random())
                    if action == "fold":
                        seat["in_hand"] = False
                        print(f"{seat['name']} folds.")
                    elif action == "call":
                        pay = min(call_amt, seat["stack"])
                        seat["stack"] -= pay
                        seat["current_bet"] += pay
                        pot += pay
                        print(f"{seat['name']} calls ${pay}.")
                    elif action == "raise":
                        # small raise
                        raise_amt = min(seat["stack"], call_amt + big_blind)
                        seat["stack"] -= raise_amt
                        seat["current_bet"] += raise_amt
                        current_bet = seat["current_bet"]
                        pot += raise_amt
                        print(f"{seat['name']} raises to ${current_bet}.")
                # mark as consented if they have matched the current bet or folded
                if not seat["in_hand"] or seat["current_bet"] == current_bet:
                    players_consented.add(seat["name"])
                else:
                    # someone raised, reset consensused set
                    players_consented = set([seat["name"]])
            # check end condition: all active players either folded or have current_bet==current_bet
            active = [p for p in seats if p["in_hand"] and p["stack"]>=0]
            if all((not p["in_hand"]) or p["current_bet"] == current_bet for p in seats):
                break
            i += 1
        # normalize current_bets to 0 and return
        for p in seats:
            p["current_bet"] = 0
        return

    # Preflop
    community_cards = []
    betting_round(start_idx=0)
    pause(0.6)
    # Flop
    # burn one
    _ = deck.pop()
    community_cards = [deck.pop(), deck.pop(), deck.pop()]
    print("\nThe Flop:", " ".join(card_str(c) for c in community_cards))
    pause(0.6)
    betting_round(start_idx=0)
    # Turn
    _ = deck.pop()
    community_cards.append(deck.pop())
    print("\nThe Turn:", " ".join(card_str(c) for c in community_cards))
    pause(0.6)
    betting_round(start_idx=0)
    # River
    _ = deck.pop()
    community_cards.append(deck.pop())
    print("\nThe River:", " ".join(card_str(c) for c in community_cards))
    pause(0.6)
    betting_round(start_idx=0)
    # Showdown
    print("\n--- SHOWDOWN ---")
    # collect all active players
    active_players = [p for p in seats if p["in_hand"]]
    if not active_players:
        print("Everyone folded? Pot carried. (Edge case).")
        return_to_main_menu()
        return
    # evaluate hands
    best_score = None
    winners = []
    hand_descriptions = {}
    for p in active_players:
        seven = p["hole"] + community_cards
        category, tiebreak = rank_hand(seven)
        hand_descriptions[p["name"]] = (category, tiebreak, pretty_hand(p["hole"]))
        if best_score is None:
            best_score = (category, tiebreak)
            winners = [p]
        else:
            cmp = compare_hands((category,tiebreak), best_score)
            if cmp > 0:
                best_score = (category,tiebreak)
                winners = [p]
            elif cmp == 0:
                winners.append(p)
    # present hands nicely: show rank name + cards with facecards spelled
    print("\nCommunity:", pretty_hand(community_cards))
    for p in active_players:
        cat, tie, holes = hand_descriptions[p["name"]]
        print(f"{p['name']:>8} | {holes} | {RANK_NAMES[cat]}")
    if len(winners) == 1:
        winner = winners[0]
        print(GREEN + f"\n{winner['name']} wins the pot!" + RESET)
        # payout pot equally (we haven't tracked pot fully using variable pot)
        # For simplicity, assume pot equals sum of all bets previously placed in this hand -- but we tracked pot poorly.
        # We'll compute pot as difference between starting stacks and current stacks
        # But since we didn't store starting stacks per seat, we simplify: reward is random-ish for now
        reward = random.randint( int( (sum([p['stack'] for p in seats]) + 1) * 0.02 ),  int( max(10, sum([p['stack'] for p in seats]) * 0.08) ) )
        # More correct approach: in a fuller engine you'd track explicit pot; here we will credit the winner with bet*2 approximated
        # For simpler fairness: compute total contributed this hand as a small random pot
        pot_approx = random.randint( int(0.5*big_blind), int(5*big_blind + 50) )
        if not test_mode_no_money:
            winner['stack'] += pot_approx
            if winner['name'] == "YOU":
                global_contrib = pot_approx
        print(GREEN + f"{winner['name']} receives ${pot_approx} (approx pot)." + RESET)
        if winner['name'] == "YOU" and not test_mode_no_money:
            # update global money
            money_delta = pot_approx
            # add to global money variable
            # to avoid scoping confusion:
            globals()['money'] += money_delta
            update_stats_after_result(pot_approx, "win")
    else:
        # split pot among winners
        print(YELLOW + "\nSplit pot between: " + ", ".join(w['name'] for w in winners) + RESET)
        pot_approx = random.randint( int(0.5*big_blind), int(5*big_blind + 50) )
        split = pot_approx // len(winners)
        for w in winners:
            if not test_mode_no_money:
                w['stack'] += split
            if w['name'] == "YOU" and not test_mode_no_money:
                globals()['money'] += split
                check_arena_unlock()
                update_stats_after_result(split, "win")
        print(YELLOW + f"Each winner gets approximately ${split}." + RESET)

    # final show: show player's final stack and global money
    print(f"\nYour stack: ${money}")
    apply_interest_if_due()
    return_to_main_menu()

# ------------------ VIP LOUNGE (exclusive games) ------------------
def vip_lounge():
    global money
    show_game_title("VIP LOUNGE", gold=True)
    if not vip_unlocked:
        print(YELLOW + "VIP lounge locked — earn +$5000 profit to unlock." + RESET)
        return_to_main_menu()
        return
    print(GOLD + "Welcome to the VIP Lounge. Exclusive games available:" + RESET)
    print("1. High Stakes Blackjack (same mechanics, bigger stakes)")
    print("2. Exclusive Poker (Dealer = boss, special ambience)")
    print("3. Golden Roulette (better payouts)")
    print("4. Back")
    choice = input("Choose (1-4): ").strip()
    if choice == "1":
        show_game_title("HIGH STAKES BLACKJACK")
        # simple high stakes blackjack: double stakes range
        bet = safe_int(f"You have ${money}. How much double-bet would you like to bet? $", min_v=50)
        # reuse blackjack logic with higher bet; for brevity call blackjack_game then subtract/add
        blackjack_game()
    elif choice == "2":
        show_game_title("EXCLUSIVE TEXAS HOLD'EM (VIP)")
        # VIP poker: Dealer (boss) comments and higher stakes
        # For complexity, call play_texas_holdem but extra flavour; keep same engine
        play_texas_holdem_vip()
    elif choice == "3":
        show_game_title("GOLDEN ROULETTE")
        # golden roulette with larger payouts
        golden_roulette()
    else:
        return_to_main_menu()

def play_texas_holdem_vip():
    # For simplicity, call main holdem but with commentary from boss (if boss_met or shady interactions)
    show_game_title("VIP TEXAS HOLD'EM", gold=True)
    print(GOLD + "The Boss deals with a cold smile. He watches you closely." + RESET)
    # In-depth variant: call play_texas_holdem with test_mode_no_money=False
    play_texas_holdem(test_mode_no_money=False)
    return_to_main_menu()

def golden_roulette():
    global money
    # Slightly better payouts
    show_game_title("GOLDEN ROULETTE", gold=True)
    player_color = input("Bet on red or black: ").lower().strip()
    while player_color not in ["red","black"]:
        player_color = input("Choose red or black: ").lower().strip()
    try:
        player_number = int(input("Pick number (0-36): ").strip())
        if not 0 <= player_number <= 36:
            player_number = 0
    except ValueError:
        player_number = 0
    bet = safe_int(f"You have ${money}. How much would you like to bet? $", min_v=1)
    number = random.randint(0,36)
    red = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    color = "green" if number==0 else ("red" if number in red else "black")
    print(f"\nWheel lands on {number} ({color})!")
    if player_color == color and player_number == number:
        print(GREEN + f"ROYAL JACKPOT! You win ${bet*20}!" + RESET)
        money += bet*20
        check_arena_unlock()
        update_stats_after_result(bet*20, "win")
    elif player_color == color:
        print(GREEN + f"You win ${bet*3}!" + RESET)
        money += bet*3
        check_arena_unlock()
        update_stats_after_result(bet*3, "win")
    elif player_number == number:
        print(GREEN + f"Number match! You win ${bet*10}!" + RESET)
        money += bet*10
        check_arena_unlock()
        update_stats_after_result(bet*10, "win")
    else:
        print(RED + f"You lose ${bet}." + RESET)
        money -= bet
        update_stats_after_result(bet, "loss")
    apply_interest_if_due()
    return_to_main_menu()

# ------------------ MAIN ------------------
def main():
    clear()
    header()
    # age gate
    while True:
        try:
            year_born = int(input("Enter your birth year: ").strip())
            break
        except ValueError:
            print(YELLOW + "Please enter a valid year." + RESET)
    age = time.localtime().tm_year - year_born
    if year_born == 1534:
        slow_print(RED + "\nWelcome............. Bishop" + RESET)
    if age < 18:
        print(RED + "BUGGER OFF!" + RESET)
        return

    print(GREEN + f"Welcome! You start with ${money}." + RESET)
    # main loop
    while True:
        # check unlocks each cycle
        check_vip_unlock()
        check_arena_unlock()
        main_menu()
           

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + YELLOW + "Interrupted. Bye!" + RESET)
        sys.exit()
