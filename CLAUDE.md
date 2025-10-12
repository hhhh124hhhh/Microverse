# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Microverse 是一个基于 Godot 4 开发的模拟上帝类沙盒游戏，专注于多智能体 AI 社交模拟系统。游戏特色是 AI 角色拥有独立的思维和记忆，能够自主进行社交互动、完成任务，并在持续的交流中发展出复杂的社会关系。

## 核心架构

### 自动加载单例系统
项目使用 Godot 的自动加载功能管理核心系统单例：
- `SettingsManager`: 全局设置管理
- `DialogManager`: 对话系统管理
- `CharacterManager`: 角色控制管理
- `APIManager`: AI API 调用管理
- `GameSaveManager`: 存档系统管理
- `SaveLoadUIManager`: 存档UI管理
- `MemoryManager`: 记忆系统管理

### AI 系统架构
1. **API 集成层** (`script/ai/APIManager.gd`):
   - 支持多种 AI 服务提供商（OpenAI、Claude、Gemini、DeepSeek、豆包、Kimi、Ollama）
   - 角色独立 AI 设置配置
   - 统一的 API 调用接口

2. **对话系统** (`script/ai/DialogManager.gd`, `script/ai/DialogService.gd`):
   - 支持多组对话同时进行
   - 基于大语言模型的自然语言对话
   - 动态对话气泡 UI 显示
   - 对话历史记录和回放功能

3. **记忆系统** (`script/ai/memory/MemoryManager.gd`):
   - 持久化长期记忆存储
   - 记忆类型和重要性分级
   - 智能记忆检索和清理
   - 格式化记忆用于 AI prompt

4. **角色系统** (`script/CharacterManager.gd`, `script/CharacterPersonality.gd`):
   - 8个预设 AI 角色，每个都有独特的性格和背景
   - 角色状态管理（金钱、心情、健康、关系）
   - 角色间情感关系系统

### 场景结构
- `scene/characters/`: 角色场景文件
- `scene/maps/Office.tscn`: 主要办公室场景
- `scene/ui/`: UI 组件场景
- `scene/prefab/`: 可复用对象（椅子、桌子等）

## 开发命令

### 运行项目
```bash
# 在 Godot 编辑器中打开项目
godot --editor --path /path/to/Microverse

# 或直接运行项目
godot --path /path/to/Microverse
```

### 测试 AI 对话功能
1. 启动游戏后按 ESC 键打开设置界面
2. 配置 AI 服务提供商和 API 密钥
3. 使用 WASD 键移动角色
4. 按 T 键开始与 AI 角色对话
5. 按 L 键结束对话
6. 按 ` 键打开控制台查看 AI 角色记忆

### 存档系统
- **保存游戏**: F1 键
- **存档位置**: `user://saves/` 目录
- **存档格式**: JSON 文件

## 关键系统交互

### 对话系统工作流程
1. `CharacterManager` 检测角色附近的其他角色
2. `DialogManager` 接收输入触发对话
3. `DialogService` 创建对话实例并管理多对话
4. `APIManager` 根据角色设置调用相应的 AI API
5. `MemoryManager` 为参与者添加对话记忆
6. UI 系统显示对话气泡和界面反馈

### AI 角色设置
每个角色的性格定义在 `CharacterPersonality.PERSONALITY_CONFIG` 中：
- `position`: 职位信息
- `personality`: 性格特征
- `speaking_style`: 说话风格
- `work_duties`: 工作职责
- `work_habits`: 工作习惯

### 记忆系统
记忆按类型分类：
- `PERSONAL`: 个人记忆
- `INTERACTION`: 互动记忆
- `TASK`: 任务记忆
- `EMOTION`: 情感记忆
- `EVENT`: 事件记忆

记忆按重要性分级（1-10），系统会自动清理旧记忆保持合理数量。

## 角色控制
- 点击角色选择/取消选择
- 点击空地让角色移动
- 点击椅子让角色移动并坐下
- 相机会自动跟随选中的角色

## 公司背景设定
游戏设定在 SleepySheep 公司，主要产品是《CountSheep》小游戏：
- 游戏宣传语："Can't Sleep? Count Sheep"
- 游戏玩法：数小羊计分游戏
- 目前十分流行，吸引了许多年轻用户购买皮肤

## 开发注意事项
- 所有 AI 角色交互都需要有效的 API 密钥
- 角色数据存储在节点的 `character_data` 元数据中
- 多对话系统需要妥善管理对话状态和内存
- 存档系统会自动收集所有角色状态和记忆数据