# forms.py
from django import forms
from .models import Question, QuestionOption, QuestionType

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['desc', 'type']

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('type')

        total_forms = int(self.data.get('options-TOTAL_FORMS'))
        filled_forms = 0

        if question_type == QuestionType.BINARY:
            total_forms = int(self.data.get('options-TOTAL_FORMS'))
            valid_binary_options = {'Sí', 'No'}

            for form_index in range(total_forms):
                option = self.data.get(f'options-{form_index}-option', '').strip()
                if option and option not in valid_binary_options:
                    raise forms.ValidationError('Para preguntas de tipo binario, solo se permiten las opciones "Sí" y "No".')
        
        for form_index in range(total_forms):
            # Verificar que los formularios no esten en blanco
            if self.data.get(f'options-{form_index}-option'):
                filled_forms += 1
        if question_type == QuestionType.NORMAL and int(filled_forms) < 2:
            raise forms.ValidationError('Las preguntas de tipo normal deben tener al menos 2 opciones.')

        if question_type == QuestionType.RANKING and int(filled_forms) < 3:
            raise forms.ValidationError('Las preguntas de tipo ranking deben tener al menos 3 opciones.')

        return cleaned_data


class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['question', 'option', 'number']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data