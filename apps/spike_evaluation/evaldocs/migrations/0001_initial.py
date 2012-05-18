# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Topic'
        db.create_table('evaldocs_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('evaldocs', ['Topic'])

        # Adding model 'Article'
        db.create_table('evaldocs_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['evaldocs.Topic'])),
        ))
        db.send_create_signal('evaldocs', ['Article'])

        # Adding model 'Section'
        db.create_table('evaldocs_section', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sort', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['evaldocs.Article'])),
        ))
        db.send_create_signal('evaldocs', ['Section'])


    def backwards(self, orm):
        
        # Deleting model 'Topic'
        db.delete_table('evaldocs_topic')

        # Deleting model 'Article'
        db.delete_table('evaldocs_article')

        # Deleting model 'Section'
        db.delete_table('evaldocs_section')


    models = {
        'evaldocs.article': {
            'Meta': {'object_name': 'Article'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['evaldocs.Topic']"})
        },
        'evaldocs.section': {
            'Meta': {'object_name': 'Section'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['evaldocs.Article']"}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'evaldocs.topic': {
            'Meta': {'object_name': 'Topic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['evaldocs']
