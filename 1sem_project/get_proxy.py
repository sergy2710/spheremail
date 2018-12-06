import random


class Proxy:

    def __init__(self, ifile=None):

        self.proxies = []

        if ifile is None:
            ifile = 'proxies.txt'

        with open(ifile, 'r') as ifile:
            for line in ifile:
                protocol, ip = line.split()
                self.proxies.append({protocol: ip})

    def get_proxy(self):
        return random.choice(self.proxies)


    def get_proxies(self):
        random.shuffle(self.proxies)
        for proxy in self.proxies:
            yield proxy
