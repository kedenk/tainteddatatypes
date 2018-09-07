import sys

myDict = {
    1: "Hello",
    2: "Bye",
    3: "Test"
}


def exist(key: int) -> bool:

    if key in myDict.keys():
        return True

    return False


def main():
    args = sys.argv
    if len(args) <= 1:
        print("Error. Need a int.")
        exit(-1)

    print(exist(int(args[1])))


if __name__ == "__main__":
    main()