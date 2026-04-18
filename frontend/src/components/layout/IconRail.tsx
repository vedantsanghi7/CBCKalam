import { MessageCircle, Search, Compass, BookOpen, History, Settings } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";

const items = [
  { to: "/",         icon: MessageCircle, label: "Chat" },
  { to: "/schemes",  icon: Compass,       label: "Browse schemes" },
  { to: "/results",  icon: Search,        label: "Search" },
  { to: "/about",    icon: BookOpen,      label: "Learn" },
  { to: "/ambiguity",icon: History,       label: "History" },
];

export function IconRail() {
  return (
    <nav aria-label="Primary" className="fixed left-4 top-4 bottom-4 flex flex-col items-center gap-3 z-20">
      <div className="glass glass-highlight flex flex-col items-center gap-2 px-2 py-4 rounded-pill">
        {items.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to} to={to}
            aria-label={label}
            className={({ isActive }) => cn(
              "w-11 h-11 rounded-full grid place-items-center transition-all",
              "hover:bg-black/5",
              isActive ? "bg-ink text-white" : "text-text-2"
            )}
          >
            <Icon size={20} strokeWidth={1.75} />
          </NavLink>
        ))}
      </div>
      <NavLink
        to="/settings"
        aria-label="Settings"
        className="glass glass-highlight w-11 h-11 mt-auto rounded-full grid place-items-center text-text-2 hover:text-text-1"
      >
        <Settings size={20} strokeWidth={1.75} />
      </NavLink>
    </nav>
  );
}
