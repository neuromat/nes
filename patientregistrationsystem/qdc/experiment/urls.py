from django.conf.urls import patterns, url

urlpatterns = patterns(
    'experiment.views',

    # keyword
    url(r'^keyword/search/$', 'keyword_search_ajax', name='keywords_search'),
    url(r'^keyword/new/(?P<research_project_id>\d+)/(?P<keyword_name>.+)/$', 'keyword_create_ajax', name='keyword_new'),
    url(r'^keyword/add/(?P<research_project_id>\d+)/(?P<keyword_id>\d+)/$', 'keyword_add_ajax', name='keyword_add'),
    url(r'^keyword/remove/(?P<research_project_id>\d+)/(?P<keyword_id>\d+)/$', 'keyword_remove_ajax',
        name='keyword_remove'),

    # research project
    url(r'^research_project/list/$', 'research_project_list', name='research_project_list'),
    url(r'^research_project/new/$', 'research_project_create', name='research_project_new'),
    url(r'^research_project/(?P<research_project_id>\d+)/$', 'research_project_view', name='research_project_view'),
    url(r'^research_project/edit/(?P<research_project_id>\d+)/$', 'research_project_update',
        name='research_project_edit'),

    # experiment
    url(r'^research_project/(?P<research_project_id>\d+)/new_experiment/$', 'experiment_create', name='experiment_new'),
    url(r'^(?P<experiment_id>\d+)/$', 'experiment_view', name='experiment_view'),
    url(r'^edit/(?P<experiment_id>\d+)/$', 'experiment_update', name='experiment_edit'),

    # group
    url(r'^(?P<experiment_id>\d+)/group/new/$', 'group_create', name='group_new'),
    url(r'^group/(?P<group_id>\d+)/$', 'group_view', name='group_view'),
    url(r'^group/edit/(?P<group_id>\d+)/$', 'group_update', name='group_edit'),

    # eeg setting
    url(r'^(?P<experiment_id>\d+)/eeg_setting/new/$', 'eeg_setting_create', name='eeg_setting_new'),
    url(r'^eeg_setting/(?P<eeg_setting_id>\d+)/$', 'eeg_setting_view', name='eeg_setting_view'),
    url(r'^eeg_setting/edit/(?P<eeg_setting_id>\d+)/$', 'eeg_setting_update', name='eeg_setting_edit'),
    url(r'^eeg_setting/(?P<eeg_setting_id>\d+)/add_equipment/(?P<equipment_category_id>\d+)/$',
        'equipment_add', name='equipment_add'),
    url(r'^eeg_setting/(?P<eeg_setting_id>\d+)/equipment/(?P<equipment_id>\d+)/$',
        'equipment_view', name='equipment_view'),

    # eeg setting (ajax)
    url(r'^equipment/get_models_by_manufacturer/(?P<equipment_category_id>\d+)/(?P<manufacturer_id>\d+)/$',
        'get_json_equipment_model_by_manufacturer'),
    url(r'^equipment/get_equipment_by_manufacturer/(?P<equipment_category_id>\d+)/(?P<manufacturer_id>\d+)/$',
        'get_json_equipment_by_manufacturer'),
    url(r'^equipment/get_equipment_by_manufacturer_and_model/(?P<equipment_category_id>\d+)/'
        r'(?P<manufacturer_id>\d+)/(?P<equipment_model_id>\d+)/$',
        'get_json_equipment_by_manufacturer_and_model'),
    url(r'^equipment/(?P<equipment_id>\d+)/attributes/$', 'get_json_equipment_attributes'),

    # cid
    url(r'^group_diseases/cid-10/$', 'search_cid10_ajax', name='cid10_search'),

    # classification_of_diseases (add, remove)
    url(r'^group/(?P<group_id>\d+)/diagnosis/(?P<classification_of_diseases_id>\d+)/$',
        'classification_of_diseases_insert', name='classification_of_diseases_insert'),
    url(r'^diagnosis/delete/(?P<group_id>\d+)/(?P<classification_of_diseases_id>\d+)/$',
        'classification_of_diseases_remove', name='classification_of_diseases_remove'),

    # subject
    url(r'^group/(?P<group_id>\d+)/subjects/$', 'subjects', name='subjects'),
    url(r'^subject/search/$', 'search_patients_ajax', name='subject_search'),
    url(r'^group/(?P<group_id>\d+)/add_subject/(?P<patient_id>\d+)/$', 'subjects_insert', name='subject_insert'),
    url(r'^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/upload_file/$', 'upload_file', name='upload_file'),

    # subject + questionnaire
    url(r'^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/$',
        'subject_questionnaire_view', name='subject_questionnaire'),
    url(r'^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/questionnaire/(?P<questionnaire_id>\d+)/add_response/$',
        'subject_questionnaire_response_create', name='subject_questionnaire_response'),
    url(r'^questionnaire_response/edit/(?P<questionnaire_response_id>\d+)/$',
        'questionnaire_response_edit', name='questionnaire_response_edit'),
    url(r'^questionnaire_response/(?P<questionnaire_response_id>\d+)/$',
        'questionnaire_response_view', name='questionnaire_response_view'),

    # subject + eeg data
    url(r'^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/eeg/$',
        'subject_eeg_view', name='subject_eeg_view'),
    url(r'^group/(?P<group_id>\d+)/subject/(?P<subject_id>\d+)/eeg/(?P<eeg_configuration_id>\d+)/add_eeg_data/$',
        'subject_eeg_data_create', name='subject_eeg_data_create'),
    url(r'^eeg_data/(?P<eeg_data_id>\d+)/$', 'eeg_data_view', name='eeg_data_view'),
    url(r'^eeg_data/edit/(?P<eeg_data_id>\d+)/$', 'eeg_data_edit', name='eeg_data_edit'),

    # experimental protocol components
    url(r'^(?P<experiment_id>\d+)/components/$', 'component_list', name='component_list'),
    url(r'^(?P<experiment_id>\d+)/new_component/(?P<component_type>\w+)/$', 'component_create', name='component_new'),
    url(r'^component/(?P<path_of_the_components>[0-9-UG]+)/$', 'component_view', name='component_view'),
    url(r'^component/edit/(?P<path_of_the_components>[0-9-UG]+)/$', 'component_update', name='component_edit'),
    url(r'^component/(?P<path_of_the_components>[0-9-UG]+)/add_new/(?P<component_type>\w+)/$', 'component_add_new',
        name='component_add_new'),
    url(r'^component/(?P<path_of_the_components>[0-9-UG]+)/add/(?P<component_id>\d+)/$', 'component_reuse',
        name='component_reuse'),
    url(r'^component/change_the_order/(?P<path_of_the_components>[0-9-UG]+)/(?P<component_configuration_index>[0-9-]+)/'
        r'(?P<command>\w+)/$', 'component_change_the_order', name='component_change_the_order'),

    # Data collection
    url(r'^group/(?P<group_id>\d+)/questionnaire/(?P<component_configuration_id>\d+)/$', 'questionnaire_view',
        name='questionnaire_view'),
)
