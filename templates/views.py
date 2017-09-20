from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Template as DjangoTemplate, Context
from django.contrib.auth.decorators import login_required
from django.views.defaults import permission_denied, page_not_found
from .storage import OverwriteStorage
from django.core.files.base import ContentFile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

# Create your views here.
from .models import *
from .tables import *

import chardet
import json


def index(request):
    # return redirect("login")
    return render(request, "templates/index.html")

def about(request):
    return render(request, "templates/about.html")


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("userprofile")
    else:
        form = UserCreationForm()
    return render(request, "templates/signup.html", {"form": form})

@login_required
def userprofile(request):
    user = request.user
    status = "Plain user"
    if user.is_staff:
        status = "Staff member"
    if user.is_superuser:
        status = "Superuser"
    # return HttpResponse("User profile: %s (%s)" %
    #                     (user.username, status))
    templates = Template.objects.filter(USER=user)
    pages = Page.objects.filter(USER=user)

    return render(request, "templates/userprofile.html",
                  {"username": user.username,
                   "status": status,
                   "templates": templates,
                   "pages": pages})


@login_required
def tempeditor(request):
    try:
        name = request.GET.get("name")
        create_new = int(request.GET.get("create_new", "0"))
        exists = Template.objects.filter(
            USER=request.user, TEMPLATE_NAME=name).exists()
        if exists == bool(create_new):
            return permission_denied(request, "You're attempting to create an existing"
                                        " page or edit a nonexistent one.")
        tpl = Template.objects.get_or_create(USER=request.user, TEMPLATE_NAME=name)
        if not tpl[1]:
            u = request.user
            filename = "templates/storage/%d-%s/%d-%s.html" % (u.id, u.username, tpl[0].id, tpl[0].TEMPLATE_NAME)
            st = OverwriteStorage()
            if not st.exists(filename):
                val = b"<b>Preview your template here.</b>"
            else:
                val = st.open(filename).read()
        else:
            val = b"<b>Preview your template here.</b>"
        enc = chardet.detect(val)["encoding"]
        val = val.decode(enc).encode("utf-8")
    except Exception as e:
        return HttpResponse(e)
    return render(request, "templates/tempedit.html",
                  {"name": name, "content": val})


@login_required
def temprender(request):
    if request.method != "POST" or (request.POST.get("template", None) is None):
        return page_not_found(request, "POST should be used")
    t = DjangoTemplate(request.POST["template"])    
    p = t.render(Context()) 
    print("P = %s" % p)
    return HttpResponse(p)

@login_required
def tempsave(request):
    if request.method != "POST" or (request.POST.get("template", None) is None) or (request.POST.get("name", None) is None):
        return page_not_found(request, "POST should be used")
    t = request.POST["template"]
    n = request.POST["name"]
    u = request.user
    tpl = Template.objects.get_or_create(USER=u, TEMPLATE_NAME=n)
    if tpl[1]:
        return permission_denied(request, "Something went wrong")
    tpl = tpl[0]
    filename = "templates/storage/%d-%s/%d-%s.html" % (u.id, u.username, tpl.id, tpl.TEMPLATE_NAME)
    OverwriteStorage().save(filename, ContentFile(t))
    return HttpResponse()

@login_required
def pageeditor(request):
    try:
        name = request.GET.get("name")
        create_new = int(request.GET.get("create_new", "0"))
        exists = Page.objects.filter(
            USER=request.user, PAGE_NAME=name).exists()
        if exists == bool(create_new):
            return permission_denied(request, "You're attempting to create an existing"
                                     " page or edit a nonexistent one.")
        pg = Page.objects.get_or_create(
            USER=request.user, PAGE_NAME=name)
        if not pg[1]:
            u = request.user
            filename = "templates/storage/%d-%s/%d-%s.json" % (
                u.id, u.username, pg[0].id, pg[0].PAGE_NAME)
            st = OverwriteStorage()
            if not st.exists(filename):
                val = b"[{\"key\": \"test\", \"value\": \"test\"}]"
            else:
                val = st.open(filename).read()
        else:
            val = b"[{\"key\": \"test\", \"value\": \"test\"}]"
        enc = chardet.detect(val)["encoding"]
        val = val.decode(enc).encode("utf-8")
        data = json.loads(val)
        table = PageTable(data)
    except Exception as e:
        return HttpResponse(e)
    return render(request, "templates/pageedit.html", {"table": table})


def pagerender(request, user_id, user_name, page_id, page_name):
    user_id = int(user_id)
    page_id = int(page_id)
    u = User.objects.get(id=user_id)
    assert(u.username == user_name)
    p = Page.objects.get(USER=u, PAGE_NAME=page_name)
    assert(p.id == page_id)
    jsonname = "templates/storage/%d-%s/%d-%s.json" % (user_id, user_name, page_id, page_name)
    ctx = json.loads(OverwriteStorage().open(jsonname).read())
    tpl = p.TEMPLATE
    filename = "templates/storage/%d-%s/%d-%s.html" % (
        tpl.USER.id, tpl.USER.username, tpl.id, tpl.TEMPLATE_NAME)
    return render(request, filename, ctx)
