import collections
import re

from operator import itemgetter

from django.utils.encoding import smart_str

from survey.models import Survey

header_explanation_fields = ['questionnaire_id',
                             'questionnaire_title',
                             'question_code',
                             'question_limesurvey_type',
                             'question_description',
                             'subquestion_code',
                             'subquestion_description',
                             'option_code',
                             'option_description',
                             'option_value',
                             'column_title']


class QuestionnaireUtils:

    # def __init__(self, user_id, export_id):
    def __init__(self):
        self.questionnaires_data = {}
        self.questionnaires_experiment_data = {}
        self.questionnaire_code_and_id = {}

    def set_questionnaire_header_and_fields(self, questionnaire, entrance_questionnaire):

        headers = []
        fields = []

        questionnaire_id = questionnaire["id"]
        for output_list in questionnaire["output_list"]:
            if output_list["field"]:
                headers.append(output_list["header"])
                fields.append(output_list["field"])

        if entrance_questionnaire:
            if questionnaire_id not in self.questionnaires_data:
                self.questionnaires_data[questionnaire_id] = {}

            self.questionnaires_data[questionnaire_id]["header"] = headers
            self.questionnaires_data[questionnaire_id]["fields"] = fields

        else:
            if questionnaire_id not in self.questionnaires_experiment_data:
                self.questionnaires_experiment_data[questionnaire_id] = {}

            self.questionnaires_experiment_data[questionnaire_id]["header"] = headers
            self.questionnaires_experiment_data[questionnaire_id]["fields"] = fields

        return headers, fields

    def set_questionnaire_experiment_header_and_fields(self, questionnaire_id, questionnaire):

        headers = []
        fields = []

        for output_list in questionnaire["output_list"]:
            if output_list["field"]:
                headers.append(output_list["header"])
                fields.append(output_list["field"])

        if questionnaire_id not in self.questionnaires_experiment_data:
            self.questionnaires_experiment_data[questionnaire_id] = {}

        self.questionnaires_experiment_data[questionnaire_id]["header"] = headers
        self.questionnaires_experiment_data[questionnaire_id]["header_questionnaire"] = headers
        self.questionnaires_experiment_data[questionnaire_id]["fields"] = fields

        return headers, fields

    # def append_questionnaire_header_and_field(self, questionnaire_id, header, fields):
    def append_questionnaire_header_and_field(self, questionnaire_id, header, fields,
                                              considers_questionnaires,
                                              considers_questionnaires_from_experiment):
        # only one header, field instance
        for field in fields:
            # if self.get_input_data('questionnaires'):
            if considers_questionnaires:
                if field not in self.questionnaires_data[questionnaire_id]["fields"]:
                    self.questionnaires_data[questionnaire_id]["header"].append(header[fields.index(field)])
                    self.questionnaires_data[questionnaire_id]["fields"].append(field)
            # if self.get_input_data('questionnaires_from_experiment'):
            if considers_questionnaires_from_experiment:
                if field not in self.questionnaires_experiment_data[questionnaire_id]["fields"]:
                    self.questionnaires_experiment_data[questionnaire_id]["header"].append(header[fields.index(field)])
                    self.questionnaires_experiment_data[questionnaire_id]["fields"].append(field)

    def get_header_questionnaire(self, questionnaire_id):
        # headers_questionnaire format: dict {questionnaire_id: {header:[header]}}

        header = []
        if questionnaire_id in self.questionnaires_data:
            header = self.questionnaires_data[questionnaire_id]["header"]
        return header

    def append_questionnaire_experiment_header_and_field(self, questionnaire_id, header, fields):
        # only one header, field instance
        for field in fields:
            if field not in self.questionnaires_experiment_data[questionnaire_id]["fields"]:
                self.questionnaires_experiment_data[questionnaire_id]["header"].append(header[fields.index(field)])
                self.questionnaires_experiment_data[questionnaire_id]["header_questionnaire"].\
                    append(header[fields.index(field)])
                self.questionnaires_experiment_data[questionnaire_id]["fields"].append(field)

    def get_header_experiment_questionnaire(self, questionnaire_id):
        # headers_questionnaire format: dict {questionnaire_id: {header:[header]}}

        header = []
        if questionnaire_id in self.questionnaires_experiment_data:
            header = self.questionnaires_experiment_data[questionnaire_id]["header"]
        return header

    # def get_questionnaire_fields(self, questionnaire_id, entrance_questionnaire):
    def get_questionnaire_fields(self, questionnaire_id, entrance_questionnaire,
                                 considers_questionnaires_from_experiments):
        # headers_questionnaire format: dict {questionnaire_id: {fields:[fields]}}

        fields = []
        if entrance_questionnaire:
            if questionnaire_id in self.questionnaires_data:
                fields = self.questionnaires_data[questionnaire_id]["fields"]
        # if self.get_input_data('questionnaires_from_experiments'):
        if considers_questionnaires_from_experiments:
            if questionnaire_id in self.questionnaires_experiment_data:
                fields = self.questionnaires_experiment_data[questionnaire_id]["fields"]

        return fields

    def get_questionnaire_experiment_fields(self, questionnaire_id):
        # headers_questionnaire format: dict {questionnaire_id: {fields:[fields]}}
        questionnaire_id = str(questionnaire_id)
        fields = []
        if questionnaire_id in self.questionnaires_experiment_data:
            fields = self.questionnaires_experiment_data[questionnaire_id]["fields"]
        return fields

    def get_header_description(self, questionnaire_id, field, entrance_questionnaire):

        if entrance_questionnaire:
            index = self.questionnaires_data[questionnaire_id]["fields"].index(field)
            header_description = self.questionnaires_data[questionnaire_id]["header"][index]
        else:
            questionnaire_id = str(questionnaire_id)
            index = self.questionnaires_experiment_data[questionnaire_id]["fields"].index(field)
            header_description = self.questionnaires_experiment_data[questionnaire_id]["header"][index]

        return header_description

    def redefine_header_and_fields(self, questionnaire_id, header_filtered, fields):

        header = self.questionnaires_data[questionnaire_id]["header"]
        fields_saved = self.questionnaires_data[questionnaire_id]["fields"]

        new_header = []
        new_fields = []

        for item in fields:
            new_header.append(header[fields.index(item)])
            new_fields.append(fields_saved[fields.index(item)])

            if item in header_filtered:
                new_header.append(header[fields.index(item)])
                new_fields.append(fields_saved[fields.index(item)])

        self.questionnaires_data[questionnaire_id]["header"] = new_header
        self.questionnaires_data[questionnaire_id]["fields"] = new_fields

    def redefine_header_and_fields_experiment(self, questionnaire_id, header_filtered, fields, header_list):

        # header = self.questionnaires_experiment_data[questionnaire_id]["header"]
        header_questionnaire = self.questionnaires_experiment_data[questionnaire_id]["header_questionnaire"]
        fields_saved = self.questionnaires_experiment_data[questionnaire_id]["fields"]

        # new_header = []
        new_fields = []
        new_header_questionnaire = []

        for item in fields:
            new_header_questionnaire.append(header_questionnaire[fields.index(item)])
            new_fields.append(fields_saved[fields.index(item)])

            if item in header_filtered:
                new_header_questionnaire.append(header_questionnaire[fields.index(item)])
                new_fields.append(fields_saved[fields.index(item)])

        # for element in header_list:
        #     new_header.append(header[element])

        self.questionnaires_experiment_data[questionnaire_id]["header"] = header_list
        self.questionnaires_experiment_data[questionnaire_id]["header_questionnaire"] = new_header_questionnaire
        self.questionnaires_experiment_data[questionnaire_id]["fields"] = new_fields

    def include_questionnaire_code_and_id(self, code, questionnaire_id):

        if code not in self.questionnaire_code_and_id:
            self.questionnaire_code_and_id[code] = str(questionnaire_id)

    def get_questionnaire_id_from_code(self, code):

        questionnaire_id = 0
        if code in self.questionnaire_code_and_id:
            questionnaire_id = self.questionnaire_code_and_id[code]

        return questionnaire_id

    def get_questionnaire_code_from_id(self, questionnaire_id):
        questionnaire_code = 0

        for code in self.questionnaire_code_and_id:
            if self.questionnaire_code_and_id[code] == str(questionnaire_id):
                questionnaire_code = code
                break

        if questionnaire_code == 0:
            survey = Survey.objects.filter(lime_survey_id=questionnaire_id).first()
            if survey:
                questionnaire_code = survey.lime_survey_id

        return questionnaire_code

    def create_questionnaire_explanation_fields(self, questionnaire_id, language, questionnaire_lime_survey,
                                                fields, entrance_questionnaire):

        """
        :param questionnaire_id:
        :param language:
        :param questionnaire_lime_survey:
        :param fields: fields from questionnaire that are to be exported. Empty means all fields (used by portal.py)
        :param entrance_questionnaire: boolean
        :return: header, formatted according to fields
                 data_rows, formatted according to fields
                 if error, both data are []
        """
        # clear fields
        fields_cleared = [field.split("[")[0] for field in fields]

        questionnaire_explanation_fields_list = [header_explanation_fields]

        fields_from_questions = []

        # for each field, verify the question description
        # get title

        questionnaire_title = questionnaire_lime_survey.get_survey_title(questionnaire_id, language)
        # questionnaire_title = self.get_title(questionnaire_id)

        questionnaire_code = self.get_questionnaire_code_from_id(questionnaire_id)

        # get fields description
        questionnaire_questions = questionnaire_lime_survey.list_questions(questionnaire_id, 0)

        for question in questionnaire_questions:

            properties = questionnaire_lime_survey.get_question_properties(question, language)

            if ('title' in properties) and (not fields_cleared or properties['title'] in fields_cleared):

                fields_from_questions.append(properties['title'])

                # cleaning the question field
                properties['question'] = re.sub('{.*?}', '', re.sub('<.*?>', '', properties['question']))
                properties['question'] = properties['question'].replace('&nbsp;', '').strip()

                question_to_list = [smart_str(questionnaire_code), smart_str(questionnaire_title),
                                    smart_str(properties['title']), smart_str(properties['type']),
                                    smart_str(properties['question'])]

                options_list = []

                if isinstance(properties['answeroptions'], dict):

                    options = collections.OrderedDict(sorted(properties['answeroptions'].items()))

                    column_scale = ['']
                    if isinstance(properties['attributes_lang'], dict):
                        column_scale = [attribute for attribute in sorted(properties['attributes_lang'].values())]

                    for option_key, option_values in options.items():
                        if len(column_scale) > option_values['scale_id']:
                            column_title = column_scale[option_values['scale_id']]
                        else:
                            column_title = ''
                        options_list.append([smart_str(option_key), smart_str(option_values['answer']),
                                             smart_str(option_values['assessment_value']), smart_str(column_title)])
                else:
                    # includes blank line
                    # options_list = [[smart_str(" ") for blank in range(4)]]  # includes blank line
                    options_list = [[smart_str(" ")] * 4]

                if isinstance(properties['subquestions'], dict):

                    sub_questions_list = [[smart_str(value['title']), smart_str(value['question'])]
                                          for value in properties['subquestions'].values()]

                    sub_questions_list = sorted(sub_questions_list, key=itemgetter(0))
                else:
                    # includes blank line
                    # sub_questions_list = [[smart_str(" ") for blank in range(2)]]  # includes blank line
                    sub_questions_list = [[smart_str(" ")] * 2]

                for sub_question in sub_questions_list:

                    for option in options_list:
                        questionnaire_explanation_fields_list.append(question_to_list + sub_question + option)

        if len(fields_cleared) != len(fields_from_questions):

            for field in fields_cleared:

                if field not in fields_from_questions:
                    description = self.get_header_description(
                        questionnaire_id, field, entrance_questionnaire)
                    question_to_list = [smart_str(questionnaire_code), smart_str(questionnaire_title),
                                        smart_str(field), smart_str(''), smart_str(description)]

                    questionnaire_explanation_fields_list.append(question_to_list)

        return questionnaire_explanation_fields_list
