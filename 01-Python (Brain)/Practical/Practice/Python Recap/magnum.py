def dash(num=8, char="-"):
    try:
        if num < 0:
            raise ValueError("Number must be non-negative.")
        else:     
            print(char * 4 * num)
    except ValueError as e:
        print(f"Error: {e}")

def title(name, type):
    if type == 1:
        print("# " + "----"*4, name, "----"*4 + " #")
    elif type == 2:
        dash(16)
        print("|" + " "*4*4, name, " "*4*4 + "|")
        dash(16)
    else:
        print("Error")

def dashTitle(name, num=8):
    dash(num + 2)
    try:
        if num < 0:
            raise ValueError("Number must not be non-negative")
        else:
            print(int(4 * (num / 2)) * " ", name)
    except ValueError as e:
        print(f"Error: {e}")
    dash(num + 2)
