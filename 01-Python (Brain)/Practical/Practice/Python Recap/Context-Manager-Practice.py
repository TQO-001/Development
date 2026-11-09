# ------------------- Bad Approach without Context Managers ------------------ #
file = open("file.txt", "w", encoding="UTF-8")
file.write("Hello, World!")
file.close()

# ------------------- Good Approach without Context Managers ------------------ #
"""
file = open("file.txt", "r", encoding="UTF-8")
try:
    file.write("Hello, New World!")
finally:
    file.close()
"""
# -------------------- Good Approach with Context Managers ------------------- #
with open("file.txt", "w", encoding="UTF-8") as f:
    f.write("Hello, New World!\nI'm Back Bitches")


def writeToFile(fileName, fileContent):
    with open(fileName, "w", encoding="UTF-8") as f:
        f.write(f"{fileContent}\n")

def appendToFile(fileName, fileContent):
    with open(fileName, "a", encoding="UTF-8") as f:
        f.write(f"{fileContent}\n")

def openFile(fileName):
    with open(fileName, "r", encoding="UTF-8") as f:
        content = f.read()
        print(content)

writeToFile("file.txt", "This is a test")
appendToFile("file.txt", "The test has worked")
openFile("file.txt")
writeToFile("file.txt", "This deleted everything")

# --------------------------- Tech with Tim example -------------------------- #

from contextlib import contextmanager

@contextmanager
def file(filename, method):
    print("Enter")
    file = open(filename, method)
    yield file
    file.close()
    print("Exit")

with file("text.txt", "w") as f:
    print("middle")
    f.write("Hello")