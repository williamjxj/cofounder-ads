# 付费 0-1 优先的发帖循环（X 每天，Reddit 周一，LinkedIn 周四）

为「接 AI 0-1 付费项目」生成并排队草稿，合伙人为第二条更窄的漏斗。**任何内容都不会自动发布。**

只依赖 **Python 3**（纯标准库）。用法见 [TODO.md](TODO.md)。为什么这样做：[docs/RESEARCH.md](docs/RESEARCH.md)、[docs/ANALYSIS.md](docs/ANALYSIS.md)、[docs/SPEC.md](docs/SPEC.md)。

> English original: [README.md](README.md)

> **当前状态（2026-09-18）：** 主 offer 是 **先接付费 scoped 0-1 项目**，合伙人只是更窄的第二条漏斗。`cta_url` 指向 GitHub Pages 落地页：`.github/workflows/pages.yml` 从 `public/` 自动部署，Pages 来源已设为 **GitHub Actions**。落地页两个按钮都直接约 Cal.com fit call，`public/og.png` 是 1200×630 的分享卡片。第一条 X 已经发出去，现在进入日常节奏，没有一次性配置了。

粘贴前先看一眼 X 的链接预览卡片：平台按 URL 缓存卡片，同一个 URL 可能仍然显示旧预览；必要时在 URL 后加 `?v=2` 强制重新抓取。

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
