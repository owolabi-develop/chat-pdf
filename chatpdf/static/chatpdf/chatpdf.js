//// pdf view function logic



document.addEventListener('DOMContentLoaded',loadPdf_document)
function loadPdf_document() {
    const pdfContainer = document.getElementById('pdf-container');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const pageNumSpan = document.getElementById('page-num');
    const goToPageInput = document.getElementById('go-to-page-input');
    const goToPageBtn = document.getElementById('go-to-page-btn');
    const zoomOutBtn = document.getElementById('zoom-out');
    const zoomInBtn = document.getElementById('zoom-in');
    const pdf_data_name = document.getElementById('pdf-data-name'); 
    
//     /// check for any save pdf links on localstorage a render it back to navbar
   
//     pdf_urls =  localStorage.getItem('pdf_urls')
//     if (pdf_urls && pdf_urls.length > 0){
//         pdf_url = pdf_urls.split(',')
    
//         let pdfurl_content = ""
//         for(let i=0; i < pdf_url.length; i++){
//         console.log(pdf_url[i])
//         pdfurl_content +=`
//         <ul>
//                 <li>
//                 <div class="pdf_url_div" onclick="loadPDF('${pdf_url[i]}')">
//                 ${pdf_url[i].replace('/media/','').slice(0,20)}</div>
//                 </li>
//         </ul>
//         `
//         }

//     document.getElementById('pdf_url').innerHTML = pdfurl_content;
   
// }else{
   
// }
 // / check for any save pdf links on localstorage a render it back to navbar

// // check for new _summary message in localstorage
// if (localStorage.getItem('new_summary')){
//     document.getElementById('chat-loader').style.display ="none";
//     document.getElementById('bot-summary').style.display ="block";
//     document.getElementById('bot-summary').innerHTML = localStorage.getItem('new_summary');
// }else{
//     document.getElementById('bot-summary').innerHTML = '';
// }
// // / check for new _summary message in localstorage 



    let pdfDoc = null;
    let scale = 1;
    let pageNum = 1;
    async function renderPage(num) {
        const page = await pdfDoc.getPage(num);
        const viewport = page.getViewport({ scale });
        const canvas = document.createElement('canvas');
        canvas.classList.add('pdf-page-canvas');
        canvas.id = `page-${num}`;
        const ctx = canvas.getContext('2d');

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: ctx,
            viewport
        };
        await page.render(renderContext).promise;

        pdfContainer.appendChild(canvas);
    }

    async function renderAllPages() {
        pdfContainer.innerHTML = '';  // Clear previous content
        for (let num = 1; num <= pdfDoc.numPages; num++) {
            await renderPage(num);
        }
        updatePageNumDisplay();
    }

    async function loadPDF(url) {
        // claer previous content localstorage  
        //sessionStorage.removeItem('pdfURL')

        const loadingTask = pdfjsLib.getDocument(url);
        pdfDoc = await loadingTask.promise;
        await renderAllPages();
        pdf_data_name.textContent = url.replace('/media/','');

        // // Store PDF URL in session
        // localStorage.setItem('pdfURL', url);
    }
    window.loadPDF = loadPDF;

    function updatePageNumDisplay() {
        pageNumSpan.textContent = `${pageNum}/${pdfDoc.numPages}`;

        // Store current page number in localStorage
        localStorage.setItem('pageNum', pageNum);
    }

    
    function scroll_to_page(currentPage){
        const targetPage = parseInt(currentPage);
        if (!isNaN(targetPage) && targetPage >= 1 && targetPage <= pdfDoc.numPages) {
            pageNum = targetPage;
            document.getElementById(`page-${pageNum}`).scrollIntoView({ behavior: 'smooth' });
            updatePageNumDisplay();
        }
        currentPage = '';
    }
 window.scroll_to_page = scroll_to_page;
 
    prevPageBtn.addEventListener('click', function() {
        if (pageNum > 1) {
            pageNum--;
            document.getElementById(`page-${pageNum}`).scrollIntoView({ behavior: 'smooth' });
            updatePageNumDisplay();
        }
    });

    nextPageBtn.addEventListener('click', function() {
        if (pageNum < pdfDoc.numPages) {
            pageNum++;
            document.getElementById(`page-${pageNum}`).scrollIntoView({ behavior: 'smooth' });
            updatePageNumDisplay();
        }
    });

    goToPageBtn.addEventListener('click', function() {
        const targetPage = parseInt(goToPageInput.value, 10);
        if (!isNaN(targetPage) && targetPage >= 1 && targetPage <= pdfDoc.numPages) {
            pageNum = targetPage;
            document.getElementById(`page-${pageNum}`).scrollIntoView({ behavior: 'smooth' });
            updatePageNumDisplay();
        }
        goToPageInput.value = '';
    });

    zoomOutBtn.addEventListener('click', () => {
        if (scale > 0.25) {
            scale -= 0.25;
            renderAllPages();
        }
    });

    zoomInBtn.addEventListener('click', () => {
        if (scale < 3) {
            scale += 0.25;
            renderAllPages();
        }
    });

    
      // Check if there is a stored PDF URL and page number in localStorage
      const storedPDFUrl = localStorage.getItem('pdfURL');
      const storedPageNum = localStorage.getItem('pageNum');
  
      if (storedPDFUrl) {
          loadPDF(storedPDFUrl).then(() => {
              if (storedPageNum) {
                  pageNum = parseInt(storedPageNum, 10);
                  scroll_to_page(pageNum);
              }
          });
      }


};



/// display pdf on sidebar
function retain_pdf_link_on_sidebar(pdf_url_name){

    let pdfurl_content = ""
    let urlarray = []

    // loop through uploaded files
    for (let i = 0; i < pdf_url_name.length; i++) {
        urlarray.push(pdf_url_name[i])
        localStorage.setItem("pdf_urls",urlarray)
        pdfurl_content +=`
        <ul>
                <li>
                <div class="pdf_url_div" onclick="loadPDF('${pdf_url_name[i]}')">
                ${pdf_url_name[i].replace('/media/uploads/','').slice(0,20)}</div>
                </li>
        </ul>
        `
        }

        document.getElementById('pdf_url').innerHTML = pdfurl_content;

}

/// bot typewriting effect function for initial summary
function startTypewriterEffect(botResponse, elementId) {
    let index = 0; // Current character index
    const letterDelay = 5; // Base delay between each character in milliseconds

    function type() {
      const currentText = botResponse.slice(0, index);
      document.getElementById(elementId).textContent = currentText;
      index++;

      if (index <= botResponse.length) {
        setTimeout(type, letterDelay + Math.random() * 5); 
      }
    }

    type(); // Start typing initially
  }


///   bot typewriting effect function for user messsage and bot response
  function bot_startTypewriterEffect(botResponse, elementId) {
    let index = 0; 
    const letterDelay = 5; 

    function type() {
      const currentText = botResponse.slice(0, index);
      document.getElementById(elementId).innerHTML = currentText;
      index++;
      document.getElementById(elementId).scrollIntoView()
      if (index <= botResponse.length) {
        setTimeout(type, letterDelay + Math.random() * 5); 
      }
    //   else {
    //     // Scroll to the new message element
    //     document.getElementById(elementId).scrollIntoView({ behavior: 'smooth', block: 'start' });
    //   }
    }

    type(); // Start typing initially
  }
  /// bot typewriting effect function

//// handle ajax file upload 

$(document).ready(function() {
    $('#file-upload').change(function(e) {  
        // clear the local storage and chat ui on new file upload

         // disable send message button
         document.getElementById('message-btn').disabled = true
         document.getElementById('message-btn').style.backgroundColor = "#d3d3d3";
         document.getElementById('message-btn').style.cursor = "not-allowed";


        // document.getElementById('bot-summary').innerHTML='';
        // document.getElementById('bot-summary').style.display ="none";
        document.getElementById('chat-bot-reponse-holder').innerHTML ='';
        localStorage.clear()
        /// get the file and crf_token
        let pdffile = this.files[0];
        let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();


        let formdata = new FormData();
        // append the file and crf_token to formdata
        formdata.append('pdffile', pdffile);
        formdata.append('csrfmiddlewaretoken', csrfToken);

        /// disable the upload button
        document.getElementById('file-upload').disabled = true
        /// show upload progress bar
        
        document.getElementById('droptext').style.display = "none";
        document.getElementById('file_loader').style.display = "block";

        /// waiting for bot response
        document.getElementById('chat-loader').style.display = "block";    
        

        /// send file upload the ajax request
         $.ajax({
            url: $('#form-upload').attr('action'),  
            type: 'POST',
            data: formdata,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log('File uploaded successfully');
               
                pdf_url_name = response['uploaded_files']
                console.log("file",pdf_url_name)

                retain_pdf_link_on_sidebar(pdf_url_name)
                
                 /// show upload progress bar
                 document.getElementById('file_loader').style.display = "none";
                 document.getElementById('droptext').style.display = "block";
                 // enable the upload button
                 document.getElementById('file-upload').disabled = false

                console.log(response['uploaded_files'][response['uploaded_files'].length - 1])
                // get the pdf file name from response and load it in the pdf viewer
                loadPDF(response['uploaded_files'][response['uploaded_files'].length - 1])

                // handle pdf bot_summary initial message
                pdf_bot_summary = response['bot_summary']
                console.log("arrayMes:",pdf_bot_summary)
                document.getElementById('chat-loader').style.display ="none";
                // document.getElementById('bot-summary').style.display ="block";
               
                 // handle pdf bot_summary initial message
                startTypewriterEffect(new_summary, 'bot-summary');
               
                

                // enable send message button
                document.getElementById('message-btn').disabled = false
                document.getElementById('message-btn').style.backgroundColor = "#1d67e6";
                document.getElementById('message-btn').style.cursor = 'pointer'
                
            },
            error: function(xhr, status, error) {
                 // Handle error response
                alert('Error uploading file. Could not read pdf'); 
                window.location.reload()              
            }
        });
        
    });

});


/// send chat message ajax

$(document).ready(function() {
    $('#chat-message-submit').on('submit',function(e) {
        document.getElementById('bot-thinking').style.display='block'
        document.getElementById('bot-thinking').scrollIntoViewIfNeeded()
       
        // handle user message send to bot
        // document.getElementById('bot_Respone_message').style.display ='none';
        document.getElementById('chat-bot-reponse-holder').innerHTML +=`
        <div id="user_message" class="user_message">
                  ${$('#chat-message').val()}
                </div>
                
        `;
        document.getElementById('user_message').scrollIntoViewIfNeeded()
       
 // handle user message send to bot

        e.preventDefault();
        // disable send message button
        document.getElementById('message-btn').disabled = true
        document.getElementById('message-btn').style.backgroundColor = "#d3d3d3";
        document.getElementById('message-btn').style.cursor = "not-allowed";
       
        let message = $('#chat-message').val();
        let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        // clear message input
        document.getElementById('chat-message').value = "";

        $.ajax({
            url: $('#chat-message-submit').attr('action'),
            type: 'POST',
            data: {
                'message': message,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                console.log('Message sent successfully');
                document.getElementById('bot-thinking').style.display='none';
                // enable send message button
                document.getElementById('message-btn').disabled = false;
                document.getElementById('message-btn').style.backgroundColor = "#1d67e6";
                document.getElementById('message-btn').style.cursor = 'pointer';
                console.log("bot",response['chat_history']);
               
                //window.location.reload()
                // Handle success response
               
                // bot_response_message_text = response['chat_history'][response['chat_history'].length - 1]['message']['text']
                // bot_response_message_page = response['chat_history'][response['chat_history'].length - 1]['message']['page']
              
                // const newMessageId = `bot_response_message_${Date.now()}`;
                // document.getElementById('chat-bot-reponse-holder').innerHTML +=`               
                //          <div id="${newMessageId}" class="bot_Respone_message shadow p-3 mb-2 bg-body-tertiary rounded p-3 h-auto d-inline-block">
                          
                //         </div>
                    
                // `;
                // bot_chat_response = ` <p>${bot_response_message_text}</p>
                //    <div onclick="scroll_to_page('${bot_response_message_page}')" class="scroll_to_page style="width:auto;">
                //     <p>${bot_response_message_page}</p>
                //     </div>`

                // bot_startTypewriterEffect(bot_chat_response,newMessageId)
                   
            },
            error: function(xhr, status, error) {
                // Handle error response
                alert('Error sending message');
                window.location.reload()
            }
        });
    });
});


   
  










