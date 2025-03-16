from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import register_user, login_user, logout_user, ProfessorViewSet, ModuleViewSet, RatingViewSet

router = DefaultRouter()
router.register(r'professors', ProfessorViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = router.urls + [
    path('register/', register_user),
    path('login/', login_user),
    path('logout/', logout_user),
]

