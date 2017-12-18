import uuid

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


def get_anonymous_group():
    group, created = Group.objects.get_or_create(name="anonymous")
    return group


def create_and_login_anonymous_user(request):
    username = uuid.uuid4().hex[:10]
    email = username + '@anonymous.com'
    password = uuid.uuid4().hex[:10]
    user = User.objects.create(username=username, email=email)
    user.set_password(password)  # this hashes the password properly
    user.save()
    user = authenticate(username=username, password=password)
    login(request, user)
    user.groups.add(get_anonymous_group())
    return user
