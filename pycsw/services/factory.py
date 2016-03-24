from .. import utilities

def get_service(identifier, config, creation_map=None):
    creation_map = creation_map or {
        "CSW_v3.0.0": "pycsw.services.csw.Csw300Service",
        "CSW_v2.0.2": "pycsw.services.csw.Csw202Service",
    }
    class_path = creation_map.get(identifier, "")
    module_path, separator, class_name = class_path.rpartition(".")
    service_class = utilities.lazy_import_dependency(module_path,
                                                     type_=class_name)
    instance = service_class.from_config(**config)
    return instance
