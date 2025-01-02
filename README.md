# 货物金额统计系统

这是一个功能完整的货物管理和金额统计系统，采用前后端分离架构，使用Flask作为后端，纯HTML/CSS/JavaScript作为前端。系统支持货物数据的录入、管理、统计和导出功能。

## 功能特点

- 货物管理
  - 添加货物（名称、分类、单价、数量）
  - 批量导入货物数据（支持文本粘贴）
  - 编辑和删除货物信息
  - 按分类筛选货物
  - 搜索货物
  
- 数据统计
  - 自动计算单个货物金额
  - 显示货物总金额
  - 按分类统计金额
  - 分页显示货物列表
  
- 数据导出
  - 支持导出货物清单
  - 支持导出统计报表

## 技术栈

- 后端
  - Flask: Python Web框架
  - SQLite: 轻量级数据库
  - RESTful API: 前后端数据交互
  
- 前端
  - HTML5: 页面结构
  - CSS3: 页面样式（响应式设计）
  - JavaScript: 前端逻辑
  - Fetch API: 异步数据请求

## 安装和运行

1. 创建并激活Python虚拟环境（推荐）：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\\Scripts\\activate   # Windows
```

2. 安装Python依赖：
```bash
pip install -r requirements.txt
```

3. 运行后端服务器：
```bash
python app.py
# 或使用批处理文件
run_server.bat  # Windows
```

4. 在浏览器中访问：
```
http://localhost:5000
```

## 项目结构

```
.
├── app.py              # Flask后端应用主文件
├── frontend/          # 前端文件夹
│   ├── index.html    # 主页面
│   ├── styles.css    # 样式文件
│   └── script.js     # JavaScript逻辑
├── uploads/          # 上传文件目录
├── goods.db          # SQLite数据库文件
├── requirements.txt  # Python依赖
├── run_server.bat    # 服务器启动脚本
└── README.md         # 项目说明
```

## API接口说明

### 货物管理接口
- GET /api/goods - 获取货物列表
  - 支持分页参数：page, per_page
  - 支持筛选参数：category, search
- POST /api/goods - 添加新货物
- PUT /api/goods/<id> - 更新货物信息
- DELETE /api/goods/<id> - 删除指定货物

### 数据统计接口
- GET /api/statistics - 获取统计数据
  - 总金额
  - 分类统计
  - 时间段统计

## 使用指南

1. 首次使用
   - 系统启动后会自动创建数据库
   - 可以通过界面添加货物或批量导入数据

2. 数据录入
   - 单个添加：填写表单提交
   - 批量导入：复制数据到文本框，点击解析

3. 数据管理
   - 使用搜索框查找货物
   - 使用分类筛选器过滤显示
   - 点击编辑或删除按钮管理数据

4. 数据统计
   - 实时显示总金额
   - 查看分类统计数据
   - 导出统计报表

## 开发说明

1. 后端开发
   - 遵循RESTful API设计规范
   - 使用SQLite进行数据持久化
   - 实现了基本的CRUD操作

2. 前端开发
   - 采用响应式设计，适配不同设备
   - 使用原生JavaScript，无需框架
   - 实现了数据的异步加载和更新

## 更新日志

### v1.0.0 (2024-01-02)
- 初始版本发布
- 实现基本的货物管理功能
- 支持数据统计和导出

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。在提交代码前，请确保：
1. 代码符合项目的编码规范
2. 新功能有足够的测试覆盖
3. 文档已经更新

## 许可证

MIT License 