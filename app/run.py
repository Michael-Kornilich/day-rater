import subprocess

if __name__ == "__main__":
    print("How was your day on the scale from 1 to 10?")
    while True:
        inp = input("> ")
        try:
            day_rank = int(inp)
        except ValueError:
            print(f"Invalid ranking '{inp}'")
            continue

        if not 1 <= day_rank <= 10:
            print(f"The rank must be between 1 and 10, {day_rank} given.")
            continue

        if int(inp) != float(inp):
            print(f"The rank must be an integer, {inp} given")
            continue
        break

    process_res = subprocess.run(["python", "daemon.py", "--day-rank", day_rank])
    if err := process_res.stderr:
        print(f"Currently the manager program is unavailable: {err}")
