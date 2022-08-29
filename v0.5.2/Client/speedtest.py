import sys
import time
import cProfile
import pstats

from scit.client import Client


class client(Client):
    def __init__(self):
        Client.__init__(self)
        self.set_name("a")

    def read(self, recv):
        self.close()


with cProfile.Profile() as pr:
    start = time.perf_counter()
    c = client()
    c.send("a", "my message")
    while c.running:
        continue

stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.dump_stats(filename="profiling.prof")
