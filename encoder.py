from typing import List
class Encoder:

    COLORS = {
        'red': 0,
        'white': 1,
        'yellow': 2,
        'blue': 3,
        'green': 4 
    }
    CIGARETTES = {
        'blend': 0,
        'bluemaster': 1,
        'dunhill': 2,
        'pallmall': 3,
        'prince': 4
    }
    PETS = {
        'birds': 0,
        'cats': 1,
        'dogs': 2,
        'fish': 3,
        'horse': 4
    }
    NATIONALITY = {
        'dane': 0,
        'brit': 1,
        'german': 2,
        'swede': 3,
        'norwegian': 4
    }

    BEVERAGES = {
        'milk': 0,
        'coffee': 1,
        'beer': 2,
        'water': 3,
        'tea': 4
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