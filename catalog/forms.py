import datetime

from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from catalog.models import BookInstance


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks (default 3)")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Return cleaned data.
        return data


class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ['imprint', 'status']

    def __init__(self, *args, **kwargs):
        super(BookInstanceForm, self).__init__(*args, **kwargs)
        self.fields['imprint'].label = "Imprint"
        self.fields['status'].label = "Status"

    def clean_status(self):
        data = self.cleaned_data['status']

        if len(data) != 1:
            raise ValidationError(_('Invalid status - too many characters'))

        if data not in 'moar':
            raise ValidationError(_(
                'Invalid status - enter m, o, a, r : maintenance, on loan, available, reserved')
            )