from django.urls import path, include
from . import views




urlpatterns = [
    path('main/', views.main_page, name='main_page'),
    path('chat/<session_identifier>', views.chat, name='chat'),
    path('formupload/<session_identifier>/', views.file_upload, name='formupload'),
    path('create_session/', views.create_session, name='create-session'),
    path('sessionId/<session_identifier>/', views.chat_session, name='chat-session'),
    path('delete/sessionId/<session_identifier>/', views.delete_session, name='delete-session'),
    
]
