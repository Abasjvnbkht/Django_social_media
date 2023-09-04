from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm, EditUserForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .models import Relation, Profile


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'account/register.html'

    def dispatch(self, request, *args, **kwargs):
        # methode dispatch hamishe aval faal mishe bad unyeki methoda faal mishe
        # in bara in estefade mishe k age karbar az url bezane k berim logi age login shode bashe in nemizare
        if request.user.is_authenticated:
            # age karbar authenticate karde bud :
            return redirect('home:home')
        else:
            return super().dispatch(request, *args, **kwargs)
            # age nakarde bud ejaze bede bagiye barname edame pyda bokone yani methode post v get ham ejra beshe

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        # az tarige request b un etelaati k az tarige POST miad mitunam dastrasi dashe basham
        if form.is_valid():
            # etelaati k karbar feresade ro eteabr sanji bokon, age doros bud:
            cd = form.cleaned_data
            User.objects.create_user(
                cd['username'], cd['email'], cd['password1'])
            messages.success(request, 'you registered success', 'success')
            return redirect('home:home')
        return render(request, self.template_name, {'form': form})
        # age etelaat valid nabud


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'account/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd['username'], password=cd['password'])
            if user is not None:
                # age hamchin karbbari dashim:
                login(request, user)
                messages.success(request, 'you loged in success', 'success')
                if self.next:
                    # self.next yani age user login nakone va b jaei bere k login bekhad hamunja login kone dge b safhe asli bar nemigarde b ahamun safhe
                    # mire k unja login khase bud
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request, 'username or password wrong', 'warning')
            return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):
    # age karbar login nakarde bashe v bekhad varede logout az url beshe redirect mishe b safhe login
    # beshe in redirect mikone b safhe login

    # yeki az in paeini ha ro bayad bezarim baraye  LoginRequiredMixin
    # login_url = '/account/login/'
    # or in setting: LOGIN_URL = '/account/login/'

    def get(slef, request):
        logout(request)
        messages.success(request, 'you loged out successfully', 'success')
        return redirect('home:home')


class UserProfileView(LoginRequiredMixin, View):
    # fgt karbarayi k login kardan profile ro bebinan

    def get(self, request, user_id):
        is_following = False
        user = get_object_or_404(User, pk=user_id)
        posts = user.posts.all()
        # posts haman related name has
        relation = Relation.objects.filter(
            from_user=request.user, to_user=user)
        if relation.exists():
            is_following = True
        return render(request, 'account/profile.html', {'user': user, 'posts': posts, 'is_following': is_following})


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'
    success_url = reverse_lazy('account:password_reset_done')
    # bade anjam shodane karemun karbaro b koja befresam
    email_template_name = 'account/password_reset_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_done.html'


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class UserFollowView(LoginRequiredMixin, View):

    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(
            from_user=request.user, to_user=user)
        # from user: karbari k login karde / to_user:kesi k mikhaym followesh konim
        if relation.exists():
            # exist barrasi mikone k aya ye objecti dakhele database vujud dare ya na
            # v in fgt bara filter estefade mishe
            messages.error(request, 'you already following this user' 'danger')
        else:
            Relation(from_user=request.user, to_user=user).save()
            # Relation.objects.create(from_user=request.user, to_user=user)
            messages.success(request, 'you followed this user', 'success')
        return redirect('account:user_profile', user.id)
        # kollan barrasi mikonnim age rabete az abl vujud nadaseh bashe age vujud dash peyghame khaat mizanim


class UserUnfollowView(LoginRequiredMixin, View):

    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(
            from_user=request.user, to_user=user)
        if relation.exists():
            # age relation vujud dash:
            relation.delete()
            messages.success(request, 'you unfollowed taht user', 'success')
        else:
            messages.error(request, 'You R not folowing this user', 'danger')
        return redirect('account:user_profile', user.id)


class EditUserView(LoginRequiredMixin, View):
    form_class = EditUserForm

    def get(self, request):
        form = self.form_class(instance=request.user.profile, initial={
                               'email': request.user.email})
        # instance un etelaati hasesh k dakhele un modele vujud dare
        # initial unaei hasan kmezafiyan v mikhaym dasti khodemun dasti vared konim
        return render(request, 'account/edit_profile.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(
                request, 'profile edited dsuccessfully', 'success')
            return redirect('account:user_profile', request.user.id)
