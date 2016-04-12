import json

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from os import path
from csv import writer
from sys import modules
from zipfile import ZipFile
from shutil import rmtree

from .forms import ExportForm, ParticipantsSelectionForm, AgeIntervalForm
from .models import Export
from .export import ExportExecution, perform_csv_response, create_directory

from export.input_export import build_complete_export_structure

from patient.models import QuestionnaireResponse
from patient.views import check_limesurvey_access

from survey.models import Survey
from survey.abc_search_engine import Questionnaires

JSON_FILENAME = "json_export.json"
EXPORT_DIRECTORY = "export"

patient_fields = [
    {"field": 'id', "header": 'id'},
    {"field": 'name', "header": 'name'},
    {"field": 'gender__name', "header": 'gender'},
    {"field": 'date_birth', "header": 'date_birth'},
    {"field": 'marital_status', "header": 'marital_status'},
    {"field": 'origin', "header": 'origin'},
    {"field": 'city', "header": 'city'},
    {"field": 'state', "header": 'state'},
    {"field": 'country', "header": 'country'},
    {"field": 'socialdemographicdata__natural_of', "header": 'natural_of'},
    {"field": 'socialdemographicdata__schooling', "header": 'schooling'},
    {"field": 'socialdemographicdata__profession', "header": 'profession'},
    {"field": 'socialdemographicdata__social_class', "header": 'social_class'},
    {"field": 'socialdemographicdata__occupation', "header": 'occupation'},
    {"field": 'socialdemographicdata__benefit_government', "header": 'benefit_government'},
    {"field": 'socialdemographicdata__religion', "header": 'religion'},
    {"field": 'socialdemographicdata__flesh_tone', "header": 'flesh_tone'},
    {"field": 'socialdemographicdata__citizenship', "header": 'citizenship'},
    {"field": 'socialdemographicdata__payment', "header": 'payment'},
    {"field": 'socialhistorydata__alcohol_period', "header": 'alcohol_period'},
    {"field": 'socialhistorydata__alcohol_frequency', "header": 'alcohol_frequency'},
    {"field": 'socialhistorydata__smoker', "header": 'smoker'},
    {"field": 'socialhistorydata__alcoholic', "header": 'alcoholic'},
    {"field": 'socialhistorydata__drugs', "header": 'drugs'},
    {"field": 'socialhistorydata__ex_smoker', "header": 'former_smoker'},
    {"field": 'socialhistorydata__alcohol_frequency', "header": 'alcohol_frequency'},
    {"field": 'socialhistorydata__amount_cigarettes', "header": 'amount_cigarettes'},
]

diagnosis_fields = [

    {"field": "medicalrecorddata__record_responsible_id", "header": 'responsible_id'},
    {"field": "medicalrecorddata__record_responsible__username", "header": 'responsible_username'},
    {"field": "medicalrecorddata__diagnosis__date", "header": 'diagnosis_date'},
    {"field": "medicalrecorddata__diagnosis__description", "header": 'diagnosis_description'},
    {"field": "medicalrecorddata__diagnosis__classification_of_diseases__description",
     "header": 'classification_of_diseases_description'},
    {"field": "medicalrecorddata__diagnosis__classification_of_diseases_id", "header": 'classification_of_diseases_id'},
]

patient_fields_inclusion = [
    ["code", "participation_code"],
]

diagnosis_fields_inclusion = [
    ["medicalrecorddata__patient__code", 'participation_code'],
]

'''

Diagnosis._meta.get_all_field_names()
['description', 'medical_record_data_id', 'complementaryexam', 'classification_of_diseases_id',
'classification_of_diseases', 'date', 'id', 'medical_record_data']


SocialDemographicData._meta.get_all_field_names()
['natural_of', 'changed_by_id', 'tv', 'wash_machine', 'flesh_tone', 'payment_id',
'house_maid', 'automobile', 'schooling', 'radio', 'profession', 'dvd', 'bath', 'freezer',
'social_class', 'schooling_id', 'occupation', 'changed_by', 'benefit_government', 'religion_id',
'flesh_tone_id', 'refrigerator', 'patient', 'religion', 'citizenship', 'id', 'patient_id', 'payment']

SocialHistoryData._meta.get_all_field_names()
['alcohol_period', 'alcohol_period_id', 'alcohol_frequency_id', 'smoker', 'alcoholic', 'drugs',
'ex_smoker', 'changed_by', 'changed_by_id',
'alcohol_frequency', 'amount_cigarettes_id', 'id', 'patient_id', 'amount_cigarettes', 'patient']


    ['email', 'address_complement', 'changed_by_id', 'cpf', 'medicalrecorddata',
     'district',
     'zipcode', 'address_number',

     'marital_status_id',
     'telephone', 'rg', 'state',
     'socialhistorydata', 'gender_id', 'changed_by', 'subject',
     'origin', 'medical_record', 'removed',
     'city',
     'marital_status',
     'country',
     'street', 'questionnaireresponse']
     'socialdemographicdata',


'''
# BASE_DIRECTORY = 'NES_EXPORT'

header_explanation_fields = ['questionnaire_id',
                             'questionnaire_title',
                             'question_code',
                             'question_description',
                             'subquestion_code',
                             'subquestion_description',
                             'option_code',
                             'option_description',
                             'option_value',
                             'column_title']


def get_headers_and_fields(output_list):
    """
    :param output_list: list with fields and headers
    :return: list of headers
             list of fields
    """

    headers = []
    fields = []

    for element in output_list:
        if element["field"]:
            headers.append(element["header"])
            fields.append(element["field"])

    return headers, fields


def read_configuration_data(json_file):
    json_data = open(json_file)

    read_data = json.load(json_data)

    json_data.close()

    return read_data


def process_participant_data(participants, participants_list):
    export_rows_participants = []

    for participant in participants:
        headers, fields = get_headers_and_fields(participant["output_list"])

        model_to_export = getattr(modules['patient.models'], 'Patient')

        db_data = model_to_export.objects.filter(id__in=participants_list).values_list(*fields).extra(order_by=['id'])

        export_rows_participants = [headers]

        # transform data
        for record in db_data:
            export_rows_participants.append([smart_str(field) for field in record])

    return export_rows_participants


def create_export_instance(user):
    export_instance = Export(user=user)

    export_instance.save()

    return export_instance


def get_export_instance(user, export_id):
    export_instance = Export.objects.get(user=user, id=export_id)

    return export_instance


def update_export_instance(input_file, output_export, export_instance):
    export_instance.input_file = input_file
    export_instance.output_export = output_export
    export_instance.save()


def update_participants_list(participants_list):
    # include participation_code

    if participants_list:
        for field, header in patient_fields_inclusion:
            participants_list.append([field, header])


def update_diagnosis_list(diagnosis_list):

    if diagnosis_list:
        for field, header in diagnosis_fields_inclusion:
            diagnosis_list.append([field, header])


# @login_required
# @permission_required('questionnaire.create_export')
# def export_create(request, template_name="export/export_data.html"):
def export_create(request, export_id, input_filename, template_name="export/export_data.html"):
    try:

        export_instance = get_export_instance(request.user, export_id)

        export = ExportExecution(export_instance.user.id, export_instance.id)

        # files_to_zip_list = []

        # export_instance = create_export_instance(request.user)
        #
        # # directory_root = path.join("export", path.join(str(request.user.id), str(export_instance.id)))
        # export.set_directory_base(request.user.id, export_instance.id)
        #
        base_directory, path_to_create = path.split(export.get_directory_base())
        #
        # path_to_create = base_directory[1]
        # base_directory = base_directory[0]
        #
        error_msg, base_directory_name = create_directory(base_directory, path_to_create)
        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)
        #
        # # Read initial json file
        # json_filename = "json_export.json"
        # path_source = path.join(settings.BASE_DIR, "export")
        # input_name = path.join(path_source, json_filename)
        #
        input_export_file = path.join("export", path.join(str(request.user.id),
                                                          path.join(str(export_instance.id), str(JSON_FILENAME))))
        #
        # # copy data to .../media/export/<user_id>/<export_id>/
        # input_filename = path.join(settings.MEDIA_ROOT, input_export_file)
        #
        # copy(input_name, input_filename)

        # prepare data to be processed

        input_data = export.read_configuration_data(input_filename)

        if not export.is_input_data_consistent() or not input_data:
            messages.error(request, _("Inconsistent data read from json file"))
            return render(request, template_name)

        # create directory base for export: /NES_EXPORT
        error_msg = export.create_export_directory()

        # error_msg, base_export_directory = create_directory(base_directory_name, base_directory)

        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)

        # process per questionnaire data

        error_msg = export.process_per_questionnaire()
        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)

        # process per participant data
        error_msg = export.process_per_participant()
        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)

        # process participants
        # only participants that were used in questionnaire: export.get_per_participant_data().keys()
        participants_list = (export.get_participants_filtered_data())
        # participants_list = (export.get_per_participant_data().keys())
        participants_input_data = export.get_input_data("participants")

        if participants_input_data and participants_list:

            export_rows_participants = process_participant_data(participants_input_data, participants_list)

            export_filename = "%s.csv" % export.get_input_data('participants')[0]["output_filename"]  # "export.csv"

            base_export_directory = export.get_export_directory()
            base_directory = export.get_input_data("base_directory")   # /NES_EXPORT

            complete_filename = path.join(base_export_directory, export_filename)

            export.files_to_zip_list.append([complete_filename, base_directory])

            with open(complete_filename, 'w', newline='', encoding='UTF-8') as csv_file:
                export_writer = writer(csv_file)
                for row in export_rows_participants:
                    export_writer.writerow(row)

        # process  diagnosis file
        diagnosis_input_data = export.get_input_data("diagnosis")

        if diagnosis_input_data and participants_list:
            export_rows_diagnosis = process_participant_data(diagnosis_input_data, participants_list)

            export_filename = "%s.csv" % export.get_input_data('diagnosis')[0]["output_filename"]  # "export.csv"

            base_directory = export.get_input_data("base_directory")   # /NES_EXPORT
            base_export_directory = export.get_export_directory()

            complete_filename = path.join(base_export_directory, export_filename)

            # files_to_zip_list.append(complete_filename)
            export.files_to_zip_list.append([complete_filename, base_directory])

            with open(complete_filename, 'w', newline='', encoding='UTF-8') as csv_file:
                export_writer = writer(csv_file)
                for row in export_rows_diagnosis:
                    export_writer.writerow(row)

        # create zip file and include files
        export_complete_filename = ""
        if export.files_to_zip_list:
            export_filename = export.get_input_data("export_filename")  # 'export.zip'

            export_complete_filename = path.join(base_directory_name, export_filename)

            with ZipFile(export_complete_filename, 'w') as zip_file:
                for filename, directory in export.files_to_zip_list:
                    fdir, fname = path.split(filename)

                    zip_file.write(filename, path.join(directory, fname))

            zip_file.close()

            output_export_file = path.join("export", path.join(str(export_instance.user.id),
                                                               path.join(str(export_instance.id),
                                                                         str(export_filename))))

            update_export_instance(input_export_file, output_export_file, export_instance)

            print("finalizado corretamente")

        # print(export_filename)
        # print(complete_filename)

        # delete temporary directory: from base_directory and below
        base_export_directory = export.get_export_directory()
        rmtree(base_export_directory)

        # messages.success(request, _("Export was finished correctly"))

        return export_complete_filename
        # return file to the user
        # zip_file = open(complete_filename, 'rb')
        # response = HttpResponse(zip_file, content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename="export.zip"'
        # response['Content-Length'] = path.getsize(complete_filename)
        # return response

    except OSError as e:
        print(e)
        error_msg = e
        messages.error(request, error_msg)
        return render(request, template_name)


@login_required
def export_view(request, template_name="export/export_data.html"):
    export_form = ExportForm(request.POST or None, initial={'title': 'title'})
    # , 'per_participant': False,
    #                                                         'per_questinnaire': False})
    # export_form.per_participant = False
    # export_form.per_questionnaire = True

    # context = {}

    # test with pagination
    # a = [{"b": "2", "c": "3"}, {"d": "7", "e": "8"}]
    # b = [1, 2, 3, 4, 5]
    # c = [7, 9, (4, 3, 2)]
    #
    # contact_list = [a, b, c]
    #
    # paginator = Paginator(contact_list, 1)  # Show 1 info per page
    #
    # page = request.GET.get('page')
    # try:
    #     contacts = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     page = 1
    #     contacts = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     page = paginator.num_pages
    #     contacts = paginator.page(paginator.num_pages)
    # page = 1
    #
    # if page == 1:

    selected_ev_quest = []
    selected_participant = []
    selected_diagnosis = []

    if request.method == "POST":

        questionnaires_selected_list = request.POST.getlist('questionnaire_selected')

        questionnaires_list = []

        previous_questionnaire_id = 0
        output_list = []
        for questionnaire in questionnaires_selected_list:
            sid, title, field, header = questionnaire.split("*")

            sid = int(sid)    # transform to integer
            if sid != previous_questionnaire_id:
                if previous_questionnaire_id != 0:
                    output_list = []

                questionnaires_list.append([sid, title, output_list])

                previous_questionnaire_id = sid

            output_list.append((field, header))

        # get participants list
        participant_selected_list = request.POST.getlist('patient_selected')

        participants_list = []

        for participant in participant_selected_list:
            participants_list.append(participant.split("*"))

        # get diagnosis list
        diagnosis_selected_list = request.POST.getlist('diagnosis_selected')

        diagnosis_list = []

        for diagnosis in diagnosis_selected_list:
            diagnosis_list.append(diagnosis.split("*"))

        selected_data_available = (len(questionnaires_selected_list) or
                                   len(participant_selected_list) or len(diagnosis_selected_list))

        if selected_data_available:

            if export_form.is_valid():
                print("valid data")

                per_participant = export_form.cleaned_data['per_participant']
                per_questionnaire = export_form.cleaned_data['per_questionnaire']

                # insert participation_code
                update_participants_list(participants_list)
                update_diagnosis_list(diagnosis_list)

                # output_filename =
                # "/Users/sueli/PycharmProjects/nes/patientregistrationsystem/qdc/export/json_export_output2.json"

                # MEDIA_ROOT/export/username_id/export_id

                # input_export_file = create_initial_directory(request.user)

                export_instance = create_export_instance(request.user)

                input_export_file = path.join(EXPORT_DIRECTORY,
                                              path.join(str(request.user.id),
                                                        path.join(str(export_instance.id), str(JSON_FILENAME))))

                # copy data to .../media/export/<user_id>/<export_id>/
                input_filename = path.join(settings.MEDIA_ROOT, input_export_file)
                create_directory(settings.MEDIA_ROOT, path.split(input_export_file)[0])

                build_complete_export_structure(per_participant, per_questionnaire, participants_list, diagnosis_list,
                                                questionnaires_list, input_filename)

                complete_filename = export_create(request, export_instance.id, input_filename)

                if complete_filename:

                    messages.success(request, _("Export was finished correctly"))

                    # return file to the user

                    # error_message = "a"
                    # return_response = complete_filename
                    #
                    # redirect_url = reverse("export_result", args=(return_response, error_message))
                    # return HttpResponseRedirect(redirect_url )

                    zip_file = open(complete_filename, 'rb')
                    response = HttpResponse(zip_file, content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename="export.zip"'
                    response['Content-Length'] = path.getsize(complete_filename)
                    return response
                else:
                    messages.error(request, _("Export data was not generated."))

            else:
                for questionnaire in questionnaires_list:
                    for field in questionnaire[2]:  # get output_list
                        selected_ev_quest.append((questionnaire[0], field[0]))

                for participant in participants_list:
                    selected_participant.append(participant[0])

                for diagnosis in diagnosis_list:
                    selected_diagnosis.append(diagnosis[0])
        else:
            messages.error(request, _("No data was select. Export data was not generated."))

    # else:
    # page 1 - list of questionnaires
    surveys = Questionnaires()
    limesurvey_available = check_limesurvey_access(request, surveys)

    questionnaires_list = []

    if limesurvey_available:
        questionnaires_list = surveys.find_all_active_questionnaires()

    surveys.release_session_key()

    questionnaires_list_final = []

    # removing surveys that are not entrance evaluation
    # entrance_evaluation_questionnaires = QuestionnaireResponse.objects.all()
    entrance_evaluation_questionnaire_ids_list = set(QuestionnaireResponse.objects.values_list('survey',
                                                                                               flat=True))

    # ev_questionnaire_ids_list = entrance_evaluation_questionnaires.values_list("survey")
    surveys_with_ev_list = Survey.objects.filter(id__in=entrance_evaluation_questionnaire_ids_list)

    for survey in surveys_with_ev_list:
        for questionnaire in questionnaires_list:
            if survey.lime_survey_id == questionnaire['sid']:
                questionnaires_list_final.append(questionnaire)
                break

    # page 2 fields

    # entrance evaluation questionnarie fields
    questionnaires_fields_list = get_questionnaire_fields(questionnaires_list_final)

    # for field in questionnaires_fields_list:
    #     for questionnaire in questionnaires_list_final:
    #         if field["sid"] == questionnaire['sid']:
    #             field["title"] = questionnaire["surveyls_title"]
    #             break

    # patient fields
    # patient_fields = []
    #
    # "output_list":{}

    # diagnosis fields

    context = {

        "limesurvey_available": limesurvey_available,
        "export_form": export_form,
        # "questionnaires_list": questionnaires_list_final,
        # "contacts": contacts,
        "patient_fields": patient_fields,
        "diagnosis_fields": diagnosis_fields,
        "questionnaires_fields_list": questionnaires_fields_list,
        "selected_ev_quest": selected_ev_quest,
        "selected_participant": selected_participant,
        "selected_diagnosis": selected_diagnosis,
    }

    # elif page == 2:

    return render(request, template_name, context)


# def export_execute():

def get_questionnaire_fields(questionnaire_code_list, language="pt-BR"):
    """
    :param questionnaire_code_list: list with questionnaire id to be formatted with json file
    :return: 1 list: questionnaires_included - questionnaire_id that was included in the .txt file

    """

    questionnaires_included = []

    questionnaire_lime_survey = Questionnaires()
    for questionnaire in questionnaire_code_list:

        questionnaire_id = questionnaire["sid"]

        responses_string = questionnaire_lime_survey.get_responses(questionnaire_id, language)

        # print("id: %d " % questionnaire_id)

        if not isinstance(responses_string, dict):

            record_question = {'sid': questionnaire_id, "title": questionnaire["surveyls_title"], "output_list": []}

            questionnaire_questions = perform_csv_response(responses_string)

            # line 0 - header information
            for question in questionnaire_questions[0]:
                # properties = questionnaire_lime_survey.get_question_properties(question, language)

                record_question["output_list"].append({"field": question, "header": question})

            questionnaires_included.append(record_question)

    questionnaire_lime_survey.release_session_key()

    return questionnaires_included


@login_required
def participant_selection(request, template_name="export/participant_selection.html"):

    participant_selection_form = ParticipantsSelectionForm(None)
    age_interval_form = AgeIntervalForm(None)

    gender_list = None
    marital_status_list = None
    age_interval = None

    if request.method == "POST":
        if request.POST['action'] == "next":

            if "gender_selection" in request.POST:
                gender_list = request.POST.getlist('gender')

            if "marital_status_selection" in request.POST:
                marital_status_list = request.POST.getlist('marital_status')

            if "age_selection" in request.POST:
                age_interval = [request.POST['min_age'], request.POST['max_age']]

    context = {
        "participant_selection_form": participant_selection_form,
        "age_interval_form": age_interval_form}

    return render(request, template_name, context)
