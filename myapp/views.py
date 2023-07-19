from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.views import status
from rest_framework.permissions import IsAuthenticated
from .my_permission import IsOwnerOrReadOnly
from rest_framework import generics
from rest_framework.permissions import BasePermission
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
import pandas as pd
import numpy as np
import geopy
from math import sin, cos, sqrt, atan2, radians




class Recomendation:
    def __init__(self, lat, long, user,category):
        self.lat = lat
        self.long = long
        self.user = user
        self.categoty = category


    def calculator (self):
        print(">>><<<<",self.categoty)
        locations = LocationLiked.objects.all()
        print("Locations",locations)
        data = {
            "User" : [],
            "Destination" : [],
            "Like" : [],
            'Distance': [],
            'PriceRange': []  
        }

        for i in locations:
            likecount = len(LocationLiked.objects.filter(location = i.location))
            data["User"].append(i.owner.email)
            data["Destination"].append(i.location.locationName)
            data["Like"].append(likecount)
            if (i.location.price > 3000):
                data["PriceRange"].append("High")
            elif (i.location.price >1000 and i.location.price <=3000):
                data["PriceRange"].append("Medium")
            else:
                data["PriceRange"].append("Low")
            
            R = 6373.0
            lat1 = radians(self.lat)
            lon1 = radians(self.long)
            lat2 = radians(i.location.latitude)
            lon2 = radians(i.location.Longitude)
            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2.71 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c
            data["Distance"].append(12)


        print("DATA",data)

        # data = {
        #     'User': ['User1', 'User1', 'User2', 'User2', 'User3', 'User4'],
        #     'Destination': ['Dest1', 'Dest2', 'Dest1', 'Dest3', 'Dest2', 'Dest3'],
        #     'Like': [1, 1, 1, 1, 1, 1],
        #     'Distance': [5, 8, 3, 10, 6, 4],
        #     'PriceRange': ['Medium', 'High', 'Low', 'High', 'Medium', 'Low']
        # }


        df = pd.DataFrame(data)

        # Create user-destination interaction matrix
        interaction_matrix = df.pivot_table(index='User', columns='Destination', values='Like', fill_value=0)

        # Create a user-based recommendation function with distance and price range
        def user_based_recommendation(user, interaction_matrix, destinations_data, top_n=3):
            user_likes = interaction_matrix.loc[user]
            similar_users = []

            for user_id, user_row in interaction_matrix.iterrows():
                if user_id == user:
                    continue
                similarity = cosine_similarity(user_likes, user_row)
                similar_users.append((user_id, similarity))

            similar_users.sort(key=lambda x: x[1], reverse=True)
            top_similar_users = similar_users[:top_n]

            recommendations = []
            for user_id, _ in top_similar_users:
                user_likes = interaction_matrix.loc[user_id]
                user_destinations = user_likes[user_likes == 1].index.tolist()

                # Filter destinations based on distance and price range similarity
                for destination in user_destinations:
                    if destination in destinations_data.index:
                        similar_destinations = find_similar_destinations(destination, destinations_data, top_n)
                        recommendations.extend(similar_destinations)

            return list(set(recommendations))[:top_n]

        # Calculate similarity between users using cosine similarity
        def cosine_similarity(user1, user2):
            numerator = np.dot(user1, user2)
            denominator = np.linalg.norm(user1) * np.linalg.norm(user2)
            return numerator / denominator

        # Find destinations similar to a given destination based on distance and price range
        def find_similar_destinations(destination, destinations_data, top_n=2):
            distance_threshold = 2  # Set your desired threshold for distance similarity
            price_range_similarity = 1  # Set your desired similarity score for price range
            distance = destinations_data.loc[destination, 'Distance']
            price_range = destinations_data.loc[destination, 'PriceRange']

            similar_destinations = destinations_data[
                (destinations_data['Distance'] <= distance + distance_threshold) &
                (destinations_data['Distance'] >= distance - distance_threshold) &
                (destinations_data['PriceRange'] == price_range)
            ]

            similar_destinations = similar_destinations[similar_destinations.index != destination]

            # If there are fewer similar destinations than required, include all of them inmmendations
            if len(similar_destinations) < top_n:
                return similar_destinations.index.tolist()
            else:
                return similar_destinations.sample(n=top_n, replace=False).index.tolist()

        # Create the destinations_data DataFrame
        destinations_data = df.drop_duplicates(subset='Destination').set_index('Destination')

        # Example usage:
        
        recommendations = user_based_recommendation(self.user, interaction_matrix, destinations_data)
        return recommendations




# view for registering users
class RegisterView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @csrf_exempt
    def post(self, request):
        print("INCOMING DATA", request.data)
        is_exist = UserData.objects.filter(email=request.data['email'])
        if is_exist:
            return Response(status=status.HTTP_409_CONFLICT)
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



class UserView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    @csrf_exempt
    def get(self, request):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)

        user = UserData.objects.filter(email=request.user.email)
        result = UserSerializer(user, many=True)
        return Response(result.data)

    @csrf_exempt
    def put(self, request, format=None):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=400)

    def delete(self, request):
        user = UserData.objects.filter(email=request.user.email).delete()
        return Response(status=status.HTTP_200_OK)


        
class LocationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, format=None):
        result = Locations.objects.all()
        print("QWEQWEQWEQWWE", result)
        serializedResult = HiddenLocationSerializer(result, many=True)
        return Response(serializedResult.data)


    @csrf_exempt
    def post(self, request):
        print("incoming location DAta", request.data)
        result = HiddenLocationSerializer(data=request.data)

        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if result.is_valid():
            print("VALIDDD")
            result.save(owner=request.user)
            return Response(result.data, status=status.HTTP_201_CREATED)
        else:
            print(result.errors)
        

        return Response(status=status.HTTP_404_NOT_FOUND)


class DetailedLocationView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, pk, format=None):
        
        singleLocation = Locations.objects.get(id=pk)
        print("SIngle Location", singleLocation)
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializedSingleData = HiddenLocationSerializer(singleLocation)
        return Response(serializedSingleData.data, status=status.HTTP_200_OK)

    @csrf_exempt
    def put(self, request, pk, format=None):
        print("INCOMING PUT DATA", request.data, pk)
        singleLocation = Locations.objects.get(id=pk)

        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if not self.check_object_permissions(self.request, singleLocation):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializedSingleData = HiddenLocationSerializer(data=singleLocation)
        return Response(serializedSingleData.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        singleLocation = Locations.objects.get(id=pk)
        singleLocation.delete()
        return Response(status="Successfully Deleted")
    
    


# View for Blogs
class BlogView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, format=None):
        blogs = Blog.objects.all()
        serializedData = BlogSerializer(blogs, many=True)
        return Response(serializedData.data)

    @csrf_exempt
    def post(self, request):
        print("Incoming BLOG  Data", request.data)
        result = BlogSerializer(data=request.data)

        if result.is_valid():
            result.save(owner=request.user)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response(result.error, status=status.HTTP_400_BAD_REQUEST)


class BlogDetail(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, pk):

        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        blog = Blog.objects.get(id=pk)
        serializedData = BlogSerializer(blog)
        return Response(serializedData.data, status=status.HTTP_200_OK)

    @csrf_exempt
    def put(self, request, pk):
        blog = Blog.objects.get(id=pk)

        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if not self.check_object_permissions(self.request, blog):
            # IsOwnerOrReadOnly().has_object_permission(request, self, blog):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializedData = BlogSerializer(data=request.data, instance=blog)
        if serializedData.is_valid():
            serializedData.save(owner=request.user)
            return Response(serializedData.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        blog = Blog.objects.get(id=pk)

        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if blog.is_valid():
            blog.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


# Comment View Starts here
class CommentLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        comment = Comment_Location.objects.filter(
            location=Locations.objects.get(id=pk))
        serializedData = CommentLocationSerializer(comment, many=True)
        return Response(serializedData.data, status=status.HTTP_200_OK)

    @csrf_exempt
    def post(self, request, pk):
        print(pk)
        data = request.data
        location = Locations.objects.get(id=pk)
        serializedData = CommentLocationSerializer(data=data)
        if serializedData.is_valid():
            serializedData.save(owner=request.user, location=location)
            return Response(status=status.HTTP_200_OK)
        else:
            print(serializedData.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DeleteCommentLocationView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    

    def delete(self, request, pk):
        print("id request, ", request, pk, self.request.user)
        comment = Comment_Location.objects.get(id=pk)

        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        self.check_object_permissions(self.request, comment)
        comment.delete()
        return Response({'message': "successfully comment deleted"}, status=status.HTTP_200_OK)


class CommentBloggerView(APIView):
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def post(self, request, pk):
        blog = Blog.objects.get(id=pk)
        print("TESTTTTTT", pk, request.data, blog)

        serializedData = CommentBlogSerializer(data=request.data)
        if serializedData.is_valid():
            serializedData.save(owner=request.user, blog=blog)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        blog = Blog.objects.get(id=pk)
        comment = Comment_Blog.objects.filter(
            blog=blog
        )
        serializedData = CommentBlogSerializer(comment, many=True)
        return Response(serializedData.data, status=status.HTTP_200_OK)


class DeleteCommentBlogView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self, request, pk):
        print("IDD", pk)
        comment = Comment_Blog.objects.get(id=pk)
        print("Comment", comment)
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        self.check_object_permissions(self.request, comment)

        comment.delete()
        return Response({'message': "successfully comment deleted"}, status=status.HTTP_200_OK)


class LocationFavoritesView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        favLocation = Favorites_Location.objects.filter(owner=request.user)

        serializedData = FavoritesSerializer(favLocation, many=True)
        return Response(serializedData.data, status=status.HTTP_200_OK)

    @csrf_exempt
    def post(self, request, pk):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        location = Locations.objects.get(id=pk)
        data = Favorites_Location.objects.create(
            location=location, owner=request.user)
        serializeData = FavoritesSerializer(data)
        return Response(serializeData.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        fav = Favorites_Location.objects.get(id=pk)

        self.check_object_permissions(self.request, fav)

        fav.delete()
        return Response(status=status.HTTP_200_OK)


class ReplyLocationComments(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    @csrf_exempt
    def post(self, request,pk):
        print("incominng", request.data)
        print("USER", request.user)
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        locationComment = Comment_Location.objects.get(id=pk)
        
        serializedData = ReplyLocationcommentSerializer(data=request.data)
        
    
        if serializedData.is_valid():
            print("VALID")
            serializedData.save(owner=request.user, comment=locationComment)
            return Response(status=status.HTTP_200_OK)
        else:
            print(serializedData.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request, pk):
        print("RESULt",pk)
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        comment = Comment_Location.objects.get(id = pk)
        result = ReplyLocationComment.objects.filter(comment= comment)
        serialiezed = ReplyLocationcommentSerializer(result, many=True)
        return Response(serialiezed.data, status=status.HTTP_200_OK)
    
    
class ReplyLocationCommentDetail(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self, request,pk):
        print("DELETING")
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        reply = ReplyLocationComment.objects.get(id = pk)

        self.check_object_permissions(self.request,reply)
        reply.delete()

        return Response(status=status.HTTP_200_OK)

            


class ReplyBlogComment(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    @csrf_exempt
    def post(self, request, pk):
        print("INCOMING DATA", request.data)

        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        blogcomment = Comment_Blog.objects.get(id=pk)
        
        serializedData = ReplyBlogCommentSerializer(data=request.data)
        print("serailiezed DAta", serializedData)

        if serializedData.is_valid():
            print("VALID")
            serializedData.save(owner=request.user, comment=blogcomment)
            return Response(status=status.HTTP_200_OK)
        else:
            print(serializedData.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, pk):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
    
        blogComment = Comment_Blog.objects.get(id = pk)
        print("BLOG COMMENT", blogComment)

        replyComments = Reply_BlogComment.objects.filter(comment = blogComment)
        
        print("Reply Comment", replyComments)


        serializedData = ReplyBlogCommentSerializer(replyComments, many=True)
        return Response(serializedData.data, status = status.HTTP_200_OK)
        
        
    

class DeleteBlogReplyComment(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self,repquest, pk):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        repliedComment  = Reply_BlogComment.objects.get(id = pk)

        self.check_object_permissions(self.request, repliedComment)

        repliedComment.delete()
        return Response(status=status.HTTP_200_OK)



        
class LikeLocation(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def post(self,request,pk):
        print("LIKEDD")
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
    
        post = Locations.objects.get(id = pk)
        filteredlist = LocationLiked.objects.filter(location = post, owner = request.user)
        
        if len(filteredlist) > 0:
            likedItem = LocationLiked.objects.get(location=post , owner = request.user)
            print("LIKEDITEM", likedItem)
            likedItem.delete()
            return Response(status=status.HTTP_200_OK)
        
        LocationLiked.objects.create(location=post , owner = request.user)
        
        return Response(status=status.HTTP_200_OK)
        



            

class AiGenerator(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def post(self,request):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        latitude = request.data["latitude"]
        longitude = request.data["longitude"]
        category= request.data['category']
       
        print("Coords", latitude, longitude)

        listedLocations = Recomendation(lat= float( latitude), long=float( longitude), user=request.user.email, category=category).calculator()
        print("RESULT", listedLocations)
        
        finalLocationCollector = []
        for i in listedLocations:
            x = Locations.objects.filter(locationName = i)
            
            convertedlocation = Locations.objects.get(id= x[0].id)
            
            
            if convertedlocation.category == category:
                finalLocationCollector.append(convertedlocation)
                

            

        serializedData = HiddenLocationSerializer(finalLocationCollector,many = True)
        


        return Response( serializedData.data, status=200)







        





