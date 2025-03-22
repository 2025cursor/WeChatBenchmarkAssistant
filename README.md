# 微信公众号文章对比工具

一个用于获取和对比多个微信公众号最近文章的工具，支持 AI 选题推荐功能。

## 功能特点

- 🔍 批量获取多个公众号的最近文章
- 📅 自动筛选最近三天的文章
- 📝 显示文章标题、发布时间和内容摘要
- 🤖 AI 智能选题推荐（需要 DeepSeek API）
- 💾 自动保存配置信息
- 📋 一键复制文章标题和推荐选题

## 安装说明

1. 克隆项目并创建虚拟环境：
```bash
# 克隆项目
git clone [项目地址]
cd WeChatBenchmarkAssistant

# 创建并激活虚拟环境
uv venv
source .venv/bin/activate  # Unix/MacOS
# 或
.venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
uv pip install .
```

## 使用说明

1. 启动应用：
```bash
python run.py
```

2. 在浏览器中访问：
```
http://localhost:5001
```

3. 使用步骤：
   - 输入微信公众平台的 Token 和 Cookie
   - 添加要查询的公众号名称
   - 点击"开始查询"获取文章列表
   - 点击"AI推荐选题"获取智能选题建议

## AI 推荐功能配置

首次使用 AI 推荐功能时，需要配置 DeepSeek API：

1. 获取 DeepSeek API Key：
   - 访问 [DeepSeek 官网](https://deepseek.com)
   - 注册并获取 API Key

2. 配置 API Key：
   - 点击"AI推荐选题"按钮
   - 在弹出的配置窗口中输入 API Key
   - 点击保存即可使用

## 项目结构

```
wxdeveloper/
├── src/
│   └── wxdeveloper/
│       ├── __init__.py
│       ├── app.py          # Flask 应用主文件
│       ├── config.py       # 配置管理
│       └── templates/      # 前端模板
│           └── index.html  # 主页面
├── run.py                  # 启动脚本
├── pyproject.toml         # 项目依赖配置
└── README.md              # 项目说明
```

## 技术栈

- 后端：
  - Flask：Web 框架
  - BeautifulSoup4：文章内容解析
  - Requests：HTTP 请求
  - Python-dotenv：配置管理

- 前端：
  - Bootstrap 5：UI 框架
  - Font Awesome：图标库
  - Vanilla JavaScript：交互逻辑

## 注意事项

1. Token 和 Cookie 获取：
   - 登录微信公众平台
   - 从浏览器开发者工具中获取

2. API 限制：
   - 请遵守微信公众平台的使用规范
   - 合理控制请求频率

3. 数据安全：
   - Token 和 Cookie 保存在本地
   - API Key 保存在服务器配置文件中

## 开发计划

- [ ] 添加文章内容导出功能
- [ ] 支持更多 AI 模型选择
- [ ] 添加文章数据统计分析
- [ ] 优化文章内容提取算法
- [ ] 添加批量导出功能

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

MIT License 