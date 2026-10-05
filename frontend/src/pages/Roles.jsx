import { useEffect, useMemo, useState } from "react";
import Layout from "../components/Layout";

const API_BASE = "http://127.0.0.1:8000";

function Roles() {
  const [activeTab, setActiveTab] = useState("roles");

  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);

  const [roleSearch, setRoleSearch] = useState("");
  const [permissionSearch, setPermissionSearch] = useState("");

  const [loadingRoles, setLoadingRoles] = useState(true);
  const [loadingPermissions, setLoadingPermissions] = useState(true);

  const [error, setError] = useState("");

  const [selectedRole, setSelectedRole] = useState(null);
  const [rolePermissions, setRolePermissions] = useState([]);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [roleDetailsLoading, setRoleDetailsLoading] = useState(false);

  const [showCreateRoleModal, setShowCreateRoleModal] = useState(false);
  const [newRoleName, setNewRoleName] = useState("");
  const [newRoleDescription, setNewRoleDescription] = useState("");
  const [createRoleLoading, setCreateRoleLoading] = useState(false);

  const [showCreatePermissionModal, setShowCreatePermissionModal] =
    useState(false);
  const [newPermissionName, setNewPermissionName] = useState("");
  const [newPermissionDescription, setNewPermissionDescription] = useState("");
  const [createPermissionLoading, setCreatePermissionLoading] = useState(false);

  const [showAddPermissionModal, setShowAddPermissionModal] = useState(false);
  const [selectedPermissionId, setSelectedPermissionId] = useState("");
  const [addPermissionLoading, setAddPermissionLoading] = useState(false);

  const [actionLoading, setActionLoading] = useState(false);

  const [showEditPermissionModal, setShowEditPermissionModal] = useState(false);
  const [editingPermission, setEditingPermission] = useState(null);
  const [editPermissionName, setEditPermissionName] = useState("");
  const [editPermissionDescription, setEditPermissionDescription] =
    useState("");
  const [editPermissionLoading, setEditPermissionLoading] = useState(false);

  const getToken = () => {
    return localStorage.getItem("access_token");
  };

  const handleResponseError = async (response, defaultMessage) => {
    let data = {};

    try {
      data = await response.json();
    } catch {
      // No JSON response
    }

    if (response.status === 401) {
      throw new Error("Your session has expired. Please log in again.");
    }

    if (response.status === 403) {
      throw new Error("You do not have permission to perform this action.");
    }

    throw new Error(data.detail || defaultMessage);
  };

  const loadRoles = async () => {
    try {
      setLoadingRoles(true);

      const token = getToken();

      const response = await fetch(`${API_BASE}/api/roles/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        await handleResponseError(response, "Failed to load roles");
      }

      const data = await response.json();
      setRoles(data);
    } catch (err) {
      console.error("Load roles error:", err);
      setError(err.message || "Failed to load roles");
    } finally {
      setLoadingRoles(false);
    }
  };

  const loadPermissions = async () => {
    try {
      setLoadingPermissions(true);

      const token = getToken();

      const response = await fetch(`${API_BASE}/api/permissions/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        await handleResponseError(response, "Failed to load permissions");
      }

      const data = await response.json();
      setPermissions(data);
    } catch (err) {
      console.error("Load permissions error:", err);
      setError(err.message || "Failed to load permissions");
    } finally {
      setLoadingPermissions(false);
    }
  };

  useEffect(() => {
    loadRoles();
    loadPermissions();
  }, []);

  const filteredRoles = useMemo(() => {
    const search = roleSearch.trim().toLowerCase();

    if (!search) {
      return roles;
    }

    return roles.filter((role) =>
      [role.name, role.description, String(role.id)]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(search)),
    );
  }, [roles, roleSearch]);

  const filteredPermissions = useMemo(() => {
    const search = permissionSearch.trim().toLowerCase();

    if (!search) {
      return permissions;
    }

    return permissions.filter((permission) =>
      [permission.name, permission.description, String(permission.id)]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(search)),
    );
  }, [permissions, permissionSearch]);

  const getRoleType = (role) => {
    if (role.is_system === true) {
      return "System";
    }

    return "Custom";
  };

  const getRoleStatus = (role) => {
    if (role.is_active === false) {
      return "Inactive";
    }

    return "Active";
  };

  const getPermissionStatus = (permission) => {
    if (permission.is_active === false) {
      return "Inactive";
    }

    return "Active";
  };

  const handleViewRole = async (role) => {
    try {
      setSelectedRole(role);
      setRolePermissions([]);
      setShowRoleModal(true);
      setRoleDetailsLoading(true);
      setError("");

      const token = getToken();

      const response = await fetch(
        `${API_BASE}/api/roles/${role.id}/permissions`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        await handleResponseError(response, "Failed to load role permissions");
      }

      const data = await response.json();

      setRolePermissions(data);
    } catch (err) {
      console.error("Load role permissions error:", err);
      setError(err.message || "Failed to load role permissions");
    } finally {
      setRoleDetailsLoading(false);
    }
  };

  const handleCreateRole = async () => {
    if (!newRoleName.trim()) {
      return;
    }

    try {
      setCreateRoleLoading(true);
      setError("");

      const token = getToken();

      const response = await fetch(`${API_BASE}/api/roles/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: newRoleName.trim(),
          description: newRoleDescription.trim() || null,
        }),
      });

      if (!response.ok) {
        await handleResponseError(response, "Failed to create role");
      }

      const data = await response.json();

      setRoles((currentRoles) => [data, ...currentRoles]);

      setNewRoleName("");
      setNewRoleDescription("");
      setShowCreateRoleModal(false);
    } catch (err) {
      console.error("Create role error:", err);
      setError(err.message || "Failed to create role");
    } finally {
      setCreateRoleLoading(false);
    }
  };

  const handleRoleStatusChange = async (role) => {
    const isCurrentlyActive = role.is_active !== false;

    const action = isCurrentlyActive ? "deactivate" : "reactivate";

    const actionText = isCurrentlyActive ? "deactivate" : "activate";

    const confirmed = window.confirm(
      `${actionText.charAt(0).toUpperCase() + actionText.slice(1)} the "${role.name}" role?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setActionLoading(true);
      setError("");

      const token = getToken();

      const response = await fetch(
        `${API_BASE}/api/roles/${role.id}/${action}`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        await handleResponseError(response, `Failed to ${actionText} role`);
      }

      const data = await response.json();

      setRoles((currentRoles) =>
        currentRoles.map((item) => (item.id === role.id ? data : item)),
      );

      if (selectedRole && selectedRole.id === role.id) {
        setSelectedRole(data);
      }
    } catch (err) {
      console.error("Role status change error:", err);

      setError(err.message || `Failed to ${actionText} role`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteRole = async (role) => {
    const confirmed = window.confirm(
      `Delete the "${role.name}" role? This action cannot be undone.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setActionLoading(true);
      setError("");

      const token = getToken();

      const response = await fetch(`${API_BASE}/api/roles/${role.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        await handleResponseError(response, "Failed to delete role");
      }

      setRoles((currentRoles) =>
        currentRoles.filter((item) => item.id !== role.id),
      );

      if (selectedRole?.id === role.id) {
        setSelectedRole(null);
        setShowRoleModal(false);
      }
    } catch (err) {
      console.error("Delete role error:", err);
      setError(err.message || "Failed to delete role");
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreatePermission = async () => {
    const permissionName = newPermissionName.trim();

    if (!permissionName) {
      return;
    }

    const parts = permissionName.split(".");

    if (parts.length < 2 || parts.some((part) => !part.trim())) {
      setError(
        "Permission name must use the format: resource.action (example: document.delete)",
      );
      return;
    }

    const resource = parts.slice(0, -1).join(".").trim();
    const action = parts[parts.length - 1].trim();

    try {
      setCreatePermissionLoading(true);
      setError("");

      const token = getToken();

      const response = await fetch(`${API_BASE}/api/permissions/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: permissionName,
          description: newPermissionDescription.trim() || null,
          resource,
          action,
        }),
      });

      if (!response.ok) {
        await handleResponseError(response, "Failed to create permission");
      }

      const data = await response.json();

      setPermissions((currentPermissions) => [data, ...currentPermissions]);

      setNewPermissionName("");
      setNewPermissionDescription("");
      setShowCreatePermissionModal(false);
    } catch (err) {
      console.error("Create permission error:", err);
      setError(err.message || "Failed to create permission");
    } finally {
      setCreatePermissionLoading(false);
    }
  };

  const handleEditPermission = async () => {
    if (!editingPermission || !editPermissionName.trim()) {
      return;
    }

    const permissionName = editPermissionName.trim();
    const parts = permissionName.split(".");

    if (parts.length < 2 || parts.some((part) => !part.trim())) {
      setError("Permission name must use the format: resource.action");
      return;
    }

    const resource = parts.slice(0, -1).join(".").trim();
    const action = parts[parts.length - 1].trim();

    try {
      setEditPermissionLoading(true);
      setError("");

      const token = getToken();

      const response = await fetch(
        `${API_BASE}/api/permissions/${editingPermission.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            name: permissionName,
            description: editPermissionDescription.trim() || null,
            resource,
            action,
          }),
        },
      );

      if (!response.ok) {
        await handleResponseError(response, "Failed to update permission");
      }

      const data = await response.json();

      setPermissions((currentPermissions) =>
        currentPermissions.map((permission) =>
          permission.id === data.id ? data : permission,
        ),
      );

      setShowEditPermissionModal(false);
      setEditingPermission(null);
    } catch (err) {
      console.error("Edit permission error:", err);
      setError(err.message || "Failed to update permission");
    } finally {
      setEditPermissionLoading(false);
    }
  };

  const handleDeletePermission = async (permission) => {
    const confirmed = window.confirm(
      `Delete the "${permission.name}" permission?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setActionLoading(true);
      setError("");

      const token = getToken();

      const response = await fetch(
        `${API_BASE}/api/permissions/${permission.id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        await handleResponseError(response, "Failed to delete permission");
      }

      setPermissions((currentPermissions) =>
        currentPermissions.filter((item) => item.id !== permission.id),
      );

      setRolePermissions((currentPermissions) =>
        currentPermissions.filter((item) => item.id !== permission.id),
      );
    } catch (err) {
      console.error("Delete permission error:", err);

      setError(err.message || "Failed to delete permission");
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddPermission = async () => {
    if (!selectedRole || !selectedPermissionId) {
      return;
    }

    try {
      setAddPermissionLoading(true);
      setError("");

      const token = getToken();

      const response = await fetch(`${API_BASE}/api/role-permissions/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          role_id: selectedRole.id,
          permission_id: Number(selectedPermissionId),
        }),
      });

      if (!response.ok) {
        await handleResponseError(response, "Failed to assign permission");
      }

      setShowAddPermissionModal(false);
      setSelectedPermissionId("");

      await handleViewRole(selectedRole);
    } catch (err) {
      console.error("Add permission error:", err);

      setError(err.message || "Failed to assign permission");
    } finally {
      setAddPermissionLoading(false);
    }
  };

  const handleRemovePermission = async (permission) => {
    if (!selectedRole) {
      return;
    }

    const permissionId = permission.id || permission.permission_id;

    const confirmed = window.confirm(
      `Remove "${permission.name}" from the "${selectedRole.name}" role?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setActionLoading(true);
      setError("");

      const token = getToken();

      const response = await fetch(
        `${API_BASE}/api/role-permissions/${selectedRole.id}/${permissionId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        await handleResponseError(response, "Failed to remove permission");
      }

      setRolePermissions((currentPermissions) =>
        currentPermissions.filter(
          (item) => (item.id || item.permission_id) !== permissionId,
        ),
      );
    } catch (err) {
      console.error("Remove permission error:", err);

      setError(err.message || "Failed to remove permission");
    } finally {
      setActionLoading(false);
    }
  };

  const availablePermissions = permissions.filter((permission) => {
    const permissionId = permission.id;

    return !rolePermissions.some(
      (rolePermission) =>
        (rolePermission.id || rolePermission.permission_id) === permissionId,
    );
  });

  return (
    <Layout>
      <div className="roles-page">
        <div className="roles-page-header">
          <div>
            <h1>Roles & Permissions</h1>
            <p>Manage roles and the permissions assigned to them.</p>
          </div>
        </div>

        {error && (
          <div className="roles-error">
            <span>{error}</span>

            <button type="button" onClick={() => setError("")}>
              ×
            </button>
          </div>
        )}

        <div className="roles-tabs">
          <button
            type="button"
            className={activeTab === "roles" ? "roles-tab active" : "roles-tab"}
            onClick={() => setActiveTab("roles")}
          >
            Roles
            <span>{roles.length}</span>
          </button>

          <button
            type="button"
            className={
              activeTab === "permissions" ? "roles-tab active" : "roles-tab"
            }
            onClick={() => setActiveTab("permissions")}
          >
            Permissions
            <span>{permissions.length}</span>
          </button>
        </div>

        {activeTab === "roles" && (
          <div className="roles-content">
            <div className="roles-toolbar">
              <input
                type="text"
                className="roles-search"
                placeholder="Search roles..."
                value={roleSearch}
                onChange={(e) => setRoleSearch(e.target.value)}
              />

              <button
                type="button"
                className="roles-primary-btn"
                onClick={() => {
                  setNewRoleName("");
                  setNewRoleDescription("");
                  setShowCreateRoleModal(true);
                }}
              >
                + Create Role
              </button>
            </div>

            <div className="roles-card">
              {loadingRoles ? (
                <div className="roles-loading">Loading roles...</div>
              ) : filteredRoles.length === 0 ? (
                <div className="roles-empty">No roles found.</div>
              ) : (
                <div className="roles-table-wrapper">
                  <table className="roles-table">
                    <thead>
                      <tr>
                        <th>Role</th>
                        <th>Description</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>ID</th>
                        <th>Actions</th>
                      </tr>
                    </thead>

                    <tbody>
                      {filteredRoles.map((role) => (
                        <tr key={role.id}>
                          <td>
                            <div className="role-name-cell">
                              <div className="role-icon">R</div>

                              <strong>{role.name}</strong>
                            </div>
                          </td>

                          <td>{role.description || "-"}</td>

                          <td>
                            <span
                              className={
                                role.is_system
                                  ? "role-type-badge system"
                                  : "role-type-badge custom"
                              }
                            >
                              {getRoleType(role)}
                            </span>
                          </td>

                          <td>
                            <span
                              className={
                                role.is_active === false
                                  ? "role-status inactive"
                                  : "role-status active"
                              }
                            >
                              {getRoleStatus(role)}
                            </span>
                          </td>

                          <td>#{role.id}</td>

                          <td>
                            <div className="role-actions">
                              <button
                                type="button"
                                className="role-view-btn"
                                onClick={() => handleViewRole(role)}
                              >
                                View
                              </button>

                              <button
                                type="button"
                                className={
                                  role.is_active === false
                                    ? "role-activate-btn"
                                    : "role-deactivate-btn"
                                }
                                disabled={
                                  actionLoading || role.is_system === true
                                }
                                title={
                                  role.is_system
                                    ? "System roles cannot be changed"
                                    : role.is_active === false
                                      ? "Activate role"
                                      : "Deactivate role"
                                }
                                onClick={() => handleRoleStatusChange(role)}
                              >
                                {role.is_active === false
                                  ? "Activate"
                                  : "Deactivate"}
                              </button>

                              <button
                                type="button"
                                className="role-delete-btn"
                                disabled={
                                  actionLoading || role.is_system === true
                                }
                                title={
                                  role.is_system
                                    ? "System roles cannot be deleted"
                                    : "Delete role"
                                }
                                onClick={() => handleDeleteRole(role)}
                              >
                                Delete
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "permissions" && (
          <div className="roles-content">
            <div className="roles-toolbar">
              <input
                type="text"
                className="roles-search"
                placeholder="Search permissions..."
                value={permissionSearch}
                onChange={(e) => setPermissionSearch(e.target.value)}
              />

              <button
                type="button"
                className="roles-primary-btn"
                onClick={() => {
                  setNewPermissionName("");
                  setNewPermissionDescription("");
                  setShowCreatePermissionModal(true);
                }}
              >
                + Create Permission
              </button>
            </div>

            <div className="roles-card">
              {loadingPermissions ? (
                <div className="roles-loading">Loading permissions...</div>
              ) : filteredPermissions.length === 0 ? (
                <div className="roles-empty">No permissions found.</div>
              ) : (
                <div className="roles-table-wrapper">
                  <table className="roles-table">
                    <thead>
                      <tr>
                        <th>Permission</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>ID</th>
                        <th>Actions</th>
                      </tr>
                    </thead>

                    <tbody>
                      {filteredPermissions.map((permission) => (
                        <tr key={permission.id}>
                          <td>
                            <div className="permission-name-cell">
                              <div className="permission-icon">P</div>

                              <strong>{permission.name}</strong>
                            </div>
                          </td>

                          <td>{permission.description || "-"}</td>

                          <td>
                            <span
                              className={
                                permission.is_active === false
                                  ? "role-status inactive"
                                  : "role-status active"
                              }
                            >
                              {getPermissionStatus(permission)}
                            </span>
                          </td>

                          <td>#{permission.id}</td>

                          <td>
                            <div className="role-actions">
                              {!permission.is_system && (
                                <>
                                  <button
                                    type="button"
                                    className="role-view-btn"
                                    disabled={actionLoading}
                                    onClick={() => {
                                      setEditingPermission(permission);
                                      setEditPermissionName(permission.name);
                                      setEditPermissionDescription(
                                        permission.description || "",
                                      );
                                      setShowEditPermissionModal(true);
                                    }}
                                  >
                                    Edit
                                  </button>

                                  <button
                                    type="button"
                                    className="role-delete-btn"
                                    disabled={actionLoading}
                                    onClick={() =>
                                      handleDeletePermission(permission)
                                    }
                                  >
                                    Delete
                                  </button>
                                </>
                              )}

                              {permission.is_system && (
                                <span className="role-form-help">
                                  System protected
                                </span>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ROLE DETAILS MODAL */}

        {showRoleModal && selectedRole && (
          <div
            className="role-modal-overlay"
            onClick={() => {
              if (!roleDetailsLoading) {
                setShowRoleModal(false);
              }
            }}
          >
            <div className="role-modal" onClick={(e) => e.stopPropagation()}>
              <div className="role-modal-header">
                <div>
                  <h2>{selectedRole.name}</h2>

                  <p>{selectedRole.description || "Role permissions"}</p>
                </div>

                <button
                  type="button"
                  className="role-modal-close"
                  onClick={() => setShowRoleModal(false)}
                >
                  ×
                </button>
              </div>

              <div className="role-modal-body">
                <div className="role-detail-summary">
                  <div>
                    <span>Role ID</span>
                    <strong>#{selectedRole.id}</strong>
                  </div>

                  <div>
                    <span>Type</span>
                    <strong>{getRoleType(selectedRole)}</strong>
                  </div>

                  <div>
                    <span>Status</span>
                    <strong>{getRoleStatus(selectedRole)}</strong>
                  </div>

                  <div>
                    <span>Permissions</span>
                    <strong>{rolePermissions.length}</strong>
                  </div>
                </div>

                <div className="role-permission-header">
                  <div>
                    <h3>Assigned Permissions</h3>

                    <span>
                      {rolePermissions.length} permission
                      {rolePermissions.length !== 1 ? "s" : ""}
                    </span>
                  </div>

                  <button
                    type="button"
                    className="role-add-permission-btn"
                    disabled={
                      selectedRole.is_system === true || roleDetailsLoading
                    }
                    title={
                      selectedRole.is_system
                        ? "System role permissions can be managed only if permitted by the backend"
                        : "Add permission"
                    }
                    onClick={() => {
                      setSelectedPermissionId("");
                      setShowAddPermissionModal(true);
                    }}
                  >
                    + Add Permission
                  </button>
                </div>

                {roleDetailsLoading ? (
                  <div className="roles-loading">Loading permissions...</div>
                ) : rolePermissions.length === 0 ? (
                  <div className="role-permission-empty">
                    No permissions assigned to this role.
                  </div>
                ) : (
                  <div className="role-permission-list">
                    {rolePermissions.map((permission, index) => (
                      <div
                        className="role-permission-item"
                        key={permission.id || permission.permission_id || index}
                      >
                        <div>
                          <strong>
                            {permission.name ||
                              permission.permission_name ||
                              `Permission #${
                                permission.id || permission.permission_id
                              }`}
                          </strong>

                          {permission.description && (
                            <span>{permission.description}</span>
                          )}
                        </div>

                        <button
                          type="button"
                          className="role-permission-remove"
                          disabled={actionLoading}
                          onClick={() => handleRemovePermission(permission)}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="role-modal-footer">
                <button
                  type="button"
                  className="role-modal-close-btn"
                  onClick={() => setShowRoleModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* CREATE ROLE MODAL */}

        {showCreateRoleModal && (
          <div
            className="role-modal-overlay"
            onClick={() => {
              if (!createRoleLoading) {
                setShowCreateRoleModal(false);
              }
            }}
          >
            <div
              className="small-role-modal"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="role-modal-header">
                <div>
                  <h2>Create Role</h2>
                  <p>Create a new enterprise role.</p>
                </div>

                <button
                  type="button"
                  className="role-modal-close"
                  onClick={() => setShowCreateRoleModal(false)}
                >
                  ×
                </button>
              </div>

              <div className="role-form-body">
                <label>Role Name</label>

                <input
                  type="text"
                  value={newRoleName}
                  placeholder="e.g. Manager"
                  onChange={(e) => setNewRoleName(e.target.value)}
                  disabled={createRoleLoading}
                />

                <label>Description</label>

                <textarea
                  value={newRoleDescription}
                  placeholder="Describe what this role is used for"
                  onChange={(e) => setNewRoleDescription(e.target.value)}
                  disabled={createRoleLoading}
                  rows="4"
                />
              </div>

              <div className="role-modal-footer">
                <button
                  type="button"
                  className="role-modal-close-btn"
                  disabled={createRoleLoading}
                  onClick={() => setShowCreateRoleModal(false)}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="roles-primary-btn"
                  disabled={createRoleLoading || !newRoleName.trim()}
                  onClick={handleCreateRole}
                >
                  {createRoleLoading ? "Creating..." : "Create Role"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* EDIT PERMISSION MODAL */}

        {showEditPermissionModal && editingPermission && (
          <div
            className="role-modal-overlay"
            onClick={() => {
              if (!editPermissionLoading) {
                setShowEditPermissionModal(false);
              }
            }}
          >
            <div
              className="small-role-modal"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="role-modal-header">
                <div>
                  <h2>Edit Permission</h2>
                  <p>Modify a custom permission.</p>
                </div>

                <button
                  type="button"
                  className="role-modal-close"
                  onClick={() => setShowEditPermissionModal(false)}
                >
                  ×
                </button>
              </div>

              <div className="role-form-body">
                <label>Permission Name</label>

                <input
                  type="text"
                  value={editPermissionName}
                  placeholder="e.g. document.delete"
                  onChange={(e) => setEditPermissionName(e.target.value)}
                  disabled={editPermissionLoading}
                />

                <label>Description</label>

                <textarea
                  value={editPermissionDescription}
                  placeholder="Describe what this permission allows"
                  onChange={(e) => setEditPermissionDescription(e.target.value)}
                  disabled={editPermissionLoading}
                  rows="4"
                />
              </div>

              <div className="role-modal-footer">
                <button
                  type="button"
                  className="role-modal-close-btn"
                  disabled={editPermissionLoading}
                  onClick={() => setShowEditPermissionModal(false)}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="roles-primary-btn"
                  disabled={editPermissionLoading || !editPermissionName.trim()}
                  onClick={handleEditPermission}
                >
                  {editPermissionLoading ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* CREATE PERMISSION MODAL */}

        {showCreatePermissionModal && (
          <div
            className="role-modal-overlay"
            onClick={() => {
              if (!createPermissionLoading) {
                setShowCreatePermissionModal(false);
              }
            }}
          >
            <div
              className="small-role-modal"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="role-modal-header">
                <div>
                  <h2>Create Permission</h2>

                  <p>Create a new custom permission.</p>
                </div>

                <button
                  type="button"
                  className="role-modal-close"
                  onClick={() => setShowCreatePermissionModal(false)}
                >
                  ×
                </button>
              </div>

              <div className="role-form-body">
                <label>Permission Name</label>

                <input
                  type="text"
                  value={newPermissionName}
                  placeholder="e.g. report.read"
                  onChange={(e) => setNewPermissionName(e.target.value)}
                  disabled={createPermissionLoading}
                />

                <label>Description</label>

                <textarea
                  value={newPermissionDescription}
                  placeholder="Describe what this permission allows"
                  onChange={(e) => setNewPermissionDescription(e.target.value)}
                  disabled={createPermissionLoading}
                  rows="4"
                />
              </div>

              <div className="role-modal-footer">
                <button
                  type="button"
                  className="role-modal-close-btn"
                  disabled={createPermissionLoading}
                  onClick={() => setShowCreatePermissionModal(false)}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="roles-primary-btn"
                  disabled={
                    createPermissionLoading || !newPermissionName.trim()
                  }
                  onClick={handleCreatePermission}
                >
                  {createPermissionLoading
                    ? "Creating..."
                    : "Create Permission"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ADD PERMISSION TO ROLE MODAL */}

        {showAddPermissionModal && selectedRole && (
          <div
            className="role-modal-overlay"
            onClick={() => {
              if (!addPermissionLoading) {
                setShowAddPermissionModal(false);
              }
            }}
          >
            <div
              className="small-role-modal"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="role-modal-header">
                <div>
                  <h2>Add Permission</h2>

                  <p>Assign a permission to {selectedRole.name}.</p>
                </div>

                <button
                  type="button"
                  className="role-modal-close"
                  onClick={() => setShowAddPermissionModal(false)}
                >
                  ×
                </button>
              </div>

              <div className="role-form-body">
                <label>Select Permission</label>

                <select
                  value={selectedPermissionId}
                  onChange={(e) => setSelectedPermissionId(e.target.value)}
                  disabled={addPermissionLoading}
                >
                  <option value="">Select a permission</option>

                  {availablePermissions.map((permission) => (
                    <option key={permission.id} value={permission.id}>
                      {permission.name}
                    </option>
                  ))}
                </select>

                {availablePermissions.length === 0 && (
                  <div className="role-form-help">
                    All available permissions are already assigned to this role.
                  </div>
                )}
              </div>

              <div className="role-modal-footer">
                <button
                  type="button"
                  className="role-modal-close-btn"
                  disabled={addPermissionLoading}
                  onClick={() => setShowAddPermissionModal(false)}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="roles-primary-btn"
                  disabled={addPermissionLoading || !selectedPermissionId}
                  onClick={handleAddPermission}
                >
                  {addPermissionLoading ? "Adding..." : "Add Permission"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default Roles;
