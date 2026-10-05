import Sidebar from './Sidebar'

function Layout({ children }) {
  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-content">
        <header className="topbar">
          <div>
            <h2>Enterprise AI</h2>
            <span>Application Intelligence</span>
          </div>

          <div className="topbar-user">
            <div className="notification">🔔</div>

            <div className="topbar-avatar">
              A
            </div>

            <div className="topbar-user-info">
              <strong>Admin User</strong>
              <span>Administrator</span>
            </div>
          </div>
        </header>

        {children}
      </div>
    </div>
  )
}

export default Layout