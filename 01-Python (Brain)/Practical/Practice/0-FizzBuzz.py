numRange = 101
for i in range(numRange):
    x = i
    if (i % 3 == 0 and i % 5 == 0):
        x = "FizzBuzz"
    elif (i % 3 == 0):
        x = "fizz"
    elif (i % 5 == 0):
        x = "buzz"
    print(x)
