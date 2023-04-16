from typing import List
from enum import Enum
import os

class Options(Enum):
    red = 0
    green = 1
    white = 2
    blue = 3
    yellow = 4

    british = 5
    swedish = 6
    danish = 7
    norwegian = 8
    german = 9

    tea = 10
    coffee = 11
    water = 12
    beer = 13
    milk = 14

    prince = 15
    blend = 16
    pallmall = 17
    bluemasters = 18
    dunhill = 19

    dog = 20
    cat = 21
    bird = 22
    horse = 23
    fish = 24
class Encoder:

    __terminal = '0'
    def __init__(self) -> None:
        self.cnf = []
        self.length = 5

    def encode(self, house:int, attr:int):
        return house + 5 * attr
    
    def __generate_house(self, start:int, end:int):
        # for a category, generate house related self.cnf
        for i in range(start, end + 1):
            # each house has a category
            houses = []
            for house in range(1, self.length+1):
                houses.append(str(self.encode(house, i)))
            houses.append(self.__terminal)
            self.cnf.append(' '.join(houses))

            for h1 in range(1, self.length+1):
                # each category only once Si,a ⇒ ¬Sj,a
                for h2 in range(1, h1):
                    self.cnf.append('-{} -{} {}'.format(
                        self.encode(h2, i), self.encode(h1, i), self.__terminal
                    ))
                # 1 category per house
                for j in range(start, end + 1):
                    if j == i:
                        continue
                    self.cnf.append('-{} -{} {}'.format(
                        self.encode(h1, i), self.encode(h1, j), self.__terminal
                    ))
        
    def and_operator(self, attr1, attr2):
        for i in range(1, 6):
            self.cnf.append('-{} {} {}'.format(
                self.encode(i, attr1), self.encode(i, attr2), self.__terminal
            ))
        
    def neighbor(self, attr1, attr2):
        self.cnf.extend([
            '-{} {} {}'.format(
                self.encode(1, attr1), self.encode(2, attr2), self.__terminal
            ),
            '-{} {} {}'.format(
                self.encode(self.length, attr1), self.encode(self.length - 1, attr2), self.__terminal
            )])
        for i in range(2, self.length):
            self.cnf.append('-{} {} {} {}'.format(
                self.encode(i, attr1), self.encode(i-1, attr2), self.encode(i+1, attr2), self.__terminal
            ))


    def generate_dimacs(self):
        self.__generate_house(Options.red.value, Options.yellow.value)
        self.__generate_house(Options.british.value, Options.german.value)
        self.__generate_house(Options.tea.value, Options.milk.value)
        self.__generate_house(Options.prince.value, Options.dunhill.value)
        self.__generate_house(Options.dog.value, Options.fish.value)
        
        # The Norwegian lives in the first house.
        '{} {}'.format(self.encode(1, Options.norwegian.value), self.__terminal)
        # The Norwegian lives next to the blue house.
        '{} {}'.format(self.encode(2, Options.blue.value), self.__terminal)
        # The man living in the center house drinks milk.
        '{} {}'.format(self.encode(3, Options.milk.value), self.__terminal)
        # The Brit lives in the red house.
        self.and_operator(Options.british.value, Options.red.value)
        # The green house’s owner drinks coffee.
        self.and_operator(Options.green.value, Options.coffee.value)
        # The Dane drinks tea.
        self.and_operator(Options.danish.value, Options.tea.value)
        # The owner of the yellow house smokes Dunhill.
        self.and_operator(Options.yellow.value, Options.dunhill.value)
        # The Swede keeps dogs as pets.
        self.and_operator(Options.swedish.value, Options.dog.value)
        # The German smokes Prince.
        self.and_operator(Options.german.value, Options.prince.value)
        # The person who smokes Pall Mall rears birds.
        self.and_operator(Options.pallmall.value, Options.bird.value)
        # The owner who smokes Bluemasters drinks beer.
        self.and_operator(Options.bluemasters.value, Options.beer.value)
        # The man who keeps the horse lives next to the man who smokes Dunhill.
        self.neighbor(Options.horse.value, Options.dunhill.value)
        # The man who smokes Blends lives next to the one who keeps cats.
        self.neighbor(Options.blend.value, Options.cat.value)
        # The man who smokes Blends has a neighbor who drinks water.
        self.neighbor(Options.blend.value, Options.water.value)
        # The green house is on the left of the white house.
        for w in range(1, self.length+1):
            for g in range(self.length, 0, -1):
                if w-1 <= g <= w:
                    continue
            self.cnf.append('-{} -{} {}'.format(
                self.encode(w, Options.white.value), self.encode(g, Options.green.value), self.__terminal
            ))
        self.cnf.insert(0, 'p cnf {} {}'.format(125, len(self.cnf)))
        return os.linesep.join(self.cnf)

if __name__ == '__main__':
    e = Encoder()
    with open('einstein_cnf.txt', 'w') as f:
        f.write(e.generate_dimacs())