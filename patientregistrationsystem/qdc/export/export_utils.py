import mne
from experiment.models import ComponentConfiguration
from experiment.views import eeg_data_reading


def create_list_of_trees(block_id, component_type, numeration=""):
    list_of_path = []

    configurations = ComponentConfiguration.objects.filter(parent_id=block_id).order_by(
        "order"
    )

    counter = 1
    for configuration in configurations:
        sub_numeration = (numeration + "." if numeration else "") + str(counter)

        if (
            not component_type
            or configuration.component.component_type == component_type
        ):
            list_of_path.append(
                [
                    [
                        configuration.id,
                        configuration.parent.identification,
                        configuration.name,
                        configuration.component.identification,
                        sub_numeration,
                    ]
                ]
            )

        # Look for steps in descendant blocks
        if configuration.component.component_type == "block":
            list_of_configurations = create_list_of_trees(
                configuration.component.id, component_type, sub_numeration
            )
            for item in list_of_configurations:
                item.insert(
                    0,
                    [
                        configuration.id,
                        configuration.parent.identification,
                        configuration.name,
                        configuration.component.identification,
                        sub_numeration,
                    ],
                )
                list_of_path.append(item)

        counter += 1

    return list_of_path


def can_export_nwb(eeg_data_list):
    for eeg_data in eeg_data_list:
        eeg_data.eeg_file_list = []
        for eeg_file in eeg_data.eeg_files.all():
            eeg_file.eeg_reading = eeg_data_reading(eeg_file, preload=True)
            eeg_file.can_export_to_nwb = False

            # v1.5
            # can export to nwb?
            if eeg_file.eeg_reading.file_format and eeg_file.eeg_reading.reading:
                if (
                    eeg_file.eeg_reading.file_format.nes_code == "MNE-RawFromEGI"
                    and hasattr(eeg_data.eeg_setting, "eeg_amplifier_setting")
                    and eeg_data.eeg_setting.eeg_amplifier_setting.number_of_channels_used
                    and eeg_data.eeg_setting.eeg_amplifier_setting.number_of_channels_used
                    == len(mne.pick_types(eeg_file.eeg_reading.reading.info, eeg=True))
                ):
                    eeg_file.can_export_to_nwb = True
            eeg_data.eeg_file_list.append(eeg_file)

    return eeg_data_list
