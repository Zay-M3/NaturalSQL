import { Outlet } from "react-router-dom";
import { Header } from "./Header";
import { Footer } from "./Footer";



const Layout = () => {
  return (
    <div className="grid h-dvh grid-rows-[auto_minmax(0,1fr)_auto] bg-linear-to-b from-emerald-50 via-slate-50 to-white text-slate-900">
      <Header />
      <div className="h-full min-h-0 overflow-hidden">
        <Outlet />
      </div>
      <Footer />
            
    </div>
  )
}

export default Layout