from multiprocessing import Process

def func(counter,somearg):
    j = 0
    for i in range(counter): j+=i
    print(somearg)

def loop(counter,arglist):
    for i in range(10):
        func(counter,arglist[i])

if __name__ == "__main__":
    heavy = Process(target=loop,args=[1000000,['heavy'+str(i) for i in range(10)]])
    light = Process(target=loop,args=[500000,['light'+str(i) for i in range(10)]])
    heavy.start()
    light.start()
    heavy.join()
    light.join()