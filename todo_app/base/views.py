from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Login view
from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task

# Create your views here.

# My LoginView


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    model = Task
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('task-list')

# simple functionl view just to test connsection

# Register


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("task-list")

    # to make the user login
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

        # to restrict a authenticated user from entering the register page
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('task-list')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"  # else give as object_list

    # refining the context data because all the users were able to see each others todos
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        # also the count of incomplete items
        context['count'] = context['tasks'].filter(complete=False).count()

        search_item = self.request.GET.get('search-area') or ''
        if search_item:
            context['tasks'] = context['tasks'].filter(
                title__icontains=search_item)

            context['search_item'] = search_item
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    # context_object_name='task'
    template_name = "base/task.html"


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy("task-list")  # using url name

    # to associate the user automatically
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy("task-list")  # using url name


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("task-list")
