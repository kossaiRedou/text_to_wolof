from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/translate/',  views.api_translate,     name='api_translate'),
    path('api/synthesize/', views.api_synthesize,    name='api_synthesize'),
    path('api/generate/',   views.api_full_pipeline, name='api_generate'),
    path('api/history/',    views.api_history,       name='api_history'),
    path('api/credits/',    views.api_credits,       name='api_credits'),
    path('api/languages/',  views.api_languages,     name='api_languages'),
    path('api/debug/',      views.api_debug_auth,    name='api_debug'),
]
