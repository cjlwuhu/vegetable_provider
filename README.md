# 智蔬供：基于图像识别的农产品供需发布平台

## 项目简介

智蔬供是一个将 **图像识别能力** 与 **农产品供需发布业务** 相结合的 Web 平台。用户可以上传蔬菜图片，系统调用 PyTorch 图像分类模型自动识别类别，并辅助完成供给信息发布。平台同时支持用户注册登录、供给信息发布、搜索筛选、分页浏览、个人发布管理、识别历史查看等功能。

本项目的重点不只是完成一个图片分类 demo，而是将 AI 推理接入真实业务流程，形成“**图片上传 → 模型推理 → 结果回填 → 信息发布 → 历史追踪**”的完整闭环。

---

## 项目背景

在农产品供需场景中，供货信息的录入通常依赖人工填写，存在分类繁琐、录入效率低的问题。  
本项目尝试通过图像分类模型自动识别蔬菜类别，减少用户手动选择分类的成本，并将识别结果接入信息发布流程，提升系统智能化程度。

---

## 功能特性

### 1. 用户模块
- 邮箱验证码注册
- 用户登录 / 退出登录
- 登录状态校验
- 登录后才能进行发布、编辑、删除、查看个人记录等操作

### 2. 农产品发布模块
- 发布供给信息
- 编辑自己的发布内容
- 删除自己的发布内容
- 查看“我的发布”
- 详情页展示供给信息

### 3. 图片识别模块
- 上传蔬菜图片
- 校验文件类型、大小和图片有效性
- 调用 PyTorch 模型完成图像分类
- 返回识别类别、置信度、Top-K 候选结果
- 自动回填分类到发布表单

### 4. 列表与检索模块
- 首页供给信息列表
- 按关键词搜索
- 按分类筛选
- 真分页查询
- 空结果提示

### 5. 识别历史模块
- 记录每次识别请求
- 保存识别结果、状态、置信度、Top-K、耗时等信息
- 支持查看“我的识别记录”

### 6. 权限与异常处理
- 用户只能编辑和删除自己的发布内容
- 资源不存在返回 404
- 越权操作返回 403
- 上传异常、数据库异常统一处理
- 数据库事务失败自动回滚

---

## 技术栈

### 后端
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Mail

### 数据库
- MySQL

### 前端
- Jinja2
- HTML / CSS / JavaScript
- jQuery
- Tailwind CSS

### AI 与图像处理
- PyTorch
- torchvision
- Pillow

---

## 项目架构

本项目采用 Flask 单体应用架构，按功能拆分为多个 Blueprint，整体结构如下：

- **表现层**：Jinja2 模板 + 静态资源
- **路由层**：按业务模块划分 Blueprint
- **业务层**：用户认证、信息发布、上传识别、搜索分页、历史记录
- **数据层**：SQLAlchemy ORM + MySQL
- **AI 推理层**：PyTorch 本地模型加载与推理

---

## 目录结构

```text
.
├── app/
│   ├── blueprints/
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── upload.py
│   │   └── vegetable.py
│   ├── decorators.py
│   ├── extensions.py
│   ├── models.py
│   └── __init__.py
├── dlmodel/
│   ├── __init__.py
│   └── model.pth
├── migrations/
├── static/
├── templates/
├── config.py
├── run.py
└── README.md
```

核心业务流程
1. 图片识别与信息发布流程
用户注册并登录系统
在发布页面上传蔬菜图片
后端校验文件类型、大小及图片有效性
系统调用 PyTorch 模型完成图像推理
返回识别类别、置信度与 Top-K 候选结果
自动回填分类信息到发布表单
用户补充价格、供应商、联系方式、产地等内容
提交后写入数据库并展示在首页列表
系统同步记录本次识别历史
2. 识别历史记录流程
用户上传图片触发识别
系统记录图片路径、识别结果、置信度、Top-K、推理耗时、状态和错误信息
用户可在“我的识别记录”页面查看历史结果
数据表设计
User

用于存储平台用户信息。

字段示例：

id
username
email
password_hash
VegetableCategory

用于存储蔬菜分类。

字段示例：

id
name
Vegetable

用于存储用户发布的农产品供给信息。

字段示例：

id
name
picture
content
price
provider
mobile
place
category_id
publisher_id
EmailCode

用于存储邮箱验证码信息。

字段示例：

id
email
code
created_at
PredictionRecord

用于记录每次图像识别请求。

字段示例：

id
user_id
image_path
predicted_category_name
confidence
top_k_json
latency_ms
status
error_message
created_at
本地运行方式
1. 克隆项目
git clone <your-repo-url>
cd <your-project-folder>
2. 创建虚拟环境并安装依赖
pip install -r requirements.txt
3. 配置环境变量

在项目根目录创建 .env 文件，填写数据库、邮箱等配置。
可参考 .env.example。

示例：

SECRET_KEY=your-secret-key

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=vegetable_provider

MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-mail-password
MAIL_DEFAULT_SENDER=your-email@example.com
4. 初始化数据库
flask db upgrade
5. 启动项目
python run.py
模型说明

本项目集成了基于 PyTorch 实现的蔬菜分类模型，用于识别用户上传的图片类别。
推理时会输出：

预测类别
置信度
Top-K 候选类别

为了提高推理结果的可解释性，系统对模型输出进行了 softmax 处理，并将概率最高的类别作为主预测结果返回给前端。

已完成的工程优化
1. 配置脱敏
数据库账号密码、邮箱授权码、SECRET_KEY 等敏感信息已迁移到环境变量
使用 .env 管理本地配置
使用 .env.example 作为模板文件
2. 上传安全校验
限制图片类型
限制上传大小
校验文件是否为真实图片
使用随机文件名保存图片，避免文件名冲突
3. 服务端表单校验
发布、编辑操作增加后端兜底校验
校验名称、价格、分类、图片等字段合法性
防止脏数据写入数据库
4. 数据库事务处理
捕获数据库约束异常
写入失败自动回滚
避免 session 进入异常状态
5. 权限控制
登录保护
用户只能查看、编辑、删除自己的发布内容
越权访问返回 403
6. 异常处理
404 页面兜底
403 页面兜底
上传失败、识别失败、数据库失败均有提示
7. 搜索与真分页
首页支持关键词搜索
支持分类筛选
支持分页查询并保留条件参数
8. AI 结果增强
除预测类别外，还返回置信度和 Top-K 候选
保存识别历史，支持用户回看推理结果
项目亮点
1. AI 能力落地到真实业务流程

本项目不是单独的图像分类 demo，而是将图像识别结果直接接入供给信息发布流程，形成完整业务闭环。

2. 识别结果更可解释

除了输出预测类别外，系统还展示置信度与 Top-K 候选结果，增强用户对模型输出的理解。

3. 具备较完整的 Web 工程能力

项目完成了登录认证、权限控制、服务端校验、搜索分页、异常处理、配置脱敏、文件上传安全校验等工程化能力建设。

4. 识别历史可追踪

系统对每次识别行为进行持久化存储，记录状态、耗时、结果和错误信息，增强了系统的可维护性与可分析性。

项目截图

建议补充以下截图，提升仓库展示效果：

首页列表页
发布页
图片识别结果展示
我的发布页
编辑发布页
我的识别记录页
后续优化方向
Docker 化部署
Redis 管理验证码与缓存
增加验证码发送频率限制
增加管理员审核后台
前后端分离重构（Vue / FastAPI）
将模型推理服务独立化部署
将识别结果展示由 alert 优化为页面内可视化模块