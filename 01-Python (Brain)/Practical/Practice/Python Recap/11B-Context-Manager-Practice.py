# -------------------------- Game Session File Lock -------------------------- #
# The Class-Based Context Manager
class SafeFileHandler:
    def __init__(self, file_name, mode):
        self.file_name = file_name
        self.mode = mode
        self.file = None

    def __enter__(self):
        print(f"[File Opened]: Accessing '{self.file_name}'...")
        self.file = open(self.file_name, self.mode)

        return self.file
            

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

        print(f"[File Closed]: '{self.file_name}' closed safely.")
        return False

# ------------------------------ Test Execution ------------------------------ #
print("\n--- Create/Write to file ---")
with SafeFileHandler("session.txt", "w") as f:
    f.write("Player: Toffy\nClass: Warrior\n")

print("\n--- Reading file back out to verify ---")
with SafeFileHandler("session.txt", "r") as f:
    for line in f:
        print(line.strip())