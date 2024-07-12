from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .chatutils import load_pdf,summarize_all_pdf,rag_message,create_pinecone_index,delete_pinecone_index
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from fpdf import FPDF
from docx2pdf import convert
import os
from . models import ChatSession,ChatSessionConversation,ChatSessionDocs,Summary
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import ChatSessionForm
import json


# Create your views here.

@login_required
@ensure_csrf_cookie
def file_upload(request,session_identifier):
   user = request.user   
   session = get_object_or_404(ChatSession,session_identifier=session_identifier)             
   if request.method == 'POST' and request.FILES.get('pdffile'):
        # get uploaded file
        uploaded_file = request.FILES.get('pdffile')
        
        # Process the uploaded file as needed and check pdf file type
        if uploaded_file and uploaded_file.content_type =='application/pdf':
            ## ChatSessionDocs
          
            file = ChatSessionDocs.objects.create(session=session,document=uploaded_file)
             
            pdf_content = load_pdf(file.document.path,str(session))
            
            summary = summarize_all_pdf(pdf_content[0].page_content,str(session))
            ## create summary_text
            Summary.objects.create(session=session, summary= summary['text'])
            
            # get sessions uploaded file
            uploaded_file = [doc.document.url for doc in ChatSessionDocs.objects.filter(session=session).all()]
            # Add bot response to session
            return JsonResponse({'uploaded_files':uploaded_file,"bot_summary":summary['text']},status=200)
        # # Process DOCX file upload
        elif uploaded_file and uploaded_file.content_type =='application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # Process DOCX file upload
            file = ChatSessionDocs.objects.create(session=session,document=uploaded_file)
            filename =f"{file.document.path.split("\\")[-1].split('.')[0]}.pdf"
           
            pdf_path = f"{settings.MEDIA_ROOT}\\uploads\\{filename}" 
            print(pdf_path)
            
            # Convert DOCX to PDF
            convert(file.document.path, pdf_path)

            # # Clean up original DOCX file
            if os.path.exists(file.document.path):
                   os.remove(file.document.path)
                   
            instance_docx = ChatSessionDocs.objects.filter(session=session).first()
            instance_docx.document = pdf_path
            instance_docx.save(update_fields=['document'])

            # # Get path of the PDF file and process the file as pdf
            pdf_content = load_pdf(pdf_path,str(session))
            summary = summarize_all_pdf(pdf_content[0].page_content,str(session))
            summary_text = summary['text']
                
             # Return a JSON response with a summary
            return JsonResponse({'uploaded_files': {}},status=200)
        elif uploaded_file and uploaded_file.content_type == 'text/plain':
            
            # Process txt file upload
            print("text/plain")
            file = ChatSessionDocs.objects.create(session=session,document=uploaded_file)
            filename =f"{file.document.path.split("\\")[-1].split('.')[0]}.pdf"
            pdf_path = f"{settings.MEDIA_ROOT}\\uploads\\{filename}" 
            print(pdf_path)
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Arial", size=12)
            with open(file.document.path, "r", encoding="utf-8") as f:
                    text = f.read()
                    pdf.multi_cell(0, 8, txt=text)
            pdf.output(pdf_path)
            
            if os.path.exists(file.document.path):
                    os.remove(file.document.path)
                 
             # Get path of the txt file and process the file as pdf
            pdf_content = load_pdf(pdf_path,str(session))
            summary = summarize_all_pdf(pdf_content[0].page_content,str(session))
            summary_text = summary['text']
        
           
    
            
            return JsonResponse({'uploaded_files':{}},status=200)
    
    # Return an empty or error JSON response if not a POST request or file not found
   return JsonResponse({'error': 'File not uploaded or invalid request'}, status=400)
    


@login_required
def main_page(request):
     ## check if user have any session and redirect them
   
    sessions = ChatSession.objects.filter(user=request.user).all()
        
    return render(request, 'chatpdf/main.html',{"user_sessions":sessions})

@login_required
@ensure_csrf_cookie
def chat(request,session_identifier):
    session = get_object_or_404(ChatSession,session_identifier=session_identifier)   
    if request.method == 'POST':
            user_message = request.POST.get('message')
            ChatSessionConversation.objects.create(session=session, role='human', content=user_message)
            print(user_message)
            if user_message:
                bot_message = rag_message(user_message,str(session))
                print("bot",type(bot_message))
                ChatSessionConversation.objects.create(session=session, role='ai', content=bot_message['text'],page_number=bot_message['page'])
            
            human_message = [message.content for message in ChatSessionConversation.objects.filter(session=session, role='human')]
            
            ai_message = [message.content for message in ChatSessionConversation.objects.filter(session=session, role='ai')]
            print(ai_message)
            
            return JsonResponse( {'chat_history':{"human":human_message,"ai":bot_message}},status=200)
   
    return JsonResponse({'error': 'chat request'}, status=400)


@login_required
def create_session(request):
    user = request.user
    if request.method == 'POST':
        session_form = ChatSessionForm(request.POST)
        if session_form.is_valid():
            session = session_form.save(commit=False)
            session.user = user
            session.save()
            session_identifier = session.session_identifier
            create_pinecone_index(str(session_identifier))
            return HttpResponseRedirect(reverse("chat-session", args=(session_identifier,)))
    else:
        session_form = ChatSessionForm()
    return render(request, 'chatpdf/create_session.html', {'form': session_form})




@login_required
def chat_session(request, session_identifier):
    user= request.user
    session = get_object_or_404(ChatSession, session_identifier=session_identifier)
    ai_conversations = ChatSessionConversation.objects.filter(session=session,role='ai')
    human_conversations = ChatSessionConversation.objects.filter(session=session,role='human')
    
    print(":",ai_conversations)
    
    session_docs = ChatSessionDocs.objects.filter(session=session)
    try:
        ai_doc_summary = Summary.objects.filter(session=session).latest('create_date')
        return render(request, 'chatpdf/chat_session.html',{"current_session":session,
                                                            "session_doc":session_docs,
                                                            "ai_doc_summary":ai_doc_summary.summary,
                                                            "ai_conversations":ai_conversations,
                                                            "human_conversations":human_conversations})
    except:
        pass
    return render(request, 'chatpdf/chat_session.html',{"current_session":session,
                                                        "session_doc":session_docs,
                                                        "ai_conversations":ai_conversations, 
                                                        "human_conversations":human_conversations})


@login_required
def delete_session(request, session_identifier):
    user= request.user
    session = get_object_or_404(ChatSession, session_identifier=session_identifier)
    session.delete()
    delete_pinecone_index(str(session_identifier))
    return HttpResponseRedirect("/main/")
   


