from flask import Flask, render_template, request, jsonify
import requests
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from . import config

# 配置日志
def setup_logger():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        'logs/wxdeveloper.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def get_article_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 查找文章主体内容
            content_div = soup.find('div', id='js_content')
            if content_div:
                # 移除所有script和style标签
                for script in content_div(["script", "style"]):
                    script.decompose()
                
                # 获取纯文本内容
                text_content = content_div.get_text(strip=True)
                # 限制内容长度，保留前500个字符
                return text_content[:500] + ('...' if len(text_content) > 500 else '')
            
            return "无法获取文章内容"
    except Exception as e:
        logger.error(f"获取文章内容失败: {str(e)}")
        return "获取文章内容失败"

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        token = data.get('token', '')
        cookie = data.get('cookie', '')
        accounts = data.get('accounts', [])

        if not all([token, cookie, accounts]):
            return jsonify({'error': '缺少必要参数'}), 400

        results = []
        three_days_ago = datetime.now() - timedelta(days=3)

        for account in accounts:
            try:
                logger.info(f"开始搜索公众号: {account}")
                
                # 1. 获取fakeid
                search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'
                headers = {
                    'Cookie': cookie,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                search_params = {
                    'action': 'search_biz',
                    'begin': 0,
                    'count': 5,
                    'query': account,
                    'token': token,
                    'lang': 'zh_CN',
                    'f': 'json',
                    'ajax': 1
                }

                logger.debug(f"搜索公众号请求参数: {search_params}")
                search_response = requests.get(search_url, headers=headers, params=search_params)
                logger.debug(f"搜索公众号响应状态码: {search_response.status_code}")
                logger.debug(f"搜索公众号响应内容: {search_response.text}")
                
                search_data = search_response.json()
                if search_data.get('base_resp', {}).get('ret') == 0 and search_data.get('list'):
                    fakeid = search_data['list'][0]['fakeid']
                    logger.info(f"获取到fakeid: {fakeid}")
                    
                    # 获取文章列表
                    articles_url = f"https://mp.weixin.qq.com/cgi-bin/appmsg"
                    params = {
                        'action': 'list_ex',
                        'begin': '0',
                        'count': '5',
                        'fakeid': fakeid,
                        'type': '9',
                        'token': token,
                        'lang': 'zh_CN',
                        'f': 'json',
                        'ajax': '1'
                    }

                    response = requests.get(articles_url, headers=headers, params=params)
                    articles_data = response.json()

                    if articles_data.get('base_resp', {}).get('ret') == 0:
                        for article in articles_data.get('app_msg_list', []):
                            publish_time = datetime.fromtimestamp(article['create_time'])
                            
                            if publish_time >= three_days_ago:
                                # 直接获取文章内容
                                content = get_article_content(article['link'])
                                
                                results.append({
                                    'account': account,
                                    'title': article['title'],
                                    'link': article['link'],
                                    'content': content,
                                    'publish_time': publish_time.strftime('%Y-%m-%d %H:%M:%S')
                                })
                else:
                    logger.warning(f"未找到公众号: {account}")
                    continue

            except Exception as e:
                logger.error(f"处理公众号 {account} 失败: {str(e)}")
                continue

        return jsonify(results)

    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/deepseek', methods=['GET', 'POST'])
def handle_deepseek_config():
    if request.method == 'GET':
        api_key = config.get_deepseek_api_key()
        return jsonify({'configured': bool(api_key)})
    else:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
        
        config.set_deepseek_api_key(api_key)
        return jsonify({'success': True})

@app.route('/recommend', methods=['POST'])
def recommend_titles():
    try:
        data = request.get_json()
        titles = data.get('titles', [])
        
        if not titles:
            return jsonify({'error': '没有找到文章标题'}), 400

        # 获取 API key
        api_key = config.get_deepseek_api_key()
        if not api_key:
            return jsonify({'error': 'DeepSeek API key not configured', 'code': 'API_KEY_REQUIRED'}), 400

        # 构建 prompt
        titles_text = "\n".join([f"- {title}" for title in titles])
        prompt = f"""你现在是一个文案编写大师，根据我提供你的文章标题，帮我推荐10个有价值的选题，符合我公众号自媒体的风格。

已有文章标题：
{titles_text}

请给出10个新的选题建议，要求：
1. 符合现有文章的风格和主题
2. 具有实用性和吸引力
3. 标题要有吸引力
4. 每个标题都要简洁明了
"""

        # 调用 DeepSeek API
        response = requests.post(
            'https://api.deepseek.com/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': prompt}
                ],
                'stream': False
            }
        )
        
        if response.status_code != 200:
            logger.error(f"DeepSeek API 调用失败: {response.text}")
            return jsonify({'error': 'AI 推荐失败'}), 500

        recommendations = response.json()
        content = recommendations.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # 处理返回的内容，提取标题
        titles = [line.strip().replace('- ', '') for line in content.split('\n') if line.strip() and line.strip().startswith('-')]
        
        return jsonify({'recommendations': titles})

    except Exception as e:
        logger.error(f"生成推荐标题失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 