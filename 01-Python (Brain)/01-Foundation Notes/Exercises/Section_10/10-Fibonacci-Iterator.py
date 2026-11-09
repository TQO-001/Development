class Fibonacci:
    def __init__(self, n: int):
        self._num = n
        self._a = 0
        self._b = 1
        self._count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._count >= self._num:
            raise StopIteration

        c = self._a
        self._a = self._b
        self._b = c + self._b

        self._count += 1

        return c

for num in Fibonacci(10): print(num)