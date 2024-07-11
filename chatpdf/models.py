from django.db import models
import uuid
from django.contrib.auth.models import User
# Create your models here.
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_identifier = models.UUIDField(default=uuid.uuid4)
    create_date = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return str(self.session_identifier)
    



class ChatSessionDocs(models.Model):
     session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
     document = models.FileField(upload_to='uploads')
     create_date = models.DateTimeField(auto_now_add=True)
     
     


class ChatSessionConversation(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    role = models.CharField(max_length=10)  # 'human' or 'ai'
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)



