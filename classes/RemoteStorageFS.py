from classes.BaseRemoteStorage import BaseRemoteStorage
import glob
import json
from os import path
from time import sleep


class RemoteStorageFS(BaseRemoteStorage):

    def __scan_path(self, spath):
        print(spath)
        dirs = glob.glob(spath + '/*')
        result = []
        for i, filenamefull in enumerate(dirs):
            if path.isdir(filenamefull):
                result += self.__scan_path(filenamefull)
            elif path.splitext(filenamefull)[1] == self.scanner.fileext:
                if self.__scan_file(filenamefull):
                    result.append(filenamefull)
                    self.containers[filenamefull] = self.scanner.container
        return result

    def __scan_file(self, sfile):
        file = open(sfile, 'r')
        s_container = file.read()
        file.close()

        return self.scanner.scan(s_container)

    def scan(self):
        self.containers = {}
        animation = ('Searching for container in {} ..... press CTRL+C to exit.',
                     ' Searching for container in {} ..... press CTRL+C to exit.',
                     '- Searching for container in {} ..... press CTRL+C to exit.',
                     '-- Searching for container in {} ..... press CTRL+C to exit.',
                     '--- Searching for container in {} ..... press CTRL+C to exit.',
                     '---- Searching for container in {} ..... press CTRL+C to exit.',
                     '---- Searching for container in {} ..... press CTRL+C to exit.',
                     '----- Searching for container in {} ..... press CTRL+C to exit.',
                     '----- Searching for container in {} ..... press CTRL+C to exit.',
                     '---- Searching for container in {} ..... press CTRL+C to exit.',
                     '---- Searching for container in {} ..... press CTRL+C to exit.',
                     '--- Searching for container in {} ..... press CTRL+C to exit.',
                     '-- Searching for container in {} ..... press CTRL+C to exit.',
                     '- Searching for container in {} ..... press CTRL+C to exit.',
                     ' Searching for container in {} ..... press CTRL+C to exit.',
                     'Searching for container in {} ..... press CTRL+C to exit.')
        counter = 0

        while not path.exists(self.path):
            print(animation[counter % 16].format(self.path))
            counter += 1
            sleep(0.05)

        res = self.__scan_path(self.path)
        while len(res) == 0:
            res = self.__scan_path(self.path)

        return res

    def save_container(self, container: str, data):
        file_container_encrypted = self.path + '/' + container + '.json'

        container_js = json.dumps(data)
        file = open(file_container_encrypted, 'w+')
        file.write(container_js)
        file.close()
        return True
