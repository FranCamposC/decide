import os
import django
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'decide.settings')
django.setup()

from factory import Factory,LazyAttribute
import subprocess
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

preguntas_predefinidas=[

    {"question_desc": "¿Cual es tu opinion sobre el cambio climatico?",
     "opciones": [
         {"number": 1, "option": "Muy preocupado/a"},
         {"number": 2, "option": "Preocupado/a"},
         {"number": 3, "option": "Neutral"},
         {"number": 4, "option": "No preocupado/a"}
     ]},

    {
        "question_desc": "¿Cuál es tu comida favorita?",
        "opciones": [
            {"number": 1, "option": "Pizza"},
            {"number": 2, "option": "Ensalada"},
            {"number": 3, "option": "Pasta"},
            {"number": 4, "option": "Sushi"}
        ]
    },
    {
        "question_desc": "¿Prefieres la playa o la montaña?",
        "opciones": [
            {"number": 1, "option": "Playa"},
            {"number": 2, "option": "Montaña"},
            {"number": 3, "option": "Ambos"},
            {"number": 4, "option": "No tengo preferencia"}
        ]
    },
    {
        "question_desc": "¿Cuál es tu género literario favorito?",
        "opciones": [
            {"number": 1, "option": "Ficción"},
            {"number": 2, "option": "No ficción"},
            {"number": 3, "option": "Ciencia ficción"},
            {"number": 4, "option": "Misterio"}
        ]
    },
    {
        "question_desc": "¿Prefieres ver películas en casa o en el cine?",
        "opciones": [
            {"number": 1, "option": "En casa"},
            {"number": 2, "option": "En el cine"},
            {"number": 3, "option": "Ambos"},
            {"number": 4, "option": "No tengo preferencia"}
        ]
    },


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

nombres_votaciones=["Votacion 1", "Votacion 2", "Votacion 3", "Votacion 4", "Votacion 5", "Votacion 6", "Votacion 7", "Votacion 8", "Votacion 9", "Votacion 10"]
local_url = getattr(settings, 'BASEURL', '127.0.0.1:8000')
fake = Faker("es_ES")

preguntas=Question.objects.all()
votaciones=Voting.objects.all()
usuarios=User.objects.all()

comando_drop_db='psql -c "DROP DATABASE decidedb"'
comando_completo_drop="sudo su - postgres -c '{O}'".format(O=comando_drop_db)

comando_create_db='psql -c "CREATE DATABASE decidedb owner decideuser"'
comando_completo_create="sudo su - postgres -c '{O}'".format(O=comando_create_db)

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
    print("Bienvenido al script de configuración de inicio de la aplicación Decide")
    time.sleep(1)
    url=input("¿Es esta la url en la que desea ejecutar la aplicación? "+local_url+" (si/no): ") 
    if url=="no":
        print("Dirigete a tu archivo local_settings.py, cambiala, y vuelve a ejecutar el script")
        exit()
    else:
        print("Url no cambiada")
    req=input("¿Desea instalar los requerimientos? (si/no): ")
    if req=="si":
        print("Instalando requerimientos...")
        os.system("pip install -r ../requirements.txt")
        print("Requerimientos instalados",end="\n\n")
    else:
        print("Requerimientos no instalados",end="\n\n")

    migr=input("¿Desea aplicar las migraciones? (si/no): ")
    if migr=="si":
        print("Aplicando migraciones...")
        time.sleep(2)
        os.system("find . -path '*/migrations/*.py' -not -name '__init__.py' -delete")
        os.system("find . -path '*/migrations/*.pyc'  -delete")
        os.system(comando_completo_drop)
        os.system(comando_completo_create)
        os.system("python manage.py makemigrations")
        os.system("python manage.py migrate")
        print("Migraciones aplicadas",end="\n\n")
    else:
        print("Migraciones no aplicadas",end="\n\n")
    db=input("¿Desea vaciar la base de datos? (si/no): ")
    if db=="si":
        print("Vaciando base de datos...")
        os.system("python manage.py flush --no-input")
        print("Base de datos vaciada,",end="\n\n")
    else:
        print("Base de datos no vaciada,",end="\n\n")
    time.sleep(2)
    pobl=input("¿Desea poblar la base de datos? (si/no): ")
    if pobl=="si":

        print("Creando usuarios...")
        time.sleep(2)

        for _ in range(50):
            user= User.objects.create_user(username=fake.user_name(), email=fake.email(),password="1234")
            print(f"Usuario creado: {user.username} con id {user.id}")
        ad=input("¿Desea crear un administrador? (si/no):" )
        if ad=="si":
            nombre=input("Introduzca el nombre del usuario administrador: ")
            gmail=input("Introduzca el email del usuario administrador: ")
            contraseña=input("Introduzca la contraseña del usuario administrador: ")
            admin = User.objects.create_superuser(username=nombre, email=gmail,password=contraseña)
            print(f"Usuario admin creado: Usuario= {admin.username} Contraseña = {contraseña}")
        else:
            pass
        print("Usuarios creados con exito",end="\n\n")
        time.sleep(2)
        print("Creando preguntas normales,ranking y opciones...")
        time.sleep(2)

        for pregunta in preguntas_predefinidas:
                q=Question.objects.create(desc=pregunta["question_desc"],
                                          type=random.choice(["NORMAL","RANKING","MULTIPLE"]))
                print(f"Pregunta de tipo {q.type} creada: {q.desc}")
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
    else:
        print("Base de datos no poblada")
        respuesta=input("¿Desea ejecutar la aplicación? (si/no):")
        if respuesta=="si":
            os.system("python manage.py runserver " + local_url.replace("http://",""))
        else:
            print("Aplicación no ejecutada")