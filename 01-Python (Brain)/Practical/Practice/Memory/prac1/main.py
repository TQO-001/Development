import time
import tracemalloc

def profile_my_code():
    # 1. Start the benchmarks
    tracemalloc.start()
    start_time = time.perf_counter()

    # 2. Run the heavy workload
    # Generating a list of 5 million integers to consume time and RAM
    heavy_list = [x for x in range(5_000_000)]

    # 3. Stop the benchmarks immediately after the workload finishes
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 4. Calculate and format results
    elapsed_ms = (end_time - start_time) * 1000
    peak_mb = peak / (1024 * 1024)

    print(f"Execution Time: {elapsed_ms:,.2f} ms")
    print(f"Peak Memory Usage: {peak_mb:,.2f} MB")

if __name__ == "__main__":
    profile_my_code()