def sqlalchemy_transaction(other_func):
    """
    A decorator to wrap handler methods that deal with transactions

    :param other_func:
    :return:
    """

    def wrapper(instance, *args, **kwargs):
        try:
            instance.session.begin()
            result = other_func(instance, *args, **kwargs)
        except Exception as err:
            instance.session.rollback()
            raise RuntimeError("ERROR: {}".format(err.orig))
        return result
    return wrapper


