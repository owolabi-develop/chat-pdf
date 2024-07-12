from . models import ChatSession

from django.forms import ModelForm


class ChatSessionForm(ModelForm):
    class Meta:
        model = ChatSession
        fields = ('name',)






