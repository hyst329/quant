from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader, Template as DjangoTemplate, Context
from django.contrib.auth.decorators import login_required
from django.views.defaults import permission_denied, page_not_found

# Create your views here.
from .models import *


def index(request):
    return redirect("login")


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
        Template.objects.get_or_create(USER=request.user, TEMPLATE_NAME=name)
    except Exception as e:
        return HttpResponse(e)
    return render(request, "templates/tempedit.html",
                  {"name": name})


@login_required
def temprender(request):
    if request.method != "POST" or (request.POST.get("template", None) is None):
        return page_not_found(request, "POST should be used")
    t = DjangoTemplate(request.POST["template"])
    p = t.render(Context()) 
    print("P = %s" % p)
    return HttpResponse(p)