fib_list = []

def fibonacci(num: int):
    a = 1
    b = 0
    for i in range(num):
        print(a)
        c = a
        a = a + b
        b = c


fibonacci(10)