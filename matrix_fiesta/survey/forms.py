from django import forms

from survey.models import QuestionTypes

class ResponseForm(forms.Form):
    # Based on https://www.caktusgroup.com/blog/2018/05/07/creating-dynamic-forms-django/
    def __init__(self, questions, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        self.questions_fields = []
        self.questions = questions
        for question in self.questions.all():
            self.add_question(question)

    def add_question(self, question, default_value=None):
        # Adds the field to the list of existing achievements related fields
        field_id = "question_"+str(question.id)
        self.questions_fields.append(field_id)

        if question.question_type == QuestionTypes.TEXTINPUT.value:
            self.fields[field_id] = forms.CharField(
                label=question.content,
                required=question.required
            )
        elif question.question_type == QuestionTypes.TEXTAREA.value:
            self.fields[field_id] = forms.CharField(
                label=question.content,
                required=question.required,
                widget=forms.Textarea
            )
        elif question.question_type == QuestionTypes.SELECT.value:
            self.fields[field_id] = forms.ChoiceField(
                label=question.content,
                required=question.required,
                choices=[(c.id, c) for c in question.choices.all()]
            )
        elif question.question_type == QuestionTypes.MULTIPLESELECT.value:
            self.fields[field_id] = forms.MultipleChoiceField(
                label=question.content,
                required=question.required,
                choices=[(c.id, c) for c in question.choices.all()]
            )
        elif question.question_type == QuestionTypes.RADIO.value:
            self.fields[field_id] = forms.ChoiceField(
                label=question.content,
                required=question.required,
                widget=forms.RadioSelect,
                choices=[(c.id, c) for c in question.choices.all()]
            )
        elif question.question_type == QuestionTypes.CHECKBOX.value:
            self.fields[field_id] = forms.MultipleChoiceField(
                label=question.content,
                required=question.required,
                widget=forms.CheckboxSelectMultiple,
                choices=[(c.id, c) for c in question.choices.all()]
            )
        else:
            self.fields[field_id] = forms.CharField(
                label=question.content,
                required=question.required
            )

        if not default_value is None:
            self.initial[field_id] = (default_value.id, default_value.value)