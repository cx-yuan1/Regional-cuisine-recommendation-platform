"""
DeepSeek AI 美食推荐对话
流式输出，支持多轮对话
"""
import os
import json
import requests
from flask import Blueprint, request, Response, current_app
from app.models.food import Food
from app.utils.response import error

bp = Blueprint('ai', __name__, url_prefix='/api/ai')


def _build_food_context():
    """获取平台美食数据用于 AI 上下文"""
    foods = Food.query.order_by(Food.rating.desc(), Food.view_count.desc()).limit(80).all()
    items = []
    for f in foods:
        tags = []
        if f.taste_tags:
            try:
                tags = json.loads(f.taste_tags) if isinstance(f.taste_tags, str) else f.taste_tags
            except Exception:
                pass
        items.append({
            'id': f.id,
            'name': f.name,
            'region': f.region,
            'category': f.category.name if f.category else '',
            'price_range': f.price_range or '',
            'rating': float(f.rating) if f.rating else 0,
            'view_count': f.view_count or 0,
            'description': (f.description or '')[:200],
            'tags': tags[:5] if tags else []
        })
    return json.dumps(items, ensure_ascii=False, indent=2)


SYSTEM_PROMPT = """你是「地域美食」平台的智能美食推荐助手。根据用户的口味偏好、预算、地域等信息，从平台美食库中推荐合适的美食。

平台美食数据（JSON格式，包含id、name、region、category、price_range、rating、description、tags等）：
{food_context}

请用自然、友好的语气回复用户。推荐时：
1. 简要说明推荐理由
2. 可提及美食名称、地域、口味特点、价格区间
3. 若用户提到具体偏好（如辣、清淡、地域），优先匹配
4. 回复控制在200字以内，保持简洁
5. 不要编造平台不存在的美食，请严格基于上述数据推荐"""


@bp.route('/chat', methods=['POST'])
def chat():
    """
     DeepSeek 流式对话
     请求体: { "messages": [{"role":"user","content":"..."}] }
     返回: SSE 流
    """
    api_key = current_app.config.get('DEEPSEEK_API_KEY')
    if not api_key:
        return error('AI 服务未配置，请设置 DEEPSEEK_API_KEY 环境变量', code=503)
    
    data = request.get_json()
    if not data or not data.get('messages'):
        return error('请提供 messages 参数')
    
    messages = data['messages']
    if not isinstance(messages, list) or len(messages) == 0:
        return error('messages 格式错误')
    
    food_context = _build_food_context()
    system_content = SYSTEM_PROMPT.format(food_context=food_context)
    
    # 构建 DeepSeek 请求
    api_messages = [{"role": "system", "content": system_content}]
    for m in messages:
        if isinstance(m, dict) and m.get('role') and m.get('content'):
            api_messages.append({"role": m["role"], "content": m["content"]})
    
    url = current_app.config.get('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": api_messages,
        "stream": True,
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    def generate():
        try:
            # 绕过系统代理，直连 DeepSeek API（避免代理 SSL 错误）
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=60,
                proxies={'http': None, 'https': None}
            ) as r:
                r.raise_for_status()
                for line in r.iter_lines(decode_unicode=True):
                    if line and line.startswith('data:'):
                        chunk = line[5:].strip()
                        if chunk == '[DONE]':
                            yield f"data: {json.dumps({'done': True})}\n\n"
                            break
                        try:
                            obj = json.loads(chunk)
                            delta = obj.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
                        except json.JSONDecodeError:
                            continue
        except requests.RequestException as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )
