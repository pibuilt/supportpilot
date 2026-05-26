import { Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-8">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(184,84,47,0.15),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(35,88,77,0.14),_transparent_24%)]" />
      <div className="absolute left-[-8rem] top-[-6rem] h-64 w-64 rounded-full bg-orange-200/40 blur-3xl" />
      <div className="absolute bottom-[-5rem] right-[-5rem] h-72 w-72 rounded-full bg-emerald-200/35 blur-3xl" />
      <div className="relative w-full max-w-md rounded-[32px] border border-white/70 bg-white/85 p-8 shadow-panel backdrop-blur">
        <Outlet />
      </div>
    </div>
  );
}
