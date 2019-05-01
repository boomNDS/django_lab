from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from polls.models import Poll, Question,Choice


def validate_even(value):
    if value % 2 != 0:
        raise ValidationError('%(value)s ไม่ใช่เลยคู่',
                              params={'value': value})


class PollForm(forms.Form):
    title = forms.CharField(label="ชื่อโพส", max_length=100, required=True)
    email = forms.CharField(validators=[validators.validate_email])
    no_questions = forms.IntegerField(
        label="จำนวยคำถาม", min_value=0, max_value=10, required=True, validators=[validate_even])
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    def clean_title(self):
        data = self.cleaned_data['title']

        if 'ไอทีหมีแพนด้า' not in data:
            raise forms.ValidationError("คุณลืมชื่อคณะ")
        return data

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and not end:
        #     raise forms.ValidationError('โปรดเลือกวันที่สิ้นสุด')
            self.add_error('end_date', 'โปรดเลือกวันที่สิ้นสุด')
        elif end and not start:
        #     raise forms.ValidationError('โปรดเลือกวันที่เริ่มต้น')
            self.add_error('start_date', 'โปรดเลือกวันที่เริ่มต้น')


class QuestionForm(forms.Form):
    question_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea)
    type = forms.ChoiceField(choices=Question.TYPES, initial="01")

class PollModelForm(forms.ModelForm):
    # email = forms.CharField(validators=[validators.validate_email])
    # no_questions = forms.IntegerField(
    #     label="จำนวยคำถาม", min_value=0, max_value=10, required=True, validators=[validate_even])
    class Meta:
        model = Poll
        exclude = ['del_flag']

class ChoiceModelForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = "__all__"
