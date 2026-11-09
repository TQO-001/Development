from functools import wraps

def double_damage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("[Cheat Code Activated]: Doubling outgoing damage values!")

        newArgs = [args[0], args[1] * 2]

        return func(*newArgs, **kwargs)
    return wrapper

# ----------------------------- The Core Function ---------------------------- #
@double_damage
def deal_damage(enemy_name, damage):
    print(f"{enemy_name} takes {damage} raw damage!")

# ------------------------------ Test Execution ------------------------------ #
deal_damage("Goblin", 50)
print(f"Function Name Verified: {deal_damage.__name__}")