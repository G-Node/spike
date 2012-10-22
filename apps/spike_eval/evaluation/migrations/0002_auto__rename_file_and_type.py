# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Deleting field 'EvaluationResultsImg.img_data'
        db.rename_column('evaluation_evaluationresultsimg', 'img_data', 'file')

        # Deleting field 'EvaluationResultsImg.img_type'
        db.rename_column('evaluation_evaluationresultsimg', 'img_type', 'file_type')


    def backwards(self, orm):
        # Deleting field 'EvaluationResultsImg.file'
        db.rename_column('evaluation_evaluationresultsimg', 'file', 'img_data')

        # Deleting field 'EvaluationResultsImg.file_type'
        db.rename_column('evaluation_evaluationresultsimg', 'file_type', 'img_type')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [],
                            {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')",
                     'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': (
                'django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                       {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [],
                                 {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'benchmark.benchmark': {
            'Meta': {'object_name': 'Benchmark'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [],
                         {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gt_access': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [],
                      {'related_name': "'benchmark owner'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'parameter': ('django.db.models.fields.CharField', [], {'default': "'ID'", 'max_length': '255'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '10'})
        },
        'benchmark.trial': {
            'Meta': {'object_name': 'Trial'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [],
                         {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'benchmark': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark.Benchmark']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parameter': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'evaluation.algorithm': {
            'Meta': {'object_name': 'Algorithm'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [],
                         {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [],
                       {'to': "orm['evaluation.Algorithm']", 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        'evaluation.evaluation': {
            'Meta': {'object_name': 'Evaluation'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [],
                         {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'evaluation_batch': (
                'django.db.models.fields.related.ForeignKey', [], {'to': "orm['evaluation.EvaluationBatch']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'task_log': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'task_state': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'trial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark.Trial']"})
        },
        'evaluation.evaluationbatch': {
            'Meta': {'object_name': 'EvaluationBatch'},
            'access': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'added_by': ('django.db.models.fields.related.ForeignKey', [],
                         {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'algorithm': (
                'django.db.models.fields.related.ForeignKey', [],
                {'default': '1', 'to': "orm['evaluation.Algorithm']"}),
            'benchmark': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark.Benchmark']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'evaluation.evaluationresults': {
            'FN': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'FNO': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'FP': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'FPA': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'FPAE': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'FPAO': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'FPAOE': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'FS': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'KS': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'KSO': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'Meta': {'object_name': 'EvaluationResults'},
            'TP': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'TPO': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'evaluation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['evaluation.Evaluation']"}),
            'found_unit': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'gt_unit': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'evaluation.evaluationresultsimg': {
            'Meta': {'object_name': 'EvaluationResultsImg'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'evaluation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['evaluation.Evaluation']"}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [],
                             {'related_name': "'taggit_taggeditem_tagged_items'",
                              'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [],
                    {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['evaluation']
