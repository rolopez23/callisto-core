import json
import logging
from distutils.util import strtobool

from django import forms

from . import report_delivery
from ..delivery import forms as delivery_forms, models as delivery_models
from ..utils import api
from .validators import Validators

logger = logging.getLogger(__name__)


class ReportingForm(
    delivery_forms.FormViewExtensionMixin,
    forms.models.ModelForm,
):
    contact_name = forms.CharField(
        label="Your preferred first name:",
    )
    contact_phone = forms.CharField(
        label="Preferred phone number to call:",
    )
    contact_voicemail = forms.CharField(
        label='Is it ok to leave a voicemail?',
    )
    contact_email = forms.EmailField(
        label="What's the best email address to reach you?",
    )
    contact_notes = forms.CharField(
        label="Any notes about how to contact you?",
        widget=forms.Textarea(),
    )
    email_confirmation = forms.ChoiceField(
        choices=[
            (True, "Yes"),
            (False, "No, thanks"),
        ],
        label="Would you like an email confirmation?",
        widget=forms.RadioSelect,
    )

    def clean_email_confirmation(self):
        if strtobool(self.data.get('email_confirmation')):
            api.NotificationApi.send_user_notification(
                self, 'submit_confirmation', self.view.site_id)

    class Meta:
        model = delivery_models.Report
        fields = [
            'contact_name',
            'contact_phone',
            'contact_voicemail',
            'contact_email',
            'contact_notes',
        ]


class SubmitToMatchingForm(
    delivery_forms.FormViewExtensionMixin,
    forms.models.ModelForm,
):
    perp_name = forms.CharField(
        label="Perpetrator's Name",
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'ex. John Jacob Jingleheimer Schmidt'},
        ),
    )
    identifier = forms.CharField(
        label=Validators.titled(),
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': Validators.examples()},
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.report = self.view.report

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier').strip()
        for identifier_info in Validators.value():
            try:
                matching_id = identifier_info['validation'](identifier)
                if matching_id:
                    prefix = identifier_info['unique_prefix']
                    # Facebook has an empty unique identifier
                    # for backwards compatibility
                    if len(prefix) > 0:
                        # FB URLs can't contain colons
                        matching_id = prefix + ":" + matching_id
                    return matching_id
            except Exception as e:
                if e.__class__ is not forms.ValidationError:
                    logger.exception(e)
                pass
        # no valid identifier found
        raise forms.ValidationError(Validators.invalid())

    def save(self, commit=True):
        output = super().save(commit=commit)

        report_content = report_delivery.MatchReportContent.from_form(self)
        self.object.encrypt_match_report(
            report_text=json.dumps(report_content.__dict__),
            key=self.cleaned_data.get('identifier'),
        )

        return output

    class Meta:
        model = delivery_models.MatchReport
        fields = ['identifier']