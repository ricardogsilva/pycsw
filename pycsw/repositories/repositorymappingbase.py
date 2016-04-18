"""Repository mapping classes for pycsw."""


class RepositoryMappingBase:
    repository_entity = None
    entity_property = None

    def __init__(self, repository_entity, entity_property):
        self.repository_entity = repository_entity
        self.entity_property = entity_property