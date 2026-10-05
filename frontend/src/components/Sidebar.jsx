import { NavLink } from 'react-router-dom'

function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">AI</div>

        <div>
          <h2>Enterprise AI</h2>
          <span>Application Intelligence</span>
        </div>
      </div>

      <nav className="sidebar-nav">

        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/chat">AI Chat</NavLink>
        <NavLink to="/documents">Documents</NavLink>
        <NavLink to="/code">Code Intelligence</NavLink>
        <NavLink to="/users">Users</NavLink>
        <NavLink to="/roles">Roles & Permissions</NavLink>
        <NavLink to="/audit-logs">Audit Logs</NavLink>
        <NavLink to="/settings">Settings</NavLink>

      </nav>

      <div className="sidebar-user">
        <div className="user-avatar">A</div>

        <div>
          <strong>Admin User</strong>
          <span>Administrator</span>
        </div>
      </div>

    </aside>
  )
}

export default Sidebar
