from django import forms
from .models import SubscribeTwitter
from django.utils import timezone


class NameForm(forms.ModelForm):
    class Meta:
        model = SubscribeTwitter
        fields = ("tw_username",)


YEAR_CHOICES = [y for y in range(2010, 2022)]


class DateUserForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(DateUserForm, self).__init__(*args, **kwargs)
        model = SubscribeTwitter
        self.fields['selected_id'].choices = [(int(o['tw_id']), o['tw_username']) for o in
                                              list(model.objects.filter(user=user).values())]

    from_date = forms.DateField(label='From date',
                                widget=forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class': 'form-control'}),
                                initial=timezone.now())
    until_date = forms.DateField(label='Until date',
                                 widget=forms.SelectDateWidget(years=YEAR_CHOICES, attrs={'class': 'form-control'}),
                                 initial=timezone.now())
    selected_id = forms.ChoiceField(
        label='Selected id',
        widget=forms.RadioSelect(attrs={'class': ''}, ),
        choices=[(352353, 'dfs')],
    )
