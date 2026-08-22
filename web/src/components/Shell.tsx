import { NavLink, Outlet } from "react-router-dom";
import {
  BarChart3,
  MessageSquare,
  Rocket,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { AmbientOrbs } from "@/components/AmbientOrbs";
import { BeamsBackground } from "@/components/BeamsBackground";
import { HeaderShimmer } from "@/components/HeaderShimmer";
import { HelixForgeBrand } from "@/components/brand/HelixForgeBrand";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LenisRouteSync } from "@/providers/SmoothScrollProvider";

const NAV = [
  { to: "/", label: "Ask", icon: MessageSquare },
  { to: "/runs", label: "Runs", icon: Rocket },
  { to: "/compare", label: "Compare", icon: BarChart3 },
] as const;

export function Shell() {
  return (
    <div className="relative min-h-screen">
      <LenisRouteSync />
      <BeamsBackground />
      <AmbientOrbs />
      <div className="relative z-10">
      <aside className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-hf-border bg-hf-panel/95 backdrop-blur-md">
        <div className="border-b border-hf-border px-5 py-6">
          <HelixForgeBrand />
        </div>
        <nav className="flex flex-1 flex-col gap-1 p-3">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors duration-200",
                  isActive
                    ? "border-l-2 border-hf-teal bg-hf-teal-dim text-hf-teal"
                    : "border-l-2 border-transparent text-hf-muted hover:bg-hf-elevated hover:text-hf-text",
                )
              }
            >
              <Icon className="size-[18px]" strokeWidth={1.75} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-hf-border p-4">
          <p className="text-xs text-hf-muted">React UI · Phase 9</p>
        </div>
      </aside>
      <div className="ml-64 flex min-h-screen flex-col">
        <header className="relative sticky top-0 z-30 shrink-0 border-b border-hf-border bg-hf-panel/80 backdrop-blur-md">
          <HeaderShimmer />
          <div className="flex h-14 items-center justify-between px-6">
            <p className="text-sm text-hf-muted">
              Ask about company policies — see how well the system answers.
            </p>
            <ThemeToggle />
          </div>
        </header>
        <main className="flex-1 p-6 pb-10">
          <Outlet />
        </main>
      </div>
      </div>
    </div>
  );
}
