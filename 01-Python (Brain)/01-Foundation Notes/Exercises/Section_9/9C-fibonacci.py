import magnum
import time
def fib(n: int) -> int:
    if n <= 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)

for x in range(20):
    print(fib(x))

magnum.dash()

nums = {}
def fib2(n: int) -> int:
    if n <= 2:
        return 1

    if n in nums:
        return nums[n]
    else:
        time.sleep(1)
        num = fib2(n-1) + fib2(n-2)
        nums[n] = num
        return num

for x in range(20):
    print(fib2(x))
