# 付费 0-1 优先的发帖循环（X 每天，Reddit 周一，LinkedIn 周四）

为「接 AI 0-1 付费项目」生成并排队草稿，合伙人为第二条更窄的漏斗。**任何内容都不会自动发布。**

只依赖 **Python 3**（纯标准库）。用法见 [TODO.md](TODO.md)。为什么这样做：[docs/RESEARCH.md](docs/RESEARCH.md)、[docs/ANALYSIS.md](docs/ANALYSIS.md)、[docs/SPEC.md](docs/SPEC.md)。

> English original: [README.md](README.md)

> **当前状态（2026-09-17）：** 主offer 从「先找股东再赚钱」改成 **先接付费 scoped 项目**。`cta_url` 指向 GitHub Pages 落地页。在仓库 Settings 里打开 Pages（GitHub Actions），确认 https://williamjxj.github.io/cofounder-ads/ 可访问，然后把今天的 X 草稿贴出去。

## 界面

```bash
python3 -m engine serve
# 看板：http://127.0.0.1:4901   落地页：http://127.0.0.1:4901/landing
```

隔壁 `platform` 项目里的包装器仍然可用。**发布仍然是手动粘贴。**

## 每天做什么

```bash
python3 -m engine tick
python3 -m engine status
# 粘贴 queue/今天/x.md 的 Post 到 X
python3 -m engine published --platform x --url 'https://x.com/YOU/status/ID'
```

`tick` 对同一天同一平台是幂等的，不会再追加一行账本。

## 节奏

| 平台 | 默认 | 你要做的 |
|---|---|---|
| X | 每天 | 审核并发布 |
| Reddit | 每周一 | 审核并发布 |
| LinkedIn | 每周四 | 审核并发布 |

## 验证

```bash
python3 -m unittest discover -s tests -v
```

## 这个项目不是什么

不是拿去卖的发帖 SaaS，不是自动发帖机器人，不引入额外 Python 依赖。
