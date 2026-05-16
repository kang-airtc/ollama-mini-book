"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // 自动滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 组件卸载时关闭 EventSource
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleSend = () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: inputValue.trim(),
      timestamp: new Date().toLocaleTimeString(),
    };

    // 添加用户消息
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // 添加AI消息占位
    const assistantMessageId = Date.now() + 1;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      timestamp: new Date().toLocaleTimeString(),
      isStreaming: true,
    };
    setMessages((prev) => [...prev, assistantMessage]);

    // 关闭之前的 EventSource
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // 创建新的 EventSource
    const encodedQuery = encodeURIComponent(userMessage.content);
    const es = new EventSource(`http://localhost:8000/llm/rag?query=${encodedQuery}&n_results=5`);
    eventSourceRef.current = es;

    let fullContent = "";

    // 监听状态事件
    es.addEventListener("status", (e) => {
      try {
        const data = JSON.parse(e.data);
        console.log("Status:", data.message);
      } catch (err) {
        console.error("Parse status error:", e.data);
      }
    });

    // 监听检索数据事件
    es.addEventListener("retrieved_data", (e) => {
      try {
        const data = JSON.parse(e.data);
        console.log("Retrieved:", data.total, "tickets");
      } catch (err) {
        console.error("Parse retrieved_data error:", e.data);
      }
    });

    // 监听 LLM 流式输出事件 - 这是主要内容
    es.addEventListener("llm_chunk", (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.content) {
          fullContent += data.content;
          
          // 更新AI消息内容
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: fullContent }
                : msg
            )
          );
        }
      } catch (err) {
        console.error("Parse llm_chunk error:", e.data);
      }
    });

    // 监听完成事件
    es.addEventListener("status", (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.message && data.message.includes("完成")) {
          // 标记流式结束
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, isStreaming: false }
                : msg
            )
          );
          setIsLoading(false);
          es.close();
          eventSourceRef.current = null;
        }
      } catch (err) {
        // 忽略
      }
    });

    // 错误处理
    es.onerror = (error) => {
      console.error("EventSource error:", error);
      if (es.readyState === EventSource.CLOSED) {
        // 检查是否已完成
        if (fullContent.length > 0) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, isStreaming: false }
                : msg
            )
          );
        } else {
          // 没有收到内容，显示错误
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: "抱歉，连接出现错误，请稍后重试。",
                    isStreaming: false,
                  }
                : msg
            )
          );
        }
        setIsLoading(false);
        eventSourceRef.current = null;
      }
    };

    // 连接关闭
    es.onclose = () => {
      console.log("EventSource closed");
      setIsLoading(false);
      eventSourceRef.current = null;
    };
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearMessages = () => {
    setMessages([]);
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsLoading(false);
  };

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#f5f5f5",
      }}
    >
      {/* 头部 */}
      <div
        style={{
          padding: "16px 20px",
          backgroundColor: "#fff",
          borderBottom: "1px solid #e0e0e0",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "20px", color: "#333" }}>
            🤖 智能工单助手
          </h1>
          <p style={{ margin: "4px 0 0", fontSize: "12px", color: "#666" }}>
            基于 RAG 技术的语义搜索与问答
          </p>
        </div>
        <button
          onClick={clearMessages}
          style={{
            padding: "8px 16px",
            backgroundColor: "#f5f5f5",
            border: "1px solid #ddd",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          清空对话
        </button>
      </div>

      {/* 消息列表 */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
        }}
      >
        {messages.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              color: "#999",
              marginTop: "100px",
            }}
          >
            <p style={{ fontSize: "16px", marginBottom: "8px" }}>
              👋 欢迎使用智能工单助手
            </p>
            <p style={{ fontSize: "14px" }}>
              您可以询问关于工单的各种问题，例如：
            </p>
            <div
              style={{
                marginTop: "20px",
                display: "flex",
                flexDirection: "column",
                gap: "8px",
                alignItems: "center",
              }}
            >
              {[
                "最近有哪些退款相关的投诉？",
                "帮我查一下物流异常的工单",
                "有哪些高优先级的未解决问题？",
                "客户对服务态度的反馈有哪些？",
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setInputValue(example)}
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#fff",
                    border: "1px solid #e0e0e0",
                    borderRadius: "20px",
                    cursor: "pointer",
                    fontSize: "14px",
                    color: "#666",
                    maxWidth: "400px",
                    textAlign: "center",
                  }}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: "flex",
                justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                alignItems: "flex-start",
                gap: "8px",
              }}
            >
              {msg.role === "assistant" && (
                <div
                  style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "50%",
                    backgroundColor: "#673AB7",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "white",
                    fontSize: "14px",
                    flexShrink: 0,
                  }}
                >
                  AI
                </div>
              )}
              <div
                style={{
                  maxWidth: "70%",
                  padding: "12px 16px",
                  backgroundColor:
                    msg.role === "user" ? "#673AB7" : "#fff",
                  color: msg.role === "user" ? "#fff" : "#333",
                  borderRadius:
                    msg.role === "user"
                      ? "16px 16px 4px 16px"
                      : "16px 16px 16px 4px",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.1)",
                  fontSize: "14px",
                  lineHeight: "1.6",
                  whiteSpace: "pre-wrap",
                }}
              >
                {msg.content}
                {msg.isStreaming && (
                  <span style={{ opacity: 0.5, marginLeft: "4px" }}>▊</span>
                )}
              </div>
              {msg.role === "user" && (
                <div
                  style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "50%",
                    backgroundColor: "#e0e0e0",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#666",
                    fontSize: "14px",
                    flexShrink: 0,
                  }}
                >
                  我
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入框 */}
      <div
        style={{
          padding: "16px 20px",
          backgroundColor: "#fff",
          borderTop: "1px solid #e0e0e0",
          display: "flex",
          gap: "12px",
          alignItems: "center",
        }}
      >
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入您的问题..."
          disabled={isLoading}
          style={{
            flex: 1,
            padding: "12px 16px",
            border: "1px solid #e0e0e0",
            borderRadius: "24px",
            fontSize: "14px",
            outline: "none",
            backgroundColor: isLoading ? "#f5f5f5" : "#fff",
          }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !inputValue.trim()}
          style={{
            padding: "12px 24px",
            backgroundColor: isLoading ? "#ccc" : "#673AB7",
            color: "white",
            border: "none",
            borderRadius: "24px",
            cursor: isLoading || !inputValue.trim() ? "not-allowed" : "pointer",
            fontSize: "14px",
            fontWeight: "500",
          }}
        >
          {isLoading ? "思考中..." : "发送"}
        </button>
      </div>
    </div>
  );
}
