# coding=utf-8
import datetime

from django.test import TestCase
from django import forms

from experiment.forms import ResearchProjectForm, ExperimentForm, GroupForm
from experiment.models import ResearchProject, Experiment, ExperimentResearcher


class ResearchProject_FormTest(TestCase):

   def setUp(self):
       self.research_projects = ResearchProject.objects.all()
       # self.research_projects.save()
       self.data = {
           'start_date': '13/07/2018',
           'end_date': '30/07/2018',
           'title': 'Experimento TOC',
           'description': 'Experimento TOC',
           'owner': 'gady'}

   def test_ResearchProjectForm_is_valid(self):
       start_date  = self.data["start_date"]
       end_date = self.data["end_date"]
       title = self.data["title"]
       description = self.data["description"]
       owner = self.data["owner"]

       research_projects = ResearchProjectForm(data={'start_date': start_date, 'end_date': end_date, 'title': title, 'description': description, 'owner': owner})
       self.assertTrue(research_projects.is_valid())

   def test_ResearchProjectForm_is_not_valid(self):
       research_projects = ResearchProjectForm(data={'start_date': "", 'end_date': "", 'title': "", 'description': "", 'owner': ""})
       self.assertFalse(research_projects.is_valid())

   def test_ResearchProjectForm_is_not_valid_start_date(self):
       research_projects = ResearchProjectForm(data={'start_date': "07/12/2018", 'end_date': self.data["end_date"], 'title': self.data["title"], 'description': self.data["description"], 'owner': self.data["owner"]})
       self.assertFalse(research_projects.is_valid())
       self.assertTrue(research_projects.errors["start_date"]) #True, porque start_date é campo obrigatório

   def test_ResearchProjectForm_is_not_valid_end_date(self):
       research_projects = ResearchProjectForm(data={'start_date': self.data["start_date"], 'end_date': "07/30/2018", 'title': self.data["title"], 'description': self.data["description"], 'owner': self.data["owner"]})
       self.assertFalse(research_projects.is_valid())
       self.assertEqual(research_projects.errors["end_date"], ["Informe uma data válida."])

   def test_ResearchProjectForm_is_not_valid_title(self):
       research_projects = ResearchProjectForm(
           data={
               'start_date': self.data["start_date"],
               'end_date': self.data["end_date"],
               'title': "",
               'description': self.data["description"],
               'owner': self.data["owner"]}
       )
       self.assertFalse(research_projects.is_valid())
       self.assertEqual(research_projects.errors["title"], ["Este campo é obrigatório."])

   def test_ResearchProjectForm_is_not_valid_description(self):
       research_projects = ResearchProjectForm(data={'start_date': self.data["start_date"], 'end_date': self.data["end_date"], 'title': self.data["title"], 'description': "", 'owner': self.data["owner"]})
       self.assertFalse(research_projects.is_valid())
       self.assertEqual(research_projects.errors["description"], ["Este campo é obrigatório."])

   def test_ResearchProjectForm_is_not_valid_owner(self):
       research_projects = ResearchProjectForm(data={'start_date': self.data["start_date"], 'end_date': self.data["end_date"], 'title': self.data["title"], 'description': self.data["description"], 'owner': ""})
       self.assertTrue(research_projects.is_valid()) # True, porque owner não é campo obrigatório

       # self.assertEqual(research_projects.errors["owner_id"], ["Este campo é obrigatório."])
       # self.assertFalse(research_projects.errors["owner_id"])

class Experiment_FormTest(TestCase):

   @classmethod
   def setUp(cls):
       cls.data = {
           'title': 'Experimento TOC',
           'description': 'Experimento TOC',
           'source_code_url': 'http://www.ime.usp.br',
           'ethics_committee_project_url': 'http://www.fm.usp.br',
           'ethics_committee_project_file':'/users/celsovi/documents/unit_tests/links.rtf',
           'is_public': '',
           'data_acquisition_is_concluded':''
       }
       cls.research_project = ResearchProject.objects.create(
           title="Research project title", start_date=datetime.date.today(),
           description="Research project description"
       )

       cls.experiment = Experiment.objects.create(
           research_project_id=cls.research_project.id,
           title="Experimento-Update",
           description="Descricao do Experimento-Update",
           source_code_url="http://www.if.usp.br",
           ethics_committee_project_url="http://www.fm.usp.br",
           ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
           is_public=" ",
           data_acquisition_is_concluded=" ")

   # def setUp(self):
   #     self.data = {
   #         'title': 'Experimento TOC',
   #         'description': 'Experimento TOC',
   #         'source_code_url': 'http://www.ime.usp.br',
   #         'ethics_committee_project_url': 'http://www.fm.usp.br',
   #         'ethics_committee_project_file':'/users/celsovi/documents/unit_tests/links.rtf',
   #         'is_public': '',
   #         'data_acquisition_is_concluded':''
   #     }
   #     self.research_project = ResearchProject.objects.create(
   #         title="Research project title", start_date=datetime.date.today(),
   #         description="Research project description"
   #     )
   #
   #     self.experiment = Experiment.objects.create(
   #         research_project_id=self.research_project.id,
   #         title="Experimento-Update",
   #         description="Descricao do Experimento-Update",
   #         source_code_url="http://www.if.usp.br",
   #         ethics_committee_project_url="http://www.fm.usp.br",
   #         ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
   #         is_public=" ",
   #         data_acquisition_is_concluded=" ")

   def test_ExperimentForm_is_valid(self):
       experimentForm = ExperimentForm(data={'research_project':self.research_project.id,'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file':self.data["ethics_committee_project_file"], 'is_public':self.data["is_public"], 'data_acquisition_is_concluded':self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experimentForm.is_valid())

   def test_ExperimentForm_is_not_valid_research_project(self):
       experiment = ExperimentForm(data={'research_project':"", 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertFalse(experiment.is_valid())
       self.assertEqual(experiment.errors["research_project"], ["Este campo é obrigatório."])

   def test_ExperimentForm_is_not_valid_title(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': "", 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertFalse(experiment.is_valid())
       self.assertEqual(experiment.errors["title"], ["Este campo é obrigatório."])

   def test_ExperimentForm_is_not_valid_description(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': "", 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertFalse(experiment.is_valid())
       self.assertEqual(experiment.errors["description"], ["Este campo é obrigatório."])

   def test_ExperimentForm_is_not_valid_source_code_url(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': "", 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experiment.is_valid())
       s = experiment.data["source_code_url"]
       s.upper()
       self.assertNotEquals(s[ : 7],"HTTP://", "Informe uma url válida.")

   def test_ExperimentForm_is_not_valid_ethics_committee_project_url(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': "", 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experiment.is_valid())
       s = experiment.data["ethics_committee_project_url"]
       s.upper()
       self.assertNotEquals(s[ : 7],"HTTP://", "Informe uma url válida.")

   def test_ExperimentForm_is_not_valid_ethics_committee_project_file(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': "", 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experiment.is_valid())

   def test_ExperimentForm_is_not_valid_is_public(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': "", 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experiment.is_valid())

   def test_ExperimentForm_is_not_valid_data_acquisition_is_concluded(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': ""})
       self.assertTrue(experiment.is_valid())


class GroupAdd_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'title': 'Experimento TOC',
            'description': 'Experimento TOC',

        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")


    def test_GroupForm_is_valid(self):
        title = self.data["title"]
        description = self.data["description"]

        groupAdd_form = GroupForm(data={'title': title, 'description': description})
        self.assertTrue(groupAdd_form.is_valid())

    def test_GroupForm_is_not_valid_title(self):
       groupAdd_form = GroupForm(data={'title': "", 'description': self.data["description"]})
       self.assertFalse(groupAdd_form.is_valid())
       self.assertEqual(groupAdd_form.errors["title"], ["Este campo é obrigatório."])

    def test_GroupForm_is_not_valid_description(self):
       groupAdd_form = GroupForm(data={'title': self.data["title"], 'description': ""})
       self.assertFalse(groupAdd_form.is_valid())
       self.assertEqual(groupAdd_form.errors["description"], ["Este campo é obrigatório."])

# class InclusaoCriteria_FormTest(TestCase):
#
#     @classmethod
#     def setUp(cls):
#         cls.data = {
#             'title': 'Experimento TOC',
#             'description': 'Experimento TOC',
#
#         }
#         cls.research_project = ResearchProject.objects.create(
#             title="Research project title", start_date=datetime.date.today(),
#             description="Research project description"
#         )
#
#         cls.experiment = Experiment.objects.create(
#             research_project_id=cls.research_project.id,
#             title="Experimento-Update",
#             description="Descricao do Experimento-Update",
#             source_code_url="http://www.if.usp.br",
#             ethics_committee_project_url="http://www.fm.usp.br",
#             ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
#             is_public=" ",
#             data_acquisition_is_concluded=" ")
#
#
#     def test_InclusaoCriteria_is_valid(self):
#         s = user_form.id["search-results-diseases"]
#         s.upper()
#         self.assertNotEquals(s[: 7], "HTTP://", "Informe uma url válida.")
#
#
# class CollaboratorAdd_FormTest(TestCase):
#
#     @classmethod
#     def setUp(cls):
#         cls.data = {
#             'title': 'Experimento TOC',
#             'description': 'Experimento TOC',
#             'source_code_url': 'http://www.ime.usp.br',
#             'ethics_committee_project_url': 'http://www.fm.usp.br',
#             'ethics_committee_project_file': '/users/celsovi/documents/unit_tests/links.rtf',
#             'is_public': '',
#             'data_acquisition_is_concluded': ''
#         }
#         cls.research_project = ResearchProject.objects.create(
#             title="Research project title", start_date=datetime.date.today(),
#             description="Research project description"
#         )
#
#         cls.experiment = Experiment.objects.create(
#             research_project_id=cls.research_project.id,
#             title="Experimento-Update",
#             description="Descricao do Experimento-Update",
#             source_code_url="http://www.if.usp.br",
#             ethics_committee_project_url="http://www.fm.usp.br",
#             ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
#             is_public=" ",
#             data_acquisition_is_concluded=" ")
#
#         cls.collaborators_added = ExperimentResearcher.objects.filter(experiment_id=cls.experiment.id)
#
#
#     def test_CollaboratorForm_is_valid(self):
#         pass
#
#
# class Subject_FormTest(TestCase):
#
#     @classmethod
#     def setUp(cls):
#         cls.data = {
#             'title': 'Experimento TOC',
#             'description': 'Experimento TOC',
#
#         }
#         cls.research_project = ResearchProject.objects.create(
#             title="Research project title", start_date=datetime.date.today(),
#             description="Research project description"
#         )
#
#         cls.experiment = Experiment.objects.create(
#             research_project_id=cls.research_project.id,
#             title="Experimento-Update",
#             description="Descricao do Experimento-Update",
#             source_code_url="http://www.if.usp.br",
#             ethics_committee_project_url="http://www.fm.usp.br",
#             ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
#             is_public=" ",
#             data_acquisition_is_concluded=" ")
#
#
#     def test_SubjectFormPorPart_is_valid(self):
#         pass
#
