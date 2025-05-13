from bodenfeuchtigkeit import Bodenfeuchtigkeit
import time

while True:
    a = Bodenfeuchtigkeit(pin_nummer=1).feuchtigkeit_in_prozent()
    time.sleep(1)
    print(a)