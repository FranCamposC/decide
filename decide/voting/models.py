from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.forms import ValidationError

from base import mods
from base.models import Auth, Key

class QuestionType(models.TextChoices):
    BINARY = 'SI_NO', 'Binario'
    RANKING = 'RANKING', 'Ranking'
    NORMAL = 'NORMAL', 'Normal'

class Question(models.Model):
    desc = models.TextField()
    type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        default=QuestionType.NORMAL
    )

    def __str__(self):
        return self.desc


    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if self.type == QuestionType.BINARY:
            if not is_new:
                self.options.all().delete()
            if not self.options.filter(option="Sí").exists():
                QuestionOption.objects.create(question=self, option="Sí", number=1)
            if not self.options.filter(option="No").exists():
                QuestionOption.objects.create(question=self, option="No", number=2)


        # Validacines del type
        elif self.type == QuestionType.RANKING and self.options.count() < 3:
            raise ValidationError('Las preguntas de tipo ranking deben tener al menos 3 opciones.')


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.question.options.count() + 2

        # Verifica si la pregunta es de tipo binario y evita crear opciones adicionales
        if self.question.type != QuestionType.BINARY or not self.question.options.exists():
            super().save(*args, **kwargs)



        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)

class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE)

    ranked = models.BooleanField(default=False)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        votes_format = []
        vote_list = []
        for vote in votes:
            for info in vote:
                if info == 'a':
                    votes_format.append(vote[info])
                if info == 'b':
                    votes_format.append(vote[info])
            vote_list.append(votes_format)
            votes_format = []
        return vote_list

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()

    def do_postproc(self):
        ranked = self.ranked
        tally = self.tally
        options = self.question.options.all()

        opts = []
        if not ranked:
            for opt in options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes
                })
        else:
            for opt in options:
                votes = 0
                for vote in tally:
                    rank = list(str(vote))
                    pos = int(rank[opt.number])
                    if pos == 1:
                        votes = votes + 3
                    elif pos == 2:
                        votes = votes + 2
                    elif pos == 3:
                        votes = votes + 1
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes
                })
        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name
