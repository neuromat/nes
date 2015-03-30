# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db.models import Q

class Migration(DataMigration):

    def new_historical_phone(self, orm, hist_pat, history_type, number=None):
        # There will be at most one phone in Telephone table for this type and patient.
        related_phone = orm.Telephone.objects.filter(patient_id=hist_pat.id, type="MA")

        # If a telephone instance for this number was never create, create one and delete it, so that we have an id to
        # assign to the historical telephone instance.
        id = None
        if related_phone.count() == 0:
            # Check if it can be found in the historical telephone table, because maybe we already created a fake number
            # in there during this migration
            related_phone = orm.HistoricalTelephone.objects.filter(patient_id=hist_pat.id, type="MA")

            if related_phone.count() == 0:
                phone = orm.Telephone(number=hist_pat.phone, type="MA", patient_id=hist_pat.id)
                phone.changed_by_id = hist_pat.changed_by_id
                phone.save()
                id = phone.id
                phone.delete()
            else:
                id = related_phone.first().id
        else:
            id = related_phone.first().id

        hist_pho = orm.HistoricalTelephone(id=id,
                                           patient_id=hist_pat.id,
                                           number=(number if number is not None else hist_pat.phone),
                                           type="MA",
                                           changed_by_id=hist_pat.changed_by_id,
                                           history_date=hist_pat.history_date,
                                           history_user=hist_pat.history_user,
                                           history_type=history_type)
        hist_pho.save()


    def new_historical_cellphone(self, orm, hist_pat, history_type, number=None):
        # There will be at most one phone in Telephone table for this type and patient.
        related_phone = orm.Telephone.objects.filter(patient_id=hist_pat.id, type="MO")

        # If a telephone instance for this number was never created, create one and delete it, so that we have an id to
        # assign to the historical telephone instance.
        id = None
        if related_phone.count() == 0:
            # Check if it can be found in the historical telephone table, because maybe we already created a fake number
            # in there during this migration
            related_phone = orm.HistoricalTelephone.objects.filter(patient_id=hist_pat.id, type="MO")

            if related_phone.count() == 0:
                phone = orm.Telephone(number=hist_pat.cellphone, type="MO", patient_id=hist_pat.id)
                phone.changed_by_id = hist_pat.changed_by_id
                phone.save()
                id = phone.id
                phone.delete()
            else:
                id = related_phone.first().id
        else:
            id = related_phone.first().id

        hist_pho = orm.HistoricalTelephone(id=id,
                                           patient_id=hist_pat.id,
                                           number=(number if number is not None else hist_pat.cellphone),
                                           type="MO",
                                           changed_by_id=hist_pat.changed_by_id,
                                           history_date=hist_pat.history_date,
                                           history_user=hist_pat.history_user,
                                           history_type=history_type)
        hist_pho.save()


    def find_changed_by(self, orm, patient, number):
        last_phone_change = orm.HistoricalPatient.objects.filter(id=patient.id,
                                                                 phone=number).order_by("history_date").last()

        if last_phone_change is not None:
            return last_phone_change.changed_by_id
        else:
            # History may not be consistent because of a previous backward migration.
            # Try to find this change in the cellphone field.
            last_phone_change = orm.HistoricalPatient.objects.filter(id=patient.id,
                                                                     cellphone=number).order_by("history_date").last()
            if last_phone_change is not None:
                return last_phone_change.changed_by_id
            else:
                # Use the id of the user that made the last change in the patient instance.
                return patient.changed_by_id


    def is_different_where_none_equal_empty(self, num1, num2):
        if num1 != num2 and not(num1 is None and num2 == "") and not(num2 is None and num1 == ""):
            return True
        else:
            return False


    def forwards(self, orm):
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for patient in orm.Patient.objects.all():
            if patient.phone is not None and patient.phone != "":
                # phone = orm.Telephone(number=patient.phone, type=orm.Telephone.MAIN, patient=patient)
                phone = orm.Telephone(number=patient.phone, type="MA", patient=patient)
                phone.changed_by_id = self.find_changed_by(orm, patient, patient.phone)
                phone.save()

            if patient.cellphone is not None and patient.cellphone != "":
                # phone = orm.Telephone(number=patient.cellphone, type=orm.Telephone.MOBILE, patient=patient)
                phone = orm.Telephone(number=patient.cellphone, type="MO", patient=patient)
                phone.changed_by_id = self.find_changed_by(orm, patient, patient.cellphone)
                phone.save()

        # For the first historical patient entry...
        hist_pat_objects = orm.HistoricalPatient.objects.order_by('history_date')

        # Figure out all the ids of patients who have historical phone numbers to migrate
        list = []
        for hist_pat in hist_pat_objects.all():
            if (hist_pat.phone is not None and hist_pat.phone != "") or (hist_pat.cellphone is not None and hist_pat.cellphone != ""):
                if hist_pat.id not in list:
                    list.append(hist_pat.id)

        for pat_id in list:
            cur_hist_pat = hist_pat_objects.filter(id=pat_id).first()

            # If it has a phone, create an entry on the historical telephone table.
            if cur_hist_pat.phone is not None and cur_hist_pat.phone != "":
                self.new_historical_phone(orm, cur_hist_pat, "+")

            # If it has a cellphone, create an entry on the historical telephone table.
            if cur_hist_pat.cellphone is not None and cur_hist_pat.cellphone != "":
                self.new_historical_cellphone(orm, cur_hist_pat, "+")

            # For each entry in the historical patient table, if the phone field is different from the previous entry,
            # add an entry in the historical phone table. Do the same for cellphone.
            for hist_pat in hist_pat_objects.filter(id=pat_id).exclude(history_id=cur_hist_pat.history_id):
                if self.is_different_where_none_equal_empty(hist_pat.phone, cur_hist_pat.phone):
                    if hist_pat.phone is None or hist_pat.phone == "":
                        self.new_historical_phone(orm, hist_pat, "-", cur_hist_pat.phone)
                    elif cur_hist_pat.phone is None or cur_hist_pat.phone == "":
                        self.new_historical_phone(orm, hist_pat, "+")
                    else:
                        self.new_historical_phone(orm, hist_pat, "~")

                if self.is_different_where_none_equal_empty(hist_pat.cellphone, cur_hist_pat.cellphone):
                    if hist_pat.cellphone is None or hist_pat.cellphone == "":
                        self.new_historical_cellphone(orm, hist_pat, "-", cur_hist_pat.cellphone)
                    elif cur_hist_pat.cellphone is None or cur_hist_pat.cellphone == "":
                        self.new_historical_cellphone(orm, hist_pat, "+")
                    else:
                        self.new_historical_cellphone(orm, hist_pat, "~")

                cur_hist_pat = hist_pat


    def check_loss_of_note(self, phone):
        if phone.note is not None and phone.note != "":
            print "Note \"" + phone.note + "\" about phone number \"" + phone.number + \
                  "\" from patient \"" + phone.patient.name + "\" will be lost."


    def move_from_patient_to_telephone(self, phone):
        if phone.type == "MO":
            # Phone will always be stored in the patient.cellphone field, moving or not what is in there to the phone
            # field.

            if phone.patient.phone is None or phone.patient.phone == "":
                phone.patient.phone = phone.patient.cellphone
            else:
                if phone.patient.cellphone is not None and phone.patient.cellphone != "":
                    print "Phone \"" + phone.patient.cellphone + "\" from patient " + phone.patient.name + " will be lost."

            phone.patient.cellphone = phone.number
            phone.patient.save()
            self.check_loss_of_note(phone)
        elif phone.type == "MA":
            # Phone will always be stored in the patient.phone field, moving or not what is in there to the cellphone
            # field.

            if phone.patient.cellphone is None or phone.patient.cellphone == "":
                phone.patient.cellphone = phone.patient.phone
            else:
                if phone.patient.phone is not None and phone.patient.phone != "":
                    print "Phone \"" + phone.patient.phone + "\" from patient " + phone.patient.name + " will be lost."

            phone.patient.phone = phone.number
            phone.patient.save()
            self.check_loss_of_note(phone)
        else:
            # We try to store phone in the patient.phone field first. If not empty, we try to store it in the cellphone
            # field. If not empty, we discard it.

            if phone.patient.phone is None or phone.patient.phone == "":
                phone.patient.phone = phone.number
                phone.patient.save()
                self.check_loss_of_note(phone)
            elif phone.patient.cellphone is None or phone.patient.cellphone == "":
                phone.patient.cellphone = phone.number
                phone.patient.save()
                self.check_loss_of_note(phone)
            else:
                print "Phone \"" + phone.number + " (" + phone.type + ") - " + phone.note + "\" from patient " +\
                      phone.patient.name + " will be lost."


    # There would never be entry on the same time, because the telephone is saved some miliseconds after the patient is
    # saved. However, when migrating forward, the entry is kept in the historical patient table. Thus, when migrating
    # backwards, this entry will be found.
    def if_no_patient_history_entry_same_time_create(self, orm, hist_pho):
        if (orm.HistoricalPatient.objects.filter(id=hist_pho.patient_id, history_date=hist_pho.history_date).count() == 0):
            src = orm.HistoricalPatient.objects.filter(id=hist_pho.patient_id,
                                                       history_date__lt=hist_pho.history_date).order_by(
                'history_date').last()
            hist_pat = orm.HistoricalPatient()
            hist_pat.id = src.id
            hist_pat.cpf = src.cpf
            hist_pat.rg = src.rg
            hist_pat.name = src.name
            hist_pat.medical_record = src.medical_record
            hist_pat.natural_of = src.natural_of
            hist_pat.citizenship = src.citizenship
            hist_pat.street = src.street
            hist_pat.address_number = src.address_number
            hist_pat.district = src.district
            hist_pat.address_complement = src.address_complement
            hist_pat.zipcode = src.zipcode
            hist_pat.country = src.country
            hist_pat.state = src.state
            hist_pat.city = src.city
            hist_pat.email = src.email
            hist_pat.date_birth = src.date_birth
            hist_pat.gender_id = src.gender_id
            hist_pat.marital_status_id = src.marital_status_id
            hist_pat.removed = src.removed
            hist_pat.changed_by_id = src.changed_by_id
            hist_pat.email = src.email

            hist_pat.history_date = hist_pho.history_date
            hist_pat.history_user_id = hist_pho.history_user_id
            hist_pat.history_type = "~" # It doesn't matter the type of change the historical telephone has.

            if hist_pho.type == "MO":
                hist_pat.cellphone = hist_pho.number
            else:
                hist_pat.phone = hist_pho.number

            hist_pat.save()


    def update_hitorical_patient_entries_in_an_interval(self, orm, hist_pho, end_time):
        for hist_pat in orm.HistoricalPatient.objects.filter(id=hist_pho.patient_id,
                                                             history_date__gte=hist_pho.history_date,
                                                             history_date__lt=end_time):
            if hist_pho.type == "MO":
                if hist_pho.history_type == "-":
                    hist_pat.cellphone = None
                else:
                    hist_pat.cellphone = hist_pho.number
            else:
                if hist_pho.history_type == "-":
                    hist_pat.phone = None
                else:
                    hist_pat.phone = hist_pho.number

            hist_pat.save()


    def migrate_historical_phone(self, orm, pat_id, type=None):
        if type is None:
            hist_pho_objects = orm.HistoricalTelephone.objects.filter(patient_id=pat_id).order_by('-history_date').exclude(type="MO")
        else:
            hist_pho_objects = orm.HistoricalTelephone.objects.filter(patient_id=pat_id).order_by('-history_date').filter(type=type)
        cur_hist_pho = hist_pho_objects.first()

        if cur_hist_pho is not None:
            # If there is no patient history entry that occurred on the same moment of the current phone history entry,
            # create one and copy data from the first patient history entry that occurred before this moment.
            self.if_no_patient_history_entry_same_time_create(orm, cur_hist_pho)

            # For this and all subsequent changes in this patient (that occurred after the last change in phone), update
            # the phone.
            self.update_hitorical_patient_entries_in_an_interval(orm, cur_hist_pho, datetime.datetime.now())

            # For all the remaining phone history entries...
            for hist_pho in hist_pho_objects.exclude(history_id=cur_hist_pho.history_id):
                # If there is no patient history entry that occurred on the same moment of the hist_pho,
                # create one and copy data from the first patient history entry that occurred before this moment.
                self.if_no_patient_history_entry_same_time_create(orm, hist_pho)

                # Update the phone field of all the historical patient entries that occurred after the update of
                # hist_pho and before the update of cur_hist_pho.
                self.update_hitorical_patient_entries_in_an_interval(orm, hist_pho, cur_hist_pho.history_date)

                cur_hist_pho = hist_pho


    def backwards(self, orm):
        for phone in orm.Telephone.objects.all():
            self.move_from_patient_to_telephone(phone)

        # Figure out all the ids of patients who have historical phone numbers to migrate
        list = []
        for hist_pho in orm.HistoricalTelephone.objects.order_by('history_date').all():
            if hist_pho.patient_id not in list:
                list.append(hist_pho.patient_id)

        for pat_id in list:
            self.migrate_historical_phone(orm, pat_id, "MO")
            self.migrate_historical_phone(orm, pat_id)


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'patient.alcoholfrequency': {
            'Meta': {'object_name': 'AlcoholFrequency'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'patient.alcoholperiod': {
            'Meta': {'object_name': 'AlcoholPeriod'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.amountcigarettes': {
            'Meta': {'object_name': 'AmountCigarettes'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.classificationofdiseases': {
            'Meta': {'object_name': 'ClassificationOfDiseases'},
            'abbreviated_description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'children'", 'null': 'True', 'to': u"orm['patient.ClassificationOfDiseases']"})
        },
        u'patient.complementaryexam': {
            'Meta': {'object_name': 'ComplementaryExam'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'diagnosis': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Diagnosis']"}),
            'doctor': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'doctor_register': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'exam_site': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'patient.diagnosis': {
            'Meta': {'unique_together': "((u'medical_record_data', u'classification_of_diseases'),)", 'object_name': 'Diagnosis'},
            'classification_of_diseases': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.ClassificationOfDiseases']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medical_record_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.MedicalRecordData']"})
        },
        u'patient.examfile': {
            'Meta': {'object_name': 'ExamFile'},
            'content': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.ComplementaryExam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'patient.fleshtone': {
            'Meta': {'object_name': 'FleshTone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.gender': {
            'Meta': {'object_name': 'Gender'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.historicalpatient': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalPatient'},
            'address_complement': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'address_number': ('django.db.models.fields.IntegerField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'cellphone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'changed_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'citizenship': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'date_birth': ('django.db.models.fields.DateField', [], {}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'gender_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'marital_status_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'medical_record': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'natural_of': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'})
        },
        u'patient.historicalsocialdemographicdata': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalSocialDemographicData'},
            'automobile': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bath': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'benefit_government': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'dvd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flesh_tone_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'freezer': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'house_maid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'patient_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'payment_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'radio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'refrigerator': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'religion_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'schooling_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'social_class': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'tv': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'wash_machine': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'patient.historicalsocialhistorydata': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalSocialHistoryData'},
            'alcohol_frequency_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'alcohol_period_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'alcoholic': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'amount_cigarettes_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'changed_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'drugs': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'ex_smoker': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'patient_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'smoker': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        u'patient.historicaltelephone': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalTelephone'},
            'changed_by_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'patient_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        u'patient.maritalstatus': {
            'Meta': {'object_name': 'MaritalStatus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.medicalrecorddata': {
            'Meta': {'object_name': 'MedicalRecordData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Patient']"}),
            'record_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'record_responsible': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'patient.patient': {
            'Meta': {'object_name': 'Patient'},
            'address_complement': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'address_number': ('django.db.models.fields.IntegerField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'cellphone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'citizenship': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '15', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'date_birth': ('django.db.models.fields.DateField', [], {}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Gender']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marital_status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.MaritalStatus']", 'null': 'True', 'blank': 'True'}),
            'medical_record': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'natural_of': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'})
        },
        u'patient.payment': {
            'Meta': {'object_name': 'Payment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.religion': {
            'Meta': {'object_name': 'Religion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.schooling': {
            'Meta': {'object_name': 'Schooling'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'patient.socialdemographicdata': {
            'Meta': {'object_name': 'SocialDemographicData'},
            'automobile': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bath': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'benefit_government': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'dvd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'flesh_tone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.FleshTone']", 'null': 'True', 'blank': 'True'}),
            'freezer': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'house_maid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Patient']"}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Payment']", 'null': 'True', 'blank': 'True'}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'radio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'refrigerator': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'religion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Religion']", 'null': 'True', 'blank': 'True'}),
            'schooling': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Schooling']", 'null': 'True', 'blank': 'True'}),
            'social_class': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'tv': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'wash_machine': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'patient.socialhistorydata': {
            'Meta': {'object_name': 'SocialHistoryData'},
            'alcohol_frequency': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['patient.AlcoholFrequency']", 'null': 'True', 'blank': 'True'}),
            'alcohol_period': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['patient.AlcoholPeriod']", 'null': 'True', 'blank': 'True'}),
            'alcoholic': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'amount_cigarettes': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['patient.AmountCigarettes']", 'null': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'drugs': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'ex_smoker': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Patient']"}),
            'smoker': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        u'patient.telephone': {
            'Meta': {'object_name': 'Telephone'},
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['patient.Patient']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        }
    }

    complete_apps = ['patient']
    symmetrical = True
