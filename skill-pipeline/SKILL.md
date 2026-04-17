---
name: skill-pipeline
description: 自动化技能入库和学习流程。首次使用引导配置GitHub仓库目录和SSH key，之后可执行技能入库（完整流程）或技能学习（本地版）。
trigger: 用户说"技能入库"、"技能学习"、"导入技能"、"初始化技能配置"等
category: hermes-core
---

# 技能入库/学习流水线（skill-pipeline）

## 功能概述

自动化技能归档、入库和 GitHub 同步流程，融合初始化配置功能。

## 触发条件

- "技能入库" — 完整流程（归档 + 本地保存 + GitHub push）
- "技能学习" — 本地版（只归档保存到 Hermes）
- "初始化技能配置" — 首次配置 Git 目录和 SSH key
- "修改技能配置" — 重新配置 Git 目录或 SSH key

## 首次使用（初始化）

### 步骤 1：配置本地 Git 仓库目录

提示用户输入存储 GitHub 技能库的本地文件夹路径。

示例路径：
- Windows: `C:\Users\15284\Desktop\git\skills`
- WSL: `/mnt/c/Users/15284/Desktop/git/skills`

验证目录是否存在且包含 `.git` 文件夹。

### 步骤 2：生成并配置 SSH Key

1. 检查 `~/.ssh/` 目录是否已有 GitHub 相关的 SSH key
2. 如无，生成新的 Ed25519 SSH key：
   ```bash
   ssh-keygen -t ed25519 -C "用户邮箱" -f ~/.ssh/github_ed25519 -N ""
   ```
3. 配置 SSH config：
   ```
   Host github.com
       HostName github.com
       User git
       IdentityFile ~/.ssh/github_ed25519
   ```
4. 将公钥内容显示给用户，提示复制到 GitHub：
   - Settings → SSH and GPG keys → New SSH key
   - Key 类型选 "Authentication key"
   - 粘贴公钥

### 步骤 3：验证连接

配置完成后测试 GitHub SSH 连接：
```bash
ssh -T git@github.com
```

### 配置保存

将配置保存到 `~/.hermes/config.yaml`：
```yaml
skill_pipeline:
  git_repo_dir: "/mnt/c/Users/15284/Desktop/git/skills"
  ssh_key_path: "~/.ssh/github_ed25519"
  initialized: true
```

## 技能入库（完整流程）

### 步骤 1：确认任务流详情

与用户确认以下信息：
- 技能名称（name）
- 技能描述（description）
- 触发条件（trigger）- 什么情况下调用这个技能
- 分类（category）- 如 hermes-core, research, devops 等
- 功能实现详情：
  - 实现了哪些功能
  - 使用的工具和技术
  - 配置方式和参数
  - 注意事项和限制
  - 可能的失败场景

### 步骤 2：生成 SKILL.md

根据确认的信息生成 YAML frontmatter + Markdown 正文的技能文档。

格式：
```yaml
---
name: 技能名称
description: 技能描述
trigger: 触发条件
category: 分类
---

# 技能标题

## 功能概述
...

## 配置方式
...

## 实现细节
...

## 注意事项
...
```

### 步骤 3：保存到两个位置

1. **Hermes 本地技能目录**：
   - 路径：`~/.hermes/skills/<category>/<name>/SKILL.md`
   - 例如：`~/.hermes/skills/research/daily-news/SKILL.md`

2. **本地 Git 仓库目录**：
   - 路径：`<配置的git_repo_dir>/<name>/SKILL.md`
   - 例如：`/mnt/c/Users/15284/Desktop/git/skills/daily-news/SKILL.md`

### 步骤 4：更新 GitHub

1. 更新 README.md（添加新技能条目）
2. Git add + commit + push：
   ```bash
   cd <git_repo_dir>
   git add -A
   git commit -m "新增技能: <name>"
   git push origin main
   ```

### 步骤 5：反馈结果

告知用户：
- 技能已保存的位置
- GitHub 仓库链接

## 技能学习（本地版）

### 步骤 1：确认任务流详情

同"技能入库"步骤 1。

### 步骤 2：生成 SKILL.md

同"技能入库"步骤 2。

### 步骤 3：只保存到 Hermes 本地

- 路径：`~/.hermes/skills/<category>/<name>/SKILL.md`
- **不**同步到 Git 仓库目录

### 步骤 4：反馈结果

告知用户技能已保存到本地 Hermes。

## 配置管理

### 查看当前配置

```bash
# 查看配置的 Git 仓库目录
grep -A2 "skill_pipeline" ~/.hermes/config.yaml

# 查看 SSH key 状态
ls -la ~/.ssh/github_ed25519*
```

### 修改配置

使用 "修改技能配置" 触发条件重新初始化。

## 注意事项

- 首次使用必须完成初始化才能执行入库/学习
- SSH key 需要用户手动复制到 GitHub（无法自动完成）
- Git push 需要网络连接，可能失败需重试
- 技能名称必须唯一，避免覆盖已有技能
- category 目录不存在时会自动创建