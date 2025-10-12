# Card Battle Arena Enhanced

🎮 **智能卡牌游戏AI系统** - 集成DeepSeek大语言模型的现代化卡牌游戏AI

## ✨ 特性

- 🤖 **多层次AI决策系统** - 规则AI + DeepSeek LLM + 混合策略
- 🎭 **6种AI人格** - 狂战士、守护者、战略大师等不同性格
- 🧠 **实时学习能力** - AI可从对战经验中进化策略
- 📊 **性能监控系统** - 实时监控AI决策质量和系统性能
- 🎯 **智能决策分析** - 基于DeepSeek的高级战术分析
- 🎮 **多种游戏模式** - AI演示、交互对战、AI互战

## 🚀 快速开始

### 一键启动
```bash
# 克隆项目
git clone <repository-url>
cd card-battle-arena-enhanced

# 运行启动脚本
./start.sh
```

### 手动启动
```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install python-dotenv aiohttp rich click pytest psutil

# 3. 配置DeepSeek API
cp .env.example .env
# 编辑 .env 文件，设置 DEEPSEEK_API_KEY

# 4. 运行游戏
python simple_main.py
```

## 🎮 游戏预览

```
🎮 游戏状态
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 属性              ┃ 我方                       ┃ 对手                        ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 生命值            │ 25/30                      │ 20/30                       │
│ 法力值            │ 6/6                        │ 4/4                         │
│ 手牌数量          │ 3                          │ 4                           │
│ 场面随从          │ 1                          │ 2                           │
└───────────────────┴────────────────────────────┴─────────────────────────────┘

🤖 AI决策 (狂战士)
┌─────────────────────────────────────────────────────────────────────┐
│ AI决策: 出牌                                                        │
│ 置信度: 0.74                                                        │
│ 推理: 狂战策略：压制造胜！ | 出卡牌 烈焰元素，价值分数: 5.90           │
│ 执行时间: 0.001秒                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## 🤖 AI系统架构

### 核心组件
- **AI引擎** - 统一的AI决策管理器
- **策略系统** - 多种AI策略实现
- **人格系统** - 个性化AI角色
- **LLM集成** - DeepSeek大语言模型集成
- **监控系统** - 性能监控与分析

### AI人格类型
| 人格 | 风格 | 激进程度 | 特点 |
|------|------|----------|------|
| 🪓 狂战士 | 快攻 | 0.90 | 极度激进，追求快速胜利 |
| 🛡️ 智慧守护者 | 控制 | 0.30 | 谨慎防御，重视场面控制 |
| ♟️ 战略大师 | 中速 | 0.50 | 长远规划，价值交换 |
| 🎪 连锁爱好者 | 组合 | 0.70 | 寻找复杂配合和连锁 |
| 🎓 适应性学习者 | 多样 | 0.50 | 灵活应变，从经验学习 |
| 🎭 娱乐玩家 | 娱乐 | 0.60 | 追求有趣和创意玩法 |

## 🔧 配置DeepSeek AI

1. **获取API密钥**
   - 访问 [DeepSeek平台](https://platform.deepseek.com/)
   - 注册账号并获取API密钥

2. **配置项目**
   ```bash
   # 编辑 .env 文件
   DEEPSEEK_API_KEY=你的API密钥
   DEEPSEEK_MODEL=deepseek-chat
   ENABLE_LLM=true
   ```

3. **测试连接**
   ```bash
   python test_deepseek.py
   ```

## 🎯 运行模式

### 1. AI人格演示
```bash
python simple_main.py
# 选择 1. AI人格演示
```

### 2. 交互式对战
```bash
python simple_main.py
# 选择 2. 交互式模式
```

### 3. DeepSeek测试
```bash
python test_deepseek.py
```

### 4. 性能基准测试
```bash
python main.py --mode benchmark
```

## 📊 技术特色

### 🧠 智能决策
- **多策略融合** - 规则 + LLM + 机器学习
- **实时分析** - <500ms决策响应
- **自适应学习** - 基于对战经验进化
- **人格化行为** - 不同性格的独特决策风格

### 🔍 DeepSeek集成
- **战术分析** - 深度游戏状态分析
- **自然语言推理** - 人类可理解的决策逻辑
- **动态提示** - 根据游戏状态调整分析策略
- **缓存优化** - 智能缓存提升响应速度

### 📈 性能监控
- **实时监控** - CPU、内存、决策时间
- **性能分析** - 策略成功率、置信度统计
- **智能告警** - 异常情况自动通知
- **数据导出** - JSON格式的详细性能报告

## 🏗️ 项目结构

```
card-battle-arena-enhanced/
├── ai_engine/                 # AI引擎核心
│   ├── strategies/           # AI策略实现
│   ├── agents/              # AI代理系统
│   ├── llm_integration/     # LLM集成
│   └── monitoring/          # 性能监控
├── game_engine/              # 游戏引擎
│   ├── cards/              # 卡牌系统
│   └── game_state/         # 游戏状态
├── config/                   # 配置管理
├── tests/                    # 测试套件
├── simple_main.py           # 简化版主程序
├── main.py                  # 完整版主程序
├── test_deepseek.py         # DeepSeek测试
├── start.sh                 # 快速启动脚本
├── requirements-core.txt    # 核心依赖
└── USAGE_GUIDE.md          # 详细使用指南
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 测试DeepSeek集成
python test_deepseek.py

# 性能基准测试
python main.py --mode benchmark
```

## 📚 文档

- [📖 使用指南](USAGE_GUIDE.md) - 详细的使用说明
- [🏗️ 项目总结](PROJECT_SUMMARY.md) - 完整的技术总结
- [🔧 配置参考](.env.example) - 配置文件示例

## 🎯 系统要求

- **Python**: 3.8+
- **操作系统**: Linux/macOS/Windows
- **内存**: 最少 100MB
- **网络**: 用于DeepSeek API调用

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [DeepSeek](https://platform.deepseek.com/) - 提供强大的大语言模型API
- [Rich](https://github.com/Textualize/rich) - 美观的终端输出
- [Original Project](https://github.com/hhhh124hhhh/context-engineering-intro/tree/main/card-battle-arena-v2) - 原始卡牌游戏项目

## 🎉 立即体验

```bash
# 克隆并运行
git clone <repository>
cd card-battle-arena-enhanced
./start.sh
```

准备好迎接前所未有的智能卡牌游戏体验了吗？ 🚀