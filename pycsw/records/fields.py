import datetime as dt


class Csw202Field:
    __counter = 0

    def __init__(self):
        prefix = self.__class__.__name__
        index = self.__class__.__counter
        self.storage_name = "_{}#{}".format(prefix, index)
        self.__class__.__counter += 1

    def __get__(self, instance, owner):
        if instance is None:
            result = self
        else:
            result = getattr(instance, self.storage_name)
        return result

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)


class TextField(Csw202Field):

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, str(value))


class DateTimeField(Csw202Field):

    def __set__(self, instance, value):
        if not isinstance(value, dt.datetime):
            raise ValueError("Value must be a datetime")
        else:
            setattr(instance, self.storage_name, str(value))
