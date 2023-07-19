from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Locations, UserData, Blog, Blog_Image, Comment_Location, Favorites_Location, Comment_Blog, Location_Image,ReplyLocationComment,LocationLiked


admin.site.register(UserData)
admin.site.register(Locations)
admin.site.register(Blog)
admin.site.register(Blog_Image)
admin.site.register(Location_Image)
admin.site.register(Comment_Location)
admin.site.register(Comment_Blog)
admin.site.register(Favorites_Location)
admin.site.register(ReplyLocationComment)
admin.site.register(LocationLiked)
