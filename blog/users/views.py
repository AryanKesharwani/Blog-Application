from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DetailView
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.generic.edit import FormView
from .models import EnquiryUser, CustomUser
from .forms import EnquiryForm  # make sure this is defined in forms.py
from posts.models import Post
from posts.models import Like



class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Registration successful. You can now log in.")
        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        messages.success(self.request, f"Welcome , {form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


class ProfileView(DetailView):
    model = CustomUser
    template_name = 'profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['posts'] = Post.objects.filter(author=user, is_published=True).order_by('-created_at')
        return context


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'my_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['profile_user'] = user
        context['posts'] = Post.objects.filter(author=user, is_published=True).order_by('-created_at')
        # context['total_likes'] = Like.objects.filter(post=)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('my_profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated.")
        self.object = form.save()
        return redirect('my_profile')

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('my_profile')
    success_message = "Your password was changed successfully."


class ContactView(FormView):
    template_name = 'contact.html'
    form_class = EnquiryForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        contact = form.save()

        # Send email to admin (customize as needed)
        send_mail(
            subject=f"New Contact Message from {contact.name}",
            message=(
                f"Name: {contact.name}\n"
                f"Email: {contact.email}\n"
                f"Contact: {contact.contact}\n"
                f"Subject: {contact.subject}\n\n"
                f"Message:\n{contact.message}"
            ),
            from_email='noreply@myblog.com',
            recipient_list=['admin@myblog.com'],
            fail_silently=True,
        )

        messages.success(self.request, "Your message has been sent successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors in the form.")
        return super().form_invalid(form)



# class PublicProfileView(DetailView):
#     model = CustomUser
#     template_name = 'profile.html'
#     slug_field = 'username'
#     slug_url_kwarg = 'username'
#     context_object_name = 'profile_user'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.get_object()
#         context['posts'] = Post.objects.filter(author=user, is_published=True).order_by('-created_at')
#         return context