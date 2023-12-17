import random
import itertools
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption, VotingOption
from datetime import datetime

class VotingModelTestCase(BaseTestCase):
    def setUp(self):
        q = Question(desc='Descripcion')
        q.save()
        
        opt1 = QuestionOption(question=q, option='opcion 1')
        opt1.save()
        opt1 = QuestionOption(question=q, option='opcion 2')
        opt1.save()

        self.v = Voting(name='Votacion', question=q)
        self.v.save()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v = None

    def testExist(self):
        v=Voting.objects.get(name='Votacion')
        self.assertEquals(v.question.options.all()[0].option, "opcion 1")

class VotingTestCase(BaseTestCase):
    def test_create_voting_API(self):
        self.login()
        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

        voting = Voting.objects.get(name='Example')
        self.assertEqual(voting.desc, 'Description example')

    def test_update_voting_405(self):
        v = self.create_voting()
        data = {} #El campo action es requerido en la request
        self.login()
        response = self.client.post('/voting/{}/'.format(v.pk), data, format= 'json')
        self.assertEquals(response.status_code, 405) 
      
    def test_to_string(self):
        #Crea un objeto votacion
        v = self.create_voting()
        #Verifica que el nombre de la votacion es test voting
        self.assertEquals(str(v),"test voting")
        #Verifica que la descripcion de la pregunta sea test question
        self.assertEquals(str(v.question),"test question")
        #Verifica que la primera opcion es option1 (2)
        self.assertEquals(str(v.question.options.all()[0]),"option 1 (2)")

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        #response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        #self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')

class LogInSuccessTests(StaticLiveServerTestCase):

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

    def successLogIn(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/")

class LogInErrorTests(StaticLiveServerTestCase):

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

    def usernameWrongLogIn(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/p').text == 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')

    def passwordWrongLogIn(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("wrongPassword")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/p').text == 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')

class QuestionsTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

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

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_list_questions(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        url = reverse('questionList')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_question_unauthorised(self):
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        url = reverse('questionList')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_create_question(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        response = self.client.post("/voting/question/create/3",{'desc': "descripcion", 'ans_0': "opcion1",'ans_1': "opcion2",'ans_2': "opcion3"})
        question = Question.objects.filter(desc="descripcion").first()
        self.assertIsNotNone(question)

    def test_create_question_unauthorised(self):
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        response = self.client.post("/voting/question/create/3",{'desc': "descripcion", 'ans_0': "opcion1",'ans_1': "opcion2",'ans_2': "opcion3"})
        question = Question.objects.filter(desc="descripcion").first()
        self.assertIsNone(question)
    
    def test_delete_question(self):
        
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        url = reverse('delete', args=[self.question.id])
        response = self.client.delete(url)
        question = Question.objects.filter(pk=self.question.id).first()
        self.assertIsNone(question)

    def test_delete_unauthorised(self):

        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        url = reverse('delete', args=[self.question.id])
        response = self.client.delete(url)
        question = Question.objects.filter(pk=self.question.id).first()
        self.assertIsNotNone(question)

    def test_edit_question(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        response = self.client.post("/voting/question/edit/"+str(self.question.id),{'desc': "descripcion", 'ans_0': "opcion1",'ans_1': "opcion2"})
        question= Question.objects.filter(pk=self.question.id).first()
        self.assertEqual(question.desc,"descripcion")

    def test_edit_question_unauthorised(self):
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        response = self.client.post("/voting/question/edit/"+str(self.question.id),{'desc': "descripcion", 'ans_0': "opcion1",'ans_1': "opcion2"})
        question= Question.objects.filter(pk=self.question.id).first()
        self.assertNotEqual(question.desc,"descripcion")



    def createQuestionSuccess(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/voting/question/add/")
        
        self.cleaner.find_element(By.ID, "id_desc").click()
        self.cleaner.find_element(By.ID, "id_desc").send_keys('Test')
        self.cleaner.find_element(By.ID, "id_options-0-number").click()
        self.cleaner.find_element(By.ID, "id_options-0-number").send_keys('1')
        self.cleaner.find_element(By.ID, "id_options-0-option").click()
        self.cleaner.find_element(By.ID, "id_options-0-option").send_keys('test1')
        self.cleaner.find_element(By.ID, "id_options-1-number").click()
        self.cleaner.find_element(By.ID, "id_options-1-number").send_keys('2')
        self.cleaner.find_element(By.ID, "id_options-1-option").click()
        self.cleaner.find_element(By.ID, "id_options-1-option").send_keys('test2')
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/voting/question/")

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/voting/question/add/")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/voting/question/add/")

class VotingTests(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.question = Question.objects.create(desc='Test Question')
        self.question.save()
        self.option1 = QuestionOption.objects.create(
            question=self.question,
            option='desc 1'
        )
        self.option1.save()
        self.option2 = QuestionOption.objects.create(
            question=self.question,
            option='desc 2'
        )
        self.option2.save()
        self.voting = Voting.objects.create(
            name='Test Voting',
            question=self.question,
            ranked=False
        )

        self.voting.save()

    def tearDown(self):
        super().tearDown()

    def test_list_voting(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        url = reverse('list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_voting_unauthorised(self):
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        url = reverse('list')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_create_voting(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        response = self.client.post(reverse('votingCreate'),{'name': "nombre", 'desc': "descripcion", 'question': self.question.id})
        voting = Voting.objects.filter(name="nombre").first()
        self.assertIsNotNone(voting)

    def test_create_voting_unauthorised(self):
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        response = self.client.post(reverse('votingCreate'),{'name': "nombre", 'desc': "descripcion", 'question': self.question.id})
        voting = Voting.objects.filter(name="nombre").first()
        self.assertIsNone(voting)

    def test_delete_voting(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        url = reverse('votingDelete', args=[self.voting.id])
        response = self.client.delete(url)
        voting = Voting.objects.filter(pk=self.voting.id).first()
        self.assertIsNone(voting)

    def test_delete_voting_unauthorised(self):

        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        url = reverse('votingDelete', args=[self.voting.id])
        response = self.client.delete(url)
        voting = Voting.objects.filter(pk=self.voting.id).first()
        self.assertIsNotNone(voting)

    def test_edit_voting(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        response = self.client.post("/voting/edit/"+str(self.voting.id),{'name': "nombre", 'desc': "descripcion", 'question': self.question.id})
        voting= Voting.objects.filter(pk=self.voting.id).first()
        self.assertEqual(voting.desc,"descripcion")

    def test_edit_voting_unauthorised(self):
        user = User.objects.get(username='noadmin')
        self.client.force_login(user)
        response = self.client.post("/voting/edit/"+str(self.voting.id),{'name': "nombre", 'desc': "descripcion", 'question': self.question.id})
        voting= Voting.objects.filter(pk=self.voting.id).first()
        self.assertNotEqual(voting.desc,"descripcion")