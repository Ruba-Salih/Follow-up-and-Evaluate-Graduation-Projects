from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from project.models import Project


class ProjectFeedback(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name=_("Project")
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_project_feedbacks',
        verbose_name=_("Sender")
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_project_feedbacks',
        verbose_name=_("Receiver (Teacher)")
    )
    title = models.CharField(_("Title"), max_length=255, blank=True)
    message = models.TextField(_("Message"), blank=True, null=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.title or _('Feedback')} {_('from')} {self.sender}"


class FeedbackReply(models.Model):
    feedback = models.OneToOneField(
        ProjectFeedback,
        on_delete=models.CASCADE,
        related_name='reply',
        verbose_name=_("Original Feedback")
    )
    message = models.TextField(_("Reply Message"), blank=True, null=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{_('Reply to Feedback')} {self.feedback.id}"


class FeedbackFile(models.Model):
    feedback = models.ForeignKey(
        ProjectFeedback,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_("Feedback")
    )
    reply = models.ForeignKey(
        FeedbackReply,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_("Reply")
    )
    file = models.FileField(_("File"), upload_to='feedback_files/')
    uploaded_at = models.DateTimeField(_("Uploaded At"), auto_now_add=True)

    def __str__(self):
        if self.reply:
            return f"{_('Reply file for Feedback')} {self.feedback.id}"
        return f"{_('Student file for Feedback')} {self.feedback.id}"

