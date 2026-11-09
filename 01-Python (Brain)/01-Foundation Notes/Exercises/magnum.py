def dash(num= 8, char: str = "=") -> str:
    print(char * num * 4)

    return f"Char type: {char} \nNum: {num}"

def title(name: str):
    dash()
    print(" " * 12, name)
    dash()

    return f"Title: {name}"

def exercise(num: int):
    return title(f"Exercise {num}")
