import asyncio
import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import EventSourceResponse
from fastapi.sse import ServerSentEvent
from agent_client import call_agent_tool, call_search_tickets_semantic
from dotenv import load_dotenv

load_dotenv()

# Ollama API 配置
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def stream_ollama_llm(prompt: str):
    """
    调用 Ollama LLM API - 流式版本
    返回异步生成器，每次 yield 一个文本片段
    """
    import httpx

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "model": OLLAMA_MODEL,
        "system": "你是一个专业的电商客服数据分析助手。请根据提供的工单数据进行分析，并给出简洁的总结和建议。",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "options": {"temperature": 0.7, "num_predict": 2000},
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE_URL}/api/chat",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    line = line.strip()

                    # 跳过空行
                    if not line:
                        continue

                    try:
                        chunk = json.loads(line)

                        # 检查是否是流式输出结束
                        if chunk.get("done", False):
                            break

                        # 获取消息内容
                        message = chunk.get("message", {})
                        if message:
                            content = message.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
                    except Exception:
                        continue
    except httpx.HTTPError as e:
        yield f"HTTP 错误: {str(e)}"
    except Exception as e:
        yield f"调用 LLM 时出错: {str(e)}"


@app.get("/")
def read_root():
    return {
        "message": "RAG Backend API",
        "endpoints": {
            "/llm/rag?query=xxx&n_results=5": "RAG模式：语义搜索 + LLM 问答",
            "/health": "健康检查",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/llm/rag", response_class=EventSourceResponse)
async def rag_stream(query: str = "", n_results: int = 5):
    """
    RAG 模式：检索增强生成
    流程：用户问题 → 向量搜索 → 结合上下文调用 LLM → 流式返回

    Args:
        query: 用户问题/查询
        n_results: 检索的相关工单数量，默认5条
    """
    if not query:
        yield ServerSentEvent(event="error", data={"message": "查询内容不能为空"})
        return

    # 阶段 1: 开始 RAG 流程
    yield ServerSentEvent(
        event="status", data={"message": f"正在分析问题: {query[:50]}..."}
    )
    await asyncio.sleep(0.3)

    # 阶段 2: 向量搜索 - 检索相关工单
    yield ServerSentEvent(event="status", data={"message": "正在进行语义检索..."})

    try:
        search_result = await call_search_tickets_semantic(query, n_results)
        search_data = json.loads(search_result)

        total_results = search_data.get("total_results", 0)

        if total_results == 0:
            yield ServerSentEvent(
                event="status", data={"message": "未找到相关工单，将基于通用知识回答"}
            )
            relevant_tickets = []
        else:
            yield ServerSentEvent(
                event="status", data={"message": f"检索到 {total_results} 条相关工单"}
            )
            relevant_tickets = search_data.get("results", [])
            # 发送检索结果给前端
            yield ServerSentEvent(
                event="retrieved_data",
                data={"total": total_results, "tickets": relevant_tickets},
            )

        await asyncio.sleep(0.3)

        # 阶段 3: 构造 RAG 提示词并调用 LLM
        yield ServerSentEvent(event="status", data={"message": "正在生成回答..."})

        # 构建提示词
        if relevant_tickets:
            # 格式化检索到的工单
            tickets_text = "\n\n".join(
                [
                    f"【工单 {i + 1}】(相关度: {t.get('similarity_score', 0):.1%})\n"
                    f"工单号: {t['ticket_no']}\n"
                    f"客户: {t['customer_name']}\n"
                    f"类型: {t['issue_type']}\n"
                    f"优先级: {t['priority']}\n"
                    f"状态: {t['status']}\n"
                    f"主题: {t['subject']}\n"
                    f"描述: {t.get('description', '无')}"
                    for i, t in enumerate(relevant_tickets)
                ]
            )

            prompt = f"""你是电商客服数据分析专家。请根据以下检索到的相关工单，回答用户的问题。

用户问题：
{query}

检索到的相关工单（共 {total_results} 条）：
{tickets_text}

请按以下格式回答：

1. 直接回答：简要回答用户的问题（2-3句话）

2. 相关工单分析：
   - 这些工单的主要特点
   - 涉及的客户和问题类型
   - 当前处理状态

3. 建议措施：
   - 针对这些工单的处理建议
   - 如何改进客服工作

注意：
- 如果检索到的工单不足以回答问题，请说明"根据现有数据无法完全回答"
- 回答要简洁专业，适合客服人员参考
"""
        else:
            # 没有检索到相关工单时
            prompt = f"""你是电商客服数据分析专家。用户提出了以下问题，但在知识库中未找到相关工单记录。

用户问题：
{query}

请基于你的专业知识，给出一个通用的回答和建议。同时说明"当前知识库中无相关工单记录，建议补充相关数据"。

请按以下格式回答：
1. 通用建议（基于专业知识）
2. 数据补充建议（需要收集哪些信息）
"""

        # 流式调用 LLM
        async for chunk in stream_ollama_llm(prompt):
            yield ServerSentEvent(event="llm_chunk", data={"content": chunk})

        # 完成
        yield ServerSentEvent(event="status", data={"message": "回答完成！"})

    except Exception as e:
        yield ServerSentEvent(
            event="error", data={"message": f"RAG 处理失败: {str(e)}"}
        )
