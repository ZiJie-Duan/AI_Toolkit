
def stream():

    for x in range(10):
        yield x
    return "True" #error


def main():
    for x in stream():
        print(x)

if __name__ == "__main__":
    main()