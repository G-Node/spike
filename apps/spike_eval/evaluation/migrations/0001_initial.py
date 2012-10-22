# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'Algorithm'
        db.create_table('evaluation_algorithm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('added_by',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['evaluation.Algorithm'], null=True,
                blank=True)),
            ))
        db.send_create_signal('evaluation', ['Algorithm'])

        # Adding model 'EvaluationBatch'
        db.create_table('evaluation_evaluationbatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('added_by',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('access', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('algorithm',
             self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['evaluation.Algorithm'])),
            ('benchmark', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['benchmark.Benchmark'])),
            ))
        db.send_create_signal('evaluation', ['EvaluationBatch'])

        # Adding model 'Evaluation'
        db.create_table('evaluation_evaluation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('added_by',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('task_state', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('task_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('task_log', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('evaluation_batch',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['evaluation.EvaluationBatch'])),
            ('trial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['benchmark.Trial'])),
            ))
        db.send_create_signal('evaluation', ['Evaluation'])

        # Adding model 'EvaluationResults'
        db.create_table('evaluation_evaluationresults', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('evaluation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['evaluation.Evaluation'])),
            ('gt_unit', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('found_unit', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('KS', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('KSO', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('FS', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('TP', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('TPO', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('FPA', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('FPAE', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('FPAO', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('FPAOE', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('FN', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('FNO', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('FP', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ))
        db.send_create_signal('evaluation', ['EvaluationResults'])

        # Adding model 'EvaluationResultsImg'
        db.create_table('evaluation_evaluationresultsimg', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('evaluation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['evaluation.Evaluation'])),
            ('img_data', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('img_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ))
        db.send_create_signal('evaluation', ['EvaluationResultsImg'])


    def backwards(self, orm):
        # Deleting model 'Algorithm'
        db.delete_table('evaluation_algorithm')

        # Deleting model 'EvaluationBatch'
        db.delete_table('evaluation_evaluationbatch')

        # Deleting model 'Evaluation'
        db.delete_table('evaluation_evaluation')

        # Deleting model 'EvaluationResults'
        db.delete_table('evaluation_evaluationresults')

        # Deleting model 'EvaluationResultsImg'
        db.delete_table('evaluation_evaluationresultsimg')


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
            'img_data': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
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
