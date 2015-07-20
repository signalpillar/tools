
class EntityApi(Api):

    class EntityType(enum.Enum):

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

    def find_entities(self, filter_value=None, filter_keys=(), filter_values=(), page_number=1):
        return self._client.get('entitymgmt/entities', params=dict(
            filter=filter_value,
            filterKeys=','.join(filter_keys),
            filterValues=','.join(filter_values),
            type=entity_type,
            page=page_number,
            start=0,
            limit=500000
        ))

    def find_entities_by_label(self, label):
        import itertools
        items_per_type = itertools.chain.from_iterable(
            self.find_entites(
                filter=label,
                filter_keys=('DisplayLabel', 'Tags'),
                filter_values=(label,),
                entity_type=type_)
            for type_ in self.EntityType)
        return (
            Entity(item.get('Id'), item.get('Name'), item.get('Type'))
            for item in items_per_type
            if item.get('DisplayLabel') == label
        )
