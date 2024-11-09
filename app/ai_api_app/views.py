import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.http import JsonResponse
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CategoryForm, TitleForm, ResponseForm, ResponseUpdateForm
from .models import CustomUser, Category, Title, Response
import requests
import json
import os
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# ロガーの設定
logger = logging.getLogger(__name__)

class SignUpView(CreateView):
    """ユーザー登録ビュー"""
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def form_valid(self, form):
        """フォームが有効な場合の処理"""
        try:
            response = super().form_valid(form)
            logger.info(f"新規ユーザーが登録されました: {self.object.username}")
            return response
        except IntegrityError:
            logger.error(f"ユーザー登録に失敗しました: {form.cleaned_data['username']}")
            form.add_error(None, "このユーザー名は既に使用されています。")
            return self.form_invalid(form)

class CustomLoginView(LoginView):
    """カスタムログインビュー"""
    form_class = CustomAuthenticationForm
    template_name = 'login.html'
    
    def form_valid(self, form):
        """フォームが有効な場合の処理"""
        response = super().form_valid(form)
        logger.info(f"ユーザーがログインしました: {self.request.user.username}")
        return response

    def get_success_url(self):
        """ログイン成功時のリダイレクト先"""
        return reverse_lazy('category_list')

    def form_invalid(self, form):
        """フォームが無効な場合の処理"""
        logger.warning(f"ログイン失敗: {form.errors}")
        return super().form_invalid(form)

@login_required
def user_profile(request):
    """ユーザープロフィール編集ビュー"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                form.save()
                logger.info(f"ユーザープロフィールが更新されました: {request.user.username}")
                return redirect('user_profile')
            except Exception as e:
                logger.error(f"プロフィール更新中にエラーが発生しました: {str(e)}")
                form.add_error(None, "プロフィールの更新中にエラーが発生しました。")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'user_profile.html', {'form': form})

@login_required
def category_list(request):
    """カテゴリ一覧ビュー"""
    try:
        categories = Category.objects.filter(user=request.user)
        return render(request, 'category_list.html', {'categories': categories})
    except Exception as e:
        logger.error(f"カテゴリ一覧の取得中にエラーが発生しました: {str(e)}")
        return render(request, 'error.html', {'message': 'カテゴリ一覧の取得に失敗しました。'})

@login_required
def category_create(request):
    """カテゴリ作成ビュー"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save(commit=False)
                category.user = request.user
                category.save()
                logger.info(f"新しいカテゴリが作成されました: {category.name}")
                return redirect('category_list')
            except IntegrityError:
                logger.error(f"カテゴリ作成に失敗しました: {form.cleaned_data['name']}")
                form.add_error(None, "同名のカテゴリが既に存在します。")
            except Exception as e:
                logger.error(f"カテゴリ作成中にエラーが発生しました: {str(e)}")
                form.add_error(None, "カテゴリの作成中にエラーが発生しました。")
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form})

@login_required
def category_update(request, pk):
    """カテゴリ更新ビュー"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                form.save()
                logger.info(f"カテゴリが更新されました: {category.name}")
                return redirect('category_list')
            except IntegrityError:
                logger.error(f"カテゴリ更新に失敗しました: {form.cleaned_data['name']}")
                form.add_error(None, "同名のカテゴリが既に存在します。")
            except Exception as e:
                logger.error(f"カテゴリ更新中にエラーが発生しました: {str(e)}")
                form.add_error(None, "カテゴリの更新中にエラーが発生しました。")
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form})

@login_required
def category_delete(request, pk):
    """カテゴリ削除ビュー"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        try:
            category.delete()
            logger.info(f"カテゴリが削除されました: {category.name}")
            return redirect('category_list')
        except Exception as e:
            logger.error(f"カテゴリ削除中にエラーが発生しました: {str(e)}")
            return render(request, 'error.html', {'message': 'カテゴリの削除に失敗しました。'})
    return render(request, 'category_confirm_delete.html', {'category': category})

@login_required
def title_list(request, category_id):
    """タイトル一覧ビュー"""
    try:
        category = get_object_or_404(Category, pk=category_id, user=request.user)
        titles = Title.objects.filter(category=category, user=request.user)
        return render(request, 'title_list.html', {'category': category, 'titles': titles})
    except Exception as e:
        logger.error(f"タイトル一覧の取得中にエラーが発生しました: {str(e)}")
        return render(request, 'error.html', {'message': 'タイトル一覧の取得に失敗しました。'})

@login_required
def title_create(request, category_id):
    """タイトル作成ビュー"""
    category = get_object_or_404(Category, pk=category_id, user=request.user)
    if request.method == 'POST':
        form = TitleForm(request.POST)
        if form.is_valid():
            try:
                title = form.save(commit=False)
                title.user = request.user
                title.category = category
                title.save()
                logger.info(f"新しいタイトルが作成されました: {title.name}")
                return redirect('title_list', category_id=category_id)
            except IntegrityError:
                logger.error(f"タイトル作成に失敗しました: {form.cleaned_data['name']}")
                form.add_error(None, "同名のタイトルが既に存在します。")
            except Exception as e:
                logger.error(f"タイトル作成中にエラーが発生しました: {str(e)}")
                form.add_error(None, "タイトルの作成中にエラーが発生しました。")
    else:
        form = TitleForm(initial={'category': category})
    return render(request, 'title_form.html', {'form': form, 'category': category})

@login_required
def title_update(request, pk):
    """タイトル更新ビュー"""
    title = get_object_or_404(Title, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TitleForm(request.POST, instance=title)
        if form.is_valid():
            try:
                form.save()
                logger.info(f"タイトルが更新されました: {title.name}")
                return redirect('title_list', category_id=title.category.id)
            except IntegrityError:
                logger.error(f"タイトル更新に失敗しました: {form.cleaned_data['name']}")
                form.add_error(None, "同名のタイトルが既に存在します。")
            except Exception as e:
                logger.error(f"タイトル更新中にエラーが発生しました: {str(e)}")
                form.add_error(None, "タイトルの更新中にエラーが発生しました。")
    else:
        form = TitleForm(instance=title)
    return render(request, 'title_form.html', {'form': form, 'category': title.category})

@login_required
def title_delete(request, pk):
    """タイトル削除ビュー"""
    title = get_object_or_404(Title, pk=pk, user=request.user)
    if request.method == 'POST':
        try:
            category_id = title.category.id
            title.delete()
            logger.info(f"タイトルが削除されました: {title.name}")
            return redirect('title_list', category_id=category_id)
        except Exception as e:
            logger.error(f"タイトル削除中にエラーが発生しました: {str(e)}")
            return render(request, 'error.html', {'message': 'タイトルの削除に失敗しました。'})
    return render(request, 'title_confirm_delete.html', {'title': title})

@login_required
def response_list(request, title_id):
    """回答一覧ビュー"""
    try:
        title = get_object_or_404(Title, pk=title_id, user=request.user)
        responses = Response.objects.filter(title=title, user=request.user)
        return render(request, 'response_list.html', {'title': title, 'responses': responses})
    except Exception as e:
        logger.error(f"回答一覧の取得中にエラーが発生しました: {str(e)}")
        return render(request, 'error.html', {'message': '回答一覧の取得に失敗しました。'})

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_claude_api(api_key, prompt):
    """Claude APIを呼び出す関数"""
    url = "https://api.anthropic.com/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }
    data = {
        "prompt": prompt,
        "model": "claude-v1",
        "max_tokens_to_sample": 1000,
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['completion']
    except requests.exceptions.RequestException as e:
        logger.error(f"Claude API呼び出し中にエラーが発生しました: {str(e)}")
        raise

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_chatgpt_api(api_key, prompt):
    """ChatGPT APIを呼び出す関数"""
    openai.api_key = api_key
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        logger.error(f"ChatGPT API呼び出し中にエラーが発生しました: {str(e)}")
        raise

def chunk_text(text, max_chunk_size=4000):
    """テキストを指定サイズのチャンクに分割する関数"""
    return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

def process_large_input(api_func, api_key, input_text):
    """大きな入力テキストを処理する関数"""
    chunks = chunk_text(input_text)
    results = []
    for chunk in chunks:
        result = api_func(api_key, chunk)
        results.append(result)
    return " ".join(results)

@login_required
def response_create(request, title_id):
    """回答作成ビュー"""
    title = get_object_or_404(Title, pk=title_id, user=request.user)
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.user = request.user
            response.title = title
            
            try:
                # APIキーをユーザーモデルから取得
                claude_api_key = request.user.claude_api_key
                chatgpt_api_key = request.user.chatgpt_api_key

                if not claude_api_key or not chatgpt_api_key:
                    raise ValueError("APIキーが設定されていません")

                # Claude APIを呼び出す
                if len(response.question) > 4000:
                    claude_response = process_large_input(call_claude_api, claude_api_key, response.question)
                else:
                    claude_response = call_claude_api(claude_api_key, response.question)
                response.claude_response = claude_response
                
                # ChatGPT APIを呼び出す
                chatgpt_prompt = f"以下の質問と回答を添削して下さい。ベストプラクティスでしょうか？\n質問内容：{response.question}\n回答：{claude_response}"
                if len(chatgpt_prompt) > 4000:
                    chatgpt_response = process_large_input(call_chatgpt_api, chatgpt_api_key, chatgpt_prompt)
                else:
                    chatgpt_response = call_chatgpt_api(chatgpt_api_key, chatgpt_prompt)
                response.chatgpt_response = chatgpt_response
                
                # Claude APIを再度呼び出して最終回答を生成
                final_prompt = f"質問: {response.question}\n\nClaudeの回答: {claude_response}\n\nChatGPTの回答: {chatgpt_response}"
                if len(final_prompt) > 4000:
                    final_response = process_large_input(call_claude_api, claude_api_key, final_prompt)
                else:
                    final_response = call_claude_api(claude_api_key, final_prompt)
                response.final_response = final_response
                
                response.save()
                logger.info(f"新しい回答が作成されました: タイトル '{title.name}' に対する回答")
                return redirect('response_detail', pk=response.pk)
            except ValueError as e:
                logger.error(f"回答作成中にエラーが発生しました: {str(e)}")
                form.add_error(None, str(e))
            except Exception as e:
                logger.error(f"API処理中にエラーが発生しました: {str(e)}")
                form.add_error(None, f"API処理中にエラーが発生しました: {str(e)}")
    else:
        form = ResponseForm(initial={'title': title})
    return render(request, 'response_form.html', {'form': form, 'title': title})

@login_required
def response_update(request, pk):
    """回答更新ビュー"""
    response = get_object_or_404(Response, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ResponseUpdateForm(request.POST, instance=response)
        if form.is_valid():
            try:
                form.save()
                logger.info(f"回答が更新されました: ID {response.id}")
                return redirect('response_list', title_id=response.title.id)
            except Exception as e:
                logger.error(f"回答更新中にエラーが発生しました: {str(e)}")
                form.add_error(None, "回答の更新中にエラーが発生しました。")
    else:
        form = ResponseUpdateForm(instance=response)
    return render(request, 'response_form.html', {'form': form, 'title': response.title})

@login_required
def response_delete(request, pk):
    """回答削除ビュー"""
    response = get_object_or_404(Response, pk=pk, user=request.user)
    if request.method == 'POST':
        try:
            title_id = response.title.id
            response.delete()
            logger.info(f"回答が削除されました: ID {pk}")
            return redirect('response_list', title_id=title_id)
        except Exception as e:
            logger.error(f"回答削除中にエラーが発生しました: {str(e)}")
            return render(request, 'error.html', {'message': '回答の削除に失敗しました。'})
    return render(request, 'response_confirm_delete.html', {'response': response})

@login_required
def response_detail(request, pk):
    """回答詳細ビュー"""
    try:
        response = get_object_or_404(Response, pk=pk, user=request.user)
        return render(request, 'response_detail.html', {'response': response})
    except Exception as e:
        logger.error(f"回答詳細の取得中にエラーが発生しました: {str(e)}")
        return render(request, 'error.html', {'message': '回答詳細の取得に失敗しました。'})