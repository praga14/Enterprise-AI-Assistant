import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import AuditTable from "../components/AuditTable";

function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);

  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const token = localStorage.getItem("access_token");

        const response = await fetch("http://127.0.0.1:8000/chat/history", {
          method: "GET",
          headers: {
            Authorization: "Bearer " + token,
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Failed to load chat history");
        }

        const formattedMessages = data.map((item) => ({
          id: item.id,
          sender: item.role === "assistant" ? "ai" : "user",
          text: item.content,

          // Chat history endpoint currently does not return
          // RAG source metadata.
          sources: [],
          auditRecords: null,
        }));

        setMessages(formattedMessages);
      } catch (error) {
        console.error("Chat history error:", error);
      } finally {
        setHistoryLoading(false);
      }
    };

    loadChatHistory();
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();

    const text = message.trim();

    if (!text || loading) {
      return;
    }

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: text,
      sources: [],
      auditRecords: null,
    };

    setMessages((previousMessages) => [...previousMessages, userMessage]);

    setMessage("");
    setLoading(true);

    try {
      const token = localStorage.getItem("access_token");

      const response = await fetch("http://127.0.0.1:8000/rag/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify({
          question: text,
          top_k: 5,
          similarity_threshold: 0.3,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to get AI response");
      }

      const aiMessage = {
        id: Date.now() + 1,
        sender: "ai",

        text:
          data.answer || data.response || data.message || JSON.stringify(data),

        // RAG source information
        sources: data.sources || [],

        // Audit information
        auditRecords: data.audit_records || null,
      };

      setMessages((previousMessages) => [...previousMessages, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        sender: "ai",
        text: "Error: " + error.message,
        sources: [],
        auditRecords: null,
      };

      setMessages((previousMessages) => [...previousMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="module-page">
        <div className="module-header">
          <h1>AI Chat</h1>

          <p>Ask questions about your enterprise knowledge.</p>
        </div>

        <div className="chat-container">
          <div className="chat-messages">
            {historyLoading && (
              <div className="chat-empty">Loading chat history...</div>
            )}

            {!historyLoading && messages.length === 0 && (
              <div className="chat-empty">
                <h3>Welcome to Enterprise AI</h3>

                <p>Ask a question about your company knowledge.</p>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={"message-row " + msg.sender}>
                <div className="message-avatar">
                  {msg.sender === "ai" ? "AI" : "A"}
                </div>

                <div className="message-content">
                  <span className="message-name">
                    {msg.sender === "ai" ? "Enterprise AI" : "You"}
                  </span>

                  <div className="message-bubble">{msg.text}</div>

                  {/* =========================
                      RAG SOURCES
                     ========================= */}

                  {msg.sender === "ai" &&
                    msg.sources &&
                    msg.sources.length > 0 && (
                      <div className="chat-sources">
                        <div className="chat-sources-title">Sources</div>

                        <div className="chat-sources-list">
                          {msg.sources.map((source, index) => (
                            <div
                              className="chat-source-item"
                              key={`${source.document_id}-${source.chunk_id}-${index}`}
                            >
                              <span className="chat-source-icon">📄</span>

                              <div className="chat-source-info">
                                <span className="chat-source-name">
                                  {source.document_name || "Unknown document"}
                                </span>

                                {source.similarity !== undefined && (
                                  <span className="chat-source-score">
                                    {(source.similarity * 100).toFixed(0)}%
                                    match
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                  {/* =========================
                      AUDIT TABLE
                     ========================= */}

                  {msg.sender === "ai" &&
                    msg.auditRecords &&
                    msg.auditRecords.length > 0 && (
                      <AuditTable records={msg.auditRecords} />
                    )}
                </div>
              </div>
            ))}

            {/* =========================
                LOADING MESSAGE
               ========================= */}

            {loading && (
              <div className="message-row ai">
                <div className="message-avatar">AI</div>

                <div className="message-content">
                  <span className="message-name">Enterprise AI</span>

                  <div className="message-bubble">Thinking...</div>
                </div>
              </div>
            )}
          </div>

          {/* =========================
              CHAT INPUT
             ========================= */}

          <form className="chat-input-area" onSubmit={handleSend}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask something about your company..."
              disabled={loading || historyLoading}
            />

            <button type="submit" disabled={loading || historyLoading}>
              {loading ? "Sending..." : "Send"}
            </button>
          </form>
        </div>
      </div>
    </Layout>
  );
}

export default Chat;
