from typing import List
class Encoder:

    Options = {
        'birds': 0,
        'cats': 1,
        'dogs': 2,
        'fish': 3,
        'horse': 4,
        'dane': 5,
        'brit': 6,
        'german': 7,
        'swede': 8,
        'norwegian': 9,
        'milk': 10,
        'coffee': 11,
        'beer': 12,
        'water': 13,
        'tea': 14,
        'red': 15,
        'white': 16,
        'yellow': 17,
        'blue': 18,
        'green': 19, 
        'blend': 20,
        'bluemaster': 21,
        'dunhill': 22,
        'pallmall': 23,
        'prince': 24
    }
    # Hot encode some index with a given value
    def __hotEncode(self, idx:int, arr_len:int=5, value:int=1):
        tmp = [0] * arr_len
        tmp[idx] = value
        return tmp

    def oneHotEncode(self, house:str, color:str, beverage:str, smoke:str, pet:str):
        encoding = []
        encoding.extend(self.__hotEncode(int(house)))
        encoding.extend(self.__hotEncode(self.COLORS[color.lower()]))
        encoding.extend(self.__hotEncode(self.BEVERAGES[beverage.lower()]))
        encoding.extend(self.__hotEncode(self.CIGARETTES[smoke.lower()]))
        encoding.extend(self.__hotEncode(self.PETS[pet.lower()]))
        return encoding