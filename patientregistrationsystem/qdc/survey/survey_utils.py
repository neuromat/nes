import collections
import re
from _csv import reader

from operator import itemgetter
from io import StringIO

from django.utils.encoding import smart_str

from survey.models import Survey

HEADER_EXPLANATION_FIELDS = [
    'questionnaire_code', 'questionnaire_title',
    'question_group',
    'question_type', 'question_type_description',
    'question_index',
    'question_code', 'question_description',
    'subquestion_code', 'subquestion_description',
    'question_scale', 'question_scale_label',
    'option_code', 'option_description'
    ]

question_types = {
    '1': 'Array Dual Scale',
    '5': '5 Point Choice',
    'A': 'Array (5 Point Choice)',
    'B': 'Array (10 Point Choice)',
    'C': 'Array (Yes/No/Uncertain)',
    'D': 'Date',
    'E': 'Array (Increase, Same, Decrease)',
    'F': 'Array (Flexible Labels)',
    'G': 'Gender',
    'H': 'Array (Flexible Labels) by Column',
    'I': 'Language Switch',
    'K': 'Multiple Numerical Input',
    'L': 'List (Radio)',
    'M': 'Multiple choice',
    'N': 'Numerical Input',
    'O': 'List With Comment',
    'P': 'Multiple choice with comments',
    'Q': 'Multiple Short Text',
    'R': 'Ranking',
    'S': 'Short Free Text',
    'T': 'Long Free Text',
    'U': 'Huge Free Text',
    'X': 'Boilerplate Question',  # não encontrado na versão do Neuromat
    'Y': 'Yes/No',
    '!': 'List (Dropdown)',
    # não encontrado na versão atual do Neuromat
    ':': 'Array (Flexible Labels) multiple drop down',
    # não encontrado na versão atual do Neuromat
    ';': 'Array (Flexible Labels) multiple texts',
    '|': 'File Upload',
    '*': 'Equation'
}


class QuestionnaireUtils:

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

    def append_questionnaire_header_and_field(self, questionnaire_id, header, fields,
                                              considers_questionnaires,
                                              considers_questionnaires_from_experiment):
        # only one header, field instance
        for field in fields:
            if considers_questionnaires:
                if field not in self.questionnaires_data[questionnaire_id]["fields"]:
                    self.questionnaires_data[questionnaire_id]["header"].append(header[fields.index(field)])
                    self.questionnaires_data[questionnaire_id]["fields"].append(field)
            if considers_questionnaires_from_experiment:
                if field not in self.questionnaires_experiment_data[questionnaire_id]["fields"]:
                    self.questionnaires_experiment_data[questionnaire_id]["header"].append(header[fields.index(field)])
                    self.questionnaires_experiment_data[questionnaire_id]["fields"].append(field)

    def get_header_questionnaire(self, questionnaire_id):
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
        header = []
        if questionnaire_id in self.questionnaires_experiment_data:
            header = \
                self.questionnaires_experiment_data[questionnaire_id]["header"]
        return header

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
            index = \
                self.questionnaires_data[questionnaire_id]["fields"].index(field)
            header_description = \
                self.questionnaires_data[questionnaire_id]["header"][index]
        else:
            questionnaire_id = str(questionnaire_id)
            index = \
                self.questionnaires_experiment_data[questionnaire_id]["fields"].index(field)
            header_description = \
                self.questionnaires_experiment_data[questionnaire_id]["header"][index]

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

        return new_header, new_fields


    def redefine_header_and_fields_experiment(self, questionnaire_id, header_filtered, fields, header_list):
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

    def create_questionnaire_explanation_fields(self, questionnaire_id,
                                                language,
                                                questionnaire_lime_survey,
                                                fields,
                                                entrance_questionnaire):
        """
        :param questionnaire_id:
        :param language:
        :param questionnaire_lime_survey:
        :param fields: fields from questionnaire that are to be exported
        :param entrance_questionnaire: boolean
        :return: header, formatted according to fields
                 data_rows, formatted according to fields
                 if error, both data are []
        """
        # clear fields
        fields_cleared = [field.split("[")[0] for field in fields]

        questionnaire_explanation_fields_list = [HEADER_EXPLANATION_FIELDS]

        fields_from_questions = []

        # for each field, verify the question description
        questionnaire_title = questionnaire_lime_survey.get_survey_title(
            questionnaire_id, language
        )
        questionnaire_code = \
            self.get_questionnaire_code_from_id(questionnaire_id)

        # get fields description
        questionnaire_questions = questionnaire_lime_survey.list_questions(
            questionnaire_id, 0
        )

        for question in questionnaire_questions:
            properties = questionnaire_lime_survey.get_question_properties(
                    question, language
                )
            question_code = \
                properties['title'] if 'title' in properties else None
            if question_code and question_code in fields_cleared:
                fields_from_questions.append(question_code)
                # clean the question description that came from limesurvey
                question_description = \
                    re.sub(
                        '{.*?}', '',
                        re.sub('<.*?>', '', properties['question'])
                    ).replace('&nbsp;', '').strip()
                question_type = smart_str(properties['type'])
                question_type_description = question_types[question_type] \
                    if question_type in question_types else ''
                question_group = \
                    self.get_group_properties(
                        questionnaire_lime_survey,
                        questionnaire_id,
                        properties['gid'],
                        language
                    )

                questionnaire_list = \
                    [smart_str(questionnaire_code),
                     smart_str(questionnaire_title)]
                question_type_list = \
                    [question_type, question_type_description]
                question_list = \
                    [smart_str(question_code),
                     smart_str(question_description)]

                scales = [""]
                # "1": "Array Dual Scale"
                if question_type == "1":
                    if isinstance(properties['attributes_lang'], dict):
                        scales = [
                            properties['attributes_lang']['dualscale_headerA']
                            if 'dualscale_headerA' in properties[
                                'attributes_lang'] else "",
                            properties['attributes_lang']['dualscale_headerB']
                            if 'dualscale_headerB' in properties[
                                'attributes_lang'] else ""
                        ]
                    else:
                        scales = ["", ""]

                # answers
                options_list = []

                if isinstance(properties['answeroptions'], dict):
                    options = collections.OrderedDict(
                        sorted(properties['answeroptions'].items())
                    )
                    for option_key, option_values in options.items():
                        options_list.append(
                            [smart_str(option_key),
                             smart_str(option_values['answer'])]
                        )
                else:
                    # include blank line
                    options_list = [[""] * 2]

                # sub-questions
                if isinstance(properties['subquestions'], dict):
                    sub_questions_list = [
                        [smart_str(value['title']),
                         smart_str(value['question'])]
                        for value in properties['subquestions'].values()
                    ]
                    sub_questions_list = sorted(
                        sub_questions_list, key=itemgetter(0)
                    )
                else:
                    # include blank line
                    sub_questions_list = [[""] * 2]

                for scale_index, scale_label in enumerate(scales):
                    scale = [scale_index + 1, scale_label] \
                        if scale_label else [""] * 2
                    for sub_question in sub_questions_list:
                        for option in options_list:

                            question_index = question_code
                            if sub_question[0]:
                                question_index += '[' + sub_question[0] + ']'
                            if scale_label:
                                question_index += \
                                    '[' + str(scale_index + 1) + ']'

                            questionnaire_explanation_fields_list.append(
                                questionnaire_list +
                                [question_group['group_name']] +
                                question_type_list +
                                [question_index] + question_list +
                                sub_question + scale + option
                            )

        if len(fields_cleared) != len(fields_from_questions):
            for field in fields_cleared:
                if field not in fields_from_questions:
                    description = self.get_header_description(
                        questionnaire_id, field, entrance_questionnaire
                    )
                    question_list = [smart_str(questionnaire_code),
                                     smart_str(questionnaire_title),
                                     '', '',
                                     smart_str(field), smart_str(field),
                                     smart_str(description)]

                    questionnaire_explanation_fields_list.append(
                        question_list
                    )

        return questionnaire_explanation_fields_list

    @staticmethod
    def get_question_list(survey, survey_id, language):
        """
        Return limesurvey multiple question types list
        TODO: make returns all question types
        :param survey:
        :param survey_id:
        :param language:
        :return: list
        """
        groups = survey.list_groups(survey_id)
        question_list = []
        for group in groups:
            if 'id' in group and group['id']['language'] == language:
                question_ids = survey.list_questions(
                    survey_id, group['id']['gid']
                )
                for id in question_ids:
                    properties = survey.get_question_properties(
                        id, group['id']['language']
                    )
                    # Multiple question ('M' or 'P') will be question if
                    # properties['subquestions'] is a dict, otherwise will
                    # be subquestion. We only wish questions
                    if isinstance(properties['subquestions'], dict) and \
                            (properties['type'] == 'M' or
                             properties['type'] == 'P'):
                        question_list.append(properties['title'])

        return question_list

    @staticmethod
    def responses_to_csv(responses_string):
        """
        :param responses_string:
        :return:
        """
        response_reader = reader(
            StringIO(responses_string.decode()), delimiter=','
        )
        responses_list = []
        for row in response_reader:
            responses_list.append(row)
        return responses_list

    @staticmethod
    def get_group_properties(survey, survey_id, gid, lang):
        """
        Return group in correct language, as of this date LimeSurvey Remote
        Control API does not return correct group by language
        :param survey: Questionnaires instance
        :param survey_id: Questionnaire (Survey) id
        :param gid: Group id
        :param lang: Group language
        :return: group dict or None
        """
        groups = survey.list_groups(survey_id)
        return next(
            (item for item in groups
             if item['gid'] == gid and item['language'] == lang),
            None
        )
