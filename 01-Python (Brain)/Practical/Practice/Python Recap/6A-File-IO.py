""" This doesn't work
# 6.1 Basic Open/Close
f = open('file.txt', 'r')
content = f.read()
f.close()
"""

"""
# 6.2 With Context Manager
## This will only work if the file already exists
with open('file.txt', 'r') as f:
    content = f.read()
"""

"""
# 6.3 Writing to files
with open('file.txt', 'w') as f:
    f.write("Hello, World!")

## to append:
with open('file.txt', 'a') as f:
    f.write("This is added to the end")
"""

"""
## Testing result of (6.3)
with open('file.txt', 'r') as f:
    content = f.read()

print(content)
"""

"""
## Testing writing mode
with open('file.txt', 'w') as f:
    f.write("This is a test, if I am correct \n" +
            "then will overwrite everything in that file") # I am right

with open('file.txt', 'r') as f:
    content = f.read()

print(content)
"""

"""
# 6.4 Working with Binary files
with open("image.png", "rb") as f:
    binary_data = f.read()

## Writing Binary
with open("binary.bin", "wb") as f:
    f.write(b"\x00\x01\x02")
"""

# 6.5 File Paths & Best Practices
from pathlib import Path

file_path = Path('docs')/'notes.txt'
with open(file_path, 'r', encoding = 'utf-8') as f:
    print(f.read())
