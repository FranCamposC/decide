from selenium.webdriver.support.ui import Select
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User

class QuestionTestCase(StaticLiveServerTestCase):

    def setUp(self):
        #Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()
        User.objects.create_superuser('admin1', 'admin@example.com', 'qwerty')
	
        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def test_Error_Creacion_Questión_Normal(self):      
       #Abre la ruta del navegador             
        self.driver.get(f'{self.live_server_url}/admin/')
       #Busca los elementos y “escribe”
        self.driver.find_element(By.ID,'id_username').send_keys("admin1")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        #ve a crear question

        self.driver.get(f'{self.live_server_url}/admin/voting/question/add/')
        #rellenar con datos 
        
        self.driver.find_element(By.ID,'id_desc').send_keys("desc test")

        submit_button = self.driver.find_element(By.CLASS_NAME,"default")
        submit_button.click()
        wait = WebDriverWait(self.driver, 5)
        error_list = self.driver.find_element(By.CLASS_NAME, 'errorlist')
        error_message = error_list.find_element(By.TAG_NAME, 'li').text
        error_text = error_message
        assert error_text == "Las preguntas de tipo normal deben tener al menos 2 opciones."

    def test_Creacion_Questión_Si_No(self):      
       #Abre la ruta del navegador             
        self.driver.get(f'{self.live_server_url}/admin/')
       #Busca los elementos y “escribe”
        self.driver.find_element(By.ID,'id_username').send_keys("admin1")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        #ve a crear question

        self.driver.get(f'{self.live_server_url}/admin/voting/question/add/')
        #rellenar con datos 
        
        self.driver.find_element(By.ID,'id_desc').send_keys("desc test")
        select_element=self.driver.find_element(By.ID,'id_type')
        select = Select(select_element)
        select.select_by_visible_text("Si_No")

        submit_button = self.driver.find_element(By.CLASS_NAME,"default")
        submit_button.click()
        wait = WebDriverWait(self.driver, 5)
        success_message_element = self.driver.find_element(By.CLASS_NAME, 'success').text
        assert success_message_element == "El question “desc test” fue agregado correctamente."

    def test_Error_Creacion_Questión_Si_No(self):      
       #Abre la ruta del navegador             
        self.driver.get(f'{self.live_server_url}/admin/')
       #Busca los elementos y “escribe”
        self.driver.find_element(By.ID,'id_username').send_keys("admin1")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        #ve a crear question
        self.driver.get(f'{self.live_server_url}/admin/voting/question/add/')
        #rellenar con datos 
        self.driver.find_element(By.ID,'id_desc').send_keys("desc test")
        select_element=self.driver.find_element(By.ID,'id_type')
        select = Select(select_element)
        select.select_by_visible_text("Si_No")
        self.driver.find_element(By.ID,'id_options-0-option').send_keys("opt")

        submit_button = self.driver.find_element(By.CLASS_NAME,"default")
        submit_button.click()

        wait = WebDriverWait(self.driver, 5)
        error_list = self.driver.find_element(By.CLASS_NAME, 'errorlist')
        error_message = error_list.find_element(By.TAG_NAME, 'li').text
        error_text = error_message
        assert error_text == 'Para preguntas de tipo binario, solo se permiten las opciones "Sí" y "No".'

    def test_Error_Creacion_Questión_Ranking(self):      
       #Abre la ruta del navegador             
        self.driver.get(f'{self.live_server_url}/admin/')
       #Busca los elementos y “escribe”
        self.driver.find_element(By.ID,'id_username').send_keys("admin1")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        #ve a crear question
        self.driver.get(f'{self.live_server_url}/admin/voting/question/add/')
        #rellenar con datos 
        self.driver.find_element(By.ID,'id_desc').send_keys("desc test")
        select_element=self.driver.find_element(By.ID,'id_type')
        select = Select(select_element)
        select.select_by_visible_text("Ranking")
        self.driver.find_element(By.ID,'id_options-0-option').send_keys("opt")

        submit_button = self.driver.find_element(By.CLASS_NAME,"default")
        submit_button.click()

        wait = WebDriverWait(self.driver, 5)
        error_list = self.driver.find_element(By.CLASS_NAME, 'errorlist')
        error_message = error_list.find_element(By.TAG_NAME, 'li').text
        error_text = error_message
        assert error_text == 'Las preguntas de tipo ranking deben tener al menos 3 opciones.'


    def test_Creacion_Questión_Normal(self):      
        #Abre la ruta del navegador             
        self.driver.get(f'{self.live_server_url}/admin/')
        #Busca los elementos y “escribe”
        self.driver.find_element(By.ID,'id_username').send_keys("admin1")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        #ve a crear question
        self.driver.get(f'{self.live_server_url}/admin/voting/question/add/')
        #rellenar con datos 
        self.driver.find_element(By.ID,'id_desc').send_keys("desc test")
        select_element=self.driver.find_element(By.ID,'id_type')
        select = Select(select_element)
        select.select_by_visible_text("Normal")
        self.driver.find_element(By.ID,'id_options-0-option').send_keys("opt0")
        self.driver.find_element(By.ID,'id_options-1-option').send_keys("opt1")

        submit_button = self.driver.find_element(By.CLASS_NAME,"default")
        submit_button.click()

        wait = WebDriverWait(self.driver, 5)
        success_message_element = self.driver.find_element(By.CLASS_NAME, 'success').text
        assert success_message_element == "El question “desc test” fue agregado correctamente."

    def test_Creacion_Questión_Ranking(self):      
        #Abre la ruta del navegador             
        self.driver.get(f'{self.live_server_url}/admin/')
        #Busca los elementos y “escribe”
        self.driver.find_element(By.ID,'id_username').send_keys("admin1")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        #ve a crear question
        self.driver.get(f'{self.live_server_url}/admin/voting/question/add/')
        #rellenar con datos 
        self.driver.find_element(By.ID,'id_desc').send_keys("desc test")
        select_element=self.driver.find_element(By.ID,'id_type')
        select = Select(select_element)
        select.select_by_visible_text("Ranking")
        self.driver.find_element(By.ID,'id_options-0-option').send_keys("opt0")
        self.driver.find_element(By.ID,'id_options-1-option').send_keys("opt1")
        self.driver.find_element(By.ID,'id_options-2-option').send_keys("opt2")

        submit_button = self.driver.find_element(By.CLASS_NAME,"default")
        submit_button.click()

        wait = WebDriverWait(self.driver, 5)
        success_message_element = self.driver.find_element(By.CLASS_NAME, 'success').text
        assert success_message_element == "El question “desc test” fue agregado correctamente."

