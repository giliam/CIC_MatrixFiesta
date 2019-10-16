import json

from django import forms
from django.utils.translation import ugettext_lazy as _

from survey.models import QuestionTypes


class ResponseForm(forms.Form):
    # Based on https://www.caktusgroup.com/blog/2018/05/07/creating-dynamic-forms-django/
    def __init__(self, questions, *args, **kwargs):
        if "anonymous" in kwargs.keys():
            self.allow_anonymous = kwargs["anonymous"]
            del kwargs["anonymous"]
        else:
            self.allow_anonymous = False

        super(forms.Form, self).__init__(*args, **kwargs)

        if self.allow_anonymous:
            # self.questions_fields.append("anonymous")
            self.fields["anonymous"] = forms.BooleanField(
                label=_("Do you want to stay anonymous?"), required=False
            )

        self.questions_fields = []
        self.questions = questions
        for question in self.questions.all():
            self.add_question(question)

    def add_question(self, question):
        # Adds the field to the list of existing achievements related fields
        field_id = "question_" + str(question.id)
        self.questions_fields.append(field_id)

        if question.question_type == QuestionTypes.TEXTINPUT.value:
            self.fields[field_id] = forms.CharField(
                label=question.content, required=question.required
            )
        elif question.question_type == QuestionTypes.TEXTAREA.value:
            self.fields[field_id] = forms.CharField(
                label=question.content,
                required=question.required,
                widget=forms.Textarea,
            )
        elif question.question_type == QuestionTypes.SELECT.value:
            self.fields[field_id] = forms.ChoiceField(
                label=question.content,
                required=question.required,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question.question_type == QuestionTypes.MULTIPLESELECT.value:
            self.fields[field_id] = forms.MultipleChoiceField(
                label=question.content,
                required=question.required,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question.question_type == QuestionTypes.RADIO.value:
            self.fields[field_id] = forms.ChoiceField(
                label=question.content,
                required=question.required,
                widget=forms.RadioSelect,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question.question_type == QuestionTypes.CHECKBOX.value:
            self.fields[field_id] = forms.MultipleChoiceField(
                label=question.content,
                required=question.required,
                widget=forms.CheckboxSelectMultiple,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        else:
            self.fields[field_id] = forms.CharField(
                label=question.content, required=question.required
            )

    def set_initial(self, response):
        if response is None:
            return False
        answer_by_question = {
            answer.question.id: answer for answer in response.answers.all()
        }

        for question in self.questions.all():
            field_id = "question_" + str(question.id)
            initial = response.answers_questions[question.id].value
            if question.is_iterable():
                self.fields[field_id].initial = [
                    c.id for c in answer_by_question[question.id].choices.all()
                ]
            else:
                self.fields[field_id].initial = answer_by_question[question.id].print()

        if response.anonymous and self.allow_anonymous:
            self.fields["anonymous"].initial = response.anonymous
        return True
