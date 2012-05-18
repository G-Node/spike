# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Evaluation'
        db.create_table('evaluations_evaluation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('algorithm', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='evaluation owner', blank=True, to=orm['auth.User'])),
            ('user_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('original_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dfiles.Version'])),
            ('publication_state', self.gf('django.db.models.fields.IntegerField')()),
            ('processing_state', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('evaluation_task_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('evaluation_log', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], blank=True)),
        ))
        db.send_create_signal('evaluations', ['Evaluation'])

        # Adding model 'EvaluationResults'
        db.create_table('evaluations_evaluationresults', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('evaluation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['evaluations.Evaluation'])),
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
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('evaluations', ['EvaluationResults'])

        # Adding model 'EvaluationResultsImg'
        db.create_table('evaluations_evaluationresultsimg', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('evaluation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['evaluations.Evaluation'])),
            ('img_data', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('img_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('evaluations', ['EvaluationResultsImg'])


    def backwards(self, orm):
        
        # Deleting model 'Evaluation'
        db.delete_table('evaluations_evaluation')

        # Deleting model 'EvaluationResults'
        db.delete_table('evaluations_evaluationresults')

        # Deleting model 'EvaluationResultsImg'
        db.delete_table('evaluations_evaluationresultsimg')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'benchmarks.benchmark': {
            'Meta': {'object_name': 'Benchmark'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'benchmark owner'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'parameter_desc': ('django.db.models.fields.CharField', [], {'default': "'Order'", 'max_length': '255'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'benchmarks.record': {
            'Meta': {'object_name': 'Record'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'blank': 'True'}),
            'benchmark': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmarks.Benchmark']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'parameter_value': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dfiles.datafile': {
            'Meta': {'object_name': 'Datafile'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'filetype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmarks.Record']", 'blank': 'True'})
        },
        'dfiles.version': {
            'Meta': {'object_name': 'Version'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'blank': 'True'}),
            'datafile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dfiles.Datafile']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raw_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'validation_log': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'validation_state': ('django.db.models.fields.CharField', [], {'default': "'I'", 'max_length': '1'}),
            'validation_task_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        },
        'evaluations.evaluation': {
            'Meta': {'object_name': 'Evaluation'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'blank': 'True'}),
            'algorithm': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'evaluation_log': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'evaluation_task_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dfiles.Version']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'evaluation owner'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'processing_state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'publication_state': ('django.db.models.fields.IntegerField', [], {}),
            'user_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'evaluations.evaluationresults': {
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
            'evaluation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['evaluations.Evaluation']"}),
            'found_unit': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'gt_unit': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'evaluations.evaluationresultsimg': {
            'Meta': {'object_name': 'EvaluationResultsImg'},
            'evaluation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['evaluations.Evaluation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_data': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'img_type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['evaluations']
