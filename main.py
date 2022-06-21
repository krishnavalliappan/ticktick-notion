import time

from ticktick_notion import TicktickNotion

trials = 0

while trials < 50:
    TicktickNotion()

    trials = trials + 1
    print(trials)
    time.sleep(10)