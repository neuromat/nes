import json
import os
import shutil
import sys
import tempfile
import zipfile
from base64 import b64decode, b64encode
from functools import reduce
from json import JSONDecodeError
from operator import or_
from os import path

import networkx as nx
from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.db.models import Count, Q
from django.utils.translation import gettext as _
from experiment.import_export_model_relations import (
    EXPERIMENT_JSON_FILES,
    FOREIGN_RELATIONS,
    JSON_FILES_DETACHED_MODELS,
    MODEL_ROOT_NODES,
    MODELS_WITH_FILE_FIELD,
    MODELS_WITH_RELATION_TO_AUTH_USER,
    ONE_TO_ONE_RELATION,
    PATIENT_JSON_FILES,
    PRE_LOADED_MODELS_FOREIGN_KEYS,
    PRE_LOADED_MODELS_INHERITANCE,
    PRE_LOADED_MODELS_NOT_EDITABLE,
    PRE_LOADED_MODELS_NOT_EDITABLE_INHERITANCE,
    PRE_LOADED_PATIENT_MODEL,
)
from experiment.models import (
    Component,
    EEGElectrodeLocalizationSystem,
    Experiment,
    FileFormat,
    Group,
    Keyword,
    Questionnaire,
    QuestionnaireResponse,
    ResearchProject,
    Subject,
)
from patient.models import ClassificationOfDiseases, Patient
from survey.abc_search_engine import Questionnaires
from survey.models import Survey
from survey.survey_utils import QuestionnaireUtils


class ExportExperiment:
    FILE_NAME_JSON = "experiment.json"
    FILE_NAME_ZIP = "experiment.zip"
    LIMESURVEY_ERROR = 1

    def __init__(self, experiment) -> None:
        self.experiment = experiment
        self.temp_dir = tempfile.mkdtemp()

    def __del__(self) -> None:
        shutil.rmtree(self.temp_dir)

    def _generate_fixture(self, filename, elements, app="experiment."):
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, filename + ".json"), "w")
        call_command(
            "dump_object",
            app + elements[0],
            "--query",
            '{"' + elements[1] + '": ' + str([self.experiment.id]) + "}",
        )
        sys.stdout = sysout

    def _generate_detached_fixture(self, filename, elements):
        with open(path.join(self.temp_dir, elements[3] + ".json")) as file:
            data = json.load(file)
        parent_ids = [
            dict_["pk"]
            for index, dict_ in enumerate(data)
            if dict_["model"] == elements[2]
        ]

        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, filename + ".json"), "w")
        call_command(
            "dump_object",
            "experiment." + elements[0],
            "--query",
            '{"' + elements[1] + '": ' + str(parent_ids) + "}",
        )
        sys.stdout = sysout

    def _generate_keywords_fixture(self):
        # Generate fixture to keywords of the research project
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, "keywords.json"), "w")
        call_command(
            "dump_object",
            "experiment.researchproject_keywords",
            "--query",
            '{"researchproject_id__in": '
            + str([self.experiment.research_project.id])
            + "}",
        )
        sys.stdout = sysout

    def _remove_auth_user_model_from_json(self):
        with open(path.join(self.temp_dir, self.FILE_NAME_JSON)) as f:
            data = f.read().replace("\n", "")

        deserialized = json.loads(data)
        while True:
            index = next(
                (
                    index
                    for (index, dict_) in enumerate(deserialized)
                    if dict_["model"] == "auth.user"
                ),
                None,
            )
            if index is None:
                break
            del deserialized[index]

        with open(path.join(self.temp_dir, self.FILE_NAME_JSON), "w") as f:
            f.write(json.dumps(deserialized))

    def _remove_researchproject_keywords_model_from_json(self):
        with open(path.join(self.temp_dir, self.FILE_NAME_JSON)) as f:
            data = f.read().replace("\n", "")

        deserialized = json.loads(data)
        indexes = [
            index
            for (index, dict_) in enumerate(deserialized)
            if dict_["model"] == "experiment.researchproject_keywords"
        ]
        for i in sorted(indexes, reverse=True):
            del deserialized[i]

        with open(path.join(self.temp_dir, self.FILE_NAME_JSON), "w") as f:
            f.write(json.dumps(deserialized))

    # TODO: In future, import groups verifying existence of group_codes in the database, not excluding them
    def _change_group_code_to_null_from_json(self):
        with open(path.join(self.temp_dir, self.FILE_NAME_JSON)) as f:
            data = f.read().replace("\n", "")

        serialized = json.loads(data)
        indexes = [
            index
            for (index, dict_) in enumerate(serialized)
            if dict_["model"] == "experiment.group"
        ]
        for i in sorted(indexes, reverse=True):
            serialized[i]["fields"]["code"] = None

        with open(path.join(self.temp_dir, self.FILE_NAME_JSON), "w") as f:
            f.write(json.dumps(serialized))

    def _remove_survey_code(self):
        with open(path.join(self.temp_dir, self.FILE_NAME_JSON)) as f:
            data = f.read().replace("\n", "")

        serialized = json.loads(data)
        indexes = [
            index
            for (index, dict_) in enumerate(serialized)
            if dict_["model"] == "survey.survey"
        ]
        for i in indexes:
            serialized[i]["fields"]["code"] = ""

        with open(path.join(self.temp_dir, self.FILE_NAME_JSON), "w") as f:
            f.write(json.dumps(serialized))

    def _update_classification_of_diseases_reference(self):
        """Change json data exported to replace references to classification
        of diseases so the reference is to code not to id. We consider that
        NES instances all share the same classification of diseases data
        """
        with open(path.join(self.temp_dir, self.FILE_NAME_JSON)) as f:
            data = f.read().replace("\n", "")

        serialized = json.loads(data)
        indexes = [
            index
            for (index, dict_) in enumerate(serialized)
            if dict_["model"] == "patient.diagnosis"
        ]
        for index in indexes:
            pk = serialized[index]["fields"]["classification_of_diseases"]
            code = ClassificationOfDiseases.objects.get(id=int(pk)).code
            # Make a list with one element as natural key in dumped data has to be a list
            serialized[index]["fields"]["classification_of_diseases"] = [code]

        # Remove ClassificationOfDiseases items: these data are preloaded in database
        while True:
            index = next(
                (
                    index
                    for (index, dict_) in enumerate(serialized)
                    if dict_["model"] == "patient.classificationofdiseases"
                ),
                None,
            )
            if index is None:
                break
            del serialized[index]

        with open(path.join(self.temp_dir, self.FILE_NAME_JSON), "w") as f:
            f.write(json.dumps(serialized))

    def get_indexes(self, app, model):
        with open(self.get_file_path("json")) as f:
            data = json.load(f)
        return [
            index
            for (index, dict_) in enumerate(data)
            if dict_["model"] == app + "." + model
        ]

    def _export_surveys(self):
        """Export experiment surveys archives using LimeSurvey RPC API.
        :return: list of survey archive paths
        """
        questionnaire_ids = Questionnaire.objects.filter(
            experiment=self.experiment
        ).values_list("survey_id", flat=True)
        surveys = Survey.objects.filter(id__in=questionnaire_ids)
        ls_interface = Questionnaires(
            settings.LIMESURVEY["URL_API"]
            + "/index.php/plugins/unsecure?plugin=extendRemoteControl&function=action"
        )
        if ls_interface.session_key is None:
            return self.LIMESURVEY_ERROR, _(
                "Could not export LimeSurvey data. Please try again. If problem persists "
                "please contact the system administator"
            )
        archive_paths = []
        for survey in surveys:
            result = ls_interface.export_survey(survey.lime_survey_id)
            if result is None:
                return self.LIMESURVEY_ERROR, _(
                    "Could not export LimeSurvey data. Please try again. If problem persists "
                    "please contact the system administator"
                )
            decoded_archive = b64decode(result)
            lsa_archive_path = os.path.join(
                self.temp_dir, str(survey.lime_survey_id) + ".lsa"
            )
            lsa_archive = open(lsa_archive_path, "wb")
            lsa_archive.write(decoded_archive)
            archive_paths.append(lsa_archive_path)

        ls_interface.release_session_key()

        return (
            archive_paths if archive_paths else []
        )  # TODO (NES_956): return empty list?

    def _create_zip_file(self, survey_archives):
        """Create zip file with experiment.json file and subdirs corresponding
        to file paths from models that have FileField fields
        :param survey_archives: list of survey archive paths
        """
        with open(self.get_file_path("json")) as f:
            data = json.load(f)

        indexes = [
            index
            for index, dict_ in enumerate(data)
            if dict_["model"] in MODELS_WITH_FILE_FIELD
        ]
        with zipfile.ZipFile(self.get_file_path(), "w") as zip_file:
            zip_file.write(
                self.get_file_path("json").encode("utf-8"), self.FILE_NAME_JSON
            )
            # Append file subdirs
            for index in indexes:
                # Relative to MEDIA_ROOT
                relative_filepath = data[index]["fields"][
                    MODELS_WITH_FILE_FIELD[data[index]["model"]]
                ]
                if relative_filepath != "":
                    absolute_filepath = path.join(
                        settings.MEDIA_ROOT, relative_filepath
                    )
                    zip_file.write(absolute_filepath, relative_filepath)
            # Append limesurvey archives if they exist
            if isinstance(survey_archives, tuple):  # There was an error
                return survey_archives
            for survey_archive_path in survey_archives:
                zip_file.write(
                    survey_archive_path, os.path.basename(survey_archive_path)
                )
        return 0, ""

    def get_file_path(self, type_="zip"):
        if type_ == "zip":
            return path.join(self.temp_dir, self.FILE_NAME_ZIP)
        elif type_ == "json":
            return path.join(self.temp_dir, self.FILE_NAME_JSON)

    def export_all(self):
        for key, value in EXPERIMENT_JSON_FILES.items():
            self._generate_fixture(key, value)
        for key, value in PATIENT_JSON_FILES.items():
            self._generate_fixture(key, value, "patient.")
        for key, value in JSON_FILES_DETACHED_MODELS.items():
            self._generate_detached_fixture(key, value)
        self._generate_keywords_fixture()

        fixtures = []
        for filename in {
            **EXPERIMENT_JSON_FILES,
            **PATIENT_JSON_FILES,
            **JSON_FILES_DETACHED_MODELS,
        }:
            fixtures.append(path.join(self.temp_dir, filename + ".json"))

        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, self.FILE_NAME_JSON), "w")
        call_command("merge_fixtures", *fixtures)
        sys.stdout = sysout

        self._remove_researchproject_keywords_model_from_json()
        self._change_group_code_to_null_from_json()
        self._remove_survey_code()
        self._update_classification_of_diseases_reference()
        self._remove_auth_user_model_from_json()

        result = []
        if self.get_indexes("experiment", "questionnaire"):
            result = self._export_surveys()
        return self._create_zip_file(result)


class ImportExperiment:
    BAD_JSON_FILE_ERROR_CODE = 1
    LIMESURVEY_ERROR = 2
    FIXTURE_FILE_NAME = "experiment.json"

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.temp_dir = tempfile.mkdtemp()
        self.data = []
        self.last_objects_before_import = dict()
        self.new_objects = dict()
        self.limesurvey_relations = dict()

    def __del__(self) -> None:
        shutil.rmtree(self.temp_dir)

    def _set_last_objects_before_import(self, research_project_id):
        """Identify last objects to deduct after import, so
        we can identify the new objects imported
        :param data: list created with json.loads from json file with
        the objects that will be imported
        """
        self.last_objects_before_import["experiment"] = Experiment.objects.last()
        if not research_project_id:
            self.last_objects_before_import[
                "research_project"
            ] = ResearchProject.objects.last()
        has_groups = next(
            (
                index
                for (index, dict_) in enumerate(self.data)
                if dict_["model"] == "experiment.group"
            ),
            None,
        )
        has_components = next(
            (
                index
                for (index, dict_) in enumerate(self.data)
                if dict_["model"] == "experiment.component"
            ),
            None,
        )
        if has_groups:
            self.last_objects_before_import["group"] = Group.objects.last()
        if has_components:
            self.last_objects_before_import["component"] = Component.objects.last()

    @staticmethod
    def _include_human_readables(components):
        """Add the titles of steps (components) of experimental protocol to display
        in import log page
        """
        human_readables = dict(Component.COMPONENT_TYPES)
        for i, component in enumerate(components):
            components[i]["human_readable"] = str(
                human_readables[component["component_type"]]
            )

    def _collect_new_objects(self):
        """Collect new objects to display to user some main objects that was
        imported
        """
        last_experiment = Experiment.objects.last()
        self.new_objects["experiment_id"] = last_experiment.id
        self.new_objects["experiment_title"] = last_experiment.title
        if "research_project" in self.last_objects_before_import:
            last_study = ResearchProject.objects.last()
            self.new_objects["research_project_id"] = last_study.id
            self.new_objects["research_project_title"] = last_study.title
        else:
            self.new_objects["research_id"] = None
        if "group" in self.last_objects_before_import:
            if self.last_objects_before_import["group"] is not None:
                last_group_before_import = self.last_objects_before_import["group"].id
                self.new_objects["groups_count"] = Group.objects.filter(
                    id__gt=last_group_before_import
                ).count()
            else:
                self.new_objects["groups_count"] = Group.objects.count()
        else:
            self.new_objects["groups_count"] = None
        if "component" in self.last_objects_before_import:
            if self.last_objects_before_import["component"] is not None:
                last_component_before_import = self.last_objects_before_import[
                    "component"
                ].id
                component_queryset = Component.objects.filter(
                    id__gt=last_component_before_import
                )
            else:
                component_queryset = Component.objects.all()
            components = component_queryset.values("component_type").annotate(
                count=Count("component_type")
            )
            self._include_human_readables(components)
            self.new_objects["components"] = list(components)

        else:
            self.new_objects["components"] = None

    def _update_research_project_pk(self, id_):
        if id_:
            research_project_index = next(
                index
                for index, dict_ in enumerate(self.data)
                if dict_["model"] == "experiment.researchproject"
            )
            del self.data[research_project_index]
            experiment_index = next(
                index
                for index, dict_ in enumerate(self.data)
                if dict_["model"] == "experiment.experiment"
            )
            self.data[experiment_index]["fields"]["research_project"] = id_

    def _verify_keywords(self):
        indexes = [
            index
            for (index, dict_) in enumerate(self.data)
            if dict_["model"] == "experiment.keyword"
        ]
        next_keyword_id = (
            Keyword.objects.last().id + 1 if Keyword.objects.count() > 0 else 1
        )
        indexes_of_keywords_already_updated = []
        for i in indexes:
            # Get the keyword and check on database if the keyword already exists.
            # If exists, update the pk of this keyword to the correspondent in the database
            # otherwise, update the pk of this keyword to next_keyword_id
            old_keyword_id = self.data[i]["pk"]
            old_keyword_string = self.data[i]["fields"]["name"]
            keyword_on_database = Keyword.objects.filter(name=old_keyword_string)

            if keyword_on_database.count() > 0:
                self.data[i]["pk"] = keyword_on_database.first().id
            else:
                self.data[i]["pk"] = next_keyword_id
                next_keyword_id += 1

            # Update all the references to the old keyword to the new one
            for index_row, dict_ in enumerate(self.data):
                if dict_["model"] == "experiment.researchproject":
                    for keyword_index, keyword in enumerate(
                        dict_["fields"]["keywords"]
                    ):
                        if (
                            keyword == old_keyword_id
                            and keyword_index not in indexes_of_keywords_already_updated
                        ):
                            self.data[index_row]["fields"]["keywords"][
                                keyword_index
                            ] = self.data[i]["pk"]
                            indexes_of_keywords_already_updated.append(keyword_index)

    def _update_patients_stuff(self, patients_to_update):
        indexes = [
            index
            for (index, dict_) in enumerate(self.data)
            if dict_["model"] == "patient.patient"
        ]

        # Update patient codes
        # TODO (Refactor): Patient model has function to generate random patient code
        patients = Patient.objects.all()
        if patients:
            last_patient_code = patients.order_by("-code").first().code
            if last_patient_code:
                numerical_part_code = int(last_patient_code.split("P")[1])
                next_numerical_part = numerical_part_code + 1
                for i in indexes:
                    if str(self.data[i]["pk"]) not in patients_to_update:
                        self.data[i]["fields"]["code"] = "P" + str(next_numerical_part)
                        next_numerical_part += 1

        for i in indexes:
            if str(self.data[i]["pk"]) not in patients_to_update:
                if Patient.objects.filter(cpf=self.data[i]["fields"]["cpf"]):
                    self.data[i]["fields"]["cpf"] = None

    def _update_references_to_user(self, request):
        for model in MODELS_WITH_RELATION_TO_AUTH_USER:
            indexes = [
                index
                for (index, dict_) in enumerate(self.data)
                if dict_["model"] == model[0]
            ]
            for i in indexes:
                self.data[i]["fields"][model[1]] = request.user.id

    def _update_survey_data(self):
        """Make dummy references to limesurvey surveys until import them in Limesurvey.
        Create new survey codes
        """
        next_code = Survey.create_random_survey_code()
        indexes = [
            index
            for index, dict_ in enumerate(self.data)
            if dict_["model"] == "survey.survey"
        ]
        if indexes:
            min_limesurvey_id = Survey.objects.order_by("lime_survey_id")[
                0
            ].lime_survey_id
            if min_limesurvey_id >= 0:
                dummy_limesurvey_id = -99
            else:
                # TODO (NES-956): testar isso
                dummy_limesurvey_id = min_limesurvey_id - 1
            for index in indexes:
                self.limesurvey_relations[
                    self.data[index]["fields"]["lime_survey_id"]
                ] = dummy_limesurvey_id
                self.data[index]["fields"]["lime_survey_id"] = dummy_limesurvey_id
                dummy_limesurvey_id -= 1

                next_code = "Q" + str(int(next_code.split("Q")[1]) + 1)
                self.data[index]["fields"]["code"] = next_code

    def _assign_right_ids(self, match_eeg_els, match_eeg_ep_list):
        # Need to save old pk to update other dependent models
        old_eeg_els_pk = self.data[match_eeg_els[0]]["pk"]

        self.data[match_eeg_els[0]]["pk"] = match_eeg_els[1].id
        for match in match_eeg_ep_list:
            self.data[match[0]]["fields"][
                "eeg_electrode_localization_system"
            ] = self.data[match_eeg_els[0]]["pk"]

        # Update other dependent models references
        # TODO (NES-965):
        #  for dependent_model in dependent_models:
        #      ...
        indexes = [
            index
            for index, dict_ in enumerate(self.data)
            if dict_["model"] == "experiment.eegelectrodenetsystem"
            and dict_["fields"]["eeg_electrode_localization_system"] == old_eeg_els_pk
        ]
        for i in indexes:
            self.data[i]["fields"]["eeg_electrode_localization_system"] = self.data[
                match_eeg_els[0]
            ]["pk"]

    def _deal_with_eegelectrodelocalizationsystem(self):
        indexes = [
            index
            for (index, dict_) in enumerate(self.data)
            if dict_["model"] == "experiment.eegelectrodelocalizationsystem"
        ]
        for eeg_els_index in indexes:
            match = True
            eeg_els = EEGElectrodeLocalizationSystem.objects.filter(
                name=self.data[eeg_els_index]["fields"]["name"],
                description=self.data[eeg_els_index]["fields"]["description"],
            ).first()
            if eeg_els:
                eeg_ep_queryset = eeg_els.electrode_positions.all()
                eeg_ep_import_indexes = [
                    index
                    for (index, dict_) in enumerate(self.data)
                    if dict_["model"] == "experiment.eegelectrodeposition"
                    and dict_["fields"]["eeg_electrode_localization_system"]
                    == self.data[eeg_els_index]["pk"]
                ]
                if eeg_ep_queryset.count() == len(eeg_ep_import_indexes):
                    match_tuple_list = []  # only to intialize
                    for eeg_ep_index in eeg_ep_import_indexes:
                        name = self.data[eeg_ep_index]["fields"]["name"]
                        coordinate_x = self.data[eeg_ep_index]["fields"]["coordinate_x"]
                        coordinate_y = self.data[eeg_ep_index]["fields"]["coordinate_y"]
                        channel_default_index = self.data[eeg_ep_index]["fields"][
                            "channel_default_index"
                        ]
                        match_instance = eeg_ep_queryset.filter(
                            name=name,
                            coordinate_x=coordinate_x,
                            coordinate_y=coordinate_y,
                            channel_default_index=channel_default_index,
                        ).first()
                        if match_instance:
                            match_tuple_list.append((eeg_ep_index, match_instance))
                            continue
                        else:
                            match = False
                            break
                    if match:
                        self._assign_right_ids(
                            (eeg_els_index, eeg_els), match_tuple_list
                        )

    def _deal_with_fileformat(self):
        file_formats = FileFormat.objects.all().order_by("-id")
        if file_formats:
            max_id = file_formats[0].id
            while True:
                index = next(
                    (
                        index
                        for (index, dict_) in enumerate(self.data)
                        if dict_["model"] == "experiment.fileformat"
                    ),
                    None,
                )
                if index is None:
                    break
                indexes_datafile = [
                    index_datafile
                    for (index_datafile, dict_) in enumerate(self.data)
                    if (
                        dict_["model"] == "experiment.eegdata"
                        or dict_["model"] == "experiment.emgdata"
                        or dict_["model"] == "experiment.additionaldata"
                        or dict_["model"] == "experiment.digitalgamephasedata"
                        or dict_["model"] == "experiment.genericdatacollectiondata"
                    )
                    and dict_["fields"]["file_format"] == self.data[index]["pk"]
                ]
                file_format = FileFormat.objects.filter(
                    nes_code=self.data[index]["fields"]["nes_code"]
                ).first()
                if file_format:
                    for index_datafile in indexes_datafile:
                        self.data[index_datafile]["fields"][
                            "file_format"
                        ] = file_format.id
                    del self.data[index]
                else:
                    file_format = FileFormat.objects.filter(
                        id=self.data[index]["pk"]
                    ).first()
                    if file_format:
                        max_id += 1
                        self.data[index]["pk"] = max_id
                        for index_datafile in indexes_datafile:
                            self.data[index_datafile]["fields"][
                                "file_format"
                            ] = self.data[index]["pk"]

    def _deal_with_models_with_unique_fields(self):
        """Some models that have unique fields need to be treated separately
        because the updating concept diverges from others. TODO (NES-965): explain better
        """
        self._deal_with_eegelectrodelocalizationsystem()
        self._deal_with_fileformat()

    def _keep_objects_pre_loaded(self):
        """For objects in fixtures initially loaded, check if the objects
        that are to be are already there. This is to avoid duplication of that objects.
        The objects checked here are the ones that can be edited. Objects that are not
        editable are simply ignored when updating indexes in _update_pks method.
        """
        self._deal_with_models_with_unique_fields()

        for model, dependent_models in PRE_LOADED_MODELS_FOREIGN_KEYS.items():
            # Treat EEGElectrodeLolizationSystem separately
            # in self._deal_with_models_with_unique_fields method
            if model[0] == "experiment.eegelectrodelocalizationsystem":
                continue
            indexes = [
                index
                for (index, dict_) in enumerate(self.data)
                if dict_["model"] == model[0]
            ]
            app_model = model[0].split(".")
            for i in indexes:
                model_class = apps.get_model(app_model[0], app_model[1])
                filter_ = {}
                for field in model[1]:
                    filter_[field] = self.data[i]["fields"][field]
                if not filter_:  # If not filter_, instance have only relational fields
                    instance = model_class.objects.first()
                else:
                    instance = model_class.objects.filter(**filter_).first()
                if instance:
                    # Deal with models that inherit from Multi-table inheritance mode
                    if self.data[i]["model"] in PRE_LOADED_MODELS_INHERITANCE:
                        app_model_inheritade = PRE_LOADED_MODELS_INHERITANCE[
                            self.data[i]["model"]
                        ][0].split(".")
                        model_class_inheritade = apps.get_model(
                            app_model_inheritade[0], app_model_inheritade[1]
                        )
                        index_inheritade = [
                            index
                            for (index, dict_inheritance) in enumerate(self.data)
                            if dict_inheritance["model"]
                            == PRE_LOADED_MODELS_INHERITANCE[self.data[i]["model"]][0]
                            and dict_inheritance["pk"] == self.data[i]["pk"]
                        ][0]
                        filter_inheritade = {}
                        for field in PRE_LOADED_MODELS_INHERITANCE[
                            self.data[i]["model"]
                        ][1]:
                            filter_inheritade[field] = self.data[index_inheritade][
                                "fields"
                            ][field]
                        instance_inheritade = model_class_inheritade.objects.filter(
                            **filter_inheritade
                        ).first()
                        if instance_inheritade:
                            self.data[index_inheritade]["pk"] = instance.id
                        else:
                            break
                    self.data[i]["pk"], old_id = instance.id, self.data[i]["pk"]
                    # Finally, assign the old id to the relation
                    for dependent_model in dependent_models:
                        dependent_indexes = [
                            index
                            for (index, dict_) in enumerate(self.data)
                            if dict_["model"] == dependent_model[0]
                            and dict_["fields"][dependent_model[1]] == old_id
                        ]
                        for dependent_index in dependent_indexes:
                            self.data[dependent_index]["fields"][
                                dependent_model[1]
                            ] = self.data[i]["pk"]

    def _update_subject(self, index, patient):
        # Though in experiment.models patient attribute is ForeignKey for Subject model,
        # in the system, Subject have a OneToOne relation with Patient so
        # prevent of creating new Subject object if not creating new Patient's objects
        # TODO: if this is the case for the future, Subject model could be
        #  changed to have OneToOne relation with Patient.
        subject = Subject.objects.get(patient=patient)
        self.data[index]["pk"], updated_id = subject.id, self.data[index]["pk"]
        dependent_indexes = self._get_indexes("experiment", "subjectofgroup")
        for dependent_index in dependent_indexes:
            if self.data[dependent_index]["fields"]["subject"] == updated_id:
                self.data[dependent_index]["fields"]["subject"] = subject.id

    def _keep_patients_pre_loaded(self, patients_to_update):
        for model, dependent_models in PRE_LOADED_PATIENT_MODEL.items():
            indexes = [
                index
                for (index, dict_) in enumerate(self.data)
                if dict_["model"] == model[0]
            ]
            for i in indexes:
                list_of_filters = []
                if self.data[i]["fields"]["cpf"]:
                    list_of_filters.append(Q(**{"cpf": self.data[i]["fields"]["cpf"]}))
                list_of_filters.append(Q(**{"name": self.data[i]["fields"]["name"]}))

                instances = Patient.objects.filter(reduce(or_, list_of_filters))
                for instance in instances:
                    if str(instance.id) in patients_to_update:
                        self.data[i]["pk"], old_id = instance.id, self.data[i]["pk"]
                        for dependent_model in dependent_models:
                            dependent_indexes = [
                                index
                                for (index, dict_) in enumerate(self.data)
                                if dict_["model"] == dependent_model[0]
                                and dict_["fields"][dependent_model[1]] == old_id
                            ]
                            for dependent_index in dependent_indexes:
                                self.data[dependent_index]["fields"][
                                    dependent_model[1]
                                ] = self.data[i]["pk"]
                                if dependent_model[0] == "experiment.subject":
                                    self._update_subject(dependent_index, instance)

    def check_for_duplicates_of_participants(self):
        try:
            with zipfile.ZipFile(self.file_path) as zip_file:
                json_file = zip_file.extract(self.FIXTURE_FILE_NAME, self.temp_dir)
                with open(json_file) as f:
                    data = json.load(f)
        except (ValueError, JSONDecodeError):
            return (
                self.BAD_JSON_FILE_ERROR_CODE,
                "Bad json file. Aborting import experiment.",
                None,
            )

        indexes = [
            index
            for (index, dict_) in enumerate(data)
            if dict_["model"] == "patient.patient"
        ]

        participants_with_conflict = []
        for i in indexes:
            # Check if the patient is already there
            if data[i]["fields"]["cpf"]:
                patient_already_in_database = Patient.objects.get(
                    name=data[i]["fields"]["name"], cpf=data[i]["fields"]["cpf"]
                )
            else:
                patient_already_in_database = Patient.objects.get(
                    code=data[i]["fields"]["code"]
                )

            if patient_already_in_database:
                participants_with_conflict.append(
                    {
                        "id_db": patient_already_in_database.pk,
                        "name_db": patient_already_in_database.name,
                        "code_db": patient_already_in_database.code,
                        "cpf_db": patient_already_in_database.cpf,
                        "id_new": data[i]["pk"],
                        "name_new": data[i]["fields"]["name"],
                        "code_new": data[i]["fields"]["code"],
                        "cpf_new": data[i]["fields"]["cpf"],
                        "selected": None,
                    }
                )

        return 0, "", participants_with_conflict

    def _verify_classification_of_diseases(self):
        indexes = [
            index
            for (index, dict_) in enumerate(self.data)
            if dict_["model"] == "patient.diagnosis"
        ]
        for index in indexes:
            class_of_diseases = ClassificationOfDiseases.objects.filter(
                code=self.data[index]["fields"]["classification_of_diseases"][0]
            ).first()
            if not class_of_diseases:
                ClassificationOfDiseases.objects.create(
                    code=self.data[index]["fields"]["classification_of_diseases"][0],
                    description="(imported, not recognized)",
                    abbreviated_description="(imported, not recognized)",
                )

    def _update_data_before_importing(
        self, request, research_project_id, patients_to_update
    ):
        self._update_survey_data()
        self._update_research_project_pk(research_project_id)
        self._verify_keywords()
        self._update_references_to_user(request)
        self._keep_objects_pre_loaded()
        self._keep_patients_pre_loaded(patients_to_update)
        self._update_patients_stuff(patients_to_update)
        self._verify_classification_of_diseases()

    @staticmethod
    def _get_first_available_id():
        last_id = 1
        for app in apps.get_app_configs():
            if app.verbose_name in ["Experiment", "Patient", "Quiz", "Survey", "Team"]:
                for model in app.get_models():
                    if (
                        "Goalkeeper" not in model.__name__
                    ):  # TODO: ver modelo com referência a outro bd: dá pau
                        last_model = model.objects.last()
                        if last_model and hasattr(last_model, "id"):
                            last_model_id = last_model.id
                            last_id = (
                                last_model_id if last_id < last_model_id else last_id
                            )
        return last_id + 1

    def _update_pks(self, digraph, successor, next_id):
        """Recursive function to update models pks based on a directed graph representing
        model relations
        """
        if (
            self.data[successor]["model"] not in ONE_TO_ONE_RELATION
            and not digraph.nodes[successor]["pre_loaded"]
        ):
            if not digraph.nodes[successor]["updated"]:
                self.data[successor]["pk"] = next_id

                # Patch for repeated next_id in same models
                model = self.data[successor]["model"]
                updated_ids = [
                    dict_["pk"]
                    for (index, dict_) in enumerate(self.data)
                    if dict_["model"] == model
                ]
                if next_id in updated_ids:
                    # Prevent from duplicated pks in same model: this is done in the recursive path
                    # TODO: verify better way to update next_id
                    next_id = max(updated_ids) + 1
                    self.data[successor]["pk"] = next_id
                digraph.nodes[successor]["updated"] = True
        for predecessor in digraph.predecessors(successor):
            if "relation" in digraph[predecessor][successor]:
                relation = digraph[predecessor][successor]["relation"]
                self.data[predecessor]["fields"][relation] = self.data[successor]["pk"]
            else:
                self.data[predecessor]["pk"] = self.data[successor]["pk"]
            next_id += 1
            self._update_pks(digraph, predecessor, next_id)

    def _build_digraph(self):
        digraph = nx.DiGraph()
        for index_from, dict_ in enumerate(self.data):
            if dict_["model"] in FOREIGN_RELATIONS:
                node_from = dict_["model"]
                nodes_to = FOREIGN_RELATIONS[node_from]
                for node_to in nodes_to:
                    index_to = next(
                        (
                            index_foreign
                            for index_foreign, dict_foreign in enumerate(self.data)
                            if dict_foreign["model"] == node_to[0]
                            and dict_foreign["pk"] == dict_["fields"][node_to[1]]
                        ),
                        None,
                    )
                    if index_to is not None:
                        digraph.add_edge(index_from, index_to)
                        digraph[index_from][index_to]["relation"] = node_to[1]
            if dict_["model"] in ONE_TO_ONE_RELATION:
                node_from = dict_["model"]
                node_to = ONE_TO_ONE_RELATION[node_from]
                index_to = next(
                    (
                        index_inheritade
                        for index_inheritade, dict_inheritade in enumerate(self.data)
                        if dict_inheritade["model"] == node_to
                        and dict_inheritade["pk"] == dict_["pk"]
                    ),
                    None,
                )
                if index_to is not None:
                    digraph.add_edge(index_from, index_to)

        for node in digraph.nodes():
            digraph.nodes[node]["atributes"] = self.data[node]
            digraph.nodes[node]["updated"] = False
            if self.data[node]["model"] not in PRE_LOADED_MODELS_NOT_EDITABLE:
                digraph.nodes[node]["pre_loaded"] = False
            else:
                digraph.nodes[node]["pre_loaded"] = True

        # set digraph.nodes[node]['pre_loaded'] == True for models inherited
        nodes = [
            node
            for node in digraph.nodes
            if self.data[node]["model"] in PRE_LOADED_MODELS_NOT_EDITABLE_INHERITANCE
        ]
        for node in nodes:
            model_inheritances = PRE_LOADED_MODELS_NOT_EDITABLE_INHERITANCE[
                self.data[node]["model"]
            ]
            for model in model_inheritances:
                node_inheritance = next(
                    node_inheritance
                    for node_inheritance in digraph.nodes
                    if self.data[node_inheritance]["model"] == model
                    and self.data[node]["pk"] == self.data[node_inheritance]["pk"]
                )
                digraph.nodes[node_inheritance]["pre_loaded"] = True

        return digraph

    def _manage_pks(self, digraph):
        next_id = self._get_first_available_id()
        for model_root_node in MODEL_ROOT_NODES:
            root_nodes = [
                index
                for index, dict_ in enumerate(self.data)
                if dict_["model"] == model_root_node
            ]
            for root_node in root_nodes:
                self._update_pks(digraph, root_node, next_id)
                next_id += 1

    def _upload_files(self):
        indexes = [
            index
            for index, dict_ in enumerate(self.data)
            if dict_["model"] in MODELS_WITH_FILE_FIELD
        ]
        with zipfile.ZipFile(self.file_path) as zip_file:
            for index in indexes:
                relative_path = self.data[index]["fields"][
                    MODELS_WITH_FILE_FIELD[self.data[index]["model"]]
                ]
                if relative_path:
                    file_path = zip_file.extract(relative_path, self.temp_dir)
                    app_model = self.data[index]["model"].split(".")
                    model_class = apps.get_model(app_model[0], app_model[1])
                    object_imported = model_class.objects.get(id=self.data[index]["pk"])
                    with File(open(file_path, "rb")) as f:
                        file_field = MODELS_WITH_FILE_FIELD[self.data[index]["model"]]
                        getattr(object_imported, file_field).save(
                            path.basename(file_path), f
                        )
                        object_imported.save()

    def _get_indexes(self, app, model):
        # TODO (NES-956): disseminate to rest of the script
        return [
            index
            for (index, dict_) in enumerate(self.data)
            if dict_["model"] == app + "." + model
        ]

    def _remove_limesurvey_participants(self):
        """Must be called after updating Limesurvey surveys references"""

        result = 0, ""
        indexes = self._get_indexes("experiment", "questionnaire")
        ls_interface = Questionnaires()
        # As there can be same survey in more than one questionnaire component,
        # create a dictionaire to nao questionnaire compontents by limesurvey
        # surveys.
        token_ids_survey = dict()
        for index in indexes:
            questionnaire = Questionnaire.objects.get(id=self.data[index]["pk"])
            limesurvey_id = questionnaire.survey.lime_survey_id
            # Initialize dict if first time of limesurvey_id
            if limesurvey_id not in token_ids_survey:
                token_ids_survey[limesurvey_id] = []
            token_ids = list(
                QuestionnaireResponse.objects.filter(
                    data_configuration_tree__component_configuration__component=questionnaire.id
                ).values_list("token_id", flat=True)
            )
            token_ids_survey[limesurvey_id] += token_ids
        for limesurvey_id, token_ids in token_ids_survey.items():
            all_participants = ls_interface.find_tokens_by_questionnaire(limesurvey_id)
            if all_participants is None:
                result = self.LIMESURVEY_ERROR, _(
                    "Could not clear all extra survey participants data."
                )
                continue
            # TODO (NES-956): don't remove participants of other experiment of this NES.
            for participant in all_participants:
                if participant["tid"] not in token_ids:
                    status_delete = ls_interface.delete_participants(
                        limesurvey_id, [participant["tid"]]
                    )
                    if status_delete is None:
                        result = self.LIMESURVEY_ERROR, _(
                            "Could not clear all extra survey participants data."
                        )
                        continue
                    responses = ls_interface.get_responses_by_token(
                        sid=limesurvey_id, token=participant["token"]
                    )
                    if responses is None:
                        result = self.LIMESURVEY_ERROR, _(
                            "Could not clear all extra survey participants data."
                        )
                        continue
                    responses = QuestionnaireUtils.responses_to_csv(responses)
                    del responses[0]  # First line is the header line
                    response_ids = []
                    for response in responses:
                        response_ids.append(int(response[0]))
                    ls_interface = Questionnaires(
                        settings.LIMESURVEY["URL_API"]
                        + "/index.php/plugins/unsecure?plugin=extendRemoteControl&function=action"
                    )
                    status = ls_interface.delete_responses(limesurvey_id, response_ids)
                    if status is None:
                        result = self.LIMESURVEY_ERROR, _(
                            "Could not clear all extra survey participants data."
                        )
                    ls_interface = Questionnaires()  # Return to access core RPC

        ls_interface.release_session_key()

        return result

    def _update_limesurvey_identification_questions(self):
        """Must be called after updating Limesurvey surveys references"""
        result = 0, ""
        indexes = self._get_indexes("experiment", "questionnaire")
        ls_interface = Questionnaires(
            settings.LIMESURVEY["URL_API"]
            + "/index.php/plugins/unsecure?plugin=extendRemoteControl&function=action"
        )
        questionnaire_utils = QuestionnaireUtils()
        for index in indexes:
            questionnaire = Questionnaire.objects.get(id=self.data[index]["pk"])
            questionnaire_responses = QuestionnaireResponse.objects.filter(
                data_configuration_tree__component_configuration__component=questionnaire.id
            )
            limesurvey_id = questionnaire.survey.lime_survey_id
            for response in questionnaire_responses:
                responsible_id = response.questionnaire_responsible_id
                subject_id = response.subject_of_group.subject_id
                token_id = response.token_id
                token = ls_interface.get_participant_properties(
                    limesurvey_id, token_id, "token"
                )
                if token is None:
                    result = self.LIMESURVEY_ERROR, _(
                        "Could not update identification questions for all responses."
                    )
                    continue
                # TODO (NES-956): get the language. By now put 'en' to test
                ls_subject_id_column_name = questionnaire_utils.get_response_column_name_for_identification_group_questions(
                    ls_interface, limesurvey_id, "subjectid", "en"
                )
                if isinstance(ls_subject_id_column_name, tuple):  # Returned error
                    result = ls_subject_id_column_name[0], _(
                        "Could not update identification questions for all "
                        "responses."
                    )
                    continue
                ls_responsible_id_column_name = questionnaire_utils.get_response_column_name_for_identification_group_questions(
                    ls_interface, limesurvey_id, "responsibleid", "en"
                )
                if isinstance(ls_responsible_id_column_name, tuple):  # Returned error
                    result = ls_responsible_id_column_name[0], _(
                        "Could not update identification questions for all "
                        "responses."
                    )
                    continue
                result_update = ls_interface.update_response(
                    limesurvey_id,
                    {
                        "token": token,
                        ls_subject_id_column_name: subject_id,
                        ls_responsible_id_column_name: responsible_id,
                    },
                )
                if not result_update:
                    return self.LIMESURVEY_ERROR, _("Could not update all responses.")

        ls_interface.release_session_key()

        return result

    def _import_limesurvey_surveys(self):
        """Import surveys to Limesurvey server
        :return: list of limsurvey surveys imported
        """
        result = 0, ""
        ls_interface = Questionnaires()
        if ls_interface.session_key is None:
            result = self.LIMESURVEY_ERROR, _(
                "Could not import survey(s) to LimeSurvey. Only Experiment data was "
                "imported. You can remove experiment imported and try again. If problem "
                "persists please contact system administrator"
            )
            return result
        limesurvey_ids = []
        # Does not add try/exception trying to open zipfile here because it
        # was done in import_all method
        with zipfile.ZipFile(self.file_path) as zip_file:
            for old_ls_id, dummy_ls_id in self.limesurvey_relations.items():
                survey_archivename = str(old_ls_id) + ".lsa"
                if survey_archivename in zip_file.namelist():
                    survey_archive = zip_file.extract(survey_archivename, self.temp_dir)
                    with open(survey_archive, "rb") as file:
                        encoded_string = b64encode(file.read())
                        encoded_string = encoded_string.decode("utf-8")
                        new_ls_id = ls_interface.import_survey(encoded_string)
                        if new_ls_id is None:
                            result = self.LIMESURVEY_ERROR, _(
                                "Could not import survey(s) to LimeSurvey. Only "
                                "Experiment data was imported. You can remove experiment "
                                "imported and try again. If problem persists please "
                                "contact system administrator"
                            )
                            return result
                        survey = Survey.objects.get(lime_survey_id=dummy_ls_id)
                        survey.lime_survey_id = new_ls_id
                        survey.save()
                        limesurvey_ids.append(new_ls_id)
                else:
                    # TODO (NES-956): add information that was not a survey archive
                    #  to this survey
                    continue

        if limesurvey_ids:
            result = self._remove_limesurvey_participants()
            if not result[0]:
                return self._update_limesurvey_identification_questions()

        return result

    def import_all(self, request, research_project_id=None, patients_to_update=None):
        # TODO: maybe this try in constructor
        try:
            with zipfile.ZipFile(self.file_path) as zip_file:
                json_file = zip_file.extract(self.FIXTURE_FILE_NAME, self.temp_dir)
                with open(json_file) as f:
                    self.data = json.load(f)
                    # To Import Log page
                    self._set_last_objects_before_import(research_project_id)
        except (ValueError, JSONDecodeError):
            return self.BAD_JSON_FILE_ERROR_CODE, _(
                "Bad json file. Aborting import experiment."
            )

        digraph = self._build_digraph()
        self._manage_pks(digraph)
        self._update_data_before_importing(
            request, research_project_id, patients_to_update
        )

        with open(path.join(self.temp_dir, self.FIXTURE_FILE_NAME), "w") as file:
            file.write(json.dumps(self.data))

        call_command("loaddata", path.join(self.temp_dir, self.FIXTURE_FILE_NAME))

        self._collect_new_objects()

        self._upload_files()
        result = self._import_limesurvey_surveys()

        return result

    def get_new_objects(self):
        return self.new_objects
