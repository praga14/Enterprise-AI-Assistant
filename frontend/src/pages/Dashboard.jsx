import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";

function Dashboard() {
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token");

        const response = await fetch("http://127.0.0.1:8000/dashboard/stats", {
          method: "GET",
          headers: {
            Authorization: "Bearer " + token,
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Failed to load dashboard");
        }

        setStats(data);
      } catch (err) {
        console.error("Dashboard error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) {
      return "-";
    }

    const date = new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
      return timestamp;
    }

    return date.toLocaleString("en-IN", {
      timeZone: "Asia/Kolkata",
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  return (
    <Layout>
      <div className="dashboard-page">
        {/* Header */}

        <div className="dashboard-header">
          <div>
            <h1>Dashboard</h1>
            <p>Enterprise AI Application Intelligence</p>
          </div>
        </div>

        {/* Error */}

        {error && <div className="dashboard-error">{error}</div>}

        {/* Welcome */}

        <div className="welcome-card">
          <div>
            <h2>Welcome back 👋</h2>

            <p>
              Manage your enterprise knowledge, users, access, documents, and
              AI-powered intelligence from one place.
            </p>
          </div>

          <button className="welcome-action" onClick={() => navigate("/chat")}>
            Ask AI
          </button>
        </div>

        {/* Statistics */}

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">👥</div>

            <div className="stat-content">
              <span className="stat-title">Total Users</span>

              <strong>{loading ? "—" : (stats?.total_users ?? 0)}</strong>

              <small>
                {loading
                  ? "Loading..."
                  : `${stats?.active_users ?? 0} active users`}
              </small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📄</div>

            <div className="stat-content">
              <span className="stat-title">Documents</span>

              <strong>{loading ? "—" : (stats?.documents ?? 0)}</strong>

              <small>Knowledge sources</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">💬</div>

            <div className="stat-content">
              <span className="stat-title">AI Conversations</span>

              <strong>{loading ? "—" : (stats?.ai_conversations ?? 0)}</strong>

              <small>AI interactions</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🛡️</div>

            <div className="stat-content">
              <span className="stat-title">Audit Events</span>

              <strong>{loading ? "—" : (stats?.audit_events ?? 0)}</strong>

              <small>Tracked activities</small>
            </div>
          </div>
        </div>

        {/* Quick Actions */}

        <div className="dashboard-section">
          <div className="section-header">
            <div>
              <h2>Quick Actions</h2>
              <p>Common enterprise tasks</p>
            </div>
          </div>

          <div className="action-grid">
            <button className="action-card" onClick={() => navigate("/chat")}>
              <div className="action-icon">💬</div>

              <div>
                <h3>Ask AI</h3>

                <p>Ask questions about company knowledge.</p>
              </div>

              <span className="action-arrow">→</span>
            </button>

            <button
              className="action-card"
              onClick={() => navigate("/documents")}
            >
              <div className="action-icon">📄</div>

              <div>
                <h3>Documents</h3>

                <p>Add and manage AI knowledge sources.</p>
              </div>

              <span className="action-arrow">→</span>
            </button>

            <button
              className="action-card"
              onClick={() => navigate("/code-intelligence")}
            >
              <div className="action-icon">💻</div>

              <div>
                <h3>Analyze Code</h3>

                <p>Understand and search your company code.</p>
              </div>

              <span className="action-arrow">→</span>
            </button>

            <button className="action-card" onClick={() => navigate("/users")}>
              <div className="action-icon">👥</div>

              <div>
                <h3>Manage Users</h3>

                <p>Manage users, roles, and access.</p>
              </div>

              <span className="action-arrow">→</span>
            </button>
          </div>
        </div>

        {/* Bottom Panels */}

        <div className="dashboard-bottom-grid">
          {/* System Overview */}

          <div className="dashboard-panel">
            <div className="panel-header">
              <div>
                <h2>System Overview</h2>

                <p>Current application status</p>
              </div>

              <span className="status-badge">● Operational</span>
            </div>

            <div className="system-list">
              <div className="system-item">
                <div>
                  <strong>AI Assistant</strong>
                  <span>LLM and chat services</span>
                </div>

                <span className="system-status">Operational</span>
              </div>

              <div className="system-item">
                <div>
                  <strong>Knowledge Base</strong>
                  <span>Documents and RAG</span>
                </div>

                <span className="system-status">Operational</span>
              </div>

              <div className="system-item">
                <div>
                  <strong>Access Intelligence</strong>
                  <span>Users, roles and permissions</span>
                </div>

                <span className="system-status">Operational</span>
              </div>

              <div className="system-item">
                <div>
                  <strong>Audit System</strong>
                  <span>Activity tracking</span>
                </div>

                <span className="system-status">Operational</span>
              </div>
            </div>
          </div>

          {/* Recent Activity */}

          <div className="dashboard-panel">
            <div className="panel-header">
              <div>
                <h2>Recent Activity</h2>

                <p>Latest enterprise activity</p>
              </div>

              <button
                className="panel-link"
                onClick={() => navigate("/audit-logs")}
              >
                View all
              </button>
            </div>

            <div className="dashboard-activity-list">
              {loading && (
                <div className="activity-loading">
                  Loading recent activity...
                </div>
              )}

              {!loading && stats?.recent_activity?.length === 0 && (
                <div className="activity-empty">
                  <div className="activity-empty-icon">🕒</div>

                  <h3>No recent activity</h3>

                  <p>Recent audit events will appear here.</p>
                </div>
              )}

              {!loading &&
                stats?.recent_activity?.map((activity) => (
                  <div className="dashboard-activity-item" key={activity.id}>
                    <div className="activity-dot">•</div>

                    <div className="activity-content">
                      <strong>{activity.action || "Activity"}</strong>

                      <span>
                        {activity.details ||
                          `${activity.resource || "System"} activity`}
                      </span>

                      <small>
                        {activity.actor || "-"}
                        {" · "}
                        {formatTimestamp(activity.timestamp)}
                      </small>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default Dashboard;
