from django.shortcuts import render,redirect
from django.http import  HttpResponse
from .models import ArticlePost,ArticleColumn
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import  Q
from comment.models import Comment
from comment.forms import  CommentForm
from django.views import View


class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')

def article_list(request):

    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    print(search,order,column,tag)
    article_list = ArticlePost.objects.all()
    if search:
        article_list = ArticlePost.objects.filter(Q(title__icontains=search)|Q(body__icontains=search))
    else:
        search=''
    if column is not None and column.isdigit():
        print('完成了')
        article_list = article_list.filter(column=column)

    if tag and tag !='None':
        article_list = article_list.filter(tags__name__in=[tag])

    if order == 'total_views':
        article_list = article_list.order_by('-total_views')
    paginator = Paginator(article_list,3)
    page=request.GET.get('page')
    #print(page)
    articles=paginator.get_page(page)

    context={'articles':articles,'order': order,'search':search,'column':column,'tag':tag}
    return render(request,'article/list.html',context)


def article_detail(request,id):
    article = ArticlePost.objects.get(id=id)
    article.total_views+=1
    article.save(update_fields=['total_views'])
    comments = Comment.objects.filter(article=id)
    comment_form = CommentForm()
    md=markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    article.body=md.convert(article.body.replace("\n", '  \n'))
    for comment in comments:
        comment.body = md.convert(comment.body.replace("\n", '  \n'))
    context={'article':article,'toc':md.toc,'comments':comments,'comment_form':comment_form,}
    return render(request,'article/detail.html',context)

@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        print('完成')
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST,request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中


            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            # 将新文章保存到数据库中
            if request.POST['column']!='none':
                new_article.column =  ArticleColumn.objects.get(id=request.POST['column'])

            new_article.save()
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = { 'article_post_form': article_post_form,'columns':columns }
        # 返回模板
        return render(request, 'article/create.html', context)

@login_required(login_url='/userprofile/login/')
def article_safe_delete(request,id):
    if request.method == "POST":
        print('完成')
        article=ArticlePost.objects.get(id=id)
        if request.user != article.author:
            return HttpResponse('对不起，您无权删除这篇文章!')
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse('仅允许post请求')


@login_required(login_url='/userprofile/login/')
def article_update(request,id):
    article = ArticlePost.objects.get(id=id)
    if request.user!=article.author:
        return HttpResponse('对不起，您无权修改这篇文章!')
    if request.method=='POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title=request.POST['title']
            article.body=request.POST['body']
            if request.POST['column'] !='none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column=None
            article.save()
            return redirect('article:article_detail',id=id)
        else :
            return HttpResponse('表单内容有误，请重新填写.')
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context={'article':article , 'article_post_form':article_post_form,'columns':columns,}
        return render(request,'article/update.html',context)





# Create your views here.
