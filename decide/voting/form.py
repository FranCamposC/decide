# forms.py
from django import forms
from .models import QuestionOption

#Formulario
class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        try:
            if not self.data.get('_delete'):
                instance = QuestionOption(
                    question=cleaned_data.get('question'),
                    number=cleaned_data.get('number'),
                    option=cleaned_data.get('option')
                )
                if instance.question.is_binary_question and instance.option.count!=0:
                    raise Exception('You cant add question options if is binary question is active')

            instance.save()
        except Exception as e:
            self.add_error('option', e)
        return cleaned_data