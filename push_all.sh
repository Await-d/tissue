#!/bin/bash

# 添加所有更改
git add .

# 提交更改
git commit -m "修复应用启动问题：修正导入路径和缩进问题"

# 获取所有远程仓库
remotes=$(git remote)

# 获取当前分支
current_branch=$(git branch --show-current)
if [ -z "$current_branch" ]; then
  current_branch="main"
fi

echo "当前分支: $current_branch"
echo "远程仓库: $remotes"

# 推送到所有远程仓库
for remote in $remotes; do
  echo "推送到 $remote..."
  git push $remote $current_branch || git push $remote master
done

echo "推送完成！" 