def dash(num :int = 8, char :str = '-', newline: bool = True):
    if newline:
        print(char * 4 * num)
    else:
        print(" " * 2 * num)
        yield

def title(name: str):
    num = 12
    dash(num=num)
    dash(num=num, newline = False)
    dash(num=num)