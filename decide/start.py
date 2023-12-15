import os
import django
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'decide.settings')
django.setup()

from factory import Factory,LazyAttribute
from factory.django import DjangoModelFactory
from faker import Faker
from django.contrib.auth.models import User
from voting.models import Question, QuestionOption, Voting
from base.models import Auth
from django.db import models
from django.conf import settings
import time
from django.db.models import TextField
from census.models import Census

fake = Faker("es_ES")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = LazyAttribute(lambda x: fake.user_name()+str(random.randint(1,100)))
    email = fake.email()
    password = TextField(default="1234")

preguntas_predefinidas=[
    {"question_desc": "¿Cual es tu opinion sobre el cambio climatico?",
     "opciones": [
         {"number": 1, "option": "Muy preocupado/a"},
         {"number": 2, "option": "Preocupado/a"},
         {"number": 3, "option": "Neutral"},
         {"number": 4, "option": "No preocupado/a"}
     ]},

    {"question_desc": "¿Cual es tu opinion sobre el aborto?",
     "opciones": [
         {"number": 1, "option": "A favor"},
         {"number": 2, "option": "En contra"},
         {"number": 3, "option": "Neutral"},
         {"number": 4, "option": "No estoy seguro/a"}
     ]},

    {"question_desc": "¿Cual es tu opinion sobre la legalizacion de la marihuana?",
     "opciones": [
         {"number": 1, "option": "A favor"},
         {"number": 2, "option": "En contra"},
         {"number": 3, "option": "Neutral"},
         {"number": 4, "option": "No estoy seguro/a"}
     ]},

    {"question_desc": "¿Cual es tu opinion sobre la legalizacion de la eutanasia?",
     "opciones": [
         {"number": 1, "option": "A favor"},
         {"number": 2, "option": "En contra"},
         {"number": 3, "option": "Neutral"},
         {"number": 4, "option": "No estoy seguro/a"}
     ]},

    {"question_desc": "¿Cual es tu opinion sobre la legalizacion de la pena de muerte?",
     "opciones": [
         {"number": 1, "option": "A favor"},
         {"number": 2, "option": "En contra"},
         {"number": 3, "option": "Neutral"},
         {"number": 4, "option": "No estoy seguro/a"}
     ]},

    {"question_desc": "¿Cual es tu tipo de comida favorita?",
     "opciones": [
         {"number": 1, "option": "Italiana"},
         {"number": 2, "option": "Mexicana"},
         {"number": 3, "option": "Asiática"},
         {"number": 4, "option": "Mediterránea"}
     ]},

    {"question_desc": "¿Como calificarias tu calidad de sueño?",
     "opciones": [
         {"number": 1, "option": "Excelente, siempre duermo bien."},
         {"number": 2, "option": "Buena, pero a veces tengo dificultades para conciliar el sueño."},
         {"number": 3, "option": "Regular, tengo problemas ocasionales de insomnio."},
         {"number": 4, "option": "Mala, tengo dificultades constantes para dormir."}
     ]},

    {"question_desc": "¿Prefieres la ciudad o el campo para vivir?",
     "opciones": [
         {"number": 1, "option": "Ciudad, me gusta la energía y las opciones que ofrece."},
         {"number": 2, "option": "Campo, prefiero la tranquilidad y la naturaleza."},
         {"number": 3, "option": "Mezcla de ambos, disfruto de lo mejor de ambos mundos."},
         {"number": 4, "option": "No tengo preferencia clara."}
     ]},

    {"question_desc": "¿Cómo manejas el estres en tu vida diaria?",
     "opciones": [
         {"number": 1, "option": "Practico la meditación y la respiración profunda."},
         {"number": 2, "option": "Hago ejercicio regularmente."},
         {"number": 3, "option": "Hablo con amigos o familiares."},
         {"number": 4, "option": "No manejo bien el estrés."}
     ]},

    {"question_desc": "¿Cual es tu destino de viaje soñado?",
     "opciones": [
         {"number": 1, "option": "Playa tropical"},
         {"number": 2, "option": "Montañas"},
         {"number": 3, "option": "Ciudad histórica"},
         {"number": 4, "option": "Aventura en la naturaleza"}
     ]}
]

preguntas=Question.objects.all()
nombres_votaciones=["Votacion 1", "Votacion 2", "Votacion 3", "Votacion 4", "Votacion 5", "Votacion 6", "Votacion 7", "Votacion 8", "Votacion 9", "Votacion 10"]
local_url = getattr(settings, 'BASEURL', '127.0.0.1:8000')
votaciones=Voting.objects.all()
usuarios=User.objects.all()

def cambiar_url_local(url_nueva):
    ruta_archivo_local_settings="./local_settings.py"

    with open(ruta_archivo_local_settings, "r") as archivo:
        lineas=archivo.readlines()
    
    for i,linea in enumerate(lineas):
        if "BASEURL" in linea:
            lineas[i]="BASEURL = '"+url_nueva+"'"
            break
    
    with open(ruta_archivo_local_settings, "w") as archivo:
        archivo.writelines(lineas)


if __name__ == '__main__':
    print("Bienvenido al script de inicio de la aplicación Decide")
    time.sleep(1)
    url=input("¿Es esta la url en la que desea ejecutar la aplicación? "+local_url+" (si/no): ") 
    if url=="no":
        local_url=input("Introduzca la url en la que desea ejecutar la aplicación: ")
        print("Url cambiada a: "+local_url)
        aviso=input("AVISO: Este cambio puede probocar problemas al ejecutar la aplicación. Lo hace bajo su responsabilidad. ¿Desea continuar con el proceso?(si/no): ")
        if aviso=="no":
            exit()
        else:
            print("Cambiando url en el archivo local_settings.py...")
            time.sleep(2)
            cambiar_url_local(local_url)
            print("Url cambiada con exito")
    else:
        print("Url no cambiada")
    print("Aplicando migraciones...")
    time.sleep(2)
    os.system("python manage.py makemigrations")
    os.system("python manage.py migrate")
    print("Migraciones aplicadas",end="\n\n")
    print("Vaciando base de datos...")
    os.system("python manage.py flush --no-input")
    print("Base de datos vaciada,",end="\n\n")
    print("Comienzo de las migraciones...")
    time.sleep(2)
    print("Creando usuarios...")
    time.sleep(2)

    for _ in range(50):
        user= UserFactory.create()
        print(f"Usuario creado: {user.username}")
    admin = User.objects.create_superuser(username="admin", email="a@a.com",password="admin")
    if admin:
        print(f"Usuario admin creado: Usuario= {admin.username} Contraseña = {admin.password}")

    print("Usuarios creados con exito",end="\n\n")
    time.sleep(2)
    print("Creando preguntas...")
    time.sleep(2)

    for pregunta in preguntas_predefinidas:
            q=Question.objects.create(desc=pregunta["question_desc"])
            print(f"Pregunta creada: {q.desc}")
            for o in pregunta["opciones"]:
                option = QuestionOption.objects.create(
                question=q,
                number=o["number"], 
                option=o["option"])
                print(f"Opcion creada: {option.option}")

    print("Preguntas creadas con exito",end="\n\n")
    time.sleep(2)
    print("Creando votaciones...")
    time.sleep(2)
    authentication=Auth.objects.create(name="local", url=local_url)
    print(f"Auth local creada: {local_url}",end="\n\n")

    time.sleep(2)

    for nombre_votacion in nombres_votaciones:
        voting_instance = Voting.objects.create(
            name=nombre_votacion,
            question=random.choice(preguntas),
            ranked=random.choice([True, False]),
        )
        voting_instance.auths.add(authentication)
        print(f"Votacion creada: {voting_instance.name}")
    print("Votaciones creadas con exito",end="\n\n")

    time.sleep(2)
    print("Creando censos...")
    time.sleep(2)

    for votacion in votaciones:
        usuarios_votacion=random.sample(list(usuarios),5)
        for usuario in usuarios_votacion:
            censo = Census.objects.create(
                voting_id=votacion.id,
                voter_id=usuario.id,
            )
            print(f"Usuario {usuario.username} agregado a la votacion {votacion.name}")

    print("Migraciones aplicadas")

    respuesta=input("¿Desea ejecutar la aplicación? (si/no):")
    if respuesta=="si":
        os.system("python manage.py runserver")
    else:
        print("Aplicación no ejecutada")