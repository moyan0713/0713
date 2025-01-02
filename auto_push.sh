#!/bin/bash

# 日志文件
LOG_FILE="git_push.log"

# 日志函数
log() {
    local message="[$(date "+%Y-%m-%d %H:%M:%S")] $1"
    echo "$message"
    echo "$message" >> "$LOG_FILE"
}

# 错误处理函数
handle_error() {
    log "错误: $1"
    exit 1
}

# 主函数
main() {
    log "开始自动上传到 GitHub..."

    # 检查是否是 Git 仓库
    if [ ! -d ".git" ]; then
        handle_error "当前目录不是 Git 仓库，请先初始化 Git"
    fi

    # 检查远程仓库是否配置
    if ! git remote -v | grep -q "origin"; then
        handle_error "未配置远程仓库，请先添加远程仓库"
    fi

    # 获取当前分支
    current_branch=$(git branch --show-current)
    if [ -z "$current_branch" ]; then
        handle_error "无法获取当前分支"
    fi

    # 检查是否有变更
    if [ -z "$(git status --porcelain)" ]; then
        log "没有需要提交的变更"
        exit 0
    fi

    # 添加变更
    log "添加变更文件..."
    git add . || handle_error "添加文件失败"

    # 提交变更
    log "提交变更..."
    git commit -m "自动提交：$(date "+%Y-%m-%d %H:%M:%S")" || handle_error "提交失败"

    # 拉取最新代码
    log "拉取最新代码..."
    git pull --rebase origin "$current_branch" || handle_error "拉取最新代码失败"

    # 推送到远程仓库
    log "推送到远程仓库..."
    git push origin "$current_branch" || handle_error "推送失败"

    log "完成！代码已成功上传到 GitHub。"
}

# 执行主函数
main "$@" 