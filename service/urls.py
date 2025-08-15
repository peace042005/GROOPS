from django.urls import path,include
from .views import (
    GroupClickCreateView,
    MyGroupsStatsView,
    RegisterUserView,
    ForgotPasswordView, 
    ResetPasswordView,
    GetUserConnect,
    VerifyCodeView,
    GroupViewSet,
    GroupFeedbackViewSet,
    GroupScrollViewSet,
    UtilisateurViewSet,
    CategorieListView,
    PaysListView,
    AllGroupViewSet,
    ProfileState,
    ModifyUserView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'groupes', GroupViewSet,basename='group')
router.register(r'feedbacks', GroupFeedbackViewSet)
router.register(r'scrolls', GroupScrollViewSet)
router.register(r'utilisateurs', UtilisateurViewSet,basename='user'),
router.register(r'utilisateurmodif',ModifyUserView,basename='usermodif' ),
router.register(r'allgroupes', AllGroupViewSet,basename='allgroup')

urlpatterns = [
    path("groups/<int:group_id>/click/", GroupClickCreateView.as_view(), name="group-click"),
    path("groups/mystats/", MyGroupsStatsView.as_view(), name="my-groups-stats"),
    path("groups/register/", RegisterUserView.as_view(), name="register"),
    path("groups/userconnect/", GetUserConnect.as_view(), name="user"),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
    path('verify_code/', VerifyCodeView.as_view()),
    path('categorie/', CategorieListView.as_view()),
    path('profilestate/', ProfileState.as_view()),
    path('pays/', PaysListView.as_view()),
     path('', include(router.urls)),
]
