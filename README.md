# Agent Ollama 实战小册

作者：**亢AIRTC**

请关注 B站 [亢AIRTC](https://space.bilibili.com/394612055) 视频教程，学习更多 AI、RTC 等知识。

---

## 简介

本书以「电商工单智能检索助手」为贯穿案例，从本地 Ollama 起步，逐步构建完整的 RAG 全栈应用：

- 本地大模型部署（Ollama）
- 文本切片 + Embedding 向量化
- ChromaDB 向量检索知识库
- FastMCP Agent 工具封装
- FastAPI SSE 流式后端
- Next.js 流式聊天前端

读者跟随章节动手，最终在本机跑出一套完整可用的本地大模型驱动的 RAG 应用。

## 目录

| 章节 | 标题 | 内容简介 |
|------|------|---------|
| 第01章 | Ollama 本地大模型快速上手 | Ollama 安装、模型拉取、CLI 验证，一行命令跑起本地 LLM |
| 第02章 | Ollama HTTP API 与流式响应 | 用 Python requests/httpx 调通 11434 端口，实现流式响应解码 |
| 第03章 | 文本切片：为向量化准备数据 | 固定长度切片 vs 带重叠切片，粒度选择与工程要点 |
| 第04章 | Embedding 向量化原理与实战 | nomic-embed-text 向量化，语义距离与相似度原理 |
| 第05章 | ChromaDB 向量数据库入门 | 集合、文档、元数据模型，内存与持久化客户端，Ollama 嵌入接入 |
| 第06章 | 构建工单知识库 | 电商工单从原始数据到向量库的完整入库流程 |
| 第07章 | FastMCP 把检索封装成 Agent 工具 | MCP 协议介绍，用 FastMCP 把检索能力标准化为 Agent 工具 |
| 第08章 | FastAPI 与 SSE 流式 RAG 后端 | 检索增强提示词构造，SSE 推流，完整 RAG 后端实现 |
| 第09章 | Next.js 前端流式聊天界面 | EventSource 接收 SSE，流式渲染检索状态与模型回答 |
| 第10章 | 全栈联调与排错 | 四进程启动顺序、常见故障、调试技巧，全栈跑通指南 |

## 配套源码

- **本书源码**：[https://github.com/kang-airtc/ollama-mini-book](https://github.com/kang-airtc/ollama-mini-book)
- Demo 代码在 `agent-ollama-demo/` 目录，按章节组织，每章独立可运行

## 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.10+ |
| Ollama | 最新版 |
| Node.js | 18+ |

本地模型推荐：
- 对话：`qwen2.5:7b` 或 `llama3.2:3b`
- Embedding：`nomic-embed-text`

## 快速开始

```bash
# 1. 拉取模型
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# 2. 安装 Python 依赖（以第5章为例）
cd agent-ollama-demo/ch05
pip install -r requirements.txt

# 3. 运行示例
python main.py
```

全栈联调步骤详见第10章。
