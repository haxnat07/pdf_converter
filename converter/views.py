import PyPDF2
import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import PDFUploadForm
from django.core.files.storage import default_storage
from django.core.mail import send_mail

import PyPDF2
import csv
import re
from io import StringIO

# Dev Phase S

def homepage(request):
    context = {}
    return render(request, 'homepage.html', context)

def about(request):
    context = {}
    return render(request, 'about.html', context)

def contact(request):
    context = {}
    return render(request, 'contact.html', context)

def mail_send(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        name_message = f"Name: {name}\nEmail: {email}\n\nMessage: {message}"
        print(name, email, subject, message)
    send_mail(
        subject,
        name_message,
        'umaisyaqoob333@gmail.com',
        ['umaisyaqoob333@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse("OK")


# Dev Phase E

def extract_text_from_pdf_to_csv(pdf_file_obj):
    reader = PyPDF2.PdfReader(pdf_file_obj)
    output = StringIO()
    csv_writer = csv.writer(output)
    
    for page_num in range(len(reader.pages) - 2):
        page = reader.pages[page_num]
        text = page.extract_text()

        # Find email addresses
        email_matches = re.findall(r'\S+@\S+', text)
        email = email_matches[0] if email_matches else ""
        
        lines = text.split('\n')
        email_index = lines.index(email) if email else 4

        # Extracting company info and billing info based on email index
        company_info = lines[:email_index + 1] if email_index else lines[:4]
        
        parts = company_info[0].split(' ')
        invoice_label = 'Invoice' if 'Invoice' in parts else ''
        company_info[0] = ' '.join(parts[:-1]) if invoice_label else company_info[0]
        
        # Writing company info to CSV
        for index, info_line in enumerate(company_info):
            if index == 0:
                csv_writer.writerow([info_line] + [''] * 3 + [invoice_label])
            else:
                csv_writer.writerow([info_line] + [''] * 3)
        
        csv_writer.writerow([])
        
        # Extracting and writing invoice and billing info
        invoice_start_index = next((i for i, line in enumerate(lines) if "Invoice no." in line), None)
        bill_to_index = next((i for i, line in enumerate(lines) if "Bill To" in line), None)
        
        bill_to_info = lines[bill_to_index:invoice_start_index] if bill_to_index else []
        invoice_info = lines[invoice_start_index:invoice_start_index+2] if invoice_start_index else []
        
        for line in lines:
            if "Invoice no." in line:
                bill_to, invoice_no = line.split("Invoice no.")
                csv_writer.writerow([bill_to.strip()] + ['', '', ''] + ["Invoice no. " + invoice_no.strip()])
            
            if "Date" in line:
                address, date = line.split("Date")
                csv_writer.writerow([address.strip()] + ['', '', ''] + ["Date " + date.strip()])
                

        description_index = next((i for i, line in enumerate(lines) if "Description" in line), None)

        if description_index:
            items_info = lines[invoice_start_index + 2:description_index] if description_index else []
        else:
            items_info = lines[invoice_start_index + 2:total_index] if total_index else []

        for item_line in items_info:
            csv_writer.writerow([item_line] + [''] * 5)

        # Writing items info
        csv_writer.writerow([''])
        csv_writer.writerow(['','Description', 'Qty', 'Unit price', 'Amount'])
        pattern = r'(Cleaning Services|Oven Cleaning|Ironing)\s+(\d+)\s+£(\d+\.\d+)\s+£(\d+\.\d+)'
        matches = re.findall(pattern, text)
        for match in matches:
            csv_writer.writerow([''] + list(match))

        # Write total amount if found
        #total_amount_match = re.search(r'Total\s+£(\d+\.\d+)', text)
        #if total_amount_match:
        #    csv_writer.writerow(['', 'Total', '', '', total_amount_match.group(1)])
            
        sub_total_line = None
        discount_line = None
        total_line = None


        for line in lines:
            if "Sub Total" in line:
                sub_total_line = line
            elif "Discount" in line:
                discount_line = line
            elif "Total" in line and "Sub Total" not in line:
                total_line = line


        if sub_total_line:
            csv_writer.writerow(['', '', '', ''] + [sub_total_line])

        if discount_line:
            csv_writer.writerow(['', '', '', ''] + [discount_line])

        if total_line:
            csv_writer.writerow(['', '', '', ''] + [total_line])


        csv_writer.writerow([])
        csv_writer.writerow([])
        footer_index = next((i for i, line in enumerate(lines) if "Thank you for choosing our services" in line), None)
        if footer_index is not None:
            csv_writer.writerow([lines[footer_index]])
            for _ in range(5):
                csv_writer.writerow([''])

    total_page = reader.pages[-2]
    text = total_page.extract_text()
    lines = text.split('\n')
    lines[0] = lines[0].replace('Inv N', 'InvN').replace('Sub Total', 'SubTotal')
    csv_writer.writerow([''] + list(lines[0].split(' ')))

    
    for line in lines[1:]:
        match = line.split(' ', 3)
        match = match[:-1] + match[-1].split(' £')
        match[-1] = '£' + match[-1]
        match[-2] = '£' + match[-2]
        csv_writer.writerow([''] + list(match))


    csv_writer.writerow([''])

    # Handling the last page for any final details
    last_page = reader.pages[-1]
    total = last_page.extract_text()
    total_lines = total.split('\n')
    for line in total_lines:
        csv_writer.writerow([''] + line.split(' '))

    output.seek(0)
    return output.getvalue()


from io import BytesIO

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            
            csv_data = extract_text_from_pdf_to_csv(pdf_file)
            
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
            
            return response
    else:
        form = PDFUploadForm()

    return render(request, 'index.html', {'form': form})