#!/usr/bin/env python3
"""
电商工单向量检索 MCP Server (HTTP/SSE 模式)
使用 FastMCP + ChromaDB + Ollama Embedding 构建
仅提供向量语义搜索功能
"""

import json
import requests
from datetime import datetime
from pathlib import Path

import chromadb
from fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP("电商工单向量检索服务-HTTP")

# ChromaDB 配置
CHROMA_DB_PATH = Path("./chroma_db")
CHROMA_DB_PATH.mkdir(exist_ok=True)

# Ollama 配置
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_EMBED_MODEL = "nomic-embed-text:latest"

# 初始化 ChromaDB 客户端
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

# 获取或创建工单集合
try:
    tickets_collection = chroma_client.get_collection("tickets")
except Exception:
    tickets_collection = chroma_client.create_collection(
        name="tickets", metadata={"description": "电商工单数据集合，支持向量检索"}
    )


def get_embedding(text: str) -> list:
    """
    调用 Ollama nomic-embed-text 模型生成向量嵌入
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": OLLAMA_EMBED_MODEL, "prompt": text},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        return result.get("embedding", [])
    except Exception as e:
        print(f"获取嵌入失败: {e}")
        return []


def format_ticket_text(ticket: dict) -> str:
    """
    将工单格式化为文本，用于向量嵌入
    """
    return (
        f"工单号:{ticket['ticket_no']} | "
        f"客户:{ticket['customer_name']} | "
        f"类型:{ticket['issue_type']} | "
        f"优先级:{ticket['priority']} | "
        f"状态:{ticket['status']} | "
        f"主题:{ticket['subject']}"
        f"{(' | 描述:' + ticket['description']) if ticket.get('description') else ''}"
    )


def clean_metadata(ticket: dict) -> dict:
    """
    清理元数据，将 None 值转换为空字符串
    ChromaDB 不支持 None 值
    """
    cleaned = {}
    for key, value in ticket.items():
        if value is None:
            cleaned[key] = ""
        else:
            cleaned[key] = value
    return cleaned


def init_sample_data():
    """初始化示例工单数据并生成向量嵌入"""
    # 检查是否已有数据
    count = tickets_collection.count()
    if count > 0:
        print(f"ChromaDB 中已有 {count} 条工单数据，跳过初始化")
        return

    sample_tickets = [
        {
            "ticket_no": "TK2024001",
            "customer_name": "张三",
            "customer_email": "zhangsan@email.com",
            "issue_type": "退款申请",
            "priority": "high",
            "status": "resolved",
            "subject": "订单未收到货要求退款",
            "description": "客户在3天前下单但物流显示异常",
            "created_at": "2024-01-15T09:30:00",
            "resolved_at": "2024-01-15T14:20:00",
            "satisfaction_score": 5,
        },
        {
            "ticket_no": "TK2024002",
            "customer_name": "李四",
            "customer_email": "lisi@email.com",
            "issue_type": "商品质量问题",
            "priority": "medium",
            "status": "in_progress",
            "subject": "收到的商品有破损",
            "description": "包装盒完好但内部商品破损",
            "created_at": "2024-01-15T10:15:00",
            "resolved_at": None,
            "satisfaction_score": None,
        },
        {
            "ticket_no": "TK2024003",
            "customer_name": "王五",
            "customer_email": "wangwu@email.com",
            "issue_type": "物流查询",
            "priority": "low",
            "status": "open",
            "subject": "查询订单物流状态",
            "description": "订单显示已发货但3天未更新物流",
            "created_at": "2024-01-15T11:00:00",
            "resolved_at": None,
            "satisfaction_score": None,
        },
        {
            "ticket_no": "TK2024004",
            "customer_name": "赵六",
            "customer_email": "zhaoliu@email.com",
            "issue_type": "发票申请",
            "priority": "medium",
            "status": "resolved",
            "subject": "申请开具增值税发票",
            "description": "需要开具公司抬头的专票",
            "created_at": "2024-01-14T16:45:00",
            "resolved_at": "2024-01-15T09:00:00",
            "satisfaction_score": 4,
        },
        {
            "ticket_no": "TK2024005",
            "customer_name": "钱七",
            "customer_email": "qianqi@email.com",
            "issue_type": "退货申请",
            "priority": "high",
            "status": "in_progress",
            "subject": "尺码不合适需要退货",
            "description": "购买的鞋子尺码偏小需要换货",
            "created_at": "2024-01-15T13:20:00",
            "resolved_at": None,
            "satisfaction_score": None,
        },
        {
            "ticket_no": "TK2024006",
            "customer_name": "孙八",
            "customer_email": "sunba@email.com",
            "issue_type": "账户问题",
            "priority": "low",
            "status": "closed",
            "subject": "无法登录账户",
            "description": "忘记密码且手机号已更换",
            "created_at": "2024-01-13T10:00:00",
            "resolved_at": "2024-01-13T11:30:00",
            "satisfaction_score": 5,
        },
        {
            "ticket_no": "TK2024007",
            "customer_name": "周九",
            "customer_email": "zhoujiu@email.com",
            "issue_type": "退款申请",
            "priority": "medium",
            "status": "open",
            "subject": "重复扣款问题",
            "description": "同一订单被扣款两次",
            "created_at": "2024-01-15T15:00:00",
            "resolved_at": None,
            "satisfaction_score": None,
        },
        {
            "ticket_no": "TK2024008",
            "customer_name": "吴十",
            "customer_email": "wushi@email.com",
            "issue_type": "商品咨询",
            "priority": "low",
            "status": "resolved",
            "subject": "询问商品规格",
            "description": "想了解某款手机的详细参数",
            "created_at": "2024-01-15T08:00:00",
            "resolved_at": "2024-01-15T08:30:00",
            "satisfaction_score": 5,
        },
        {
            "ticket_no": "TK2024009",
            "customer_name": "郑一",
            "customer_email": "zhengyi@email.com",
            "issue_type": "投诉建议",
            "priority": "high",
            "status": "in_progress",
            "subject": "客服态度投诉",
            "description": "对上次客服处理结果不满意",
            "created_at": "2024-01-15T16:00:00",
            "resolved_at": None,
            "satisfaction_score": None,
        },
        {
            "ticket_no": "TK2024010",
            "customer_name": "陈二",
            "customer_email": "chener@email.com",
            "issue_type": "物流查询",
            "priority": "medium",
            "status": "resolved",
            "subject": "快递显示已签收但未收到",
            "description": "可能是快递柜或代收点",
            "created_at": "2024-01-14T14:20:00",
            "resolved_at": "2024-01-15T10:00:00",
            "satisfaction_score": 4,
        },
    ]

    print(f"正在初始化 {len(sample_tickets)} 条示例数据...")

    for ticket in sample_tickets:
        # 生成文本并嵌入
        ticket_text = format_ticket_text(ticket)
        embedding = get_embedding(ticket_text)

        if embedding:
            # 清理元数据（移除 None 值）
            cleaned_metadata = clean_metadata(ticket)
            # 存储到 ChromaDB
            tickets_collection.add(
                ids=[ticket["ticket_no"]],
                embeddings=[embedding],
                documents=[ticket_text],
                metadatas=[cleaned_metadata],
            )
            print(f"✅ {ticket['ticket_no']}: {ticket['subject'][:30]}...")
        else:
            print(f"❌ {ticket['ticket_no']}: 嵌入失败")

    print(f"✅ 初始化完成，共添加 {tickets_collection.count()} 条数据")


@mcp.tool()
def search_tickets_semantic(query: str, n_results: int = 5) -> str:
    """
    语义搜索工单 - 使用向量相似度

    Args:
        query: 搜索查询（自然语言描述）
        n_results: 返回结果数量，默认5条
    """
    try:
        # 生成查询的向量嵌入
        query_embedding = get_embedding(query)

        if not query_embedding:
            return json.dumps({"error": "生成查询向量失败"}, ensure_ascii=False)

        # 在 ChromaDB 中进行向量搜索
        results = tickets_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "documents", "distances"],
        )

        # 格式化结果
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, ticket_id in enumerate(results["ids"][0]):
                ticket = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                document = results["documents"][0][i]

                search_results.append(
                    {
                        "ticket_no": ticket_id,
                        "customer_name": ticket.get("customer_name", ""),
                        "issue_type": ticket.get("issue_type", ""),
                        "priority": ticket.get("priority", ""),
                        "status": ticket.get("status", ""),
                        "subject": ticket.get("subject", ""),
                        "description": ticket.get("description", ""),
                        "created_at": ticket.get("created_at", ""),
                        "similarity_score": round(1 - distance, 4),  # 转换为相似度分数
                        "matched_text": document[:100] + "..."
                        if len(document) > 100
                        else document,
                    }
                )

        return json.dumps(
            {
                "query": query,
                "total_results": len(search_results),
                "results": search_results,
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception as e:
        return json.dumps({"error": f"搜索失败: {str(e)}"}, ensure_ascii=False)


@mcp.tool()
def rebuild_vector_store() -> str:
    """重建向量库（清空后重新初始化示例数据）"""
    try:
        # 清空集合
        all_ids = tickets_collection.get()["ids"]
        if all_ids:
            tickets_collection.delete(ids=all_ids)
            print(f"已清空 {len(all_ids)} 条旧数据")

        # 重新初始化
        init_sample_data()

        return json.dumps(
            {
                "success": True,
                "message": f"向量库重建完成，当前共 {tickets_collection.count()} 条数据",
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"error": f"重建失败: {str(e)}"}, ensure_ascii=False)


if __name__ == "__main__":
    # 初始化示例数据
    init_sample_data()

    print("\n启动电商工单向量检索 MCP Server...")
    print("服务端点: http://localhost:8001/mcp")
    print("\n提供工具:")
    print("  • search_tickets_semantic - 语义搜索（向量检索）")
    print("  • rebuild_vector_store - 重建向量库")

    mcp.run(transport="streamable-http", port=8001, path="/mcp")
