from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from notifications.models import Notification
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-sent_at')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
@require_POST
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.read = True
    notification.save()
    return JsonResponse({'success': True})