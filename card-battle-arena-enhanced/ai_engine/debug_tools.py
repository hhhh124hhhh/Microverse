"""
AI决策调试工具
提供详细的AI决策过程分析和性能监控
"""
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

from .strategies.base import AIAction, ActionType, GameContext

logger = logging.getLogger(__name__)


@dataclass
class DecisionRecord:
    """决策记录"""
    timestamp: float
    game_id: str
    turn_number: int
    strategy_name: str
    action_type: str
    confidence: float
    reasoning: str
    execution_time: float
    game_state_snapshot: Dict[str, Any]
    llm_interaction: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceMetrics:
    """性能指标"""
    total_decisions: int = 0
    successful_decisions: int = 0
    average_execution_time: float = 0.0
    confidence_distribution: Dict[str, int] = None
    action_type_distribution: Dict[str, int] = None
    strategy_performance: Dict[str, Dict[str, Any]] = None

    def __post_init__(self):
        if self.confidence_distribution is None:
            self.confidence_distribution = {
                "high (>0.8)": 0,
                "medium (0.5-0.8)": 0,
                "low (<0.5)": 0
            }
        if self.action_type_distribution is None:
            self.action_type_distribution = {action.value: 0 for action in ActionType}
        if self.strategy_performance is None:
            self.strategy_performance = {}


class AIDebugger:
    """AI决策调试器"""

    def __init__(self, log_file: str = "ai_decisions.json"):
        self.log_file = Path(log_file)
        self.decision_history: List[DecisionRecord] = []
        self.current_session_start = time.time()
        self.performance_metrics = PerformanceMetrics()

        # 确保日志目录存在
        self.log_file.parent.mkdir(exist_ok=True)

        logger.info("🔧 AI调试器已初始化")

    def record_decision(self, action: AIAction, strategy_name: str,
                       context: GameContext, llm_data: Optional[Dict[str, Any]] = None):
        """记录AI决策"""
        record = DecisionRecord(
            timestamp=time.time(),
            game_id=context.game_id,
            turn_number=context.turn_number,
            strategy_name=strategy_name,
            action_type=action.action_type.value,
            confidence=action.confidence,
            reasoning=action.reasoning,
            execution_time=action.execution_time,
            game_state_snapshot=self._create_game_state_snapshot(context),
            llm_interaction=llm_data
        )

        self.decision_history.append(record)
        self._update_performance_metrics(record)

        logger.info(f"📝 记录决策: {strategy_name} -> {action.action_type.value}")

    def _create_game_state_snapshot(self, context: GameContext) -> Dict[str, Any]:
        """创建游戏状态快照"""
        return {
            "player_health": context.player_health,
            "opponent_health": context.opponent_health,
            "player_mana": context.player_mana,
            "opponent_mana": context.opponent_mana,
            "hand_count": len(context.player_hand),
            "player_field_count": len(context.player_field),
            "opponent_field_count": len(context.opponent_field),
            "turn_number": context.turn_number,
            "phase": context.phase
        }

    def _update_performance_metrics(self, record: DecisionRecord):
        """更新性能指标"""
        self.performance_metrics.total_decisions += 1
        self.performance_metrics.successful_decisions += 1

        # 更新平均执行时间
        total_time = (self.performance_metrics.average_execution_time *
                     (self.performance_metrics.total_decisions - 1) + record.execution_time)
        self.performance_metrics.average_execution_time = total_time / self.performance_metrics.total_decisions

        # 更新置信度分布
        if record.confidence > 0.8:
            self.performance_metrics.confidence_distribution["high (>0.8)"] += 1
        elif record.confidence >= 0.5:
            self.performance_metrics.confidence_distribution["medium (0.5-0.8)"] += 1
        else:
            self.performance_metrics.confidence_distribution["low (<0.5)"] += 1

        # 更新动作类型分布
        self.performance_metrics.action_type_distribution[record.action_type] += 1

        # 更新策略性能
        if record.strategy_name not in self.performance_metrics.strategy_performance:
            self.performance_metrics.strategy_performance[record.strategy_name] = {
                "decisions": 0,
                "avg_confidence": 0.0,
                "avg_time": 0.0,
                "actions": {}
            }

        strategy_stats = self.performance_metrics.strategy_performance[record.strategy_name]
        strategy_stats["decisions"] += 1

        # 更新策略平均置信度
        old_avg = strategy_stats["avg_confidence"]
        count = strategy_stats["decisions"]
        strategy_stats["avg_confidence"] = (old_avg * (count - 1) + record.confidence) / count

        # 更新策略平均时间
        old_time = strategy_stats["avg_time"]
        strategy_stats["avg_time"] = (old_time * (count - 1) + record.execution_time) / count

        # 更新策略动作分布
        if record.action_type not in strategy_stats["actions"]:
            strategy_stats["actions"][record.action_type] = 0
        strategy_stats["actions"][record.action_type] += 1

    def analyze_decision_patterns(self) -> Dict[str, Any]:
        """分析决策模式"""
        if not self.decision_history:
            return {"message": "暂无决策数据"}

        # 分析最近的决策趋势
        recent_decisions = self.decision_history[-20:]  # 最近20个决策

        # 按策略分析
        strategy_analysis = {}
        for record in recent_decisions:
            strategy = record.strategy_name
            if strategy not in strategy_analysis:
                strategy_analysis[strategy] = {
                    "count": 0,
                    "avg_confidence": 0.0,
                    "avg_time": 0.0,
                    "common_actions": {}
                }

            stats = strategy_analysis[strategy]
            stats["count"] += 1
            stats["avg_confidence"] = (stats["avg_confidence"] * (stats["count"] - 1) + record.confidence) / stats["count"]
            stats["avg_time"] = (stats["avg_time"] * (stats["count"] - 1) + record.execution_time) / stats["count"]

            action = record.action_type
            if action not in stats["common_actions"]:
                stats["common_actions"][action] = 0
            stats["common_actions"][action] += 1

        # 分析时间趋势
        time_analysis = {
            "avg_decision_time": sum(r.execution_time for r in recent_decisions) / len(recent_decisions),
            "slowest_decision": max(recent_decisions, key=lambda r: r.execution_time),
            "fastest_decision": min(recent_decisions, key=lambda r: r.execution_time)
        }

        # 分析置信度趋势
        confidence_trend = [record.confidence for record in recent_decisions]
        confidence_analysis = {
            "avg_confidence": sum(confidence_trend) / len(confidence_trend),
            "confidence_trend": "increasing" if len(confidence_trend) > 1 and confidence_trend[-1] > confidence_trend[0] else "stable",
            "high_confidence_ratio": sum(1 for c in confidence_trend if c > 0.8) / len(confidence_trend)
        }

        return {
            "total_decisions_analyzed": len(recent_decisions),
            "strategy_analysis": strategy_analysis,
            "time_analysis": time_analysis,
            "confidence_analysis": confidence_analysis,
            "analysis_timestamp": time.time()
        }

    def get_decision_details(self, game_id: str, turn_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取特定决策的详细信息"""
        decisions = []
        for record in self.decision_history:
            if record.game_id == game_id:
                if turn_number is None or record.turn_number == turn_number:
                    decisions.append(asdict(record))
        return decisions

    def export_debug_report(self, output_file: Optional[str] = None) -> str:
        """导出调试报告"""
        if output_file is None:
            timestamp = int(time.time())
            output_file = f"ai_debug_report_{timestamp}.json"

        report = {
            "session_info": {
                "start_time": self.current_session_start,
                "duration": time.time() - self.current_session_start,
                "total_decisions": len(self.decision_history)
            },
            "performance_metrics": asdict(self.performance_metrics),
            "decision_patterns": self.analyze_decision_patterns(),
            "recent_decisions": [asdict(record) for record in self.decision_history[-10:]],
            "export_timestamp": time.time()
        }

        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 调试报告已导出到: {output_path}")
        return str(output_path)

    def print_performance_summary(self):
        """打印性能摘要"""
        metrics = self.performance_metrics
        patterns = self.analyze_decision_patterns()

        print("\n" + "="*60)
        print("🔍 AI决策性能分析报告")
        print("="*60)

        print(f"\n📊 总体统计:")
        print(f"   总决策数: {metrics.total_decisions}")
        print(f"   成功决策数: {metrics.successful_decisions}")
        print(f"   平均执行时间: {metrics.average_execution_time:.3f}秒")

        print(f"\n🎯 置信度分布:")
        for level, count in metrics.confidence_distribution.items():
            percentage = count / max(1, metrics.total_decisions) * 100
            print(f"   {level}: {count} ({percentage:.1f}%)")

        print(f"\n🎮 动作类型分布:")
        for action_type, count in metrics.action_type_distribution.items():
            if count > 0:
                percentage = count / max(1, metrics.total_decisions) * 100
                print(f"   {action_type}: {count} ({percentage:.1f}%)")

        if "strategy_analysis" in patterns:
            print(f"\n🧠 策略性能分析:")
            for strategy, stats in patterns["strategy_analysis"].items():
                print(f"   {strategy}:")
                print(f"     决策数: {stats['count']}")
                print(f"     平均置信度: {stats['avg_confidence']:.3f}")
                print(f"     平均耗时: {stats['avg_time']:.3f}秒")
                most_common = max(stats["common_actions"].items(), key=lambda x: x[1])
                print(f"     最常用动作: {most_common[0]} ({most_common[1]}次)")

        print(f"\n📈 最近趋势:")
        if "confidence_analysis" in patterns:
            conf_analysis = patterns["confidence_analysis"]
            print(f"   平均置信度: {conf_analysis['avg_confidence']:.3f}")
            print(f"   置信度趋势: {conf_analysis['confidence_trend']}")
            print(f"   高置信度比例: {conf_analysis['high_confidence_ratio']:.1%}")

        if "time_analysis" in patterns:
            time_analysis = patterns["time_analysis"]
            print(f"   平均决策时间: {time_analysis['avg_decision_time']:.3f}秒")

        print("\n" + "="*60)

    def clear_history(self):
        """清空决策历史"""
        self.decision_history.clear()
        self.performance_metrics = PerformanceMetrics()
        self.current_session_start = time.time()
        logger.info("🗑️ 调试历史已清空")

    def save_session(self, filename: Optional[str] = None):
        """保存当前调试会话"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"ai_debug_session_{timestamp}.json"

        session_data = {
            "session_start": self.current_session_start,
            "decision_history": [asdict(record) for record in self.decision_history],
            "performance_metrics": asdict(self.performance_metrics)
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 调试会话已保存到: {filename}")

    def load_session(self, filename: str):
        """加载调试会话"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            self.current_session_start = session_data["session_start"]

            # 重建决策历史
            self.decision_history.clear()
            for record_data in session_data["decision_history"]:
                record = DecisionRecord(**record_data)
                self.decision_history.append(record)

            # 重建性能指标
            metrics_data = session_data["performance_metrics"]
            self.performance_metrics = PerformanceMetrics(**metrics_data)

            logger.info(f"📂 调试会话已从 {filename} 加载")

        except Exception as e:
            logger.error(f"❌ 加载调试会话失败: {e}")


# 全局调试器实例
debugger = AIDebugger()