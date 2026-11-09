# Create Sample text file
filename = "sample_log"

with open(filename, 'w') as f:
    f.write("INFO: Starting system\nDEBUG: Loading modules\nSUCCESS: Ready\n")

def read_log(filepath):
    pass