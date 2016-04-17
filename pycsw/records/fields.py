import datetime as dt


class CswTypenameProperty:
    __counter = 0

    def __init__(self, public_name, namespace=None, queryable=False,
                 returnable=False, mapped_to=None, description=None):
        """A descriptor class for managing CSW TypeName proerties.

        This class holds information on a specific property of some CSW
        TypeName.

        Parameters
        ----------
        public_name: str
            The name by which this property is known.
        namespace: str, optional
            The namespace where this property is defined.
        queryable: bool, optional
            Whether the property is queryable by clients of the catalogue.
        returnable: bool, optional
            Whether the property is returnable when responing to requests.
        mapped_to: str, optional
            To which field does the property correspond to in the curently
            configured repository.
        description: str, optional
            A description of the property.

        """

        _prefix = self.__class__.__name__
        index = self.__class__.__counter
        self.storage_name = "_{}#{}".format(_prefix, index)
        self.__class__.__counter += 1
        self.public_name = public_name
        self.namespace = namespace
        self.queryable = queryable
        self.returnable = returnable
        self.mapped_to = mapped_to
        self.description = description

    def __get__(self, instance, owner):
        if instance is None:
            result = self
        else:
            result = getattr(instance, self.storage_name)
        return result

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)

    @property
    def fqdn(self):
        return "{{{0.namespace}}}{0.public_name}".format(self)


class CswTypenamePropertyText(CswTypenameProperty):

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, str(value))


class CswTypenamePropertyDatetime(CswTypenameProperty):

    def __set__(self, instance, value):
        if not isinstance(value, dt.datetime):
            raise ValueError("Value must be a datetime")
        else:
            setattr(instance, self.storage_name, str(value))


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
