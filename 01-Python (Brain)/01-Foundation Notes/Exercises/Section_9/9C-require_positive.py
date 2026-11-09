from functools import wraps

def require_positive(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            first_val = args[0]
            if first_val <= 0:
                raise ValueError(f"Damage[{first_val}] can't be less than zero")
            else:
                return func(*args, **kwargs)
        except ValueError as e:
            print(f"Error: {e}")
    return wrapper

@require_positive
def deal_damage(amount: int):
    print(f"{amount} DMG")

deal_damage(-5)
deal_damage(20)