import sys
import os
import json
import logging
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register, StarTools
from astrbot.api import AstrBotConfig

logger = logging.getLogger("astrbot")


@register("astrbot_plugin_only_listen", "victical", "控制Bot是否只听管理员的消息", "1.0.0", "https://github.com/victical/astrbot_plugin_only_listen")
class OnlyListenToMe(Star):
    """
    只听我的插件
    
    在群聊中控制 Bot 是否只响应管理员的消息。
    开启后，非管理员的消息将被拦截，Bot 不会处理。
    """
    
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        
        # 使用规范的插件数据目录
        plugin_data_dir = StarTools.get_data_dir()
        os.makedirs(plugin_data_dir, exist_ok=True)
        self._data_file = os.path.join(plugin_data_dir, "sleep_groups.json")
        
        # 存储已开启"只听我的"模式的群ID
        # 格式: {group_id: True/False}
        self._sleep_groups: dict[str, bool] = {}
        
    def _load_data(self) -> None:
        """从 JSON 文件加载数据"""
        if os.path.exists(self._data_file):
            try:
                with open(self._data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._sleep_groups = data if isinstance(data, dict) else {}
                logger.info(f"[只听我的] 已加载屏蔽群数据: {len(self._sleep_groups)} 条")
            except Exception as e:
                logger.error(f"[只听我的] 加载数据失败: {e}")
                self._sleep_groups = {}
        else:
            self._sleep_groups = {}
    
    def _save_data(self) -> None:
        """保存数据到 JSON 文件"""
        try:
            with open(self._data_file, "w", encoding="utf-8") as f:
                json.dump(self._sleep_groups, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[只听我的] 保存数据失败: {e}")
    
    def _is_sleep_group(self, group_id: str) -> bool:
        """检查群是否开启了"只听我的"模式"""
        return self._sleep_groups.get(group_id, False)
    
    @filter.on_astrbot_loaded()
    async def on_loaded(self) -> None:
        """插件加载完成后初始化数据"""
        self._load_data()
        logger.info("[只听我的] 插件初始化完成")
    
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE, priority=sys.maxsize - 1)
    async def on_group_message(self, event: AstrMessageEvent):
        """
        群消息拦截处理器（高优先级）
        
        如果群开启了"只听我的"模式，且发送者不是管理员，则拦截消息。
        """
        group_id = event.get_group_id()
        if not group_id:
            return
        
        # 检查是否开启了"只听我的"模式
        if not self._is_sleep_group(group_id):
            return
        
        # 管理员消息放行
        if event.is_admin():
            return
        
        # 非管理员消息，拦截（停止事件传播）
        event.stop_event()
    
    @filter.regex(r"^#?只听我的$")
    async def enable_owner_only(self, event: AstrMessageEvent):
        """
        开启"只听我的"模式（关键词触发，无需指令前缀）
        
        开启后，Bot 在当前群只响应管理员的消息。
        仅管理员可用。
        """
        # 仅管理员可用
        if not event.is_admin():
            return
        
        group_id = event.get_group_id()
        if not group_id:
            return
        
        if self._is_sleep_group(group_id):
            yield event.plain_result("不要再说了~")
            return
        
        # 开启屏蔽模式
        self._sleep_groups[group_id] = True
        self._save_data()
        
        logger.info(f"[只听我的] 群 {group_id} 开启了屏蔽模式")
        yield event.plain_result("好的，现在只听主人的消息了~")
    
    @filter.regex(r"^#?听大家的$")
    async def disable_owner_only(self, event: AstrMessageEvent):
        """
        关闭"只听我的"模式（关键词触发，无需指令前缀）
        
        关闭后，Bot 在当前群恢复响应所有人的消息。
        仅管理员可用。
        """
        # 仅管理员可用
        if not event.is_admin():
            return
        
        group_id = event.get_group_id()
        if not group_id:
            return
        
        if not self._is_sleep_group(group_id):
            yield event.plain_result("不要再说了~")
            return
        
        # 关闭屏蔽模式
        self._sleep_groups[group_id] = False
        self._save_data()
        
        logger.info(f"[只听我的] 群 {group_id} 关闭了屏蔽模式")
        yield event.plain_result("好的，现在开始听大家的消息了~")
    
    @filter.regex(r"^#?(屏蔽列表|屏蔽群列表)$")
    async def list_sleep_groups(self, event: AstrMessageEvent):
        """
        查看已开启"只听我的"模式的群列表（关键词触发）
        仅管理员可用。
        """
        # 仅管理员可用
        if not event.is_admin():
            return
        
        # 过滤出开启屏蔽的群
        sleep_groups = [gid for gid, status in self._sleep_groups.items() if status]
        
        if not sleep_groups:
            yield event.plain_result("📋 当前没有群开启'只听我的'模式")
            return
        
        msg = "📋 已开启'只听我的'模式的群列表：\n"
        for gid in sleep_groups:
            msg += f"  • {gid}\n"
        
        yield event.plain_result(msg)
    
    async def terminate(self):
        """插件卸载时的清理工作"""
        logger.info("[只听我的] 插件已卸载")
