from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Post, Comment, Vote
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import PostCreateUpdateForm, CommentCreateForm, CommentReplyForm, PostSearchForm
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class HomeView(View):
    form_class = PostSearchForm

    def get(self, request):
        posts = Post.objects.all()
        if request.GET.get('search'):
            # methode GET ye chizi miad unchizi k dakhele prantez has ro baram begir(get) tu get age un chiizi k mikhaym ro nabud megdare none miare
            # get bara pythone v GET bara httprequest
            posts = posts.filter(body__contains=request.GET['search'])
            # tuye kodum fild bayad jostoju kone ? dakhele body dar Post
            # tuye postayi k bara man miad age dakheelsh chizi bia una ro filter bokon
            # tuye unhayi k bara man miad bia unaro filter bokon v un magadiiri bara mna biar k filter karde budam
            # __contains yani un megdari k karbar migarde mikham k dakhele body bashe ch aval ya akharesh
            # age ino nazanim bayad karbar bara search hamun chizi ro search kone k dar database save na kam na bish
            # in joze fieldlooksup dar models dajngo hasesh
            # dobare harchi k filter kardam ro mirizam dakhel posts va uno dar zir dakhele dict neshun dadim
        return render(request, 'home/index.html', {'posts': posts, 'form': self.form_class})


class PostDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(
            Post, pk=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)
        # post = Post.objects.get(pk=post_id, slug=post_slug)
        # balaei haman or_404 hasesh fgt mige age peyda kardi k hich nashod 404 bede

    def get(self, request, *args, **kwargs):
        comments = self.post_instance.pcomments.filter(is_reply=False)
        can_like = False
        if request.user.is_authenticated and self.post_instance.user_can_like(request.user):
            # age karbar login karde bud v posti k darim rush kar mikonim ro migiram v un method dakhele model ro seda mizanam yani un methode true feresade bud
            can_like = True
        return render(request, 'home/detail.html', {'post': self.post_instance, 'comments': comments,
                                                    'form': self.form_class, 'reply_form': self.form_class_reply, 'can_like': can_like})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            # kodom karbari in commenta ro sabt karde
            new_comment.post = self.post_instance
            # b kodum post has
            new_comment.save()
            messages.success(
                request, 'your comment is submited successfully', 'success')
            return redirect('home:post_detail', self.post_instance.id, self.post_instance.slug)


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if post.user.id == request.user.id:
            post.delete()
            messages.success(request, 'post deleted succeessfully', 'succeess')
        else:
            messages.error(request, 'yo cant delete this post', 'danger')
        return redirect('home:home')


class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def setup(self, request, *args, **kwargs):
        # setup etelaati k garare dakhele hame method ha estefade beshe ro dakhele khodesh zakire mikone k fgt ye bar be database vasl beshim
        # ino estefade mikonim k dakhele har method dge har bar bar datavbase ro seda nazanim
        # fgt yek bar b dataase vasl shim
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        # dakhele self zakhire mishe k gabele dastrasi bashe dar digare method ha
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if not post.user.id == request.user.id:
            messages.error(request, 'you cant upadte this post', 'danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
        # bade ejra dispatch akhar sar hatman bayad super ro return konim

    def get(self, request, *args, **kwargs):
        # b ellate tamiziye code b ja post_id args v kwrags minevisim
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'home/update.html', {'form': form})

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            # commit false yani felan dast negahdar va b database nade ino ta kami tagiyirate dge ham bezanam besh
            new_post.slug = slugify(form.cleaned_data['body'][:15])
            # slugify miad gavanine marbut b sklug ha ro b body matnemun ezafe mikone
            new_post.save()
            messages.success(request, 'updated is ok', 'success')
            return redirect('home:post_detail', post.id, post.slug)


class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, 'home/create.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:15])
            new_post.user = request.user
            # chon dakhele post ino moarefi kardim ba foreign key bayad ino ham moshakhas konim
            new_post.save()
            messages.success(request, 'you created a new post', 'success')
            return redirect('home:post_detail', new_post.id, new_post.slug)
        # b poste sakhte shode befres v id vslugeshoham mifresam


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        # aval khode poste ro migirim k bedunim b kodun post ijad mikonim
        comment = get_object_or_404(Comment, id=comment_id)
        # khode comment ro migirim k bedunim b kodun comment ijad mikonim
        form = self.form_class(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            # reply 2vomy dakhele modelhas
            reply.is_reply = True
            reply.save()
            messages.success(request, 'you replyed successfully', 'successs')
        return redirect('home:post_detail', post.id, post.slug)


class PostLikeView(LoginRequiredMixin, View):

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like = Vote.objects.filter(post=post, user=request.user)
        # inja darim chek mikonim k karbar gablan like karde budesh
        # un likaei ro bara man biar k marbut b in post has va user hamun kasi bashe k like karde
        if like.exists():
            # age hamchin chizi vujud dash:
            messages.error(
                request, 'you have already like this post', 'danger')
        else:
            Vote.objects.create(post=post, user=request.user)
            messages.success(request, 'you liked this post', 'success')
        return redirect('home:post_detail', post.id, post.slug)
