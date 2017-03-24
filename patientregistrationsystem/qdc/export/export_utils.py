from experiment.models import Component, ComponentConfiguration


def create_list_of_trees(block_id, component_type):

    list_of_path = []

    configurations = ComponentConfiguration.objects.filter(parent_id=block_id)

    if component_type:
        configurations = configurations.filter(component__component_type=component_type)

    for configuration in configurations:
        list_of_path.append(
            [[configuration.id,
              configuration.parent.identification,
              configuration.name,
              configuration.component.identification]]
        )

    # Look for steps in descendant blocks.
    block_configurations = ComponentConfiguration.objects.filter(parent_id=block_id,
                                                                 component__component_type="block")

    for block_configuration in block_configurations:
        list_of_configurations = create_list_of_trees(block_configuration.component.id, component_type)
        for item in list_of_configurations:
            item.insert(0,
                        [block_configuration.id,
                         block_configuration.parent.identification,
                         block_configuration.name,
                         block_configuration.component.identification])
            list_of_path.append(item)

    return list_of_path