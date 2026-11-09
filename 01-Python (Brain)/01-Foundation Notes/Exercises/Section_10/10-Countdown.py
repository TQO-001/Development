def countdown(n: int):
    try:
        while (True):
            if n == 0:
                raise StopIteration("End Of Countdown")
            else:
                yield n
                n -= 1
    except StopIteration as e:
        print(f"Error: {e}")

manual_count = countdown(5)
print(next(manual_count))
print(next(manual_count))
print(next(manual_count))

# HR line seperator
print("=" * 4 * 8)

auto_count = countdown(10)

for i in range(15):
    print(next(auto_count))