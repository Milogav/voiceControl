from voiceController import voiceController
import os

if __name__ == '__main__':

    cwd = os.path.dirname(os.path.realpath(__file__))
    commandJsonPath = os.path.join(cwd,'commands.json')

    vc = voiceController(commandJsonPath,language='es-ES')
    vc.start()
