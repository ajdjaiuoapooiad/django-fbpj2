



from core.models import FriendRequest, Notification
from userauths.models import User


def my_context_processor(request):

    try:
        friend_request = FriendRequest.objects.filter(receiver=request.user)
    except:
        friend_request = None
        
    try:
        notification = Notification.objects.filter(user=request.user)
    except:
        notification = None


    return {
        "friend_request":friend_request,
        "notification":notification,
    }
    
 