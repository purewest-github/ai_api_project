from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import UserAPIKeysForm
from .models import UserAPIKeys
from statsd import StatsClient
from django.conf import settings
import time


@login_required
def api_keys_settings(request):
    user_api_keys, created = UserAPIKeys.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserAPIKeysForm(request.POST, instance=user_api_keys)
        if form.is_valid():
            form.save()
            return redirect('api_keys_settings')
    else:
        form = UserAPIKeysForm(instance=user_api_keys)
    
    return render(request, 'api_keys_settings.html', {'form': form})

@login_required
def use_api(request):
    try:
        user_api_keys = UserAPIKeys.objects.get(user=request.user)
        claude_api_key = user_api_keys.claude_api_key
        chatgpt_api_key = user_api_keys.chatgpt_api_key

        if not claude_api_key or not chatgpt_api_key:
            return JsonResponse({'error': 'API keys not set for this user'}, status=400)

        # ここでClaude APIとChatGPT APIを使用する処理を実装
        # 例: response = call_ai_api(claude_api_key, chatgpt_api_key, request.data)

        return JsonResponse({'success': True, 'data': 'API call successful'})
    except UserAPIKeys.DoesNotExist:
        return JsonResponse({'error': 'User API keys not found'}, status=404)


statsd = StatsClient(host=settings.STATSD_HOST, 
                     port=settings.STATSD_PORT, 
                     prefix=settings.STATSD_PREFIX)

def example_view(request):
    # リクエスト数をカウント
    statsd.incr('example_view.requests')

    start_time = time.time()

    # ここに実際の処理を記述
    # ...

    # 処理時間を記録
    duration = time.time() - start_time
    statsd.timing('example_view.duration', duration)

    return JsonResponse({"status": "success"})