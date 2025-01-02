# 货物金额统计系统

## 项目设置

1. 安装 Git
   - 访问 [Git 官网](https://git-scm.com/downloads)
   - 下载并安装适用于 Windows 的最新版本
   - 安装时选择以下选项：
     * 将 Git 添加到系统环境变量 PATH
     * 选择默认的终端为 Windows 命令提示符
   - 安装完成后重启电脑或注销重新登录

2. 验证 Git 安装
   ```bash
   # 打开命令提示符或 PowerShell，运行：
   git --version
   ```

3. 配置 Git
   ```bash
   # 设置用户名和邮箱
   git config --global user.name "moyan0713"
   git config --global user.email "你的邮箱"
   ```

4. 初始化仓库
   ```bash
   # 在项目目录下运行：
   git init
   git add .
   git commit -m "first commit"
   git branch -M main
   ```

5. 关联远程仓库
   ```bash
   git remote add origin https://github.com/moyan0713/0713.git
   git push -u origin main
   ```

6. 使用自动上传脚本
   - 每次更新代码后运行 `auto_push.sh`
   - 脚本会自动处理代码提交和推送
   - 查看 `git_push.log` 了解上传详情

## 功能特性

- 货物数据管理
- Excel 数据导入
- 订单数据粘贴解析
- 自动计算金额
- 分类统计
- 数据导出

## 技术栈

- 前端：HTML, CSS, JavaScript
- 后端：Python, Flask
- 数据库：SQLite
- 自动化：Shell Script 