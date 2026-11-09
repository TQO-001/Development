import time

def read_logs(filepath):
    with open(filepath, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            else:
                line = line.rstrip()
            print(f"\rReading: {line}", end="", flush=True)
            yield line

        print("Task Complete")

filename = "sample_log"
logging = read_logs(filename)

for log_line in logging:
    time.sleep(2)