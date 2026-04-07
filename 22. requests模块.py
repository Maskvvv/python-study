import requests
import json

print("=" * 50)
print("Python requests 模块演示 - HTTP 请求")
print("=" * 50)

BASE_URL = 'https://httpbin.org'

# 1. GET 请求 - 基础
print("\n【1. GET 请求 - 基础】")
response = requests.get(f'{BASE_URL}/get')
print(f"状态码: {response.status_code}")
print(f"响应类型: {type(response)}")
print(f"响应内容 (前100字符): {response.text[:100]}...")

# 2. GET 请求 - 带参数
print("\n【2. GET 请求 - 带参数】")
params = {'name': 'Python', 'version': '3.12'}
response = requests.get(f'{BASE_URL}/get', params=params)
print(f"请求URL: {response.url}")
data = response.json()
print(f"参数: {data['args']}")

# 3. POST 请求 - 表单数据
print("\n【3. POST 请求 - 表单数据】")
form_data = {'username': 'admin', 'password': '123456'}
response = requests.post(f'{BASE_URL}/post', data=form_data)
result = response.json()
print(f"表单数据: {result['form']}")

# 4. POST 请求 - JSON 数据
print("\n【4. POST 请求 - JSON 数据】")
json_data = {'name': '测试用户', 'age': 25, 'skills': ['Python', 'Java']}
response = requests.post(f'{BASE_URL}/post', json=json_data)
result = response.json()
print(f"JSON数据: {result['json']}")

# 5. 自定义请求头
print("\n【5. 自定义请求头】")
headers = {
    'User-Agent': 'MyPythonApp/1.0',
    'Accept': 'application/json',
    'X-Custom-Header': 'CustomValue'
}
response = requests.get(f'{BASE_URL}/headers', headers=headers)
result = response.json()
print(f"请求头: {result['headers']}")

# 6. 响应对象属性
print("\n【6. 响应对象属性】")
response = requests.get(f'{BASE_URL}/get')
print(f"状态码: {response.status_code}")
print(f"编码: {response.encoding}")
print(f"Cookies: {response.cookies}")
print(f"响应头: {dict(response.headers)}")
print(f"是否成功: {response.ok}")

# 7. 处理 JSON 响应
print("\n【7. 处理 JSON 响应】")
response = requests.get(f'{BASE_URL}/json')
json_result = response.json()
print(f"JSON内容: {json_result}")

# 8. 超时设置
print("\n【8. 超时设置】")
try:
    response = requests.get(f'{BASE_URL}/delay/1', timeout=2)
    print(f"请求成功，状态码: {response.status_code}")
except requests.Timeout:
    print("请求超时!")
except requests.RequestException as e:
    print(f"请求错误: {e}")

# 9. 异常处理
print("\n【9. 异常处理】")
try:
    response = requests.get('https://httpbin.org/status/404')
    response.raise_for_status()
except requests.HTTPError as e:
    print(f"HTTP错误: {e}")
except requests.ConnectionError:
    print("连接错误!")
except requests.Timeout:
    print("请求超时!")
except requests.RequestException as e:
    print(f"请求异常: {e}")

# 10. Session 会话
print("\n【10. Session 会话】")
session = requests.Session()
session.headers.update({'User-Agent': 'MySession/1.0'})

response1 = session.get(f'{BASE_URL}/cookies/set/session_cookie/test123')
print(f"设置Cookie后: {session.cookies.get_dict()}")

response2 = session.get(f'{BASE_URL}/cookies')
print(f"访问Cookie: {response2.json()['cookies']}")

session.close()

# 11. Cookie 操作
print("\n【11. Cookie 操作】")
cookies = {'user_id': '12345', 'token': 'abcxyz'}
response = requests.get(f'{BASE_URL}/cookies', cookies=cookies)
print(f"发送的Cookie: {response.json()['cookies']}")

# 12. 文件上传
print("\n【12. 文件上传】")
files = {'file': ('test.txt', '这是文件内容\nHello World!', 'text/plain')}
response = requests.post(f'{BASE_URL}/post', files=files)
result = response.json()
print(f"上传文件名: {result['files']['file']}")

# 13. 流式下载
print("\n【13. 流式下载】")
response = requests.get(f'{BASE_URL}/stream/5', stream=True)
print("流式数据:")
for i, line in enumerate(response.iter_lines()):
    if line:
        print(f"  行{i+1}: {line.decode('utf-8')[:50]}...")
        if i >= 2:
            print("  ...")
            break

# 14. 认证
print("\n【14. 基础认证】")
response = requests.get(f'{BASE_URL}/basic-auth/user/pass', auth=('user', 'pass'))
print(f"认证结果: {response.json()}")

# 15. PUT 请求
print("\n【15. PUT 请求】")
response = requests.put(f'{BASE_URL}/put', data={'key': 'value'})
print(f"PUT响应: {response.json()['form']}")

# 16. DELETE 请求
print("\n【16. DELETE 请求】")
response = requests.delete(f'{BASE_URL}/delete')
print(f"DELETE状态码: {response.status_code}")

# 17. PATCH 请求
print("\n【17. PATCH 请求】")
response = requests.patch(f'{BASE_URL}/patch', json={'field': 'updated'})
print(f"PATCH响应: {response.json()['json']}")

# 18. 重定向处理
print("\n【18. 重定向处理】")
response = requests.get(f'{BASE_URL}/redirect/2', allow_redirects=True)
print(f"最终URL: {response.url}")
print(f"重定向历史: {[r.url for r in response.history]}")

# 19. 代理设置
print("\n【19. 代理设置（示例）】")
print("""
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}
response = requests.get(url, proxies=proxies)
""")

# 20. 常用状态码说明
print("\n【20. 常用 HTTP 状态码】")
status_codes = {
    200: 'OK - 请求成功',
    201: 'Created - 资源创建成功',
    204: 'No Content - 无内容返回',
    301: 'Moved Permanently - 永久重定向',
    302: 'Found - 临时重定向',
    400: 'Bad Request - 请求错误',
    401: 'Unauthorized - 未授权',
    403: 'Forbidden - 禁止访问',
    404: 'Not Found - 资源不存在',
    500: 'Internal Server Error - 服务器错误',
    502: 'Bad Gateway - 网关错误',
    503: 'Service Unavailable - 服务不可用'
}
for code, desc in status_codes.items():
    print(f"  {code}: {desc}")

print("\n" + "=" * 50)
print("requests 模块演示完成！🎉")
print("=" * 50)
print("\n💡 提示: 此演示使用 httpbin.org 作为测试服务器")
print("   安装命令: pip install requests")
