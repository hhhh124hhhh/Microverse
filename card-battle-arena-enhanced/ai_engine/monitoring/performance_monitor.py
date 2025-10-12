"""
AI性能监控系统
实时监控AI决策性能、资源使用情况和系统健康状态
"""
import time
import asyncio
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from collections import deque, defaultdict
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    decision_time_ms: float
    confidence_score: float
    strategy_name: str
    game_id: str
    success: bool


@dataclass
class SystemHealth:
    """系统健康状态"""
    status: str  # healthy, warning, critical
    cpu_usage: float
    memory_usage: float
    active_strategies: int
    error_rate: float
    avg_response_time: float
    last_update: float


@dataclass
class AlertConfig:
    """告警配置"""
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0
    response_time_threshold: float = 5000.0  # 毫秒
    error_rate_threshold: float = 0.1
    confidence_threshold: float = 0.3


class PerformanceMonitor:
    """AI性能监控器"""

    def __init__(self, max_history: int = 10000, alert_config: AlertConfig = None):
        self.max_history = max_history
        self.alert_config = alert_config or AlertConfig()

        # 性能数据存储
        self.metrics_history: deque = deque(maxlen=max_history)
        self.strategy_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.game_stats: Dict[str, List[PerformanceMetrics]] = defaultdict(list)

        # 实时监控状态
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_interval = 1.0  # 秒

        # 告警系统
        self.alert_callbacks: List[Callable] = []
        self.active_alerts: List[Dict[str, Any]] = []

        # 统计缓存
        self._stats_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 5.0  # 缓存5秒

        logger.info("性能监控器初始化完成")

    def start_monitoring(self):
        """开始性能监控"""
        if self.is_monitoring:
            logger.warning("性能监控已在运行")
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("性能监控已启动")

    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        logger.info("性能监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 收集系统指标
                system_metrics = self._collect_system_metrics()

                # 检查告警条件
                self._check_alerts(system_metrics)

                # 清理过期数据
                self._cleanup_old_data()

                time.sleep(self.monitor_interval)

            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                time.sleep(self.monitor_interval)

    def _collect_system_metrics(self) -> Dict[str, float]:
        """收集系统性能指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "memory_used_mb": 0.0,
                "timestamp": time.time()
            }

    def record_decision(self, strategy_name: str, game_id: str,
                       decision_time: float, confidence: float,
                       success: bool):
        """记录AI决策数据"""
        system_metrics = self._collect_system_metrics()

        metrics = PerformanceMetrics(
            timestamp=system_metrics["timestamp"],
            cpu_percent=system_metrics["cpu_percent"],
            memory_percent=system_metrics["memory_percent"],
            memory_used_mb=system_metrics["memory_used_mb"],
            decision_time_ms=decision_time * 1000,  # 转换为毫秒
            confidence_score=confidence,
            strategy_name=strategy_name,
            game_id=game_id,
            success=success
        )

        # 存储到历史记录
        self.metrics_history.append(metrics)
        self.game_stats[game_id].append(metrics)

        # 更新策略统计
        self._update_strategy_stats(strategy_name, metrics)

        # 清理缓存
        self._invalidate_cache()

    def _update_strategy_stats(self, strategy_name: str, metrics: PerformanceMetrics):
        """更新策略统计信息"""
        if strategy_name not in self.strategy_stats:
            self.strategy_stats[strategy_name] = {
                "total_decisions": 0,
                "successful_decisions": 0,
                "total_time": 0.0,
                "confidence_sum": 0.0,
                "last_decision": 0.0,
                "errors": 0
            }

        stats = self.strategy_stats[strategy_name]
        stats["total_decisions"] += 1
        stats["total_time"] += metrics.decision_time_ms
        stats["confidence_sum"] += metrics.confidence_score
        stats["last_decision"] = metrics.timestamp

        if metrics.success:
            stats["successful_decisions"] += 1
        else:
            stats["errors"] += 1

    def _check_alerts(self, system_metrics: Dict[str, float]):
        """检查告警条件"""
        alerts = []

        # CPU使用率告警
        if system_metrics["cpu_percent"] > self.alert_config.cpu_threshold:
            alerts.append({
                "type": "cpu_high",
                "message": f"CPU使用率过高: {system_metrics['cpu_percent']:.1f}%",
                "severity": "warning" if system_metrics["cpu_percent"] < 90 else "critical",
                "timestamp": system_metrics["timestamp"]
            })

        # 内存使用率告警
        if system_metrics["memory_percent"] > self.alert_config.memory_threshold:
            alerts.append({
                "type": "memory_high",
                "message": f"内存使用率过高: {system_metrics['memory_percent']:.1f}%",
                "severity": "warning" if system_metrics["memory_percent"] < 95 else "critical",
                "timestamp": system_metrics["timestamp"]
            })

        # 检查响应时间告警
        recent_metrics = [m for m in self.metrics_history
                         if time.time() - m.timestamp < 300]  # 最近5分钟

        if recent_metrics:
            avg_response_time = sum(m.decision_time_ms for m in recent_metrics) / len(recent_metrics)
            if avg_response_time > self.alert_config.response_time_threshold:
                alerts.append({
                    "type": "response_time_high",
                    "message": f"平均响应时间过长: {avg_response_time:.1f}ms",
                    "severity": "warning",
                    "timestamp": time.time()
                })

        # 触发告警回调
        for alert in alerts:
            self._trigger_alert(alert)

    def _trigger_alert(self, alert: Dict[str, Any]):
        """触发告警"""
        # 检查是否是重复告警
        recent_alerts = [a for a in self.active_alerts
                        if time.time() - a["timestamp"] < 300]  # 5分钟内

        for recent_alert in recent_alerts:
            if (recent_alert["type"] == alert["type"] and
                recent_alert["severity"] == alert["severity"]):
                return  # 重复告警，跳过

        # 添加到活跃告警
        self.active_alerts.append(alert)

        # 清理过期告警
        self.active_alerts = [a for a in self.active_alerts
                             if time.time() - a["timestamp"] < 3600]  # 1小时

        # 调用告警回调
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"告警回调执行失败: {e}")

        logger.warning(f"🚨 系统告警: {alert['message']}")

    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)

    def get_system_health(self) -> SystemHealth:
        """获取系统健康状态"""
        system_metrics = self._collect_system_metrics()

        # 计算最近5分钟的统计
        recent_metrics = [m for m in self.metrics_history
                         if time.time() - m.timestamp < 300]

        if recent_metrics:
            avg_response_time = sum(m.decision_time_ms for m in recent_metrics) / len(recent_metrics)
            error_rate = sum(1 for m in recent_metrics if not m.success) / len(recent_metrics)
            success_count = sum(1 for m in recent_metrics if m.success)
        else:
            avg_response_time = 0.0
            error_rate = 0.0
            success_count = 0

        # 确定健康状态
        if (system_metrics["cpu_percent"] > 90 or
            system_metrics["memory_percent"] > 95 or
            error_rate > 0.2):
            status = "critical"
        elif (system_metrics["cpu_percent"] > 70 or
              system_metrics["memory_percent"] > 80 or
              avg_response_time > 3000 or
              error_rate > 0.1):
            status = "warning"
        else:
            status = "healthy"

        return SystemHealth(
            status=status,
            cpu_usage=system_metrics["cpu_percent"],
            memory_usage=system_metrics["memory_percent"],
            active_strategies=len(self.strategy_stats),
            error_rate=error_rate,
            avg_response_time=avg_response_time,
            last_update=system_metrics["timestamp"]
        )

    def get_performance_summary(self, time_window: int = 3600) -> Dict[str, Any]:
        """获取性能摘要"""
        current_time = time.time()

        # 检查缓存
        if (current_time - self._cache_timestamp < self._cache_ttl and
            "performance_summary" in self._stats_cache):
            return self._stats_cache["performance_summary"]

        # 获取时间窗口内的数据
        window_metrics = [m for m in self.metrics_history
                         if current_time - m.timestamp <= time_window]

        if not window_metrics:
            summary = {
                "total_decisions": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "avg_confidence": 0.0,
                "strategies_used": [],
                "time_window": time_window
            }
        else:
            # 基础统计
            total_decisions = len(window_metrics)
            successful_decisions = sum(1 for m in window_metrics if m.success)
            success_rate = successful_decisions / total_decisions
            avg_response_time = sum(m.decision_time_ms for m in window_metrics) / total_decisions
            avg_confidence = sum(m.confidence_score for m in window_metrics) / total_decisions

            # 策略使用统计
            strategy_counts = defaultdict(int)
            for m in window_metrics:
                strategy_counts[m.strategy_name] += 1

            strategies_used = [
                {"name": name, "usage": count, "percentage": count / total_decisions * 100}
                for name, count in strategy_counts.items()
            ]

            summary = {
                "total_decisions": total_decisions,
                "successful_decisions": successful_decisions,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "avg_confidence": avg_confidence,
                "strategies_used": strategies_used,
                "time_window": time_window,
                "timestamp": current_time
            }

        # 缓存结果
        self._stats_cache["performance_summary"] = summary
        self._cache_timestamp = current_time

        return summary

    def get_strategy_performance(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """获取特定策略的性能统计"""
        if strategy_name not in self.strategy_stats:
            return None

        stats = self.strategy_stats[strategy_name]

        if stats["total_decisions"] == 0:
            return {
                "strategy_name": strategy_name,
                "total_decisions": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "avg_confidence": 0.0
            }

        success_rate = stats["successful_decisions"] / stats["total_decisions"]
        avg_response_time = stats["total_time"] / stats["total_decisions"]
        avg_confidence = stats["confidence_sum"] / stats["total_decisions"]

        return {
            "strategy_name": strategy_name,
            "total_decisions": stats["total_decisions"],
            "successful_decisions": stats["successful_decisions"],
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "avg_confidence": avg_confidence,
            "error_count": stats["errors"],
            "last_decision": stats["last_decision"]
        }

    def export_metrics(self, file_path: str, format: str = "json"):
        """导出性能指标数据"""
        try:
            if format.lower() == "json":
                data = {
                    "export_timestamp": time.time(),
                    "system_health": asdict(self.get_system_health()),
                    "performance_summary": self.get_performance_summary(),
                    "strategy_stats": {
                        name: self.get_strategy_performance(name)
                        for name in self.strategy_stats.keys()
                    },
                    "active_alerts": self.active_alerts,
                    "recent_metrics": [
                        asdict(m) for m in list(self.metrics_history)[-1000:]
                    ]
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            else:
                raise ValueError(f"不支持的导出格式: {format}")

            logger.info(f"性能指标已导出到: {file_path}")

        except Exception as e:
            logger.error(f"导出性能指标失败: {e}")
            raise

    def _cleanup_old_data(self):
        """清理过期数据"""
        current_time = time.time()
        max_age = 24 * 3600  # 24小时

        # 清理游戏统计
        expired_games = [
            game_id for game_id, metrics in self.game_stats.items()
            if not metrics or current_time - metrics[-1].timestamp > max_age
        ]

        for game_id in expired_games:
            del self.game_stats[game_id]

        if expired_games:
            logger.debug(f"清理了 {len(expired_games)} 个过期游戏记录")

    def _invalidate_cache(self):
        """使缓存失效"""
        self._stats_cache.clear()
        self._cache_timestamp = 0

    def reset_statistics(self):
        """重置所有统计信息"""
        self.metrics_history.clear()
        self.strategy_stats.clear()
        self.game_stats.clear()
        self.active_alerts.clear()
        self._invalidate_cache()
        logger.info("性能监控统计信息已重置")


# 默认告警回调函数
def default_alert_callback(alert: Dict[str, Any]):
    """默认告警回调 - 输出到日志"""
    level = "WARNING" if alert["severity"] == "warning" else "ERROR"
    print(f"[{level}] {alert['message']}")


# 文件告警回调函数
def file_alert_callback(log_file: str = "ai_alerts.log"):
    """文件告警回调 - 写入到文件"""
    def callback(alert: Dict[str, Any]):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alert["timestamp"]))
        log_entry = f"[{timestamp}] [{alert['severity'].upper()}] {alert['message']}\n"

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"写入告警日志失败: {e}")

    return callback