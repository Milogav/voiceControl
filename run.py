from voiceController import voiceController
import os

if __name__ == '__main__':

    cwd = os.path.dirname(os.path.realpath(__file__))
    language='es-ES'
    commandTablePath = os.path.join(cwd,'commands_%s.table' % language)

    vc = voiceController(commandTablePath,language=language)
    vc.start()
