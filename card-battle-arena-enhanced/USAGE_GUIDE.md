# Card Battle Arena Enhanced - 使用指南

## 🎮 快速开始

### 1. 环境准备

```bash
# 克隆或下载项目
cd card-battle-arena-enhanced

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install python-dotenv aiohttp rich click pytest psutil
```

### 2. 配置DeepSeek API

1. **获取API密钥**
   - 访问 [DeepSeek平台](https://platform.deepseek.com/)
   - 注册账号并登录
   - 在控制台获取API密钥

2. **配置环境变量**
   ```bash
   # 编辑 .env 文件
   nano .env
   ```

   设置以下配置：
   ```env
   DEEPSEEK_API_KEY=你的API密钥
   DEEPSEEK_MODEL=deepseek-chat
   ENABLE_LLM=true
   ```

### 3. 运行游戏

#### 基础命令行版本
```bash
# 运行简化版游戏
python simple_main.py
```

#### 完整版本（需要更多依赖）
```bash
# 安装完整依赖
pip install pygame numpy openai anthropic scikit-learn

# 运行完整版游戏
python main.py --mode demo
```

### 4. 测试DeepSeek集成

```bash
# 测试API连接和功能
python test_deepseek.py
```

## 🎯 游戏模式

### 1. AI人格演示模式
展示不同性格AI的决策风格：
- **狂战士**: 激进进攻型
- **智慧守护者**: 谨慎防御型
- **战略大师**: 长远规划型
- **适应性学习者**: 灵活应变型

### 2. 交互式模式
与AI进行实时对战：
```bash
python simple_main.py
# 选择 2. 交互式模式
```

可用命令：
- `ai` - 查看AI决策
- `state` - 显示游戏状态
- `stats` - 查看AI统计
- `learn` - 模拟学习
- `new` - 新游戏
- `help` - 显示帮助
- `quit` - 退出

### 3. AI对战模式
观看不同AI互相对战：
```bash
python main.py --mode ai-vs-ai --games 5
```

## 🤖 AI配置

### 策略类型
- `rule_based`: 基于规则的AI
- `llm_enhanced`: DeepSeek增强AI
- `hybrid`: 混合策略AI

### 人格类型
- `aggressive_berserker`: 狂战士
- `wise_defender`: 智慧守护者
- `strategic_mastermind`: 战略大师
- `combo_enthusiast`: 连锁爱好者
- `adaptive_learner`: 适应性学习者
- `fun_seeker`: 娱乐玩家

### 配置示例
```bash
# 指定AI策略和人格
python main.py --strategy hybrid --personality aggressive_berserker

# 设置难度级别
python main.py --difficulty hard

# 运行多场游戏
python main.py --games 10
```

## 🔧 高级配置

### 环境变量配置
在 `.env` 文件中设置：

```env
# DeepSeek配置
DEEPSEEK_API_KEY=你的API密钥
DEEPSEEK_MODEL=deepseek-chat

# 游戏配置
DEFAULT_AI_STRATEGY=hybrid
DEFAULT_PERSONALITY=adaptive_learner
GAME_MODE=demo
ENABLE_LLM=true

# 监控配置
ENABLE_MONITORING=true
LOG_LEVEL=INFO

# 显示配置
SHOW_THINKING=true
SHOW_EMOTIONS=true
SHOW_PERFORMANCE=true
```

### 自定义AI人格
```python
from ai_engine.agents.agent_personality import PersonalityProfile

custom_profile = PersonalityProfile(
    name="自定义人格",
    description="你的个性化AI描述",
    traits=[PersonalityTrait.AGGRESSIVE, PersonalityTrait.RISK_TAKER],
    play_style=PlayStyle.AGGRO,
    risk_tolerance=0.8,
    aggression_level=0.9,
    patience_level=0.2
)
```

## 📊 性能监控

### 查看实时统计
游戏中会显示：
- AI决策时间
- 置信度评分
- 情感状态
- 学习进度

### 导出性能数据
```python
from ai_engine.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()
# ... 运行游戏
monitor.export_metrics("performance_data.json")
```

## 🐛 故障排除

### 常见问题

1. **ModuleNotFoundError**
   ```bash
   # 确保虚拟环境已激活
   source venv/bin/activate
   # 重新安装依赖
   pip install python-dotenv aiohttp rich click pytest psutil
   ```

2. **DeepSeek API错误**
   - 检查API密钥是否正确
   - 确认网络连接
   - 验证API配额

3. **ImportError**
   ```bash
   # 检查Python路径
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

### 调试模式
```bash
# 启用详细日志
python simple_main.py --verbose

# 运行测试
pytest tests/ -v
```

## 📚 扩展开发

### 添加新的AI策略
```python
from ai_engine.strategies.base import AIStrategy

class CustomStrategy(AIStrategy):
    async def make_decision(self, context):
        # 实现你的AI逻辑
        pass
```

### 集成其他LLM
```python
from ai_engine.llm_integration.base import BaseLLMClient

class CustomLLMClient(BaseLLMClient):
    async def chat_completion(self, messages):
        # 实现你的LLM调用逻辑
        pass
```

## 🎉 成功案例

### 运行示例
```bash
$ python simple_main.py
🎮 Card Battle Arena Enhanced - 简化版
🤖 智能AI决策系统演示
============================================================
📋 配置信息:
   默认AI策略: hybrid
   默认AI人格: adaptive_learner
   LLM功能: 启用
   监控功能: 启用

选择运行模式:
1. AI人格演示
2. 交互式模式

🎭 AI人格决策演示
==================================================
🎮 游戏状态表格...
🤖 AI决策结果...
📊 性能统计...
```

### DeepSeek集成示例
```bash
$ python test_deepseek.py
🧪 DeepSeek AI集成测试
==================================================
🔧 DeepSeek模型: deepseek-chat
🤖 默认策略: hybrid
👥 默认人格: adaptive_learner

🔍 API连接测试...
✅ DeepSeek API连接成功!
📝 响应: 我是DeepSeek，一个由深度求索开发的大语言模型...
⏱️  响应时间: 1.23秒
📊 Token使用: {'prompt_tokens': 20, 'completion_tokens': 50, 'total_tokens': 70}

🎉 所有测试通过！DeepSeek AI集成配置成功！
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 运行测试
5. 创建Pull Request

## 📄 许可证

本项目基于MIT许可证开源。

## 🔗 相关链接

- [DeepSeek平台](https://platform.deepseek.com/)
- [项目文档](PROJECT_SUMMARY.md)
- [技术架构](docs/ARCHITECTURE.md)
- [API参考](docs/API_REFERENCE.md)