import math
from scipy.stats import t, f
import json
from pynput import keyboard
import time


class KeyLogger:
    def __init__(self):
        self.prev_press_time = time.time()
        self.intervals = []
        self.entered_phrase = ''

    def on_press(self, key):
        try:
            if key == keyboard.Key.enter:
                return False
            self.entered_phrase += key.char

        except AttributeError:
            if key == keyboard.Key.space:
                self.entered_phrase += ' '

        press_time = time.time()
        interval = press_time - self.prev_press_time
        self.intervals.append(interval)
        self.prev_press_time = press_time

    def start(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            print("Введіть фразу: ")
            listener.join()
            return self.intervals, self.entered_phrase


def drop_outlier(y):
    i=0
    n=len(y)

    while i<n:
        y1 = y[:i]+y[i+1:]    # y`
        M = sum(y1)/len(y1)

        sum_value = 0
        for j in range(len(y1)):
            sum_value += (y1[j]-M)**2

        S = math.sqrt(sum_value/(len(y1)-1))

        tP = abs((y[i]-M)/S)
        tT = t.ppf(1 - 0.05 / 2, len(y1) - 1)

        if tP > tT:
            y = y1
            n -= 1
        else:
            i += 1
    return y


def test(y, xl):
    n = len(y)
    r = 0

    ke = len(xl)

    for i in range(ke):

        Mxl = sum(xl[i]) / len(xl[i])
        sum_value = 0
        for x in xl[i]:
            sum_value += (x - Mxl) ** 2
        S1 = math.sqrt(sum_value / len(xl[i]))

        My = sum(y) / len(y)
        sum_value = 0
        for yi in y:
            sum_value += (yi - My) ** 2
        S2 = math.sqrt(sum_value / len(xl[i]))

        Smax_sq = max(S1 ** 2, S2 ** 2)
        Smin_sq = min(S1 ** 2, S2 ** 2)

        Fp = Smax_sq / Smin_sq
        Ft = f.ppf(1 - 0.05 / 2, n - 1, n - 1)

        if Fp <= Ft:
            Sxl_sq = sum((xli - Mxl) ** 2 for xli in xl[i]) / (len(xl) - 1)
            Sy_sq = sum((yi - My) ** 2 for yi in y) / (n - 1)
            S = math.sqrt((Sxl_sq + Sy_sq) * (n - 1) / (2 * n - 1))
            tP = abs(Mxl - My) / S * math.sqrt(2 / n)
            tT = t.ppf(1 - 0.05 / 2, n - 1)

            if tP <= tT:
                r += 1
    P = r / ke

    return P

def train():
    ke = int(input("Number of train iters:"))
    passwd = input("passwd: ")
    etalon_array = []
    i = 0

    while i < ke:
        kl = KeyLogger()
        intervals, entered_passwd = kl.start()
        x=0
        if entered_passwd != passwd:
            print("entered_passwd != passwd")
        else:
            i += 1
            intervals = drop_outlier(intervals)
            etalon_array.append(intervals)
            print("Intervals added")

    with open("etalon.txt", "w") as file:
        json.dump(etalon_array, file)
        print("File created")

def auth():
    ke = int(input("Number of auth attempts:"))
    passwd = input("passwd:")
    user_characteristics = []
    iter= 0

    while iter < ke:
        kl = KeyLogger()
        user_intervals, entered_passwd = kl.start()
        if entered_passwd != passwd:
            print("entered_passwd != passwd")
        else:
            iter += 1

            with open("etalon.txt", "r") as file:
                etalon = json.load(file)
                etalon = [[float(num) for num in item] for item in etalon]

            user_intervals = drop_outlier(user_intervals)
            P=test(user_intervals, etalon)
            print("P", P)
            if P>=0.8:
                etalon.append(user_intervals)
                with open("etalon.txt", "w") as file:
                    json.dump(etalon, file)
                    print("File updated")

auth()
