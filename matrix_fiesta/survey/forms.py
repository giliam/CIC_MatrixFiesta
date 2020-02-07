import json

from django import forms
from django.utils.translation import ugettext_lazy as _

from survey.models import QuestionTypes


def _is_non_field_question(question):
    return question.question_type in [
        QuestionTypes.TITLE.value,
        QuestionTypes.DESCRIPTION.value,
    ]


class ResponseForm(forms.Form):
    # Based on https://www.caktusgroup.com/blog/2018/05/07/creating-dynamic-forms-django/
    def __init__(self, questions, *args, **kwargs):
        if "anonymous" in kwargs.keys():
            self.allow_anonymous = kwargs["anonymous"]
            del kwargs["anonymous"]
        else:
            self.allow_anonymous = False

        super(forms.Form, self).__init__(*args, **kwargs)

        self.questions_fields = []
        if self.allow_anonymous:
            self.questions_fields.append("anonymous")
            self.fields["anonymous"] = forms.BooleanField(
                label=_("Do you want to stay anonymous?"), required=False
            )

        self.other_fields = {}
        self.questions = questions
        for question in self.questions.all():
            self.add_question(question)

    def add_question(self, question):
        # Adds the field to the list of existing achievements related fields
        field_id = "question_" + str(question.id)
        self.questions_fields.append(field_id)
        question_type = question.question_type

        if question_type == QuestionTypes.TEXTINPUT.value:
            field = forms.CharField(label=question.content, required=question.required)
        elif question_type == QuestionTypes.TEXTAREA.value:
            field = forms.CharField(
                label=question.content,
                required=question.required,
                widget=forms.Textarea,
            )
        elif question_type == QuestionTypes.SELECT.value:
            field = forms.ChoiceField(
                label=question.content,
                required=question.required,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question_type == QuestionTypes.MULTIPLESELECT.value:
            field = forms.MultipleChoiceField(
                label=question.content,
                required=question.required,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question_type == QuestionTypes.RADIO.value:
            field = forms.ChoiceField(
                label=question.content,
                required=question.required,
                widget=forms.RadioSelect,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question_type == QuestionTypes.CHECKBOX.value:
            field = forms.MultipleChoiceField(
                label=question.content,
                required=question.required,
                widget=forms.CheckboxSelectMultiple,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif _is_non_field_question(question):
            field = {
                "type": str(QuestionTypes(question_type).name),
                "content": question.content,
                "non_field": True,
            }
        else:
            field = forms.CharField(label=question.content, required=question.required)

        if not _is_non_field_question(question):
            self.fields[field_id] = field
        else:
            self.other_fields[field_id] = field

    def __iter__(self):
        for field_id in self.questions_fields:
            if field_id in self.other_fields:
                yield self.other_fields.get(field_id)
            else:
                yield self[field_id]

    def set_initial(self, response):
        if response is None:
            return False
        answer_by_question = {
            answer.question.id: answer for answer in response.answers.all()
        }

        for question in self.questions.all():
            field_id = "question_" + str(question.id)
            if not _is_non_field_question(question):
                initial = response.answers_questions[question.id].value
                # We test the case where initial contains ",", ie. a list.
                if question.is_iterable() and "," in initial:
                    self.fields[field_id].initial = [
                        c.id for c in answer_by_question[question.id].choices.all()
                    ]

                else:
                    self.fields[field_id].initial = answer_by_question[
                        question.id
                    ].print()

        if response.anonymous and self.allow_anonymous:
            self.fields["anonymous"].initial = response.anonymous
        return True
