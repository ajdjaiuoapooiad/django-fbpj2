from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from core.models import ChatMessage, Comment, FriendRequest, Notification, Post, ReplyComment
import shortuuid
from django.utils.text import slugify
from django.utils.timesince import timesince
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery,Q

from userauths.models import User




# Notifications Keys
noti_new_like = "New Like"
noti_new_follower = "New Follower"
noti_friend_request = "Friend Request"
noti_new_comment = "New Comment"
noti_comment_liked = "Comment Liked"
noti_comment_replied = "Comment Replied"
noti_friend_request_accepted = "Friend Request Accepted"





@login_required
def index(request):
    posts = Post.objects.filter(active=True, visibility="Everyone")

    context = {
        "posts":posts
    }
    return render(request, "core/index.html", context)


@login_required
def post_detail(request, slug):
    post = Post.objects.get(active=True, visibility="Everyone", slug=slug)
    context = {
        "p":post
    }
    return render(request, "core/post-detail.html", context)



def send_notification(user, sender, post, comment, notification_type):
    notification = Notification.objects.create(
        user=user, 
        sender=sender, 
        post=post, 
        comment=comment, 
        notification_type=notification_type
    )
    return notification










@csrf_exempt
def create_post(request):

    if request.method == 'POST':
        title = request.POST.get('post-caption')
        visibility = request.POST.get('visibility')
        image = request.FILES.get('post-thumbnail')

        print("Title ============", title)
        print("thumbnail ============", image)
        print("visibility ============", visibility)

        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if title and image:
            post = Post(title=title, image=image, visibility=visibility, user=request.user, slug=slugify(title) + "-" + str(uniqueid.lower()))
            post.save()

            
            return JsonResponse({'post': {
                'title': post.title,
                'image_url': post.image.url,
                "full_name":post.user.profile.full_name,
                "profile_image":post.user.profile.image.url,
                "date":timesince(post.date),
                "id":post.id,
            }})
        else:
            return JsonResponse({'error': 'Invalid post data'})

    return JsonResponse({"data":"Sent"})



@csrf_exempt
def like_post(request):

    id = request.GET['id']
    post = Post.objects.get(id=id)
    user = request.user
    bool = False 

    if user in post.likes.all():
        post.likes.remove(user)
        bool = False
    else:
        post.likes.add(user)
        bool = True 
        # Do this during noticiation lecture
        if post.user != request.user:
            send_notification(post.user, user, post, None, noti_new_like)
        
    data = {
        "bool":bool,
        'likes':post.likes.all().count()
    }
    return JsonResponse({"data":data})


@csrf_exempt
def comment_on_post(request):

    id = request.GET['id']
    comment = request.GET['comment']
    post = Post.objects.get(id=id)
    comment_count = Comment.objects.filter(post=post).count()
    user = request.user

    new_comment = Comment.objects.create(
        post=post,
        comment=comment,
        user=user
    )


    data = {
        "bool":True,
        'comment':new_comment.comment,
        "profile_image":new_comment.user.profile.image.url,
        "date":timesince(new_comment.date),
        "comment_id":new_comment.id,
        "post_id":new_comment.post.id,
        "comment_count":comment_count + int(1)
    }
    return JsonResponse({"data":data})


@csrf_exempt
def like_comment(request):

    id = request.GET['id']
    comment = Comment.objects.get(id=id)
    user = request.user
    bool = False 

    if user in comment.likes.all():
        comment.likes.remove(user)
        bool = False
    else:
        comment.likes.add(user)
        bool = True 


    data = {
        "bool":bool,
        'likes':comment.likes.all().count()
    }
    return JsonResponse({"data":data})


@csrf_exempt
def reply_comment(request):

    id = request.GET['id']
    reply = request.GET['reply']

    comment = Comment.objects.get(id=id)
    user = request.user

    new_reply = ReplyComment.objects.create(
        comment=comment,
        reply=reply,
        user=user,
    )

    
    data = {
        "bool":True,
        'reply':new_reply.reply,
        "profile_image":new_reply.user.profile.image.url,
        "date":timesince(new_reply.date),
        "reply_id":new_reply.id,
        "post_id":new_reply.comment.post.id,

    }
    return JsonResponse({"data":data})



@csrf_exempt
def delete_comment(request):
    id = request.GET['id']
    
    comment = Comment.objects.get(id=id, user=request.user)
    comment.delete()

    data = {
        "bool":True,
    }
    return JsonResponse({"data":data})


@csrf_exempt
def add_friend(request):
    sender = request.user
    receiver_id = request.GET['id'] 
    bool = False

    if sender.id == int(receiver_id):
        return JsonResponse({'error': 'You cannot send a friend request to yourself.'})
    
    receiver = User.objects.get(id=receiver_id)
    
    try:
        friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
        if friend_request:
            friend_request.delete()
        bool = False
        return JsonResponse({'error': 'Cancelled', 'bool':bool})
    except FriendRequest.DoesNotExist:
        friend_request = FriendRequest(sender=sender, receiver=receiver)
        friend_request.save()
        bool = True
        

        return JsonResponse({'success': 'Sent',  'bool':bool})


@csrf_exempt
def accept_friend_request(request):
    id = request.GET['id'] 

    receiver = request.user
    sender = User.objects.get(id=id)
    
    friend_request = FriendRequest.objects.filter(receiver=receiver, sender=sender).first()

    receiver.profile.friends.add(sender)
    sender.profile.friends.add(receiver)

    friend_request.delete()

    data = {
        "message":"Accepted",
        "bool":True,
    }
    
    return JsonResponse({'data': data})




@csrf_exempt
def reject_friend_request(request):
    id = request.GET['id'] 

    receiver = request.user
    sender = User.objects.get(id=id)
    
    friend_request = FriendRequest.objects.filter(receiver=receiver, sender=sender).first()
    friend_request.delete()

    data = {
        "message":"Rejected",
        "bool":True,
    }
    return JsonResponse({'data': data})



@csrf_exempt
def unfriend(request):
    sender = request.user
    friend_id = request.GET['id'] 
    bool = False

    if sender.id == int(friend_id):
        return JsonResponse({'error': 'You cannot unfriend yourself, wait a minute how did you even send yourself a friend request?.'})
    
    my_friend = User.objects.get(id=friend_id)
    
    if my_friend in sender.profile.friends.all():
        sender.profile.friends.remove(my_friend)
        my_friend.profile.friends.remove(sender)
        bool = True
        return JsonResponse({'success': 'Unfriend Successfull',  'bool':bool})
    

@login_required
def inbox(request):
    user_id = request.user

    chat_message = ChatMessage.objects.filter(
        id__in =  Subquery(
            User.objects.filter(
                Q(sender__reciever=user_id) |
                Q(reciever__sender=user_id)
            ).distinct().annotate(
                last_msg=Subquery(
                    ChatMessage.objects.filter(
                        Q(sender=OuterRef('id'),reciever=user_id) |
                        Q(reciever=OuterRef('id'),sender=user_id)
                    ).order_by('-id')[:1].values_list('id',flat=True) 
                )
            ).values_list('last_msg', flat=True).order_by("-id")
        )
    ).order_by("-id")
    
    context = {
        'chat_message': chat_message,
    }
    return render(request, 'chat/inbox.html', context)

@login_required
def inbox_detail(request, username):
    user_id = request.user
    message_list = ChatMessage.objects.filter(
        id__in =  Subquery(
            User.objects.filter(
                Q(sender__reciever=user_id) |
                Q(reciever__sender=user_id)
            ).distinct().annotate(
                last_msg=Subquery(
                    ChatMessage.objects.filter(
                        Q(sender=OuterRef('id'),reciever=user_id) |
                        Q(reciever=OuterRef('id'),sender=user_id)
                    ).order_by('-id')[:1].values_list('id',flat=True) 
                )
            ).values_list('last_msg', flat=True).order_by("-id")
        )
    ).order_by("-id")


    
    sender = request.user
    receiver = User.objects.get(username=username)
    receiver_details = User.objects.get(username=username)
    
    messages_detail = ChatMessage.objects.filter(
        Q(sender=sender, reciever=receiver) | Q(sender=receiver, reciever=sender)
    ).order_by("date")

    messages_detail.update(is_read=True)
    
    if messages_detail:
        r = messages_detail.first()
        reciever = User.objects.get(username=r.reciever)
    else:
        reciever = User.objects.get(username=username)

    context = {
        'message_detail': messages_detail,
        "reciever":reciever,
        "sender":sender,
        "receiver_details":receiver_details,
        "message_list":message_list,
    }
    return render(request, 'chat/inbox_detail.html', context)




