import { useEffect, useState } from "react";
import Layout from "../components/Layout";

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [showViewModal, setShowViewModal] = useState(false);
  const [accessDocument, setAccessDocument] = useState(null);
  const [showAccessModal, setShowAccessModal] = useState(false);
  const [accessLoading, setAccessLoading] = useState(false);
  const [accessData, setAccessData] = useState(null);
  const [showGrantModal, setShowGrantModal] = useState(false);
  const [grantType, setGrantType] = useState("user");
  const [grantUsername, setGrantUsername] = useState("");
  const [grantRoleId, setGrantRoleId] = useState("");
  const [grantLoading, setGrantLoading] = useState(false);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError("");

      const token = localStorage.getItem("access_token");

      const response = await fetch("http://127.0.0.1:8000/documents", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        throw new Error("Your session has expired. Please log in again.");
      }

      if (response.status === 403) {
        throw new Error("You do not have permission to view documents.");
      }

      if (!response.ok) {
        throw new Error(`Failed to load documents (${response.status})`);
      }

      const data = await response.json();

      setDocuments(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Document loading error:", err);
      setError(err.message || "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) {
      return;
    }

    try {
      setUploading(true);
      setError("");

      const token = localStorage.getItem("access_token");

      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://127.0.0.1:8000/documents/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.status === 401) {
        throw new Error("Your session has expired. Please log in again.");
      }

      if (response.status === 403) {
        throw new Error("You do not have permission to upload documents.");
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to upload document");
      }

      // Add the newly uploaded document to the list
      setDocuments((currentDocuments) => [data, ...currentDocuments]);

      // Close modal
      setShowUploadModal(false);
      setSelectedFile(null);
    } catch (err) {
      console.error("Document upload error:", err);
      setError(err.message || "Failed to upload document");
    } finally {
      setUploading(false);
    }
  };

  const handleView = (document) => {
    setSelectedDocument(document);
    setShowViewModal(true);
  };

  const handleManageAccess = async (document) => {
    try {
      setAccessDocument(document);
      setShowAccessModal(true);
      setAccessLoading(true);
      setAccessData(null);
      setError("");

      const token = localStorage.getItem("access_token");

      const response = await fetch(
        `http://127.0.0.1:8000/access-query/document/${encodeURIComponent(
          document.name,
        )}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (response.status === 401) {
        throw new Error("Your session has expired. Please log in again.");
      }

      if (response.status === 403) {
        throw new Error("You do not have permission to view document access.");
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load document access");
      }

      setAccessData(data);
    } catch (err) {
      console.error("Document access error:", err);

      setError(err.message || "Failed to load document access");
    } finally {
      setAccessLoading(false);
    }
  };

  const handleDelete = async (document) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${document.name}"?\n\nThis will also remove its chunks and embeddings.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(document.id);
      setError("");

      const token = localStorage.getItem("access_token");

      const response = await fetch(
        `http://127.0.0.1:8000/documents/${document.id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (response.status === 401) {
        throw new Error("Your session has expired. Please log in again.");
      }

      if (response.status === 403) {
        throw new Error("You do not have permission to delete documents.");
      }

      if (response.status === 404) {
        throw new Error("Document was not found.");
      }

      if (!response.ok) {
        throw new Error(`Failed to delete document (${response.status})`);
      }

      // Remove deleted document from UI immediately
      setDocuments((currentDocuments) =>
        currentDocuments.filter((item) => item.id !== document.id),
      );
    } catch (err) {
      console.error("Document deletion error:", err);
      setError(err.message || "Failed to delete document");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredDocuments = documents.filter((document) =>
    document.name?.toLowerCase().includes(search.toLowerCase()),
  );

  const formatDate = (timestamp) => {
    if (!timestamp) return "-";

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

  const handleGrantAccess = async () => {
    if (!accessDocument) {
      return;
    }

    try {
      setGrantLoading(true);
      setError("");

      const token = localStorage.getItem("access_token");

      let url = "";

      if (grantType === "user") {
        url =
          `http://127.0.0.1:8000/document-access/grant-user` +
          `?username=${encodeURIComponent(grantUsername.trim())}` +
          `&document_id=${accessDocument.id}`;
      } else {
        url =
          `http://127.0.0.1:8000/document-access/grant` +
          `?username=${encodeURIComponent(grantUsername.trim())}` +
          `&document_id=${accessDocument.id}` +
          `&role_id=${grantRoleId}`;
      }

      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (response.status === 401) {
        throw new Error("Your session has expired. Please log in again.");
      }

      if (response.status === 403) {
        throw new Error("You do not have permission to grant document access.");
      }

      if (!response.ok) {
        throw new Error(data.detail || "Failed to grant document access");
      }

      setShowGrantModal(false);

      await handleManageAccess(accessDocument);
    } catch (err) {
      console.error("Grant access error:", err);

      setError(err.message || "Failed to grant document access");
    } finally {
      setGrantLoading(false);
    }
  };

  const handleRevokeAccess = async (user) => {
    if (!accessDocument) {
      return;
    }

    const confirmed = window.confirm(
      `Revoke ${user.full_name || user.username}'s access to ${accessDocument.name}?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setAccessLoading(true);
      setError("");

      const token = localStorage.getItem("access_token");

      let url = "";

      if (user.access_type === "role") {
        url =
          `http://127.0.0.1:8000/document-access/revoke` +
          `?document_id=${accessDocument.id}` +
          `&role_id=${user.role_id}`;
      } else {
        url =
          `http://127.0.0.1:8000/document-access/revoke-user` +
          `?username=${encodeURIComponent(user.username)}` +
          `&document_id=${accessDocument.id}`;
      }

      const response = await fetch(url, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (response.status === 401) {
        throw new Error("Your session has expired. Please log in again.");
      }

      if (response.status === 403) {
        throw new Error(
          "You do not have permission to revoke document access.",
        );
      }

      if (!response.ok) {
        throw new Error(data.detail || "Failed to revoke document access");
      }

      await handleManageAccess(accessDocument);
    } catch (err) {
      console.error("Revoke access error:", err);

      setError(err.message || "Failed to revoke document access");
    } finally {
      setAccessLoading(false);
    }
  };

  return (
    <Layout>
      <div className="documents-page">
        {/* Header */}
        <div className="documents-header">
          <div>
            <h1>Documents</h1>
            <p>Manage enterprise knowledge and AI document sources.</p>
          </div>

          <button
            className="documents-upload-btn"
            type="button"
            onClick={() => setShowUploadModal(true)}
          >
            + Upload Document
          </button>
        </div>

        {/* Toolbar */}
        <div className="documents-toolbar">
          <div className="documents-search">
            <span>🔍</span>

            <input
              type="text"
              placeholder="Search documents..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div className="documents-count">
            {filteredDocuments.length} document
            {filteredDocuments.length !== 1 ? "s" : ""}
          </div>
        </div>

        {/* Error */}
        {error && <div className="documents-error">{error}</div>}

        {/* Loading */}
        {loading ? (
          <div className="documents-state">Loading documents...</div>
        ) : filteredDocuments.length === 0 ? (
          <div className="documents-state">
            <div className="documents-empty-icon">📄</div>

            <h3>No documents found</h3>

            <p>
              {search
                ? "No documents match your search."
                : "No documents have been uploaded yet."}
            </p>
          </div>
        ) : (
          <div className="documents-table-wrapper">
            <table className="documents-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Type</th>
                  <th>Uploaded By</th>
                  <th>Created</th>
                  <th>Updated</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {filteredDocuments.map((document) => (
                  <tr key={document.id}>
                    <td>
                      <div className="document-name-cell">
                        <div className="document-icon">📄</div>

                        <div>
                          <strong>{document.name}</strong>

                          <span>Document #{document.id}</span>
                        </div>
                      </div>
                    </td>

                    <td>
                      <span className="document-type">
                        {document.file_type?.toUpperCase() || "-"}
                      </span>
                    </td>

                    <td>User #{document.uploaded_by}</td>

                    <td>{formatDate(document.created_at)}</td>

                    <td>{formatDate(document.updated_at)}</td>

                    <td>
                      <div className="document-actions">
                        <button
                          className="document-view-btn"
                          type="button"
                          onClick={() => handleView(document)}
                        >
                          View
                        </button>

                        <button
                          className="document-access-btn"
                          type="button"
                          onClick={() => handleManageAccess(document)}
                        >
                          Access
                        </button>

                        <button
                          className="document-delete-btn"
                          type="button"
                          disabled={deletingId === document.id}
                          onClick={() => handleDelete(document)}
                        >
                          {deletingId === document.id
                            ? "Deleting..."
                            : "Delete"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {showViewModal && selectedDocument && (
          <div
            className="document-view-overlay"
            onClick={() => {
              setShowViewModal(false);
              setSelectedDocument(null);
            }}
          >
            <div
              className="document-view-modal"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="document-view-header">
                <div>
                  <h2>Document Details</h2>
                  <p>Information and extracted content</p>
                </div>

                <button
                  type="button"
                  className="document-view-close"
                  onClick={() => {
                    setShowViewModal(false);
                    setSelectedDocument(null);
                  }}
                ></button>
              </div>

              <div className="document-view-content">
                <div className="document-info-grid">
                  <div className="document-info-item">
                    <span>File Name</span>
                    <strong>{selectedDocument.name || "-"}</strong>
                  </div>

                  <div className="document-info-item">
                    <span>File Type</span>
                    <strong>
                      {selectedDocument.file_type
                        ? selectedDocument.file_type.toUpperCase()
                        : "-"}
                    </strong>
                  </div>

                  <div className="document-info-item">
                    <span>Uploaded By</span>
                    <strong>{selectedDocument.uploaded_by || "-"}</strong>
                  </div>

                  <div className="document-info-item">
                    <span>Created</span>
                    <strong>
                      {selectedDocument.created_at
                        ? new Date(selectedDocument.created_at).toLocaleString(
                            "en-IN",
                          )
                        : "-"}
                    </strong>
                  </div>

                  <div className="document-info-item">
                    <span>Updated</span>
                    <strong>
                      {selectedDocument.updated_at
                        ? new Date(selectedDocument.updated_at).toLocaleString(
                            "en-IN",
                          )
                        : "-"}
                    </strong>
                  </div>
                </div>

                <div className="document-text-section">
                  <div className="document-text-title">Extracted Text</div>

                  <div className="document-text-content">
                    {selectedDocument.extracted_text
                      ? selectedDocument.extracted_text
                      : "No extracted text available for this document."}
                  </div>
                </div>
              </div>

              <div className="document-view-footer">
                <button
                  type="button"
                  className="document-view-done-btn"
                  onClick={() => {
                    setShowViewModal(false);
                    setSelectedDocument(null);
                  }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
        {showUploadModal && (
          <div
            className="upload-modal-overlay"
            onClick={() => {
              if (!uploading) {
                setShowUploadModal(false);
                setSelectedFile(null);
              }
            }}
          >
            <div className="upload-modal" onClick={(e) => e.stopPropagation()}>
              <div className="upload-modal-header">
                <div>
                  <h2>Upload Document</h2>
                  <p>Add a document to the enterprise AI knowledge base.</p>
                </div>

                <button
                  type="button"
                  className="upload-modal-close"
                  disabled={uploading}
                  onClick={() => {
                    setShowUploadModal(false);
                    setSelectedFile(null);
                  }}
                >
                  ×
                </button>
              </div>

              <div className="upload-file-area">
                <div className="upload-file-icon">📄</div>

                <h3>Select a document</h3>

                <p>Supported formats: PDF, DOCX, TXT, MD</p>

                <label className="upload-file-button">
                  Choose File
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt,.md"
                    onChange={(e) => {
                      setSelectedFile(e.target.files?.[0] || null);
                    }}
                    disabled={uploading}
                  />
                </label>

                {selectedFile && (
                  <div className="selected-file">
                    <span>📄</span>

                    <div>
                      <strong>{selectedFile.name}</strong>

                      <small>{(selectedFile.size / 1024).toFixed(1)} KB</small>
                    </div>
                  </div>
                )}
              </div>

              <div className="upload-modal-actions">
                <button
                  type="button"
                  className="upload-cancel-btn"
                  disabled={uploading}
                  onClick={() => {
                    setShowUploadModal(false);
                    setSelectedFile(null);
                  }}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="upload-submit-btn"
                  disabled={!selectedFile || uploading}
                  onClick={handleUpload}
                >
                  {uploading ? "Uploading..." : "Upload Document"}
                </button>
              </div>
            </div>
          </div>
        )}

        {showAccessModal && (
          <div
            className="access-modal-overlay"
            onClick={() => {
              if (!accessLoading) {
                setShowAccessModal(false);
                setAccessDocument(null);
                setAccessData(null);
              }
            }}
          >
            <div className="access-modal" onClick={(e) => e.stopPropagation()}>
              <div className="access-modal-header">
                <div>
                  <h2>Manage Document Access</h2>
                  <p>Control who can access this enterprise document.</p>
                </div>

                <button
                  type="button"
                  className="access-modal-close"
                  disabled={accessLoading}
                  onClick={() => {
                    setShowAccessModal(false);
                    setAccessDocument(null);
                    setAccessData(null);
                  }}
                ></button>
              </div>

              <div className="access-modal-document">
                <span className="access-document-icon">📄</span>

                <div>
                  <strong>{accessDocument?.name || "Document"}</strong>

                  <span>
                    Document ID:{" "}
                    {accessData?.document_id || accessDocument?.id || "-"}
                  </span>
                </div>
              </div>

              <div className="access-modal-body">
                {accessLoading ? (
                  <div className="access-loading">
                    Loading access information...
                  </div>
                ) : accessData ? (
                  <>
                    <div className="access-section">
                      <div className="access-section-header">
                        <div>
                          <h3>Users with Access</h3>
                          <p>Users who can currently access this document.</p>
                        </div>

                        <span className="access-count">
                          {accessData.users?.length || 0}
                        </span>
                      </div>

                      {accessData.users?.length > 0 ? (
                        <div className="access-user-list">
                          {accessData.users.map((user) => (
                            <div
                              className="access-user-item"
                              key={`${user.user_id}-${user.role_id || "direct"}`}
                            >
                              <div className="access-user-avatar">
                                {(user.full_name || user.username || "?")
                                  .charAt(0)
                                  .toUpperCase()}
                              </div>

                              <div className="access-user-info">
                                <strong>
                                  {user.full_name || user.username}
                                </strong>

                                <span>@{user.username}</span>
                              </div>

                              <div className="access-user-source">
                                <span className="access-type-badge">
                                  {user.access_type === "role"
                                    ? "Role Access"
                                    : "Direct Access"}
                                </span>

                                <small>{user.access_reason || "-"}</small>

                                <button
                                  type="button"
                                  className="access-revoke-btn"
                                  onClick={() => handleRevokeAccess(user)}
                                >
                                  Revoke
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="access-empty">
                          No users currently have access to this document.
                        </div>
                      )}
                    </div>
                    <div className="access-grant-wrapper">
                      <button
                        type="button"
                        className="access-grant-btn"
                        onClick={() => {
                          console.log("GRANT ACCESS BUTTON CLICKED");

                          setGrantUsername("");
                          setGrantRoleId("");
                          setGrantType("user");
                          setShowGrantModal(true);
                        }}
                      >
                        + Grant Access
                      </button>
                    </div>
                    <div className="access-info-box">
                      <span>ⓘ</span>
                      <p>
                        Access is currently provided through assigned roles or
                        direct user access.
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="access-empty">
                    No access information available.
                  </div>
                )}
              </div>

              <div className="access-modal-footer">
                <button
                  type="button"
                  className="access-close-btn"
                  onClick={() => {
                    setShowAccessModal(false);
                    setAccessDocument(null);
                    setAccessData(null);
                  }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
        {showGrantModal && (
          <div
            className="grant-modal-overlay"
            onClick={() => {
              if (!grantLoading) {
                setShowGrantModal(false);
              }
            }}
          >
            <div className="grant-modal" onClick={(e) => e.stopPropagation()}>
              <div className="grant-modal-header">
                <div>
                  <h2>Grant Document Access</h2>
                  <p>Give a user access to this document.</p>
                </div>

                <button
                  type="button"
                  className="grant-modal-close"
                  disabled={grantLoading}
                  onClick={() => setShowGrantModal(false)}
                >
                  ×
                </button>
              </div>

              <div className="grant-modal-body">
                <div className="grant-document-info">
                  <span>📄</span>

                  <strong>{accessDocument?.name || "Document"}</strong>
                </div>

                <label className="grant-label">Access Type</label>

                <div className="grant-type-options">
                  <button
                    type="button"
                    className={
                      grantType === "user"
                        ? "grant-type-option active"
                        : "grant-type-option"
                    }
                    onClick={() => setGrantType("user")}
                  >
                    Direct User
                  </button>

                  <button
                    type="button"
                    className={
                      grantType === "role"
                        ? "grant-type-option active"
                        : "grant-type-option"
                    }
                    onClick={() => setGrantType("role")}
                  >
                    Role
                  </button>
                </div>

                <label className="grant-label">Username</label>

                <input
                  type="text"
                  className="grant-input"
                  placeholder="Enter username"
                  value={grantUsername}
                  onChange={(e) => setGrantUsername(e.target.value)}
                  disabled={grantLoading}
                />

                {grantType === "role" && (
                  <>
                    <label className="grant-label">Role ID</label>

                    <input
                      type="number"
                      className="grant-input"
                      placeholder="Enter role ID"
                      value={grantRoleId}
                      onChange={(e) => setGrantRoleId(e.target.value)}
                      disabled={grantLoading}
                    />
                  </>
                )}
              </div>

              <div className="grant-modal-footer">
                <button
                  type="button"
                  className="grant-cancel-btn"
                  disabled={grantLoading}
                  onClick={() => setShowGrantModal(false)}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="grant-submit-btn"
                  disabled={
                    grantLoading ||
                    !grantUsername.trim() ||
                    (grantType === "role" && !grantRoleId)
                  }
                  onClick={handleGrantAccess}
                >
                  {grantLoading ? "Granting..." : "Grant Access"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default Documents;
