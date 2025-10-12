#!/bin/bash

# Card Battle Arena Enhanced - 快速启动脚本

echo "🎮 Card Battle Arena Enhanced - 快速启动"
echo "================================================"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "🐍 Python版本: $PYTHON_VERSION"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📚 检查依赖..."
pip install -q python-dotenv aiohttp rich click pytest psutil

# 检查DeepSeek配置
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，创建默认配置..."
    cp .env.example .env
    echo "📝 请编辑 .env 文件并设置你的DeepSeek API密钥"
fi

# 检查API密钥
API_KEY=$(grep DEEPSEEK_API_KEY .env | cut -d'=' -f2)
if [ "$API_KEY" = "your_deepseek_api_key_here" ]; then
    echo "⚠️  未配置DeepSeek API密钥"
    echo "请按以下步骤配置："
    echo "1. 访问 https://platform.deepseek.com/"
    echo "2. 注册账号并获取API密钥"
    echo "3. 编辑 .env 文件："
    echo "   nano .env"
    echo "4. 设置 DEEPSEEK_API_KEY=你的API密钥"
    echo ""
    echo "现在将以基础模式运行游戏..."
    echo ""
    read -p "按Enter键继续，或Ctrl+C退出"
fi

# 选择运行模式
echo ""
echo "🎯 选择运行模式："
echo "1. AI人格演示"
echo "2. 交互式模式"
echo "3. 测试DeepSeek API"
echo "4. 运行测试套件"
echo ""
read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo "🎭 启动AI人格演示..."
        python simple_main.py
        ;;
    2)
        echo "🎮 启动交互式模式..."
        python simple_main.py
        ;;
    3)
        echo "🧪 测试DeepSeek API..."
        python test_deepseek.py
        ;;
    4)
        echo "🔬 运行测试套件..."
        python -m pytest tests/ -v
        ;;
    *)
        echo "❌ 无效选择，启动默认演示..."
        python simple_main.py
        ;;
esac

echo ""
echo "👋 感谢使用 Card Battle Arena Enhanced!"
echo "📚 查看使用指南: cat USAGE_GUIDE.md"