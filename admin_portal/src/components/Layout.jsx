import { useState } from "react";
import Sidebar from "./Sidebar.jsx";
import Topbar from "./Topbar.jsx";

const Layout = ({ children }) => {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="min-h-screen bg-primary-50">
      <Topbar onToggleSidebar={() => setMobileNavOpen((prev) => !prev)} />
      <div className="flex">
        <Sidebar onNavigate={() => setMobileNavOpen(false)} />
        {mobileNavOpen && (
          <div className="lg:hidden fixed inset-0 z-40 bg-black/40" onClick={() => setMobileNavOpen(false)}>
            <div
              className="absolute left-0 top-0 bottom-0 w-64 bg-white shadow-lg"
              onClick={(event) => event.stopPropagation()}
            >
              <Sidebar mobile onNavigate={() => setMobileNavOpen(false)} />
            </div>
          </div>
        )}
        <main className="flex-1 px-4 lg:px-8 py-6">
          <div className="max-w-6xl mx-auto">{children}</div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
