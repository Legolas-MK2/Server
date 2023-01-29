import sys
import time
import cProfile
import pstats

from scit_client.client import Client


class client(Client):
    def __init__(self):
        Client.__init__(self)
        self.set_name("a")

    def read(self, recv):
        print(recv)
        self.close()


with cProfile.Profile() as pr:
    c = client()
    c.send("a", "my message")
    start = time.perf_counter()
    while c.running:
        pass
    print(time.perf_counter()-start)

stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.dump_stats(filename="profiling.prof")
