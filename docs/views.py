from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, TemplateView
from .models import DocumentInfo, HoldDocs, DocumentType
from django.urls import reverse, reverse_lazy
from .forms import FileFieldForm, NewDocInfo
import PyPDF2
import os
import fitz
from django import forms
from django.forms import HiddenInput, SelectDateWidget

#I'm going to put a new comment in here

class HomeView(TemplateView):
    template_name = 'home.html'
    #  template_name = 'index.html'


class TestView(UpdateView):
    model = HoldDocs
    fields = ['file_name', 'content']
    template_name = 'enter_document.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        context['pdfurl'] = self.get_object().file_name.url
        i = 4
        return context


class EnterDoctype(CreateView):
    model=DocumentType
    template_name = 'add_doc.html'
    # template_name = 'add-update-type.html'
    fields = ['doc_type']
    success_url = reverse_lazy('enter_doctype')



class DocumentCreate(CreateView):
    form_class = NewDocInfo
    model = DocumentInfo
    template_name = 'add_doc.html'
    success_url = reverse_lazy('home')

    def get_initial(self):
        initial = super(DocumentCreate, self).get_initial()
        initial['title'] = 'test entry III'
        initial['key_words'] = 'These are No Key Words'
        initial['doc_type'] = 3
        initial['file_name'] = 1
        initial['doc_ref_id'] = 'NA'
        return initial


class DocumentUpdate(UpdateView):
    model = DocumentInfo
    template_name = 'update_doc.html'
    fields = ['title', 'doc_date', 'doc_type', 'subject',
              'description', 'key_words', 'parties', 'file_name', 'restricted']
    success_url = reverse_lazy('search_documents')


class DocumentDelete(DeleteView):
    model = DocumentInfo
    success_url = reverse_lazy('home')


class HoldDocCreate(CreateView):
    model = HoldDocs
    template_name = 'update_doc.html'
    fields = '__all__'

class HoldDocUpdate(UpdateView):
    model = DocumentInfo
    form_class = NewDocInfo
    template_name = 'update_doc.html'
    success_url = reverse_lazy('search_documents')

    def get_context_data(self, **kwargs):
        context = super(HoldDocUpdate,self).get_context_data(**kwargs)
        pdf = context["object"].file_name
        docloc = settings.DOC_URL
        docloc = docloc + str(pdf)
        context["docloc"] = docloc
        return context



# Search with filter - view as list
def search_documents(request):
    docs = None
    if request.GET.get('search'):
        search = request.GET.get('search')
        docs = DocumentInfo.objects.filter(file_name__content__icontains=search)
    else:
        docs = DocumentInfo.objects.all()

    return render(request, 'search.html', {
        'docs': docs, 'docloc': settings.DOC_URL
    })


class FileFieldView(FormView):
    form_class = FileFieldForm
    template_name = 'multi_upload.html'
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        # save_path = "D:\\BIMC Docs Backup\\Temp\\"

        if form.is_valid():
            for f in files:
                doc = HoldDocs.objects.create(file_name=f)
                doc.save
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def update_content_field(request):
    MEDIA_ROOT = getattr(settings, "MEDIA_ROOT", None)
    qs = HoldDocs.objects.filter(content__isnull=True)
    for q in qs:
        file_loc = os.path.join(MEDIA_ROOT) + q.file_name.name
        pdfFileObj = open(file_loc, 'rb')
        pdfreader = PyPDF2.PdfFileReader(pdfFileObj)
        # printing number of pages in pdf file
        pages = pdfreader.numPages
        mytext = ""
        for pageObj in pdfreader.pages:
            mytext += pageObj.extractText()
        pdfFileObj.close()
        q.content = mytext
        q.old_file_name = 'Update V'
        q.save()

    return redirect('home')

"""
def miner_pdf_view(request):
    output_string = StringIO()
    MEDIA_ROOT = getattr(settings, "MEDIA_ROOT", None)
    qs = HoldDocs.objects.filter(content__isnull=True)
    for q in qs:
        in_file = os.path.join(MEDIA_ROOT) + q.file_name.name
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
        mytext = output_string.getvalue()
        q.content = mytext
        q.old_file_name = 'Miner_Update'
        q.save()
    return redirect('home')
"""

# testing PMUPDF

def fitz_pdf_view(request):
    MEDIA_ROOT = getattr(settings, "MEDIA_ROOT", None)
    qs = HoldDocs.objects.filter(content__isnull=True)
    for q in qs:
        filepath = os.path.join(MEDIA_ROOT) + q.file_name.name
        doc = fitz.open(filepath)
        mytext = ""
        for page in doc:
            mytext += page.getText()
        newtext = mytext.strip().replace('\n', ' ')
        q.content = newtext
        q.old_file_name = 'fritz update'
        q.save()
    return redirect('home')

from django.conf import settings


def show_pdf(request):
    msg = ""
    err = ""
    myform = NewDocInfo()
    #form = form_class
    if request.method == 'POST':
        form = NewDocInfo(request.POST)
        if form.is_valid():
            form.save()
        else:
            myform = form
    doc = HoldDocs.objects.defer("content").filter(processed=False)
    doc_count=doc.count()
    if doc_count == 0:
        msg = "No Documents to show"
        return redirect(reverse('home'))

    if request.GET.get('next'):
        docnum = int(request.GET.get('next'))
    else:
        docnum = 0

    nextdoc = docnum + 1
    if nextdoc > doc_count-1:
        nextdoc = doc_count - 1
        docnum = nextdoc
        msg = "Last document in list"
    if docnum > 0:
        prevdoc = docnum - 1
    else:
        prevdoc = 0
        msg = 'First document in list.'
    #  fix the name so we don't have to do string functions
    pdf = doc[docnum].file_name.name
    nextpk = doc[docnum].pk
    myform = NewDocInfo(initial={'title': pdf, 'description': 'any description', 'file_name': nextpk})
    docloc = settings.DOC_URL + pdf
    return render(request, 'ShowPDF.html', {'form': myform, "err": err, 'pdf': docloc, 'nextdoc': nextdoc, 'prevdoc': prevdoc, 'msg': msg})

def add_edit_doctype(request):
    edit_val=""
    if request.method == 'POST':
        tgt = request.POST['pk']
        if request.POST['todo'] == 'delete':
            x = DocumentType.objects.filter(pk=tgt)
            x.delete()
    doctypes=DocumentType.objects.all()
    return render(request, 'add-update-type.html', {'doctypes':doctypes, 'edit_val':edit_val})
