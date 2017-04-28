from experiment.models import ComponentConfiguration


def create_list_of_trees(block_id, component_type, numeration=''):

    list_of_path = []

    configurations = ComponentConfiguration.objects.filter(parent_id=block_id).order_by('order')

    counter = 1
    for configuration in configurations:

        sub_numeration = (numeration + '.' if numeration else '') + str(counter)

        if not component_type or configuration.component.component_type == component_type:
            list_of_path.append(
                [[configuration.id,
                  configuration.parent.identification,
                  configuration.name,
                  configuration.component.identification,
                  sub_numeration]]
            )

        # Look for steps in descendant blocks
        if configuration.component.component_type == 'block':
            list_of_configurations = create_list_of_trees(configuration.component.id, component_type, sub_numeration)
            for item in list_of_configurations:
                item.insert(0,
                            [configuration.id,
                             configuration.parent.identification,
                             configuration.name,
                             configuration.component.identification,
                             sub_numeration])
                list_of_path.append(item)

        counter += 1

    return list_of_path
