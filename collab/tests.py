from collab.models import Project
from django.test import TestCase
import json
DATA ={

    'titre': 'testchantier123', 'date_archivage': 'April 2, 2019', 'description': 'test123', 'date_suppression': '', 'test': '', 'csrfmiddlewaretoken': 'e', 'status': '0', 'feature': 'chantier'
}

# Create your tests here.

class DataMixin(object):

    def create_project(self):
        return Project.objects.create(title='projtest', description='test')


# @test_settings
class TestFeature(DataMixin, TestCase):

    def setUp(self):
        project = self.create_project()

    def test_get_feature(self):

        project = Project.objects.get(title='projtest')
        response = self.client.get('/projet/'+project.slug+'/ajout/')
        # feature est  bien cree
        self.assertEqual(response.status_code, 200)

    def test_post_feature(self):

        project = Project.objects.get(title='projtest')
        response = self.client.post('/projet/'+project.slug+'/ajout/', {'data': json.dumps(DATA)})
        # feature est  bien cree
        self.assertEqual(response.status_code, 200)
