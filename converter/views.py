import PyPDF2
import csv
from django.http import HttpResponse
from django.shortcuts import render
from .forms import PDFUploadForm
from django.core.files.storage import default_storage



def extract_text_from_pdf_to_csv(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    lines = []
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        if text:
            for line in text.split('\n'):
                lines.append([line])
    return lines


def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            file_name = default_storage.save(pdf_file.name, pdf_file)
            csv_lines = extract_text_from_pdf_to_csv(default_storage.open(file_name))
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
            writer = csv.writer(response)
            writer.writerows(csv_lines)
            return response
    else:
        form = PDFUploadForm()
    return render(request, 'index.html', {'form': form})


'''
def index(request):
    return render(request, 'index.html')
    '''