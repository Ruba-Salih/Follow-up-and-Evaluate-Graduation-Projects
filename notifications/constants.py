# notifications/constants.py

MEETING_REQUEST = 'meeting_request'
MEETING_ACCEPT = 'meeting_accept'
MEETING_DECLINED = 'meeting_declined'
GRADE_RELEASED = 'grade_released'
PROJECT_COMMENT = 'project_comment'
ANNOUNCEMENT = 'announcement'

NOTIFICATION_TYPES = [
    (MEETING_REQUEST, 'Meeting Request'),
    (MEETING_ACCEPT, 'Meeting Accepted'),
    (MEETING_DECLINED,'Meeting Declined'),
    (GRADE_RELEASED, 'Grade Released'),
    (PROJECT_COMMENT, 'Project Comment'),
    (ANNOUNCEMENT, 'Announcement'),
]
