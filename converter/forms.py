from django import forms

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(widget=forms.FileInput({'class': 'custom-class'}))
