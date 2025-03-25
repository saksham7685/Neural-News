from django.urls import path
from .views import RegisterUserView, LoginUserView, GetUserProfileView , GenreSelectionView ,DeleteUserView ,UpdateProfileView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('getProfile/', GetUserProfileView.as_view(), name='profile'), # GET Profile
    path("updateProfile/", UpdateProfileView.as_view(), name="update-profile"),  # PATCH profile
    path("deleteProfile/", DeleteUserView.as_view(), name="delete-user"),  # DELETE account
    path("select-genres/", GenreSelectionView.as_view(), name="select-genres"),
]