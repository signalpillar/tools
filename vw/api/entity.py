"""
vw.api.entity
-------------
"""

# std
from collections import namedtuple
import enum

# local
from .core import Api


class EntityType(enum.Enum):
    """Enumeration of supported entity types."""

    application = 'Application'
    host = 'Host'
    hba = 'HBA'
    host_port = 'HostPort'
    esx_cluster = 'ESXCluster'
    esx_host = 'ESXHost'
    vm = 'VirtualMachine'
    storage_array = 'StorageArray'
    storage_controller = 'StorageController'
    storage_port = 'StoragePort'
    io_module = 'IOModule'


Entity = namedtuple('Entity', 'id name type')


class EntityApi(Api):
    """Wrapper for the entities entrypoint."""

    def get_entity_properties(self, entity_id, with_archived=False):
        """
        :rtype: dict
        """
        return self._client.get('entitymgmt/entity/properties', params=dict(
            ids=entity_id,
            withArchived={False: 'false', True: 'true'}[with_archived]
        ), verify=False) or {}

    def find_entities_by_pattern(self, pattern, entity_type=None):
        """Find entities by specified pattern that may occur in in DisplayLabel or Tags

        :param str pattern: Name or partial name of the entity.
        :param str entity_type: Optional type of the entity.
        :rtype: list[dict]
        """
        assert pattern
        return self.find_entities(
            filter_value=pattern,
            filter_keys=('DisplayLabel', 'Tags'),
            filter_values=(pattern,),
            entity_type=entity_type)

    def find_entities(self,
                      filter_value=None,
                      entity_type=None,
                      filter_keys=(),
                      filter_values=(),
                      page_number=1):
        """
        :type filter_value: str
        :type entity_type: str
        :type filter_keys: Sequence
        :type filter_value: Sequence
        :type page_number: int
        :rtype: list[dict]
        """
        return self._client.get('entitymgmt/entities', params=dict(
            filter=filter_value,
            filterKeys=','.join(filter_keys),
            filterValues=','.join(filter_values),
            type=entity_type,
            page=page_number,
            start=0,
            limit=500000
        ), verify=False)

    def find_itls_by_id(self, entity_id, filter_keys=(), page_number=1, start=0, limit=500000):
        return self._client.get('entitymgmt/app/{}/itls'.format(entity_id), params=dict(
            filterKeys=','.join(filter_keys),
            page=page_number,
            start=start,
            limit=limit,
        ), verify=False)
