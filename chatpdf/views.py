from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .chatutils import load_pdf,summarize_all_pdf,rag_message
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from fpdf import FPDF
from docx2pdf import convert
import os

# Create your views here.


@ensure_csrf_cookie
def file_upload(request):
   if 'bot_summary' not in request.session:
        request.session['bot_summary'] = []
   if 'uploaded_files' not in request.session:
        request.session['uploaded_files'] = []
                
   if request.method == 'POST' and request.FILES.get('pdffile'):
        # get uploaded file
        fs = FileSystemStorage(location=settings.MEDIA_ROOT) 
        uploaded_file = request.FILES.get('pdffile')
        
        # Process the uploaded file as needed and check pdf file type
        if uploaded_file and uploaded_file.content_type =='application/pdf':
            name = fs.save(uploaded_file.name, uploaded_file)
            
            url = fs.url(name)
            file_path = fs.path(name)
            pdf_content = load_pdf(file_path)
            
            summary = summarize_all_pdf(pdf_content[0].page_content)
            summary_text = summary['text']
           
            
            # Add bot response to session
            request.session['bot_summary'].append({'summary': summary_text})
            request.session['uploaded_files'].append({'pdf_upload':url})
            request.session.modified = True
            
            return JsonResponse({'uploaded_files': request.session['uploaded_files'],'bot_summary':request.session['bot_summary']},status=200)
        # Process DOCX file upload
        elif uploaded_file and uploaded_file.content_type =='application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # Process DOCX file upload
            name = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(name)
            pdf_filename = f"{name.split('.')[0]}.pdf"  
            print(pdf_filename)
            pdf_path = fs.location + '/' + pdf_filename  
            
            # Convert DOCX to PDF
            convert(file_path, pdf_path)

            # Clean up original DOCX file
            if os.path.exists(file_path):
                os.remove(file_path)

            # Get URL of the PDF file and process the file as pdf
            url = fs.url(pdf_filename)
            pdf_content = load_pdf(pdf_path)
            summary = summarize_all_pdf(pdf_content[0].page_content)
            summary_text = summary['text']
            
            
            request.session['bot_summary'].append({'summary': summary_text})
            request.session['uploaded_files'].append({'pdf_upload':url})
            request.session.modified = True
             
             # Return a JSON response with a summary
            return JsonResponse({'uploaded_files': request.session['uploaded_files'],'bot_summary':request.session['bot_summary']},status=200)
        elif uploaded_file and uploaded_file.content_type == 'text/plain':
           print("text/plain")
           name = fs.save(uploaded_file.name, uploaded_file)
           file_path = fs.path(name)
           pdf_filename = f"{name.split('.')[0]}.pdf"  
           print(pdf_filename)
           pdf_path = fs.location + '/' + pdf_filename
           print(pdf_path)  
           pdf = FPDF()
           pdf.add_page()
            
           pdf.set_font("Arial", size=12)
           with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                pdf.multi_cell(0, 8, txt=text)
           pdf.output(pdf_path)
           
           if os.path.exists(file_path):
                os.remove(file_path)
                
                
             # Get URL of the txt file and process the file as pdf
           url = fs.url(pdf_filename)
           pdf_content = load_pdf(pdf_path)
           summary = summarize_all_pdf(pdf_content[0].page_content)
           summary_text = summary['text']
        
           
           
           request.session['bot_summary'].append({'summary': summary_text})
           request.session['uploaded_files'].append({'pdf_upload':url})
           request.session.modified = True
            
           return JsonResponse({'uploaded_files': request.session['uploaded_files'],'bot_summary':request.session['bot_summary']},status=200)
    
    # Return an empty or error JSON response if not a POST request or file not found
   return JsonResponse({'error': 'File not uploaded or invalid request'}, status=400)
    


@ensure_csrf_cookie
def chat(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    if 'uploaded_files' not in request.session:
        request.session['uploaded_files'] = []

    if request.method == 'POST':
            user_message = request.POST.get('message')
            print(user_message)
            if user_message:
                bot_message = rag_message(user_message)
            
            # Add bot messages to session
                request.session['chat_history'].append({'role': 'bot', 'message': bot_message})
                request.session.modified = True
              
            
            return JsonResponse( {'chat_history': request.session['chat_history'],'uploaded_files': request.session['uploaded_files']},status=200)
    print(request.session['uploaded_files'])
    #print(request.session['chat_history'])
    #request.session.flush()
    return render(request, 'chatpdf/chat.html', {'uploaded_files': request.session.get('uploaded_files',[]),'chat_history': request.session.get('chat_history', [])})

