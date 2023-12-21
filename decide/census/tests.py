import csv
import random
import io
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from .models import Census
from voting.models import Question, Voting
from base import mods
from base.tests import BaseTestCase
from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse
from voting.models import Voting, Question, QuestionOption

class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

        self.question = Question.objects.create(desc='Test Question')
        self.question.save()
        self.option1 = QuestionOption.objects.create(
            question=self.question,
            number=1,
            option='Option 1'
        )
        self.option1.save()
        self.option2 = QuestionOption.objects.create(
            question=self.question,
            number=2,
            option='Option 2'
        )
        self.option2.save()
        self.voting = Voting.objects.create(
            name='Test Voting',
            question=self.question
        )
        self.voting.save()
        self.user1 = User.objects.create(
            username='User 1'
        )
        self.user1.save()
        self.user2 = User.objects.create(
            username='User 2'
        )
        self.user2.save()
        self.user3 = User.objects.create(
            username='User 3'
        )
        self.user3.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [1]})

    def test_add_new_voters_conflict(self):
        data = {'voting_id': 1, 'voters': [1]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)

    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())

    def test_list_census(self):
        Census.delete(Census.objects.all().first())
        voters = [self.user1.id, self.user2.id, self.user3.id]
        for v in voters:
            census = Census.objects.create(voting_id=self.voting.id,voter_id=v)
            census.save()
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        url = reverse('census_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_census_unauthorised(self):
        Census.delete(Census.objects.all().first())
        voters = [self.user1.id, self.user2.id, self.user3.id]
        for v in voters:
            census = Census.objects.create(voting_id=self.voting.id,voter_id=v)
            census.save()
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        url = reverse('census_list')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_create_census(self):
        voters = [1, 2, 3]
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        response = self.client.post(reverse('create_census'), {'v': self.voting.id, 'u': voters})
        for voter in voters:
            census = Census.objects.filter(voting_id=self.voting.id, voter_id=voter).first()
            self.assertIsNotNone(census)

    def test_create_census_unauthorised(self):
        voters = [1, 2, 3]
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        response = self.client.post(reverse('create_census'), {'v': self.voting.id, 'u': voters})
        for voter in voters:
            census = Census.objects.filter(voting_id=self.voting.id, voter_id=voter).first()
            self.assertIsNone(census)

    def test_delete_census(self):
        voters = [1, 2, 3]
        for v in voters:
            census = Census.objects.create(voting_id=self.voting.id,voter_id=v)
            census.save()
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        url = reverse('delete_census', args=[self.voting.id])
        response = self.client.delete(url)
        for voter in voters:
            census = Census.objects.filter(voting_id=self.voting.id, voter_id=voter).first()
            self.assertIsNone(census)
    
    def test_delete_unauthorised(self):
        voters = [1, 2, 3]
        for v in voters:
            census = Census.objects.create(voting_id=self.voting.id,voter_id=v)
            census.save()
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        url = reverse('delete_census', args=[self.voting.id])
        response = self.client.delete(url)
        for voter in voters:
            census = Census.objects.filter(voting_id=self.voting.id, voter_id=voter).first()
            self.assertIsNotNone(census)

    def test_edit_census(self):
        voters = [self.user1.id, self.user3.id]
        newVoters = [self.user1.id, self.user2.id]
        for v in voters:
            census = Census.objects.create(voting_id=self.voting.id,voter_id=v)
            census.save()
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        url = reverse('edit_census', args=[self.voting.id])
        response = self.client.post(url, {'u': newVoters})
        for voter in newVoters:
            census = Census.objects.filter(voting_id=self.voting.id, voter_id=voter).first()
            self.assertIsNotNone(census)
        self.assertIsNone(Census.objects.filter(voting_id=self.voting.id, voter_id=self.user3.id).first())

    def test_edit_census_unauthorised(self):
        voters = [self.user1.id, self.user3.id]
        newVoters = [self.user1.id, self.user2.id]
        for v in voters:
            census = Census.objects.create(voting_id=self.voting.id,voter_id=v)
            census.save()
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        url = reverse('edit_census', args=[self.voting.id])
        response = self.client.post(url, {'u': newVoters})
        for voter in voters:
            census = Census.objects.filter(voting_id=self.voting.id, voter_id=voter).first()
            self.assertIsNotNone(census)
        self.assertIsNone(Census.objects.filter(voting_id=self.voting.id, voter_id=self.user2.id).first())

class CensusTest(StaticLiveServerTestCase):
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def createCensusSuccess(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys(now.strftime("%m%d%M%S"))
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys(now.strftime("%m%d%M%S"))
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/census/census")

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/census/census/add")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/census/census/add")

    def createCensusValueError(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys('64654654654654')
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys('64654654654654')
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/census/census/add")

class CensusExportTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.census = Census(voting_id = 1, voter_id = 1)
        self.census.save()
        q = Question(desc='none')
        q.save()
        self.voting = Voting(name = "Test", question = q)
        self.voting.save()
    def tearDown(self):
        super().tearDown()
        self.census = None
        self.voting = None
    def test_export_census_csv(self):
        response = self.client.get('/census/export/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="census.csv"')
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        self.assertEqual(body[0], ['voting_id', 'voter_id'])
        self.assertEqual(body[1], ['1', '1'])
    def test_export_census_csv_no_census(self):
        response = self.client.get('/census/export/143')
        content = response.content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content))
        body = list(csv_reader)
        self.assertEqual(body[0], ['voting_id', 'voter_id'])
        self.assertEqual(len(body), 1, "The body should be empty")
    def test_export_census_csv_invalid_voting_id(self):
        response = self.client.get('/census/export/abc')
        self.assertEqual(response.status_code, 404)


class Test_Prueba(BasicTestCase):
    def test_Prueb(self):
        self.assertTrue(True)
