class MetaModules(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)