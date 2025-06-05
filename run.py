if __name__ == "__main__":
    day_rank: int
    print("How was your day on the scale from 1 to 10?")
    while True:
        inp = input("> ")
        try:
            day_rank = int(inp)
            if not 1 <= day_rank <= 10: raise ValueError
            break
        except ValueError:
            print(f"Invalid ranking '{inp}'")
