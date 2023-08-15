import collections
import re
from io import StringIO
from operator import itemgetter

# TODO (NES-956): see this
from _csv import reader
from django.utils.encoding import smart_str
from django.utils.translation import gettext as _
from survey.abc_search_engine import Questionnaires
from survey.models import Survey

HEADER_EXPLANATION_FIELDS = [
    ("questionnaire_code", "string"),
    ("questionnaire_title", "string"),
    ("question_group", "string"),
    ("question_order", "integer"),
    ("question_type", "string"),
    ("question_type_description", "string"),
    ("question_index", "string"),
    ("question_code", "string"),
    ("question_description", "string"),
    ("subquestion_code", "string"),
    ("subquestion_description", "string"),
    ("question_scale", "string"),
    ("question_scale_label", "string"),
    ("option_code", "string"),
    ("option_description", "string"),
]

QUESTION_TYPES = {
    "1": ("Array Dual Scale", "string", "default"),
    "5": ("5 Point Choice", "string", "default"),
    "A": ("Array (5 Point Choice)", "string", "default"),
    "B": ("Array (10 Point Choice)", "string", "default"),
    "C": ("Array (Yes/No/Uncertain)", "string", "default"),
    "D": ("Date", "datetime", "%Y-%m-%d %H:%M:%S"),
    "E": ("Array (Increase, Same, Decrease)", "string", "default"),
    "F": ("Array (Flexible Labels)", "string", "default"),
    "G": ("Gender", "string", "default"),
    "H": ("Array (Flexible Labels) by Column", "string", "default"),
    "I": ("Language Switch", "string", "default"),
    "K": ("Multiple Numerical Input", "number", "default"),
    "L": ("List (Radio)", "string", "default"),
    "M": ("Multiple choice", "string", "default"),
    "N": ("Numerical Input", "number", "default"),
    "O": ("List With Comment", "string", "default"),
    "P": ("Multiple choice with comments", "string", "default"),
    "Q": ("Multiple Short Text", "string", "default"),
    "R": ("Ranking", "string", "default"),
    "S": ("Short Free Text", "string", "default"),
    "T": ("Long Free Text", "string", "default"),
    "U": ("Huge Free Text", "string", "default"),
    # não encontrado na versão do Neuromat
    "X": ("Boilerplate Question", "string", "default"),
    "Y": ("Yes/No", "string", "default"),
    "!": ("List (Dropdown)", "string", "default"),
    # não encontrado na versão atual do Neuromat
    ":": ("Array (Flexible Labels) multiple drop down", "string", "default"),
    # não( encontrado na versão atual do Neuromat
    ";": ("Array (Flexible Labels) multiple texts", "string", "default"),
    "|": ("File Upload", "string", "default"),
    "*": ("Equation", "string", "default"),
}


class QuestionnaireUtils:
    LIMESURVEY_ERROR = 1

    def __init__(self):
        self.questionnaires_data = {}
        self.questionnaires_experiment_data = {}
        self.questionnaire_code_and_id = {}

    def set_questionnaire_header_and_fields(
        self, questionnaire, entrance_questionnaire
    ):
        headers = []
        fields = []

        questionnaire_id = questionnaire["id"]
        for output_list in questionnaire["output_list"]:
            if (
                output_list["field"] != "fileUpload"
                and output_list["field"] != "fileUpload[filecount]"
            ):
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

    def set_questionnaire_experiment_header_and_fields(
        self, questionnaire_id, questionnaire
    ):
        headers = []
        fields = []

        for output_list in questionnaire["output_list"]:
            if output_list["field"]:
                headers.append(output_list["header"])
                fields.append(output_list["field"])

        if questionnaire_id not in self.questionnaires_experiment_data:
            self.questionnaires_experiment_data[questionnaire_id] = {}

        self.questionnaires_experiment_data[questionnaire_id]["header"] = headers
        self.questionnaires_experiment_data[questionnaire_id][
            "header_questionnaire"
        ] = headers
        self.questionnaires_experiment_data[questionnaire_id]["fields"] = fields

        return headers, fields

    def append_questionnaire_header_and_field(
        self,
        questionnaire_id,
        header,
        fields,
        considers_questionnaires,
        considers_questionnaires_from_experiment,
    ):
        # Only one header, field instance
        for field in fields:
            if considers_questionnaires:
                if field not in self.questionnaires_data[questionnaire_id]["fields"]:
                    self.questionnaires_data[questionnaire_id]["header"].append(
                        header[fields.index(field)]
                    )
                    self.questionnaires_data[questionnaire_id]["fields"].append(field)
            if considers_questionnaires_from_experiment:
                if (
                    field
                    not in self.questionnaires_experiment_data[questionnaire_id][
                        "fields"
                    ]
                ):
                    self.questionnaires_experiment_data[questionnaire_id][
                        "header"
                    ].append(header[fields.index(field)])
                    self.questionnaires_experiment_data[questionnaire_id][
                        "fields"
                    ].append(field)

    def get_header_questionnaire(self, questionnaire_id):
        header = []
        if questionnaire_id in self.questionnaires_data:
            header = self.questionnaires_data[questionnaire_id]["header"]
        return header

    def append_questionnaire_experiment_header_and_field(
        self, questionnaire_id, header, fields
    ):
        # only one header, field instance
        for field in fields:
            if (
                field
                not in self.questionnaires_experiment_data[questionnaire_id]["fields"]
            ):
                self.questionnaires_experiment_data[questionnaire_id]["header"].append(
                    header[fields.index(field)]
                )
                self.questionnaires_experiment_data[questionnaire_id][
                    "header_questionnaire"
                ].append(header[fields.index(field)])
                self.questionnaires_experiment_data[questionnaire_id]["fields"].append(
                    field
                )

    def get_header_experiment_questionnaire(self, questionnaire_id):
        header = []
        if questionnaire_id in self.questionnaires_experiment_data:
            header = self.questionnaires_experiment_data[questionnaire_id]["header"]
        return header

    def get_questionnaire_fields(
        self,
        questionnaire_id,
        entrance_questionnaire,
        considers_questionnaires_from_experiments,
    ):
        fields = []
        if entrance_questionnaire:
            if questionnaire_id in self.questionnaires_data:
                fields = self.questionnaires_data[questionnaire_id]["fields"]
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
            header_description = self.questionnaires_data[questionnaire_id]["header"][
                index
            ]
        else:
            questionnaire_id = str(questionnaire_id)
            index = self.questionnaires_experiment_data[questionnaire_id][
                "fields"
            ].index(field)
            header_description = self.questionnaires_experiment_data[questionnaire_id][
                "header"
            ][index]

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

    def redefine_header_and_fields_experiment(
        self, questionnaire_id, header_filtered, fields, header_list
    ):
        header_questionnaire = self.questionnaires_experiment_data[questionnaire_id][
            "header_questionnaire"
        ]
        fields_saved = self.questionnaires_experiment_data[questionnaire_id]["fields"]

        # new_header = []
        new_fields = []
        new_header_questionnaire = []

        for item in fields:
            new_header_questionnaire.append(header_questionnaire[fields.index(item)])
            new_fields.append(fields_saved[fields.index(item)])

            if item in header_filtered:
                new_header_questionnaire.append(
                    header_questionnaire[fields.index(item)]
                )
                new_fields.append(fields_saved[fields.index(item)])

        self.questionnaires_experiment_data[questionnaire_id][
            "header"
        ] = new_header_questionnaire
        self.questionnaires_experiment_data[questionnaire_id][
            "header_questionnaire"
        ] = new_header_questionnaire
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

    def create_questionnaire_explanation_fields(
        self,
        questionnaire_id,
        language,
        questionnaire_lime_survey,
        fields,
        entrance_questionnaire,
    ):
        """
        :param questionnaire_id:
        :param language:
        :param questionnaire_lime_survey:
        :param fields: fields from questionnaire that are to be exported
        :param entrance_questionnaire: boolean
        :return: tupple: (int, list) - list: header, formatted according to fields
                 data_rows, formatted according to fields, in case of success, else empty []

        """
        # Clear fields
        fields_cleared = [field.split("[")[0] for field in fields]
        questionnaire_explanation_fields_list = [
            [item[0] for item in HEADER_EXPLANATION_FIELDS]
        ]
        fields_from_questions = []
        # For each field, verify the question description
        questionnaire_title = questionnaire_lime_survey.get_survey_title(
            questionnaire_id, language
        )
        questionnaire_code = self.get_questionnaire_code_from_id(questionnaire_id)
        # Get fields description
        questionnaire_questions = questionnaire_lime_survey.list_questions_ids(
            questionnaire_id, 0
        )
        if not questionnaire_questions:
            return Questionnaires.ERROR_CODE, []

        for question in questionnaire_questions:
            properties = questionnaire_lime_survey.get_question_properties(
                question, language
            )
            if properties is None:
                return Questionnaires.ERROR_CODE, []
            question_code = properties["title"] if "title" in properties else None
            if question_code and question_code in fields_cleared:
                fields_from_questions.append(question_code)
                # clean the question description that came from limesurvey
                question_description = (
                    re.sub("{.*?}", "", re.sub("<.*?>", "", properties["question"]))
                    .replace("&nbsp;", "")
                    .strip()
                )
                question_type = smart_str(properties["type"])
                question_type_description = (
                    QUESTION_TYPES[question_type][0]
                    if question_type in QUESTION_TYPES
                    else ""
                )
                question_group = self.get_group_properties(
                    questionnaire_lime_survey,
                    questionnaire_id,
                    properties["gid"],
                    language,
                )
                if question_group is None:
                    return Questionnaires.ERROR_CODE, []
                question_order = properties["question_order"]

                questionnaire_list = [
                    smart_str(questionnaire_code),
                    smart_str(questionnaire_title),
                ]
                question_type_list = [
                    smart_str(question_order),
                    question_type,
                    question_type_description,
                ]
                question_list = [
                    smart_str(question_code),
                    smart_str(question_description),
                ]

                scales = [""]
                # "1": "Array Dual Scale"
                if question_type == "1":
                    if isinstance(properties["attributes_lang"], dict):
                        scales = [
                            properties["attributes_lang"]["dualscale_headerA"]
                            if "dualscale_headerA" in properties["attributes_lang"]
                            else "",
                            properties["attributes_lang"]["dualscale_headerB"]
                            if "dualscale_headerB" in properties["attributes_lang"]
                            else "",
                        ]
                    else:
                        scales = ["", ""]

                # Answers
                options_list = []

                if isinstance(properties["answeroptions"], dict):
                    options = collections.OrderedDict(
                        sorted(properties["answeroptions"].items())
                    )
                    for option_key, option_values in options.items():
                        options_list.append(
                            [smart_str(option_key), smart_str(option_values["answer"])]
                        )
                else:
                    # Include blank line
                    options_list = [[""] * 2]

                # Sub-questions
                if isinstance(properties["subquestions"], dict):
                    sub_questions_list = [
                        [smart_str(value["title"]), smart_str(value["question"])]
                        for value in properties["subquestions"].values()
                    ]
                    sub_questions_list = sorted(sub_questions_list, key=itemgetter(0))
                else:
                    # Include blank line
                    sub_questions_list = [[""] * 2]

                for scale_index, scale_label in enumerate(scales):
                    scale = [scale_index + 1, scale_label] if scale_label else [""] * 2
                    for sub_question in sub_questions_list:
                        for option in options_list:
                            question_index = question_code
                            if sub_question[0]:
                                question_index += "[" + sub_question[0] + "]"
                            if scale_label:
                                question_index += "[" + str(scale_index + 1) + "]"
                            questionnaire_explanation_fields_list.append(
                                questionnaire_list
                                + [question_group["group_name"]]
                                + question_type_list
                                + [question_index]
                                + question_list
                                + sub_question
                                + scale
                                + option
                            )

        if len(fields_cleared) != len(fields_from_questions):
            for field in fields_cleared:
                if field not in fields_from_questions:
                    description = self.get_header_description(
                        questionnaire_id, field, entrance_questionnaire
                    )
                    question_list = [
                        smart_str(questionnaire_code),
                        smart_str(questionnaire_title),
                        "",
                        "",
                        smart_str(field),
                        smart_str(field),
                        smart_str(description),
                    ]
                    questionnaire_explanation_fields_list.append(question_list)

        return 0, questionnaire_explanation_fields_list

    @staticmethod
    # TODO (NES-991): maybe get questions by group. Getting all questions
    def get_questions(limesurvey_connection, survey_id, language, types=None):
        """Return limesurvey multiple question types list
        :param limesurvey_connection: survey.Questionnaires instance
        :param survey_id:
        :param language:
        :param types: list of question types. Defaults to return all questions
        :return: tupple: (int, list) - (0, list) in case of success,
        else (Questionnaires.ERROR_code, empty list)
        """
        result = limesurvey_connection.list_groups(survey_id)
        if result is None:
            return Questionnaires.ERROR_CODE, []
        questions = []
        for group in result:
            if group["id"]["language"] == language:
                group_questions = limesurvey_connection.list_questions(
                    survey_id, group["id"]["gid"]
                )
                if not group_questions:
                    return Questionnaires.ERROR_CODE, []
                else:
                    questions.extend(group_questions)
                if types is not None:
                    questions = [item for item in questions if item["type"] in types]

        return 0, questions

    @staticmethod
    def responses_to_csv(responses_string):
        """
        :param responses_string:
        :return:
        """
        response_reader = reader(StringIO(responses_string), delimiter=",")
        responses_list = []
        for row in response_reader:
            responses_list.append(row)
        return responses_list

    @staticmethod
    def get_group_properties(survey, survey_id, gid, lang):
        """
        Return group in correct language, as at this date LimeSurvey Remote
        Control API does not return correct group by language
        :param survey: Questionnaires instance
        :param survey_id: Questionnaire (Survey) id
        :param gid: Group id
        :param lang: Group language
        :return: group dict or None
        """
        groups = survey.list_groups(survey_id)
        return next(
            (
                item
                for item in groups
                if item["gid"] == gid and item["language"] == lang
            ),
            None,
        )

    def get_response_column_name_for_identification_group_questions(
        self, survey, limesurvey_id, question_title, lang
    ):
        """
        Return response table column name that is formed by <limesurvey_id>X<group_id>X<question_id>
        :param survey: Limesurvey ABC interface
        :param limesurvey_id: Limesurvey survey id
        :param question_title: title of limesurvey survey question (it's unique in Limesurvey)
        :param lang: Limesurvey survey language
        :return: column name or string with error
        """
        question_groups = survey.list_groups(limesurvey_id)
        if question_groups is None:
            return self.LIMESURVEY_ERROR, _(
                "Could not get list of groups from LimeSurvey"
            )
        group = next(
            (
                item
                for item in question_groups
                if item["group_name"] == "Identification"
            ),
            None,
        )
        if group is None:
            return self.LIMESURVEY_ERROR, _(
                "There's no group with name Identification."
            )
        questions = survey.list_questions(limesurvey_id, group["gid"])
        if questions is None:
            return self.LIMESURVEY_ERROR, _(
                "Could not get list of groups from LimeSurvey"
            )
        index = next(
            (
                index
                for index, dict_ in enumerate(questions)
                if dict_["title"] == question_title
            ),
            None,
        )
        if index is None:
            return self.LIMESURVEY_ERROR, _(
                "There's no question with name %s" % question_title
            )
        else:
            return (
                str(limesurvey_id)
                + "X"
                + str(group["gid"])
                + "X"
                + str(questions[index]["qid"])
            )


def find_questionnaire_name(survey, language_code):
    language_code = language_code.lower()
    titles = {"pt-br": survey.pt_title, "en": survey.en_title}
    fallback_language = "en" if language_code == "pt-br" else "pt-br"

    if titles[language_code] is not None and titles[language_code] != "":
        title = titles[language_code]
    elif titles[fallback_language] is not None and titles[fallback_language] != "":
        title = titles[fallback_language]
    else:
        surveys = Questionnaires()
        title = surveys.get_survey_title(survey.lime_survey_id)
        surveys.release_session_key()

    return {"sid": survey.lime_survey_id, "name": title}
