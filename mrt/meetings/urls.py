from flask import Blueprint, g
from flask import current_app as app

from mrt.models import Meeting

from mrt.meetings import Meetings, MeetingEdit
from mrt.meetings import Participants, ParticipantEdit
from mrt.meetings import Categories, CategoryEdit


meetings = Blueprint('meetings', __name__, url_prefix='/meetings')


meetings.add_url_rule('', view_func=Meetings.as_view('home'))

meeting_edit_func = MeetingEdit.as_view('edit')
meetings.add_url_rule('/add', view_func=meeting_edit_func)
meetings.add_url_rule('/<int:meeting_id>/edit', view_func=meeting_edit_func)

# participants
meetings.add_url_rule('/<int:meeting_id>/participants',
                      view_func=Participants.as_view('participants'))
participant_edit_func = ParticipantEdit.as_view('participant_edit')
meetings.add_url_rule('/<int:meeting_id>/participants/add',
                      view_func=participant_edit_func)
meetings.add_url_rule('/<int:meeting_id>/participants/<int:participant_id>/edit',
                      view_func=participant_edit_func)
# categories
meetings.add_url_rule('/<int:meeting_id>/settings/categories',
                      view_func=Categories.as_view('categories'))
category_edit_func = CategoryEdit.as_view('category_edit')
meetings.add_url_rule(
    '/<int:meeting_id>/settings/categories/add',
    view_func=category_edit_func)
meetings.add_url_rule(
    '/<int:meeting_id>/settings/categories/<int:category_id>/edit',
    view_func=category_edit_func)


@meetings.url_defaults
def add_meeting_id(endpoint, values):
    meeting = getattr(g, 'meeting', None)
    if 'meeting_id' in values or not meeting:
        return
    if app.url_map.is_endpoint_expecting(endpoint, 'meeting_id'):
        values.setdefault('meeting_id', meeting.id)


@meetings.url_value_preprocessor
def add_meeting_global(endpoint, values):
    g.meeting = None
    if app.url_map.is_endpoint_expecting(endpoint, 'meeting_id'):
        meeting_id = values.pop('meeting_id', None)
        if meeting_id:
            g.meeting = Meeting.query.get_or_404(meeting_id)
