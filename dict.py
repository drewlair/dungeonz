import math
randomDict = {"hello": "world"}

def foo2():
    global randomDict
    print(randomDict)
    msg = randomDict
    randomDict["hello"] = "goodbye"
    print(msg)


def foo1():
    foo2()

def main():
    #global randomDict
    foo1()
    print(randomDict)
    print(math.atan(1)*360*0.5/math.pi)

if __name__ == "__main__":
    main()