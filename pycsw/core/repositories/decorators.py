import logging
from sqlalchemy.orm import exc


LOGGER = logging.getLogger(__name__)


def sqlalchemy_transaction(other_func):
    """
    A decorator to wrap handler methods that deal with transactions

    :param other_func:
    :return:
    """

    def wrapper(instance, *args, **kwargs):
        try:
            result = other_func(instance, *args, **kwargs)
            instance.session.commit()
        except exc.UnmappedInstanceError as err:
            instance.session.rollback()
            raise RuntimeError(err)
        except Exception as err:
            instance.session.rollback()
            LOGGER.error(err)
            raise RuntimeError("ERROR: {}".format(err.orig))
        return result
    return wrapper


