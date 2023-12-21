from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
from voting.models import Voting, Question, QuestionOption

class CensusTestCase(StaticLiveServerTestCase):

    def setUp(self):
        #Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()
	
        #Opciones de Chrome
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
        self.voting = Voting.objects.create(
            name='Test Voting',
            question=self.question
        )
        self.voting.save()
        User.objects.create_superuser('admin_census', 'admin@example.com', 'qwerty')
        # Inicio de sesión como admin
        self.driver.get(f'{self.live_server_url}/admin/')
        #Busca los elementos y “escribe”
        self.driver.find_element(By.ID,'id_username').send_keys("admin_census")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        
        #Verifica que nos hemos logado porque aparece la barra de herramientas superior
        self.assertTrue(len(self.driver.find_elements(By.ID, 'user-tools'))==1)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def test_add_new_voters(self):      
       #Abre la ruta del navegador             
       self.driver.get(f'{self.live_server_url}/census/create')
       #Busca los elementos y “escribe”
       self.driver.find_element(By.ID,'v').find_elements(By.TAG_NAME, 'option')[0].click()
       self.driver.find_element(By.ID,'u').find_elements(By.TAG_NAME, 'option')[0].click()
       self.driver.find_element(By.TAG_NAME, 'button').click()
       
       #Verifica que el censo se ha creado
       self.driver.get(f'{self.live_server_url}/census/list/')
       self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME, 'card-title')) > 0)
        
    def test_export_census_csv(self):
        #Abre la ruta del navegador             
        self.driver.get(f'{self.live_server_url}/census/create')
        #Busca los elementos y “escribe”
        self.driver.find_element(By.ID,'v').find_elements(By.TAG_NAME, 'option')[0].click()
        self.driver.find_element(By.ID,'u').find_elements(By.TAG_NAME, 'option')[0].click()
        self.driver.find_element(By.TAG_NAME, 'button').click()
       
        self.driver.get(f'{self.live_server_url}/census/list/')       
        # response = self.driver.find_element(By.LINK_TEXT, 'Exportar').click()
        response = self.client.get('/census/export/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="census.csv"')
        

