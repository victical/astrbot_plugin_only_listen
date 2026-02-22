# AstrBot 只听我的插件

<div align="center">

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.0%2B-orange.svg)](https://github.com/Soulter/AstrBot)

</div>

## 📖 介绍

`astrbot_plugin_only_listen` 是一款为 AstrBot 设计的群聊管理插件。它允许管理员控制 Bot 是否只响应管理员的消息，适用于需要限制 Bot 响应范围的场景。

## ✨ 功能特性

- 🔒 **只听我的模式**：开启后，Bot 在群聊中只响应管理员的消息
- 🔓 **听大家的模式**：关闭后，Bot 恢复响应所有人的消息
- 📋 **屏蔽列表查看**：查看已开启"只听我的"模式的群列表
- 💾 **数据持久化**：使用 AstrBot 内置 KV 存储，重启后配置不丢失
- ⚡ **高优先级拦截**：使用超高优先级确保在其他插件之前拦截消息

## 📦 安装

### 方法一：插件市场安装

在 AstrBot 管理面板的插件市场搜索 `astrbot_plugin_only_listen`，点击安装即可。

### 方法二：手动安装

```bash
# 克隆仓库到插件目录
cd /path/to/AstrBot/data/plugins
git clone https://github.com/victical/astrbot_plugin_only_listen.git

# 重启 AstrBot
```

## ⌨️ 使用说明

### 触发关键词

| 关键词 | 说明 |
|:---|:---|
| `只听我的` 或 `#只听我的` | 开启"只听我的"模式，Bot 只响应管理员消息 |
| `听大家的` 或 `#听大家的` | 关闭"只听我的"模式，Bot 恢复响应所有人 |
| `屏蔽列表` 或 `#屏蔽列表` | 查看已开启"只听我的"模式的群列表 |

> ⚠️ **注意**：此插件仅管理员可用，非管理员发送关键词无响应。

### 使用示例

```
管理员: 只听我的
Bot: 好的，现在只听主人的消息了~

管理员: #只听我的
Bot: 好的，现在只听主人的消息了~

管理员: 只听我的 (已开启时)
Bot: 不要再说了~

管理员: 听大家的
Bot: 好的，现在开始听大家的消息了~

管理员: 屏蔽列表
Bot: 📋 已开启'只听我的'模式的群列表：
     • 123456789
     • 987654321
```

## 🔧 工作原理

1. **消息拦截**：插件使用超高优先级 (`sys.maxsize - 1`) 的群消息处理器
2. **权限判断**：通过 `event.is_admin()` 判断发送者是否为管理员
3. **事件停止**：非管理员消息调用 `event.stop_event()` 停止事件传播
4. **数据存储**：使用 JSON 文件持久化配置（存储于 `data/plugins_data/astrbot_plugin_only_listen/sleep_groups.json`）

## 📌 注意事项

- 此插件仅在群聊中生效，私聊不受影响
- 管理员身份由 AstrBot 核心配置决定（`admins_id`）
- 开启"只听我的"模式后，普通用户的消息仍会被其他插件接收（如果其他插件优先级更高）

## 🤝 贡献指南

- 🌟 Star 这个项目！
- 🐛 提交 Issue 报告问题
- 💡 提出新功能建议
- 🔧 提交 Pull Request 改进代码

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。
