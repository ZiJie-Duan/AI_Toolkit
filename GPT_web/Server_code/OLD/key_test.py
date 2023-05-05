from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/auth', methods=['GET'])
def auth():
    # 从请求的 Cookie 中提取令牌
    token = request.cookies.get('token')

    # 检查令牌是否存在于您的存储系统中（例如数据库或 JSON 文件）
    is_valid = check_token(token)

    # 如果令牌有效，返回 HTTP 200 状态码，否则返回 HTTP 403 状态码
    if is_valid:
        return jsonify({"message": "Valid token"}), 200
    else:
        return jsonify({"message": "Invalid token"}), 403

def check_token(token):
    # 在这里实现您的令牌验证逻辑
    # 例如，从数据库或 JSON 文件中检查令牌是否存在
    # 如果令牌有效，返回 True；否则返回 False
    print("123")
    print(token)
    if token == "Mozhiao":

        return True
    else:
        return False


if __name__ == '__main__':
    app.run(host='localhost', port=5020)
