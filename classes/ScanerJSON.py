from classes.BaseScaner import BaseScaner
import json


class ScanerJSON(BaseScaner):

    def __init__(self):
        self.fileext = '.json'

    def scan(self, data: str):
        try:
            self.container = json.loads(data)
        except json.decoder.JSONDecodeError:
            return False

        return 'container' in self.container\
               and 'name' in self.container['container']\
               and 'users' in self.container\
               and 'msg' in self.container\
               and 'pub' in self.container