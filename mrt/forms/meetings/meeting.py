from flask.ext.login import current_user
from wtforms import fields, widgets
from wtforms.validators import ValidationError, InputRequired
from wtforms_alchemy import ModelFormField

from mrt.models import db, Meeting, Staff, Participant
from mrt.models import Phrase, PhraseDefault, Translation
from mrt.models import CustomField, CustomFieldChoice
from mrt.models import MeetingType, Category

from mrt.forms.base import BaseForm, TranslationInputForm, MultiCheckboxField
from mrt.forms.base import CategoryField, EmailRequired, EmailField

from mrt.utils import copy_attributes
from mrt.definitions import MEETING_SETTINGS


_CUSTOM_FIELD_MAPPER = {
    'StringField': CustomField.TEXT,
    'BooleanField': CustomField.CHECKBOX,
    'SelectField': CustomField.SELECT,
    'CountryField': CustomField.COUNTRY,
    'CategoryField': CustomField.CATEGORY,
    'EmailField': CustomField.EMAIL,
}


class MeetingEditForm(BaseForm):

    class Meta:
        model = Meeting
        field_args = {
            'venue_address': {
                'widget': widgets.TextArea()
            },
            'date_start': {
                'format': '%d.%m.%Y',
            },
            'date_end': {
                'format': '%d.%m.%Y',
            }
        }

    title = ModelFormField(TranslationInputForm, label='Description')
    badge_header = ModelFormField(TranslationInputForm, label='Badge header')
    venue_city = ModelFormField(TranslationInputForm, label='City')
    meeting_type_slug = fields.SelectField('Meeting Type')
    photo_field_id = fields.SelectField('Photo Field', coerce=int)
    settings = MultiCheckboxField('Settings', choices=MEETING_SETTINGS)

    def __init__(self, *args, **kwargs):
        super(MeetingEditForm, self).__init__(*args, **kwargs)
        self.badge_header.english.validators = []
        delattr(self.badge_header.english.flags, 'required')
        self.meeting_type_slug.choices = [
            (mt.slug, mt.label) for mt in MeetingType.query.ignore_def()]
        self.photo_field_id.choices = [(0, '-----')]
        if self.obj:
            query = self.obj.custom_fields.filter_by(field_type='image')
            image_fields = [(x.id, x.label) for x in query]
            self.photo_field_id.choices += image_fields

    def validate_photo_field_id(self, field):
        if field.data == 0:
            field.data = None

    def validate_settings(self, field):
        settings = dict(MEETING_SETTINGS)
        for key in field.data:
            if key not in settings:
                raise ValidationError("Setting doesn't exist")

    def _clean_badge_header(self, meeting):
        if not self.badge_header.data['english']:
            old_badge_header, meeting.badge_header = meeting.badge_header, None
            if old_badge_header.id:
                db.session.delete(old_badge_header)

    def _save_phrases(self, meeting):
        phrases_default = (
            PhraseDefault.query
            .filter_by(meeting_type_slug=meeting.meeting_type_slug)
        )
        for phrase_default in phrases_default:
            phrase = copy_attributes(Phrase(), phrase_default)
            phrase.description = (
                copy_attributes(Translation(), phrase_default.description)
                if phrase_default.description else Translation(english=''))
            phrase.meeting = meeting
            db.session.add(phrase)
            db.session.flush()

    def _save_categories(self, meeting):
        for category_default in meeting.meeting_type.default_categories:
            category = copy_attributes(Category(), category_default)
            category.title = copy_attributes(Translation(),
                                             category_default.title)
            category.meeting = meeting
            db.session.add(category)
            db.session.flush()

    def save(self):
        meeting = self.obj or Meeting()
        self.populate_obj(meeting)
        self._clean_badge_header(meeting)
        if meeting.id is None:
            meeting.owner = current_user.staff
            db.session.add(meeting)
            self._save_phrases(meeting)
            self._save_categories(meeting)
            add_custom_fields_for_meeting(
                meeting, form_class=ParticipantDummyForm)
        if meeting.media_participant_enabled:
            add_custom_fields_for_meeting(
                meeting, form_class=MediaParticipantDummyForm)
        db.session.commit()
        return meeting


class ParticipantDummyForm(BaseForm):

    CUSTOM_FIELD_TYPE = 'participant'

    category_id = CategoryField('Category', validators=[InputRequired()],
                                coerce=int, choices=[])
    email = EmailField('Email', validators=[EmailRequired(), InputRequired()])

    class Meta:
        model = Participant
        exclude = ('deleted', 'registration_token', 'participant_type')
        visible_on_registration_form = (
            'title', 'first_name', 'last_name', 'email', 'category_id',
            'language', 'country', 'represented_country',
            'represented_organization',)
        field_args = {
            'language': {'validators': [InputRequired()]},
            'country': {'validators': [InputRequired()]}
        }


class DefaultParticipantDummyForm(BaseForm):

    CUSTOM_FIELD_TYPE = 'participant'

    email = EmailField('Email', validators=[EmailRequired(), InputRequired()])

    class Meta:
        model = Participant
        exclude = ('deleted', 'registration_token', 'participant_type',
                   'attended', 'verified', 'credentials')
        visible_on_registration_form = []
        field_args = {
            'language': {'validators': [InputRequired()]},
            'country': {'validators': [InputRequired()]}
        }


class MediaParticipantDummyForm(BaseForm):

    CUSTOM_FIELD_TYPE = 'media'

    category_id = CategoryField('Category', validators=[InputRequired()],
                                coerce=int, choices=[])
    email = EmailField('Email', validators=[EmailRequired(), InputRequired()])

    class Meta:
        model = Participant
        only = ('title', 'first_name', 'last_name', 'email', 'category_id')
        visible_on_registration_form = (
            'title', 'first_name', 'last_name', 'email', 'category_id')


class DefaultMediaParticipantDummyForm(BaseForm):

    CUSTOM_FIELD_TYPE = 'media'

    email = EmailField('Email', validators=[EmailRequired(), InputRequired()])

    class Meta:
        model = Participant
        only = ('title', 'first_name', 'last_name', 'email')
        visible_on_registration_form = []


class MeetingFilterForm(BaseForm):

    meeting_type = fields.SelectField('Filter by type', choices=[])

    def __init__(self, *args, **kwargs):
        super(MeetingFilterForm, self).__init__(*args, **kwargs)
        choices = [(m.slug, m.label) for m in MeetingType.query.ignore_def()]
        self.meeting_type.choices = [('', 'All')] + choices


class MeetingChangeOwnerForm(BaseForm):

    owner_id = fields.SelectField('Owner', coerce=int)

    def __init__(self, *args, **kwargs):
        super(MeetingChangeOwnerForm, self).__init__(*args, **kwargs)
        self.owner_id.choices = [(i.id, i) for i in Staff.query.all()]

    def save(self):
        self.populate_obj(self.obj)
        db.session.commit()


def add_custom_fields_for_meeting(meeting, form_class=ParticipantDummyForm):
    """Adds participants fields as CustomFields to meeting."""
    form = form_class()
    for i, field in enumerate(form):
        query = (
            CustomField.query
            .filter_by(slug=field.name, meeting=meeting)
            .filter_by(custom_field_type=form.CUSTOM_FIELD_TYPE)
        )
        if query.scalar():
            continue
        custom_field = CustomField()
        custom_field.meeting = meeting
        custom_field.slug = field.name
        custom_field.label = Translation(english=unicode(field.label.text))
        custom_field.required = field.flags.required
        custom_field.field_type = _CUSTOM_FIELD_MAPPER[field.type]
        custom_field.is_primary = True
        custom_field.custom_field_type = form.CUSTOM_FIELD_TYPE
        if field.name in form.meta.visible_on_registration_form:
            custom_field.visible_on_registration_form = True
        else:
            custom_field.visible_on_registration_form = False
        custom_field.sort = i + 1
        db.session.add(custom_field)

        if custom_field.field_type == CustomField.SELECT:
            _add_choice_values_for_custom_field(
                custom_field, field.choices)
    db.session.commit()


def _add_choice_values_for_custom_field(custom_field, choices):
    """Adds CustomFieldChoices for CustomField."""
    for value, label in (choices or []):
        custom_field_choice = CustomFieldChoice(custom_field=custom_field)
        custom_field_choice.value = Translation(english=value)
        db.session.add(custom_field_choice)
