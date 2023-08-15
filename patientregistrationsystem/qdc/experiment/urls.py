from django.urls import re_path
from experiment import views

urlpatterns = [
    # keyword
    re_path(r"^keyword/search/$", views.keyword_search_ajax, name="keywords_search"),
    re_path(
        r"^keyword/new/(?P<research_project_id>\d+)/(?P<keyword_name>.+)/$",
        views.keyword_create_ajax,
        name="keyword_new",
    ),
    re_path(
        r"^keyword/add/(?P<research_project_id>\d+)/(?P<keyword_id>\d+)/$",
        views.keyword_add_ajax,
        name="keyword_add",
    ),
    re_path(
        r"^keyword/remove/(?P<research_project_id>\d+)/(?P<keyword_id>\d+)/$",
        views.keyword_remove_ajax,
        name="keyword_remove",
    ),
    # research project
    re_path(
        r"^research_project/list/$",
        views.research_project_list,
        name="research_project_list",
    ),
    re_path(
        r"^research_project/new/$",
        views.research_project_create,
        name="research_project_new",
    ),
    re_path(
        r"^research_project/(?P<research_project_id>\d+)/$",
        views.research_project_view,
        name="research_project_view",
    ),
    re_path(
        r"^research_project/edit/(?P<research_project_id>\d+)/$",
        views.research_project_update,
        name="research_project_edit",
    ),
    # publication
    re_path(r"^publication/list/$", views.publication_list, name="publication_list"),
    re_path(r"^publication/new/$", views.publication_create, name="publication_new"),
    re_path(
        r"^publication/(?P<publication_id>\d+)/$",
        views.publication_view,
        name="publication_view",
    ),
    re_path(
        r"^publication/edit/(?P<publication_id>\d+)/$",
        views.publication_update,
        name="publication_edit",
    ),
    re_path(
        r"^publication/(?P<publication_id>\d+)/add_experiment/$",
        views.publication_add_experiment,
        name="publication_add_experiment",
    ),
    # publication (ajax)
    re_path(
        r"^get_experiments_by_research_project/(?P<research_project_id>\d+)/$",
        views.get_experiments_by_research_project,
    ),
    # collaborator
    re_path(
        r"^researchers/(?P<experiment_id>\d+)/new_researcher/$",
        views.collaborator_create,
        name="collaborator_new",
    ),
    # experiment
    re_path(
        r"^research_project/(?P<research_project_id>\d+)/new_experiment/$",
        views.experiment_create,
        name="experiment_new",
    ),
    re_path(
        r"^(?P<experiment_id>\d+)/$", views.experiment_view, name="experiment_view"
    ),
    re_path(
        r"^edit/(?P<experiment_id>\d+)/$",
        views.experiment_update,
        name="experiment_edit",
    ),
    re_path(
        r"^experiment_research/change_the_order/(?P<collaborator_position_id>\d+)/(?P<command>\w+)/$",
        views.experiment_research_change_order,
        name="experiment_research_change_order",
    ),
    # export
    re_path(
        r"^(?P<experiment_id>\d+)/export/$",
        views.experiment_export,
        name="experiment_export",
    ),
    # import
    re_path(r"^import/$", views.experiment_import, name="experiment_import"),
    re_path(
        r"^import/(?P<research_project_id>\d+)/$",
        views.experiment_import,
        name="experiment_import",
    ),
    re_path(r"^import/results/$", views.import_log, name="import_log"),
    # Schedule of sending
    re_path(
        r"^schedule_of_sending/(?P<experiment_id>\d+)/$",
        views.experiment_schedule_of_sending,
        name="experiment_schedule_of_sending",
    ),
    re_path(
        r"^schedule_of_sending/list/$",
        views.schedule_of_sending_list,
        name="schedule_of_sending_list",
    ),
    # group
    re_path(
        r"^(?P<experiment_id>\d+)/group/new/$", views.group_create, name="group_new"
    ),
    re_path(r"^group/(?P<group_id>\d+)/$", views.group_view, name="group_view"),
    re_path(r"^group/edit/(?P<group_id>\d+)/$", views.group_update, name="group_edit"),
    # equipment
    re_path(r"^setup/$", views.setup_menu, name="setup_menu"),
    # register manufacturer
    re_path(r"^manufacturer/list/$", views.manufacturer_list, name="manufacturer_list"),
    re_path(r"^manufacturer/new/$", views.manufacturer_create, name="manufacturer_new"),
    re_path(
        r"^manufacturer/(?P<manufacturer_id>\d+)/$",
        views.manufacturer_view,
        name="manufacturer_view",
    ),
    re_path(
        r"^manufacturer/edit/(?P<manufacturer_id>\d+)/$",
        views.manufacturer_update,
        name="manufacturer_edit",
    ),
    # register amplifier
    re_path(r"^amplifier/list/$", views.amplifier_list, name="amplifier_list"),
    re_path(r"^amplifier/new/$", views.amplifier_create, name="amplifier_new"),
    re_path(
        r"^amplifier/(?P<amplifier_id>\d+)/$",
        views.amplifier_view,
        name="amplifier_view",
    ),
    re_path(
        r"^amplifier/edit/(?P<amplifier_id>\d+)/$",
        views.amplifier_update,
        name="amplifier_edit",
    ),
    # register eeg solution
    re_path(r"^eegsolution/list/$", views.eegsolution_list, name="eegsolution_list"),
    re_path(r"^eegsolution/new/$", views.eegsolution_create, name="eegsolution_new"),
    re_path(
        r"^eegsolution/(?P<eegsolution_id>\d+)/$",
        views.eegsolution_view,
        name="eegsolution_view",
    ),
    re_path(
        r"^eegsolution/edit/(?P<eegsolution_id>\d+)/$",
        views.eegsolution_update,
        name="eegsolution_edit",
    ),
    # register filter type
    re_path(r"^filtertype/list/$", views.filtertype_list, name="filtertype_list"),
    re_path(r"^filtertype/new/$", views.filtertype_create, name="filtertype_new"),
    re_path(
        r"^filtertype/(?P<filtertype_id>\d+)/$",
        views.filtertype_view,
        name="filtertype_view",
    ),
    re_path(
        r"^filtertype/edit/(?P<filtertype_id>\d+)/$",
        views.filtertype_update,
        name="filtertype_edit",
    ),
    # register electrode model
    re_path(
        r"^electrodemodel/list/$", views.electrodemodel_list, name="electrodemodel_list"
    ),
    re_path(
        r"^electrodemodel/new/$", views.electrodemodel_create, name="electrodemodel_new"
    ),
    re_path(
        r"^electrodemodel/(?P<electrodemodel_id>\d+)/$",
        views.electrodemodel_view,
        name="electrodemodel_view",
    ),
    re_path(
        r"^electrodemodel/edit/(?P<electrodemodel_id>\d+)/$",
        views.electrodemodel_update,
        name="electrodemodel_edit",
    ),
    # register material
    re_path(r"^material/list/$", views.material_list, name="material_list"),
    re_path(r"^material/new/$", views.material_create, name="material_new"),
    re_path(
        r"^material/(?P<material_id>\d+)/$", views.material_view, name="material_view"
    ),
    re_path(
        r"^material/edit/(?P<material_id>\d+)/$",
        views.material_update,
        name="material_edit",
    ),
    # register eeg electrode net
    re_path(
        r"^eegelectrodenet/list/$",
        views.eegelectrodenet_list,
        name="eegelectrodenet_list",
    ),
    re_path(
        r"^eegelectrodenet/new/$",
        views.eegelectrodenet_create,
        name="eegelectrodenet_new",
    ),
    re_path(
        r"^eegelectrodenet/(?P<eegelectrodenet_id>\d+)/$",
        views.eegelectrodenet_view,
        name="eegelectrodenet_view",
    ),
    re_path(
        r"^eegelectrodenet/edit/(?P<eegelectrodenet_id>\d+)/$",
        views.eegelectrodenet_update,
        name="eegelectrodenet_edit",
    ),
    # register cap size
    re_path(
        r"^eeg_electrode_cap_size/(?P<eegelectrode_cap_id>\d+)/add_size/$",
        views.eegelectrodenet_cap_size_create,
        name="eegelectrodenet_add_size",
    ),
    re_path(
        r"^eeg_electrode_cap_size/(?P<eegelectrode_cap_size_id>\d+)/$",
        views.eegelectrodenet_cap_size_view,
        name="eegelectrodenet_cap_size_view",
    ),
    re_path(
        r"^eeg_electrode_cap_size/(?P<eegelectrode_cap_size_id>\d+)/edit/$",
        views.eegelectrodenet_cap_size_update,
        name="eegelectrodenet_cap_size_edit",
    ),
    # register A/D converter
    re_path(r"^ad_converter/list/$", views.ad_converter_list, name="ad_converter_list"),
    re_path(r"^ad_converter/new/$", views.ad_converter_create, name="ad_converter_new"),
    re_path(
        r"^ad_converter/(?P<ad_converter_id>\d+)/$",
        views.ad_converter_view,
        name="ad_converter_view",
    ),
    re_path(
        r"^ad_converter/edit/(?P<ad_converter_id>\d+)/$",
        views.ad_converter_update,
        name="ad_converter_edit",
    ),
    # register Standardization system (EMG Electrode Placement System)
    re_path(
        r"^standardization_system/list/$",
        views.standardization_system_list,
        name="standardization_system_list",
    ),
    re_path(
        r"^standardization_system/new/$",
        views.standardization_system_create,
        name="standardization_system_new",
    ),
    re_path(
        r"^standardization_system/(?P<standardization_system_id>\d+)/$",
        views.standardization_system_view,
        name="standardization_system_view",
    ),
    re_path(
        r"^standardization_system/edit/(?P<standardization_system_id>\d+)/$",
        views.standardization_system_update,
        name="standardization_system_edit",
    ),
    re_path(
        r"^standardization_system/(?P<standardization_system_id>\d+)/new_placement/(?P<placement_type>\w+)/$",
        views.emg_electrode_placement_create,
        name="emg_electrode_placement_new",
    ),
    re_path(
        r"^emg_electrode_placement/(?P<emg_electrode_placement_id>\d+)/$",
        views.emg_electrode_placement_view,
        name="emg_electrode_placement_view",
    ),
    re_path(
        r"^emg_electrode_placement/(?P<emg_electrode_placement_id>\d+)/edit/$",
        views.emg_electrode_placement_update,
        name="emg_electrode_placement_edit",
    ),
    # register muscle
    re_path(r"^muscle/list/$", views.muscle_list, name="muscle_list"),
    re_path(r"^muscle/new/$", views.muscle_create, name="muscle_new"),
    re_path(r"^muscle/(?P<muscle_id>\d+)/$", views.muscle_view, name="muscle_view"),
    re_path(
        r"^muscle/edit/(?P<muscle_id>\d+)/$", views.muscle_update, name="muscle_edit"
    ),
    re_path(
        r"^muscle/(?P<muscle_id>\d+)/new_muscle_subdivision/$",
        views.muscle_subdivision_create,
        name="muscle_subdivision_new",
    ),
    re_path(
        r"^muscle_subdivision/(?P<muscle_subdivision_id>\d+)/$",
        views.muscle_subdivision_view,
        name="muscle_subdivision_view",
    ),
    re_path(
        r"^muscle_subdivision/(?P<muscle_subdivision_id>\d+)/edit/$",
        views.muscle_subdivision_update,
        name="muscle_subdivision_edit",
    ),
    re_path(
        r"^muscle/(?P<muscle_id>\d+)/new_muscle_side/$",
        views.muscle_side_create,
        name="muscle_side_new",
    ),
    re_path(
        r"^muscle_side/(?P<muscle_side_id>\d+)/$",
        views.muscle_side_view,
        name="muscle_side_view",
    ),
    re_path(
        r"^muscle_side/(?P<muscle_side_id>\d+)/edit/$",
        views.muscle_side_update,
        name="muscle_side_edit",
    ),
    # register software
    re_path(r"^software/list/$", views.software_list, name="software_list"),
    re_path(r"^software/new/$", views.software_create, name="software_new"),
    re_path(
        r"^software/(?P<software_id>\d+)/$", views.software_view, name="software_view"
    ),
    re_path(
        r"^software/edit/(?P<software_id>\d+)/$",
        views.software_update,
        name="software_edit",
    ),
    re_path(
        r"^software/(?P<software_id>\d+)/new_version/$",
        views.software_version_create,
        name="software_version_new",
    ),
    re_path(
        r"^software_version/(?P<software_version_id>\d+)/$",
        views.software_version_view,
        name="software_version_view",
    ),
    re_path(
        r"^software_version/(?P<software_version_id>\d+)/edit/$",
        views.software_version_update,
        name="software_version_edit",
    ),
    # register EMG electrode placement
    # register coil model
    re_path(r"^coil/list/$", views.coil_list, name="coil_list"),
    re_path(r"^coil/new/$", views.coil_create, name="coil_new"),
    re_path(r"^coil/(?P<coil_id>\d+)/$", views.coil_view, name="coil_view"),
    re_path(r"^coil/edit/(?P<coil_id>\d+)/$", views.coil_update, name="coil_edit"),
    # register TMS device
    re_path(r"^tmsdevice/list/$", views.tmsdevice_list, name="tmsdevice_list"),
    re_path(r"^tmsdevice/new/$", views.tmsdevice_create, name="tmsdevice_new"),
    re_path(
        r"^tmsdevice/(?P<tmsdevice_id>\d+)/$",
        views.tmsdevice_view,
        name="tmsdevice_view",
    ),
    re_path(
        r"^tmsdevice/edit/(?P<tmsdevice_id>\d+)/$",
        views.tmsdevice_update,
        name="tmsdevice_edit",
    ),
    # TMS Localization system and position
    re_path(
        r"^tms_localization_system/list/$",
        views.tms_localization_system_list,
        name="tms_localization_system_list",
    ),
    re_path(
        r"^tms_localization_system/new/$",
        views.tms_localization_system_create,
        name="tms_localization_system_new",
    ),
    re_path(
        r"^tms_localization_system/(?P<tms_localization_system_id>\d+)/$",
        views.tms_localization_system_view,
        name="tms_localization_system_view",
    ),
    re_path(
        r"^tms_localization_system/edit/(?P<tms_localization_system_id>\d+)/$",
        views.tms_localization_system_update,
        name="tms_localization_system_update",
    ),
    # re_path(r'^tms_localization_system/(?P<tms_localization_system_id>\d+)/new_tms_position/$',
    #     views.tms_localization_system_position_create, name='tms_localization_system_position_create'),
    # re_path(r'^tms_localization_system/(?P<tms_localization_system_id>\d+)/tms_position/(?P<tms_position_id>\d+)$',
    #     views.tms_localization_system_position_view, name='tms_localization_system_position_view'),
    # re_path(r'^tms_localization_system/(?P<tms_localization_system_id>\d+)/tms_position/edit/(?P<tms_position_id>\d+)$',
    #     views.tms_localization_system_position_update, name='tms_localization_system_position_update'),
    # Localization system and position
    re_path(
        r"^eeg_electrode_localization_system/list/$",
        views.eeg_electrode_localization_system_list,
        name="eeg_electrode_localization_system_list",
    ),
    re_path(
        r"^eeg_electrode_localization_system/new/$",
        views.eeg_electrode_localization_system_create,
        name="eeg_electrode_localization_system_new",
    ),
    re_path(
        r"^eeg_electrode_localization_system/(?P<eeg_electrode_localization_system_id>\d+)/$",
        views.eeg_electrode_localization_system_view,
        name="eeg_electrode_localization_system_view",
    ),
    re_path(
        r"^eeg_electrode_localization_system/edit/(?P<eeg_electrode_localization_system_id>\d+)/$",
        views.eeg_electrode_localization_system_update,
        name="eeg_electrode_localization_system_edit",
    ),
    re_path(
        r"^eeg_electrode_localization_system/(?P<eeg_electrode_localization_system_id>\d+)/new_position/$",
        views.eeg_electrode_position_create,
        name="eeg_electrode_position_create",
    ),
    re_path(
        r"^eeg_electrode_position/(?P<eeg_electrode_position_id>\d+)/$",
        views.eeg_electrode_position_view,
        name="eeg_electrode_position_view",
    ),
    re_path(
        r"^eeg_electrode_position/edit/(?P<eeg_electrode_position_id>\d+)/$",
        views.eeg_electrode_position_update,
        name="eeg_electrode_position_edit",
    ),
    re_path(
        r"^eeg_electrode_localization_system/(?P<eeg_electrode_localization_system_id>\d+)/new_coordinates/$",
        views.eeg_electrode_coordinates_create,
        name="eeg_electrode_coordinates_create",
    ),
    re_path(
        r"^eeg_electrode_localization_system/test/(?P<eeg_electrode_localization_system_id>\d+)/$",
        views.eeg_electrode_localization_system_test,
        name="eeg_electrode_localization_system_test",
    ),
    re_path(
        r"^eeg_electrode_position/change_the_order/(?P<eeg_electrode_position_id>\d+)/(?P<command>\w+)/$",
        views.eeg_electrode_position_change_the_order,
        name="eeg_electrode_position_change_the_order",
    ),
    # eeg setting
    re_path(
        r"^(?P<experiment_id>\d+)/eeg_setting/new/$",
        views.eeg_setting_create,
        name="eeg_setting_new",
    ),
    re_path(
        r"^eeg_setting/(?P<eeg_setting_id>\d+)/$",
        views.eeg_setting_view,
        name="eeg_setting_view",
    ),
    re_path(
        r"^eeg_setting/edit/(?P<eeg_setting_id>\d+)/$",
        views.eeg_setting_update,
        name="eeg_setting_edit",
    ),
    re_path(
        r"^eeg_setting/(?P<eeg_setting_id>\d+)/(?P<eeg_setting_type>\w+)/$",
        views.view_eeg_setting_type,
        name="view_eeg_setting_type",
    ),
    re_path(
        r"^eeg_setting/(?P<eeg_setting_id>\d+)/(?P<eeg_setting_type>\w+)/edit/$",
        views.edit_eeg_setting_type,
        name="edit_eeg_setting_type",
    ),
    re_path(
        r"^eeg_setting/eeg_electrode_position_status/(?P<eeg_setting_id>\d+)/$",
        views.eeg_electrode_position_setting,
        name="eeg_electrode_position_setting",
    ),
    re_path(
        r"^eeg_setting/eeg_electrode_cap/(?P<eeg_setting_id>\d+)/$",
        views.eeg_electrode_cap_setting,
        name="eeg_electrode_cap_setting",
    ),
    re_path(
        r"^eeg_setting/eeg_electrode_position_status/edit/(?P<eeg_setting_id>\d+)/$",
        views.edit_eeg_electrode_position_setting,
        name="edit_eeg_electrode_position_setting",
    ),
    re_path(
        r"^eeg_setting/eeg_electrode_position_status_model/(?P<eeg_setting_id>\d+)/$",
        views.eeg_electrode_position_setting_model,
        name="eeg_electrode_position_setting_model",
    ),
    re_path(
        r"^eeg_setting/eeg_electrode_position_status_model/edit/(?P<eeg_setting_id>\d+)/$",
        views.edit_eeg_electrode_position_setting_model,
        name="edit_eeg_electrode_position_setting_model",
    ),
    re_path(
        r"^eeg_electrode_position_setting/change_the_order/(?P<eeg_electrode_position_setting_id>\d+)/"
        r"(?P<command>\w+)/$",
        views.eeg_electrode_position_setting_change_the_order,
        name="eeg_electrode_position_setting_change_the_order",
    ),
    # eeg setting (ajax)
    re_path(
        r"^equipment/get_equipment_by_manufacturer/(?P<equipment_type>\w+)/(?P<manufacturer_id>\d+)/$",
        views.get_json_equipment_by_manufacturer,
    ),
    re_path(
        r"^equipment/(?P<equipment_id>\d+)/attributes/$",
        views.get_json_equipment_attributes,
    ),
    re_path(
        r"^solution/(?P<solution_id>\d+)/attributes/$",
        views.get_json_solution_attributes,
    ),
    re_path(
        r"^filter/(?P<filter_id>\d+)/attributes/$", views.get_json_filter_attributes
    ),
    re_path(
        r"^equipment/get_localization_system_by_electrode_net/(?P<equipment_id>\d+)/$",
        views.get_localization_system_by_electrode_net,
    ),
    re_path(
        r"^equipment/get_equipment_by_manufacturer_and_localization_system/"
        r"(?P<manufacturer_id>\w+)/(?P<eeg_localization_system_id>\d+)/$",
        views.get_equipment_by_manufacturer_and_localization_system,
    ),
    re_path(
        r"^eeg_electrode_localization_system/get_positions/(?P<eeg_electrode_localization_system_id>\d+)/$",
        views.get_json_positions,
    ),
    # emg setting
    re_path(
        r"^(?P<experiment_id>\d+)/emg_setting/new/$",
        views.emg_setting_create,
        name="emg_setting_new",
    ),
    re_path(
        r"^emg_setting/(?P<emg_setting_id>\d+)/$",
        views.emg_setting_view,
        name="emg_setting_view",
    ),
    re_path(
        r"^emg_setting/edit/(?P<emg_setting_id>\d+)/$",
        views.emg_setting_update,
        name="emg_setting_edit",
    ),
    re_path(
        r"^emg_setting/(?P<emg_setting_id>\d+)/digital_filter/$",
        views.emg_setting_digital_filter,
        name="emg_setting_digital_filter",
    ),
    re_path(
        r"^emg_setting/(?P<emg_setting_id>\d+)/digital_filter/edit/$",
        views.emg_setting_digital_filter_edit,
        name="emg_setting_digital_filter_edit",
    ),
    re_path(
        r"^emg_setting/(?P<emg_setting_id>\d+)/ad_converter/$",
        views.emg_setting_ad_converter,
        name="emg_setting_ad_converter",
    ),
    re_path(
        r"^emg_setting/(?P<emg_setting_id>\d+)/ad_converter/edit/$",
        views.emg_setting_ad_converter_edit,
        name="emg_setting_ad_converter_edit",
    ),
    re_path(
        r"^emg_setting/(?P<emg_setting_id>\d+)/electrode/add/$",
        views.emg_setting_electrode_add,
        name="emg_setting_electrode_add",
    ),
    re_path(
        r"^emg_electrode_setting/(?P<emg_electrode_setting_id>\d+)/$",
        views.emg_electrode_setting_view,
        name="emg_electrode_setting_view",
    ),
    re_path(
        r"^emg_electrode_setting/(?P<emg_electrode_setting_id>\d+)/edit/$",
        views.emg_electrode_setting_edit,
        name="emg_electrode_setting_edit",
    ),
    re_path(
        r"^emg_electrode_setting/(?P<emg_electrode_setting_id>\d+)/preamplifier/$",
        views.emg_electrode_setting_preamplifier,
        name="emg_electrode_setting_preamplifier",
    ),
    re_path(
        r"^emg_electrode_setting/(?P<emg_electrode_setting_id>\d+)/preamplifier/edit/$",
        views.emg_electrode_setting_preamplifier_edit,
        name="emg_electrode_setting_preamplifier_edit",
    ),
    re_path(
        r"^emg_electrode_setting/(?P<emg_electrode_setting_id>\d+)/amplifier/$",
        views.emg_electrode_setting_amplifier,
        name="emg_electrode_setting_amplifier",
    ),
    re_path(
        r"^emg_electrode_setting/(?P<emg_electrode_setting_id>\d+)/amplifier/edit/$",
        views.emg_electrode_setting_amplifier_edit,
        name="emg_electrode_setting_amplifier_edit",
    ),
    # emg setting (ajax)
    re_path(
        r"^emg_setting/get_muscle_side_by_electrode_placement/(?P<emg_electrode_placement_id>\d+)/$",
        views.get_json_muscle_side_by_electrode_placement,
    ),
    re_path(
        r"^emg_setting/get_electrode_model/(?P<electrode_id>\d+)/attributes/$",
        views.get_json_electrode_model,
    ),
    re_path(
        r"^emg_setting/get_electrode_by_type/(?P<electrode_type>\w+)/$",
        views.get_json_electrode_by_type,
    ),
    re_path(
        r"^emg_setting/get_electrode_placement_by_type/(?P<electrode_type>\w+)/$",
        views.get_electrode_placement_by_type,
    ),
    re_path(
        r"^emg_setting/get_description_by_placement/(?P<emg_electrode_type>\w+)/(?P<emg_electrode_placement_id>\d+)/$",
        views.get_anatomical_description_by_placement,
    ),
    re_path(
        r"^coilmodel/(?P<coilmodel_id>\d+)/attributes/$",
        views.get_json_coilmodel_attributes,
    ),
    # tms setting
    re_path(
        r"^(?P<experiment_id>\d+)/tms_setting/new/$",
        views.tms_setting_create,
        name="tms_setting_new",
    ),
    re_path(
        r"^tms_setting/(?P<tms_setting_id>\d+)/$",
        views.tms_setting_view,
        name="tms_setting_view",
    ),
    re_path(
        r"^tms_setting/edit/(?P<tms_setting_id>\d+)/$",
        views.tms_setting_update,
        name="tms_setting_edit",
    ),
    re_path(
        r"^tms_setting/(?P<tms_setting_id>\d+)/tms_device/$",
        views.tms_setting_tms_device,
        name="tms_setting_tms_device",
    ),
    re_path(
        r"^tms_setting/(?P<tms_setting_id>\d+)/tms_device/edit/$",
        views.tms_setting_tms_device_edit,
        name="tms_setting_tms_device_edit",
    ),
    re_path(
        r"^tms_setting/(?P<tms_setting_id>\d+)/coil_model/$",
        views.tms_setting_coil_model,
        name="tms_setting_coil_model",
    ),
    # context tree setting
    re_path(
        r"^(?P<experiment_id>\d+)/context_tree/new/$",
        views.context_tree_create,
        name="context_tree_new",
    ),
    re_path(
        r"^context_tree/(?P<context_tree_id>\d+)/$",
        views.context_tree_view,
        name="context_tree_view",
    ),
    re_path(
        r"^context_tree/edit/(?P<context_tree_id>\d+)/$",
        views.context_tree_update,
        name="context_tree_edit",
    ),
    # cid
    re_path(r"^group_diseases/cid-10/$", views.search_cid10_ajax, name="cid10_search"),
    # classification_of_diseases (add, remove)
    re_path(
        r"^group/(?P<group_id>\d+)/diagnosis/(?P<classification_of_diseases_id>\d+)/$",
        views.classification_of_diseases_insert,
        name="classification_of_diseases_insert",
    ),
    re_path(
        r"^diagnosis/delete/(?P<group_id>\d+)/(?P<classification_of_diseases_id>\d+)/$",
        views.classification_of_diseases_remove,
        name="classification_of_diseases_remove",
    ),
    # subject
    re_path(r"^group/(?P<group_id>\d+)/subjects/$", views.subjects, name="subjects"),
    re_path(r"^subject/search/$", views.search_patients_ajax, name="subject_search"),
    re_path(
        r"^group/(?P<group_id>\d+)/add_subject/(?P<patient_id>\d+)/$",
        views.subjects_insert,
        name="subject_insert",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/upload_file/$",
        views.upload_file,
        name="upload_file",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/search_subjects/$",
        views.search_subjects,
        name="search_subjects",
    ),
    # subject + questionnaire
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/$",
        views.subject_questionnaire_view,
        name="subject_questionnaire",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/questionnaire/"
        r"(?P<questionnaire_id>[0-9-]+)/add_response/$",
        views.subject_questionnaire_response_create,
        name="subject_questionnaire_response",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/questionnaire/"
        r"(?P<questionnaire_id>[0-9-]+)/reuse_fill/(?P<patient_questionnaire_response_id>\d+)$",
        views.subject_questionnaire_response_reuse,
        name="subject_questionnaire_response_reuse",
    ),
    re_path(
        r"^questionnaire_response/edit/(?P<questionnaire_response_id>\d+)/$",
        views.questionnaire_response_edit,
        name="questionnaire_response_edit",
    ),
    re_path(
        r"^questionnaire_response/(?P<questionnaire_response_id>\d+)/$",
        views.questionnaire_response_view,
        name="questionnaire_response_view",
    ),
    # subject + questionnaire data
    re_path(
        r"^group/(?P<group_id>\d+)/load_questionnaire_data/$",
        views.load_questionnaire_data,
        name="load_questionnaire_data",
    ),
    # subject + eeg data
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/eeg/$",
        views.subject_eeg_view,
        name="subject_eeg_view",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/eeg/(?P<eeg_configuration_id>[0-9-]+)/add_eeg_data/$",
        views.subject_eeg_data_create,
        name="subject_eeg_data_create",
    ),
    re_path(
        r"^eeg_data/(?P<eeg_data_id>\d+)/(?P<tab>\d+)/$",
        views.eeg_data_view,
        name="eeg_data_view",
    ),
    re_path(
        r"^eeg_data/edit/(?P<eeg_data_id>\d+)/(?P<tab>\d+)/$",
        views.eeg_data_edit,
        name="eeg_data_edit",
    ),
    re_path(
        r"^eeg_data/edit_image/(?P<eeg_data_id>\d+)/(?P<tab>\d+)/$",
        views.eeg_image_edit,
        name="eeg_image_edit",
    ),
    re_path(
        r"^eeg_file/(?P<eeg_file_id>\d+)/export_nwb/(?P<some_number>\d+)/(?P<process_requisition>\d+)/$",
        views.eeg_file_export_nwb,
        name="eeg_file_export_nwb",
    ),
    re_path(
        r"^eeg_electrode_position_collection_status/change_the_order/"
        r"(?P<eeg_electrode_position_collection_status_id>\d+)/(?P<command>\w+)/$",
        views.eeg_electrode_position_collection_status_change_the_order,
        name="eeg_electrode_position_collection_status_change_the_order",
    ),
    # eeg_data (ajax)
    re_path(
        r"^equipment/get_cap_size_list_from_eeg_setting/(?P<eeg_setting_id>\d+)/$",
        views.get_cap_size_list_from_eeg_setting,
    ),
    re_path(r"eeg_data/edit_image/set_worked_positions/$", views.set_worked_positions),
    re_path(
        r"^eeg_data/get_process_requisition_status/(?P<process_requisition>\d+)/$",
        views.eeg_data_get_process_requisition_status,
    ),
    # subject + emg data
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/emg/$",
        views.subject_emg_view,
        name="subject_emg_view",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/emg/(?P<emg_configuration_id>[0-9-]+)/add_emg_data/$",
        views.subject_emg_data_create,
        name="subject_emg_data_create",
    ),
    re_path(
        r"^emg_data/(?P<emg_data_id>\d+)/$", views.emg_data_view, name="emg_data_view"
    ),
    re_path(
        r"^emg_data/edit/(?P<emg_data_id>\d+)/$",
        views.emg_data_edit,
        name="emg_data_edit",
    ),
    # subject + tms_data
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/tms/$",
        views.subject_tms_view,
        name="subject_tms_view",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/tms/(?P<tms_configuration_id>[0-9-]+)/add_tms_data/$",
        views.subject_tms_data_create,
        name="subject_tms_data_create",
    ),
    re_path(
        r"^tms_data/(?P<tms_data_id>\d+)/$", views.tms_data_view, name="tms_data_view"
    ),
    re_path(
        r"^tms_data/edit/(?P<tms_data_id>\d+)/(?P<tab>\d+)/$",
        views.tms_data_edit,
        name="tms_data_edit",
    ),
    re_path(
        r"^tms_data/(?P<tms_data_id>\d+)/position_setting_register/$",
        views.tms_data_position_setting_register,
        name="tms_data_position_setting_register",
    ),
    re_path(
        r"^tms_data/(?P<tms_data_id>\d+)/position_setting_view/$",
        views.tms_data_position_setting_view,
        name="tms_data_position_setting_view",
    ),
    # data collection
    re_path(
        r"^group/(?P<group_id>\d+)/data_collection_manage/"
        r"(?P<path_of_configuration>[0-9-]+)/(?P<data_type>\w+)/$",
        views.data_collection_manage,
        name="data_collection_manage",
    ),
    # tms_data(ajax)
    re_path(
        r"^get_pulse_by_tms_setting/(?P<tms_setting_id>\d+)/$",
        views.get_pulse_by_tms_setting,
    ),
    # subject + digital_game_phase_data
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/digital_game_phase/$",
        views.subject_digital_game_phase_view,
        name="subject_digital_game_phase_view",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/digital_game_phase/"
        r"(?P<digital_game_phase_configuration_id>[0-9-]+)/add_digital_game_phase_data/$",
        views.subject_digital_game_phase_data_create,
        name="subject_digital_game_phase_data_create",
    ),
    re_path(
        r"^digital_game_phase_data/(?P<digital_game_phase_data_id>\d+)/$",
        views.digital_game_phase_data_view,
        name="digital_game_phase_data_view",
    ),
    re_path(
        r"^digital_game_phase_data/edit/(?P<digital_game_phase_data_id>\d+)/$",
        views.digital_game_phase_data_edit,
        name="digital_game_phase_data_edit",
    ),
    # subject + goalkeeper_game_data
    re_path(
        r"^group/(?P<group_id>\d+)/goalkeeper_game_data/$",
        views.group_goalkeeper_game_data,
        name="group_goalkeeper_game_data",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/load_goalkeeper_game_data/$",
        views.load_group_goalkeeper_game_data,
        name="load_group_goalkeeper_game_data",
    ),
    # subject + generic_data_collection_data
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/generic_data_collection/$",
        views.subject_generic_data_collection_view,
        name="subject_generic_data_collection_view",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/generic_data_collection/"
        r"(?P<generic_data_collection_configuration_id>[0-9-]+)/add_generic_data_collection_data/$",
        views.subject_generic_data_collection_data_create,
        name="subject_generic_data_collection_data_create",
    ),
    re_path(
        r"^generic_data_collection_data/(?P<generic_data_collection_data_id>\d+)/$",
        views.generic_data_collection_data_view,
        name="generic_data_collection_data_view",
    ),
    re_path(
        r"^generic_data_collection_data/edit/(?P<generic_data_collection_data_id>\d+)/$",
        views.generic_data_collection_data_edit,
        name="generic_data_collection_data_edit",
    ),
    # subject + additional data
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/additional_data/$",
        views.subject_additional_data_view,
        name="subject_additional_data_view",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/additional_data/"
        r"(?P<path_of_configuration>[0-9-]+)/add/$",
        views.subject_additional_data_create,
        name="subject_additional_data_create",
    ),
    re_path(
        r"^additional_data/(?P<additional_data_id>\d+)/$",
        views.additional_data_view,
        name="additional_data_view",
    ),
    re_path(
        r"^additional_data/edit/(?P<additional_data_id>\d+)/$",
        views.additional_data_edit,
        name="additional_data_edit",
    ),
    re_path(
        r"^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/subject_step_data/"
        r"(?P<path_of_configuration>[0-9-]+)/add/$",
        views.subject_step_data_create,
        name="subject_step_data_create",
    ),
    re_path(
        r"^subject_step_data/edit/(?P<subject_step_data_id>\d+)/$",
        views.subject_step_data_edit,
        name="subject_step_data_edit",
    ),
    # experimental protocol components
    re_path(
        r"^(?P<experiment_id>\d+)/components/$",
        views.component_list,
        name="component_list",
    ),
    re_path(
        r"^(?P<experiment_id>\d+)/new_component/(?P<component_type>\w+)/$",
        views.component_create,
        name="component_new",
    ),
    re_path(
        r"^component/(?P<path_of_the_components>[0-9-UG]+)/$",
        views.component_view,
        name="component_view",
    ),
    re_path(
        r"^component/edit/(?P<path_of_the_components>[0-9-UG]+)/$",
        views.component_update,
        name="component_edit",
    ),
    re_path(
        r"^component/(?P<path_of_the_components>[0-9-UG]+)/add_new/(?P<component_type>\w+)/$",
        views.component_add_new,
        name="component_add_new",
    ),
    re_path(
        r"^component/(?P<path_of_the_components>[0-9-UG]+)/add/(?P<component_id>\d+)/$",
        views.component_reuse,
        name="component_reuse",
    ),
    re_path(
        r"^component/change_the_order/(?P<path_of_the_components>[0-9-UG]+)/(?P<component_configuration_index>[0-9-]+)/"
        r"(?P<command>\w+)/$",
        views.component_change_the_order,
        name="component_change_the_order",
    ),
    # Questionnaire
    re_path(
        r"^group/(?P<group_id>\d+)/questionnaire/(?P<component_configuration_id>\d+)/$",
        views.questionnaire_view,
        name="questionnaire_view",
    ),
]
