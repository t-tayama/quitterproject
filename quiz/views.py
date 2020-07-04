from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone

from account.models import User

from .forms import QuizCreateForm, ContactCreateForm, ReportCreateForm
from .models import Quiz, Category, Tag, Answer, Contact
from .func import  get_quiz_dict


# ! コードはあえて冗長に書いています。注意 ！

# TODO お気に入り
# TODO Userモデルへフィールド追加（メールとお気に入り）


def home(request):
    """
    * ホーム画面（PV数降順５件、正答率昇順５件）
    """
    all_quiz_list = Quiz.objects.order_by('-created_at')
    quiz_dict = get_quiz_dict(all_quiz_list)

    pv_sorted_list = sorted(quiz_dict.items(), reverse=True, key=lambda x: x[1]['total_count'])[:5]
    correct_rate_sorted_list = sorted(quiz_dict.items(), reverse=True, key=lambda x: (x[1]['correct_rate'], x[1]['total_count']))[:5]

    context = {
        'pv_sorted_list': pv_sorted_list,
        'correct_rate_sorted_list': correct_rate_sorted_list
    }
    return render(request, 'quiz/home.html', context)



def index(request):
    """
    * 仮ホーム画面（最新5件リスト表示、作成日降順）
    """
    latest_quiz_list = Quiz.objects.order_by('-created_at')[:5]
    quiz_dict = get_quiz_dict(latest_quiz_list)
    context = {
        'quiz_dict': quiz_dict
        }
    return render(request, 'quiz/index.html', context)


class QuizListView(ListView):
    """
    * 問題一覧表示（全件リスト表示、作成日降順、１ページ10件）
    """
    model = Quiz
    context_object_name = 'quiz_list'
    template_name = 'quiz/list.html'
    ordering = ['-created_at']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_quiz_list = Quiz.objects.order_by('-created_at')
        quiz_dict = get_quiz_dict(all_quiz_list)
        context['quiz_dict'] = quiz_dict
        return context


class QuizSearchView(ListView):
    """
    * 検索結果表示（タイトル・問題文によるOR検索、作成日降順、１ページ10件）
    """
    model = Quiz
    template_name = 'quiz/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_quiz_list = Quiz.objects.order_by('-created_at')
        keyword = self.request.GET.get('keyword') # inputタグのname="keyword"が対応
        if keyword:
            search_list = all_quiz_list.filter(
                Q(title__icontains=keyword)|Q(text__icontains=keyword)
            )
            quiz_dict = get_quiz_dict(search_list)
            context['quiz_dict'] = quiz_dict
        return context


class QuizCategoryView(ListView):
    """
    * カテゴリによる絞り込み表示
    """
    model = Quiz
    template_name = 'quiz/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # category = get_object_or_404(Category, pk=self.kwargs['category_pk'])
        # queryset = Quiz.objects.order_by('-created_at').filter(category=category)
        category_pk = self.kwargs['category_pk']
        category_quiz_list = Quiz.objects.order_by('-created_at').filter(category__pk=category_pk)
        quiz_dict = get_quiz_dict(category_quiz_list)
        context['quiz_dict'] = quiz_dict
        return context


class QuizTagView(ListView):
    """
    * タグによる絞り込み表示
    """
    model = Quiz
    template_name = 'quiz/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # tag = get_object_or_404(Tag, pk=self.kwargs['pk'])
        # queryset = Quiz.objects.order_by('-created_at').filter(tag=tag)
        tag_pk = self.kwargs['tag_pk']
        tag_quiz_list = Quiz.objects.order_by('-created_at').filter(tag__pk=tag_pk)
        quiz_dict = get_quiz_dict(tag_quiz_list)
        context['quiz_dict'] = quiz_dict
        return context


@login_required
def detail(request, quiz_pk):
    """
    * 問題の詳細表示(回答フォーム)
    """
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    quiz_id = quiz.id
    answer = Answer.objects.filter(quiz=quiz.id) # 問題IDでフィルターした回答履歴
    total_count = answer.count() # 総回答数
    correct_count = answer.filter(is_correct=True).count() # 正解の回答数
    try:
        correct_rate =  f'{correct_count / total_count * 100:.1f}%'
    except ZeroDivisionError:
        correct_rate = f'まだ回答した方がいません。'
    context = {
        'quiz': quiz,
        'total_count':total_count,
        'correct_rate':correct_rate,
        }
    return render(request, 'quiz/detail.html', context)


@login_required
def answer(request, quiz_pk):
    """
    * 回答ボタンが押された際の処理
    * 問題の正解と選択された選択肢を比較し正誤判定
    * Answerテーブルへの保存
    """
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    answerer = request.user
    try:
        selected_value = request.POST['selected']
        if selected_value == quiz.correct_answer:
            is_correct = True
        else:
            is_correct = False
        answer = Answer.objects.create(
            quiz=quiz,
            answerer=answerer,
            selected_value=selected_value,
            is_correct=is_correct
        )
        answer.save()
        context = {
            'quiz': quiz,
        'is_correct': is_correct
        }
        return render(request, 'quiz/result.html', context)
    except KeyError:
        context = {
            'quiz': quiz,
            'error_message': 'いづれかを選択してください。'
        }
        return render(request, 'quiz/detail.html', context)


def result(request, quiz_pk):
    """
    * 正誤判定を表示
    """
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    context = {'quiz': quiz}
    return render(request, 'quiz/result.html', context)


@login_required
def create(request):
    """
    * Quizの新規作成
    """
    if request.method == "POST":
        form = QuizCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            quiz = form.instance
            return redirect('quiz:detail', quiz_pk=quiz.pk)
    else:
        form = QuizCreateForm()
    context = {
        'word': '作成',
        'form': form,
        }
    return render(request, 'quiz/quizform.html', context)


@login_required
def edit(request, quiz_pk):
    """
    * Quizの編集
    """
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    request_user = request.user
    quiz_author = quiz.author
    if request.method == 'POST':
        form = QuizCreateForm(request.POST, instance=quiz)
        if form.is_valid():
            form.instance.author = request.user
            form.instance.created_at = timezone.now()
            form.save()
            return redirect('quiz:detail', quiz_pk=quiz.pk)
    else:
        form = QuizCreateForm(instance=quiz)
    context = {
        'word': '編集',
        'form': form,
        'request_user': request_user,
        'quiz_author': quiz_author,
            }
    return render(request, 'quiz/quizform.html', context)


@login_required
def delete(request, quiz_pk):
    """
    * Quizの消去
    """
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    request_user = request.user
    quiz_author = quiz.author
    if request.method == 'POST':
        quiz.delete()
        return redirect('quiz:list')
    context = {
        'quiz': quiz,
        'request_user': request_user,
        'quiz_author': quiz_author,
    }
    return render(request, 'quiz/confirm_delete.html', context)


@login_required
def mypage(request):
    user = request.user
    created_quiz_list = Quiz.objects.filter(author=user).order_by('-created_at')
    quiz_dict = get_quiz_dict(created_quiz_list)
    answer_history = Answer.objects.filter(answerer=user).order_by('-answered_at')
    if request.method == 'POST':
        if 'favorite' in request.POST:
            context = {}
        elif 'created' in request.POST:
            context = {
                'quiz_dict': quiz_dict,
                       }
        elif 'answered' in request.POST:
            context = {
                'answer_history': answer_history,
                }
    else:
        context = {
            'quiz_dict': quiz_dict,
            'answer_history': answer_history,
        }
    return render(request, 'quiz/mypage.html', context)


def contact(request):
    if request.method == "POST":
        form = ContactCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quiz:postok')
    else:
        form = ContactCreateForm()
    context = {
            'form': form,
        }
    return render(request, 'quiz/contactform.html', context)


def postok(request):
    context = {
        'comment':'お問い合わせありがとうございました。',
        }
    return render(request, 'quiz/postok.html', context)


@login_required
def report(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    reporter = request.user
    if request.method == "POST":
        form = ReportCreateForm(request.POST)
        if form.is_valid():
            form.instance.reporter = request.user
            form.instance.quiz = quiz
            form.save()
            return redirect('quiz:postok')
    else:
        form = ReportCreateForm()
    context = {
        'form': form,
        'reporter':reporter,
        'quiz':quiz
        }
    return render(request, 'quiz/reportform.html', context)







