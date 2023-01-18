from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .forms import RoomForm, UserForm, MyUserCreationForm
from .models import Room, Topic, Message, User

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not Exist')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Password is incorrect')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'Account was created for '+ user.username)
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error has occured during registration')

    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)

def home(request):
    q = request.GET.get('q')
    rooms = Room.objects.all()
    if q:
        rooms = rooms.filter(
            Q(name__icontains=q) |
            Q(topic__name__icontains=q) |
            Q(description__icontains=q)
        )
    topic = Topic.objects.all()
    topic = topic[:5]
    room_count = rooms.count()

    msgs = Message.objects.all().order_by('-created')
    if q:
        msgs = msgs.filter(Q(room__topic__name__icontains=q))

    #limit the message body to 100 characters
    for msg in msgs:
        if len(msg.body)>50:
            msg.body = msg.body[:50] + '...'

    context = {'rooms': rooms, 'topics': topic, 'room_count': room_count, 'msgs': msgs}
    return render(request, 'base/home.html', context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    msgs = room.message_set.all().order_by('created')
    participants = room.participants.all()
    if request.method == 'POST':
        msg = request.POST.get('body')
        if msg != '':
            room.message_set.create(user=request.user, body=msg)
            room.participants.add(request.user)
            return redirect('room', pk=room.id)

    context = {'room': room, 'msgs': msgs, 'participants': participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    msgs = user.message_set.all()
    topics = Topic.objects.all()

    room_count = rooms.count()
    msg_count = msgs.count()

    context = {'user': user, 'rooms': rooms, 'msgs': msgs, 'topics':topics, 'room_count': room_count, 'msg_count': msg_count}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {'form': form}
    return render(request, 'base/update-user.html', context)

@login_required(login_url='login')
def createRoom(request):
    page = 'create'
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    context = {'form': form, 'topics': topics, 'page': page}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return redirect('home')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return redirect('home')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj': room}
    return render(request, 'base/delete.html', context)

@login_required
def deleteMessage(request, pk):
    msg = Message.objects.get(id=pk)
    room = msg.room.id
    if request.user != msg.user:
        return redirect('home')
    if request.method == 'POST':
        msg.delete()
        return redirect('room', pk=room)
    context = {'obj': msg}
    return render(request, 'base/delete.html', context)

def topicsPage(request):
    topics = Topic.objects.all()
    q = request.GET.get('q')
    if q:
        topics = topics.filter(
            Q(name__icontains=q)
        )
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    msgs = Message.objects.all().order_by('-created')
    msgs = msgs[:3]
    for msg in msgs:
        if len(msg.body)>50:
            msg.body = msg.body[:50] + '...'
    context = {'msgs': msgs}
    return render(request, 'base/activity.html', context)