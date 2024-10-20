from django.db import models
import shortuuid
from shortuuid.django_fields import ShortUUIDField
from userauths.models import user_directory_path
from userauths.models import User
from django.utils.text import slugify
from django.utils.html import mark_safe




VISIBILITY = (
    ("Only Me","Only Me"),
    ("Everyone","Everyone"),
)
FRIEND_REQUEST = (
    ("pending","pending"),
    ("accept","Accept"),
    ("reject","Reject"),
)

NOTIFICATION_TYPE = (
    ("Friend Request", "Friend Request"),
    ("Friend Request Accepted", "Friend Request Accepted"),
    ("New Follower", "New Follower"),
    ("New Like", "New Like"),
    ("New Comment", "New Comment"),
    ("Comment Liked", "Comment Liked"),
    ("Comment Replied", "Comment Replied"),
    

)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=500, blank=True ,null=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    video = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    pid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")
    likes = models.ManyToManyField(User, blank=True, related_name="likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Post"
    
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(Post, self).save(*args, **kwargs) 
        
    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))
    
    def post_comments(self):
        comments = Comment.objects.filter(post=self, active=True)
        return comments
    
    

class Gallery(models.Model):
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to="gallery", null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.post)
    
    class Meta:
        verbose_name_plural = "Gallery"

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 30px;" />' % (self.image))



class FriendRequest(models.Model):
    fid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="request_sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="request_receiver")
    status = models.CharField(max_length=10, default="pending", choices=FRIEND_REQUEST)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}"
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Friend Request"

class Friend(models.Model):
    fid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Friend"
        

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500, blank=True ,null=True)
    date = models.DateTimeField(auto_now_add=True)
    cid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")
    likes = models.ManyToManyField(User, blank=True, related_name="comment_likes")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Comment"
        
    def comment_replies(self):
        comment_replies = ReplyComment.objects.filter(comment=self, active=True)
        return comment_replies

        

class ReplyComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reply = models.CharField(max_length=500, blank=True ,null=True)
    date = models.DateTimeField(auto_now_add=True)
    cid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Reply Comment"
        
        
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="noti_user")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="noti_sender")
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name="noti_post")
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, blank=True, related_name="noti_comment")
    notification_type = models.CharField(max_length=100, choices=NOTIFICATION_TYPE, default="none")
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    nid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")
    
    class Meta:
        verbose_name_plural = "Notification"

    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"
    
    
    
    
    
    
class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    memebers = models.ManyToManyField(User, blank=True, related_name="memebers")

    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    name = models.CharField(max_length=500, blank=True ,null=True)
    description = models.TextField(blank=True ,null=True)
    video = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    gid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Group"
    
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
        super(Group, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))
    
    
    
class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=500, blank=True ,null=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    pid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")
    likes = models.ManyToManyField(User, blank=True, related_name="group_post_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Group Post"
    
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(GroupPost, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))


class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    followers = models.ManyToManyField(User, blank=True, related_name="page_followers")
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    name = models.CharField(max_length=500, blank=True ,null=True)
    description = models.TextField(blank=True ,null=True)
    video = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    gid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Page"
    
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
        super(Page, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))
    


class PagePost(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=500, blank=True ,null=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    visibility = models.CharField(max_length=10, default="everyone", choices=VISIBILITY)
    pid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")
    likes = models.ManyToManyField(User, blank=True, related_name="page_post_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Page Post"
    
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(PagePost, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))
    
    