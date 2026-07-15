from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from emergency_requests.models import BroadcastLog
from emergency_requests.services import respond_to_broadcast


@csrf_exempt
def sms_webhook(request):
    """Inbound SMS webhook — facilities reply 'ACCEPT <id>' or 'DECLINE <id>'."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    body = request.POST.get('Body', '').upper().strip()
    parts = body.split()
    if len(parts) == 2 and parts[0] in ('ACCEPT', 'DECLINE'):
        action, broadcast_id = parts
        try:
            broadcast = BroadcastLog.objects.select_related('request', 'facility').get(id=broadcast_id)
        except (BroadcastLog.DoesNotExist, ValueError):
            return HttpResponse('OK')
        respond_to_broadcast(broadcast, available=(action == 'ACCEPT'))

    return HttpResponse('OK')
