from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import User


class UserManager(BaseUserManager):
    use_in_migration = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        
       
        user.set_password(password)
        user.save(using=self._db)
        return user
       
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password, **extra_fields)




class UserData(AbstractBaseUser, PermissionsMixin):
    username = None
    name = models.CharField(max_length=100, unique=True) 
    email = models.EmailField(max_length=100, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=True)
    profile_image = models.ImageField(
        upload_to="./images/ProfileImages/", null=True, blank=True, default="")

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


# HiddenLocation Model Starts here
class Locations(models.Model):
    LOCATIONS_CHOICES = (
    ("Cultural", "Cultural"),
    ("Street", "Street"),
    ("Nature", "Nature"),
    ("Clubs&Bar", "Clubs&Bar"),
    ("Mountains", "Mountains"),
    ("Historical", "Historical"),
    ("Others", "Others"),

)
    locationName = models.CharField(max_length=250)
    category = models.CharField(
        max_length = 20,
        choices = LOCATIONS_CHOICES,
        default = '1'
        )
    
    locationDescription = models.TextField()
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)
    latitude = models.FloatField(default=0)
    Longitude = models.FloatField(default=0)
    price = models.PositiveIntegerField(default=0)
    likes = models.IntegerField(default = 0)



    def __str__(self):
        return self.locationName


class Location_Image(models.Model):
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="hiddenLocationImages", default="")


# Blog model starts here
class Blog(models.Model):
    blogTitle = models.CharField(max_length=250)
    tagS= models.CharField(null=True,blank=True)
    blogDescription = models.TextField()
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.blogTitle


class Blog_Image(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images', default='')

    def __str__(self):
        return self.blog.blogTitle


# Comment Model Here
class Comment_Location(models.Model):
    commentText = models.CharField(max_length=250)
    location = models.ForeignKey(
        Locations, on_delete=models.CASCADE)
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.commentText


class Comment_Blog(models.Model):
    commentText = models.CharField(max_length=250)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.commentText


# Favorites
class Favorites_Location(models.Model):
    location = models.ForeignKey(
        Locations, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.location.locationName





class ReplyLocationComment(models.Model):
    comment = models.ForeignKey(Comment_Location, on_delete=models.CASCADE)
    owner  = models.ForeignKey(UserData, on_delete=models.CASCADE)
    reply  = models.TextField(max_length=250)
    time_stamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment
    



class Reply_BlogComment(models.Model):
    comment = models.ForeignKey(Comment_Blog, on_delete=models.CASCADE)
    replyCommmentText= models.CharField(max_length=250)
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.replyCommmentText


class LocationLiked(models.Model):
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    owner = models.ForeignKey(UserData, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.owner.name

