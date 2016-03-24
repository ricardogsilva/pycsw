import importlib


def lazy_import_dependency(python_path, type_=None):
    the_module = importlib.import_module(python_path)
    result = the_module
    if type_ is not None:
        the_class = getattr(the_module, type_)
        result = the_class
    return result

