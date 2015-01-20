from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    # experiment
    url(r'^list/$', 'experiment.views.experiment_list', name='experiment_list'),
    url(r'^new/$', 'experiment.views.experiment_create', name='experiment_new'),
    url(r'^edit/(?P<experiment_id>\d+)/$', 'experiment.views.experiment_update', name='experiment_edit'),

    # group
    url(r'^(?P<experiment_id>\d+)/group/new/$',
        'experiment.views.group_create', name='group_new'),
    url(r'^group/edit/(?P<group_id>\d+)/$',
        'experiment.views.group_update', name='group_edit'),

    # cid
    url(r'^group_diseases/cid-10/$', 'experiment.views.search_cid10_ajax', name='cid10_search'),

    # classification_of_diseases (add, remove)
    url(r'^group/edit/(?P<group_id>\d+)/diagnosis/(?P<classification_of_diseases_id>\d+)/$',
        'experiment.views.classification_of_diseases_insert', name='classification_of_diseases_insert'),
    url(r'^diagnosis/delete/(?P<group_id>\d+)/(?P<classification_of_diseases_id>\d+)/$',
        'experiment.views.classification_of_diseases_remove', name='classification_of_diseases_remove'),

    # questionnaire
    url(r'^group/(?P<group_id>\d+)/questionnaire/new/$',
        'experiment.views.questionnaire_create', name='questionnaire_new'),
    url(r'^questionnaire/edit/(?P<questionnaire_configuration_id>\d+)/$',
        'experiment.views.questionnaire_update', name='questionnaire_edit'),

    # subject
    url(r'^group/(?P<group_id>\d+)/subjects/$', 'experiment.views.subjects', name='subjects'),
    url(r'^subject/search/$', 'experiment.views.search_patients_ajax', name='subject_search'),
    url(r'^group/(?P<group_id>\d+)/subjects/(?P<patient_id>\d+)/$',
        'experiment.views.subjects_insert', name='subject_insert'),
    url(r'^group/(?P<group_id>\d+)/subjects/(?P<subject_id>\d+)/upload_file/$',
        'experiment.views.upload_file', name='upload_file'),

    # subject + questionnaire
    url(r'^group/(?P<group_id>\d+)/subjects/(?P<subject_id>\d+)/questionnaire/$',
        'experiment.views.subject_questionnaire_view', name='subject_questionnaire'),
    url(r'^subjects/(?P<subject_id>\d+)/questionnaire/(?P<questionnaire_id>\d+)/response/$',
        'experiment.views.subject_questionnaire_response_create', name='subject_questionnaire_response'),
    url(r'^questionnaire_response/edit/(?P<questionnaire_response_id>\d+)/$',
        'experiment.views.questionnaire_response_update', name='questionnaire_response_edit'),
    url(r'^questionnaire_response/(?P<questionnaire_response_id>\d+)/$',
        'experiment.views.questionnaire_response_view', name='questionnaire_response_view'),

    # component swap order
    url(r'^component/edit/(?P<component_id>\d+)/(?P<component_type>\w+)/(?P<first_order>\d+)/'
        r'(?P<second_order>\d+)/$',
        'experiment.views.swap_component', name='swap_component'),

    # experimental protocol components
    url(r'^(?P<experiment_id>\d+)/components/$',
        'experiment.views.component_list', name='component_list'),
    url(r'^(?P<experiment_id>\d+)/new_component/(?P<component_type>\w+)/$',
        'experiment.views.component_create', name='component_new'),
    url(r'^component/edit/(?P<component_id>\d+)/(?P<component_type>\w+)/$',
        'experiment.views.component_update', name='component_edit'),

    # experimental protocol components with configuration
    url(r'^(?P<experiment_id>\d+)/sequence/(?P<sequence_id>\d+)/new_component/(?P<component_type>\w+)/$',
        'experiment.views.sequence_component_create', name='sequence_component_new'),
    url(r'^(?P<experiment_id>\d+)/sequence/(?P<sequence_id>\d+)/component/(?P<component_id>\d+)/$',
        'experiment.views.sequence_component_reuse', name='sequence_component_reuse'),
    url(r'^component_configuration/(?P<component_configuration_id_list>[0-9-]+)/$',
        'experiment.views.sequence_component_update', name='sequence_component_update'),

    # configuration of experimental protocol
    url(r'^group/(?P<group_id>\d+)/experimental_protocol/new/$',
        'experiment.views.experimental_protocol_create', name='experimental_protocol_new'),
    # url(r'^group/(?P<group_id>\d+)/experimental_protocol/(?P<experimental_protocol_id>\d+)/$',
    #     'experiment.views.experimental_protocol_reuse', name='experimental_protocol_reuse'),
    # url(r'^experimental_protocol/(?P<experimental_protocol_id>\d+)/$',
    #     'experiment.views.experimental_protocol_update', name='experimental_protocol_update'),

)
