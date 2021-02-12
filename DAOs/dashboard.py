import json

# TODO:
# Actuellement la structure de la classe Dashboard recopie celle
# des fichiers JSON. C'est peut être pas une bonne idée car si on
# fait évoluer les fichiers JSON, faudra refactoriser pas mal de choses.
class Dashboard:

    def __init__(self, configPath):
        with open(configPath, 'r') as configFile:
            content = json.load(configFile)

            self.path = configPath
            self.name = content["name"]

            self.reddit = content["reddit"]
            self.twitter = content["twitter"]

    def update(self):
        with open(self.path, 'r') as configFile:
            content = json.load(configFile)

            self.name = content["name"]

            self.reddit = content["reddit"]
            self.twitter = content["twitter"]
