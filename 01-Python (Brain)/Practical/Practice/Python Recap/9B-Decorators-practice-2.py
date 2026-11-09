from functools import wraps

def double_damage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_args = [args[0], (args[1] * 2)]
        return func(*new_args, **kwargs)
    print(func.__name__)
    return wrapper


@double_damage
def deal_damage(enemy_name, damage):
    print(f"{enemy_name} takes {damage} raw damage!")

deal_damage("James Dean", 15)
