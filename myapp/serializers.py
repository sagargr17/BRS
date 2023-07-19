from rest_framework import serializers
from myapp.models import *
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ["id", "email", "name", "profile_image", "password"]


    def create(self, validated_data):
        print("DATA",validated_data)
        image = validated_data['profile_image']
        user = get_user_model().objects.create(email=validated_data['email'],
                                       name=validated_data['name'], profile_image=image)
       
        user.set_password(validated_data.get('password'))
        user.save()
        return user
    
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     # Remove the password hash field from the serialized data
    #     data['owner'] = [data['owner']['email'], data['owner']
    #                      ['profile_image'], data['owner']['name']]
    #     return data
    
class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog_Image
        fields = "__all__"


class BlogSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.FileField(
            allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Blog
        fields = ['id', 'blogTitle', 'blogDescription',
                  'owner', 'time_stamp', 'uploaded_images', 'images','tagS']
        depth = 1

    def get_images(self, blog):
        images = Blog_Image.objects.filter(blog=blog)
        serializer = BlogImageSerializer(images, many=True)
        return serializer.data

    def create(self, validated_data):
        print("Blog details in serializers", validated_data)
        upload_image = validated_data.pop('uploaded_images')
        blog = Blog.objects.create(**validated_data)

        for i in upload_image:
            Blog_Image.objects.create(blog=blog, image=i)

        return blog

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Remove the password hash field from the serialized data
        data['owner'] = [data['owner']['email'], data['owner']
                         ['profile_image'], data['owner']['name']]
        return data


class HiddenImageLocationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Location_Image
        fields = ['id', 'image']
        depth = 1


class LikedLocationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocationLiked
        fields = ["id","location","likeCount","owner"]
        depth = 1


    

class HiddenLocationSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    likedCount = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.FileField(
            allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Locations
        fields = ["id", "owner", "images", "locationName","category",
                  "time_stamp", "locationDescription", "uploaded_images","price", "latitude","Longitude","likedCount"]
        depth = 1

    def get_images(self, hiddenLocation):
        images = Location_Image.objects.filter(
            location=hiddenLocation)
        serializedData = HiddenImageLocationSerializers(images, many=True)
        return serializedData.data
    

    def get_likedCount(self, hiddenLocation):
        # print("Hidden Location", hiddenLocation)
        count = LocationLiked.objects.filter(location = hiddenLocation)
        print("COunt",hiddenLocation, count, len(count))
        return  {"like" : len(count)}
    
    
    def create(self, validate_data):
        print("location Name", validate_data)
        upload_images = validate_data.pop('uploaded_images')
        location = Locations.objects.create(**validate_data)

        for i in upload_images:
            Location_Image.objects.create(
                location=location, image=i)
        return location
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["owner"] = [data['owner']['email'], data['owner']
                         ['profile_image']]
        return data


class CommentLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment_Location
        fields = ["id", "commentText", "location", "owner", 'time_stamp']
        depth = 1

    def create(self, validate_data):
        print("dATA", validate_data)
        location = validate_data.pop('location')
        commentLocation = Comment_Location.objects.create(
            location=location, **validate_data)
        return commentLocation

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["owner"] = [data['owner']['email'], data['owner']['profile_image']]
        return data


class CommentBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment_Blog
        fields = ["id", "commentText", "blog", "owner", 'time_stamp']
        depth = 1

    def create(self, validated_data):
        print("RTR", validated_data)
        blog = validated_data.pop('blog')
        commentLocation = Comment_Blog.objects.create(
            blog=blog, **validated_data)
        return commentLocation

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Remove the password hash field from the serialized data
        data['owner'] = [data['owner']['email'], data['owner']
                         ['profile_image'], data['owner']['name']]
        return data


class ReplyLocationcommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyLocationComment
        fields = ["id", "comment", "reply", "owner", 'time_stamp']
        depth = 1

    def create(self, validated_data):
        comment = validated_data.pop('comment')
        replyComment = ReplyLocationComment.objects.create(
            comment=comment, **validated_data)
        return replyComment
    
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['owner'] =[ data['owner']['email'], data['owner']['profile_image'] ]
        return data

    

class ReplyBlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply_BlogComment
        fields = ["id", "comment", "replyCommmentText", "owner", 'time_stamp']
        depth = 1

    def create(self, validated_data):
        comment = validated_data.pop('comment')
        replyComment = Reply_BlogComment.objects.create(
            comment=comment, **validated_data)
        return replyComment
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['owner'] =[ data['owner']['email'], data['owner']['profile_image'] ]
        return data

    

    

class FavoritesSerializer(serializers.ModelSerializer):
    # locationOwner = serializers.SerializerMethodField()

    class Meta:
        model = Favorites_Location
        fields = ["id", 'location', 'time_stamp', 'owner', ]
        depth = 1

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["owner"] = [data['owner']['email'], data['owner']['profile_image'] ]
        return data


