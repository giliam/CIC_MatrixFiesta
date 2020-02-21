from enum import Enum
import json

from django import forms
from django.utils.translation import ugettext_lazy as _

from survey import models


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

        if question_type == models.QuestionTypes.TEXTINPUT.value:
            field = forms.CharField(label=question.content, required=question.required)
        elif question_type == models.QuestionTypes.TEXTAREA.value:
            field = forms.CharField(
                label=question.content,
                required=question.required,
                widget=forms.Textarea,
            )
        elif question_type == models.QuestionTypes.SELECT.value:
            field = forms.ChoiceField(
                label=question.content,
                required=question.required,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question_type == models.QuestionTypes.MULTIPLESELECT.value:
            field = forms.MultipleChoiceField(
                label=question.content,
                required=question.required,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question_type == models.QuestionTypes.RADIO.value:
            field = forms.ChoiceField(
                label=question.content,
                required=question.required,
                widget=forms.RadioSelect,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question_type == models.QuestionTypes.CHECKBOX.value:
            field = forms.MultipleChoiceField(
                label=question.content,
                required=question.required,
                widget=forms.CheckboxSelectMultiple,
                choices=[(c.id, c) for c in question.choices.all()],
            )
        elif question.is_non_field():
            field = {
                "type": str(models.QuestionTypes(question_type).name),
                "content": question.content,
                "non_field": True,
            }
        else:
            field = forms.CharField(label=question.content, required=question.required)

        if not question.is_non_field():
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
            if not question.is_non_field():
                # If the question has ever been answered.
                if question.id in response.answers_questions:
                    if question.is_iterable():
                        initial = response.answers_questions[question.id].choices.all()
                    else:
                        initial = response.answers_questions[question.id].value
                    # We test the case where initial contains ",", ie. a list.
                    if question.is_iterable():
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


class SurveyCreationForm(forms.ModelForm):
    class Meta:
        model = models.Survey
        exclude = ("slug",)
        labels = {
            "name": _("Name"),
            "opened": _("Opened"),
            "archived": _("Archived"),
            "ecue": _("ECUE"),
            "promotionyear": _("Promotion"),
            "allow_anonymous": _("Allow anonymous"),
        }


class QuestionCreationForm(forms.ModelForm):
    choices = forms.CharField(
        label=_("Choices (separate by new line) for multiple choices questions"),
        widget=forms.Textarea,
        required=False,
    )

    class Meta:
        model = models.Question
        exclude = ("survey", "choices")
        labels = {
            "question_type": _("Question type"),
            "content": _("Content"),
            "required": _("Required"),
            "order": _("Order"),
        }


class QuestionInsertionForm(QuestionCreationForm):
    class Meta(QuestionCreationForm.Meta):
        exclude = ("survey", "choices", "order")


class ConfirmationForm(forms.Form):
    pass


class BatchActions(Enum):
    DUPLICATE = "duplicate"
    REMOVE = "remove"


class BatchSelectionForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["action"] = forms.ChoiceField(
            label=_("Which action?"),
            required=True,
            widget=forms.Select,
            choices=[(action.value, _(action.value)) for action in BatchActions],
        )

        self.questions_fields = []
        self.questions = questions
        for question in self.questions.all():
            self.add_question(question)

    def is_hidden(self):
        return False

    def add_question(self, question):
        field_id = "question_" + str(question.id)
        self.fields[field_id] = forms.BooleanField(
            required=False, label=question.content
        )
        self.questions_fields.append(field_id)


class BatchRemoveForm(BatchSelectionForm):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(questions, *args, **kwargs)
        self.fields["action"].non_question = True

        data = args[0]
        to_delete_fields = []
        for field_name, field in self.fields.items():
            field.widget = forms.HiddenInput()
            if field_name != "action" and not data.get(field_name, False):
                to_delete_fields.append(field_name)

        for field_name in to_delete_fields:
            del self.fields[field_name]

        self.fields["confirm"] = forms.BooleanField(
            label=_("Do you really confirm the deletion of all following elements?"),
            required=True,
        )
        self.fields["confirm"].non_question = True

    def is_hidden(self):
        print("Child readonly")
        return True


class BatchDuplicateForm(BatchSelectionForm):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(questions, *args, **kwargs)
        self.fields["action"].non_question = True

        data = args[0]
        to_delete_fields = []
        for field_name, field in self.fields.items():
            field.widget = forms.HiddenInput()
            if field_name != "action" and not data.get(field_name, False):
                to_delete_fields.append(field_name)
        print(to_delete_fields)

        for field_name in to_delete_fields:
            del self.fields[field_name]

        # self.fields["action"] = forms.CharField(
        #     widget=forms.HiddenInput(), initial=BatchActions.DUPLICATE.value
        # )

        self.fields["question_above"] = forms.ChoiceField(
            required=True,
            label=_("Which question should be above your duplicates?"),
            choices=[(0, _("........top......."))]
            + [(question.id, question.content) for question in questions.all()],
        )
        self.fields["question_above"].non_question = True
