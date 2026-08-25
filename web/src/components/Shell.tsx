import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  BarChart3,
  Menu,
  MessageSquare,
  Rocket,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { AmbientOrbs } from "@/components/AmbientOrbs";
import { BeamsBackground } from "@/components/BeamsBackground";
import { HeaderShimmer } from "@/components/HeaderShimmer";
import { HelixForgeBrand } from "@/components/brand/HelixForgeBrand";
import { HelixForgeWordmark } from "@/components/brand/HelixForgeWordmark";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LenisRouteSync } from "@/providers/SmoothScrollProvider";

const NAV = [
  { to: "/", label: "Ask", icon: MessageSquare },
  { to: "/runs", label: "Runs", icon: Rocket },
  { to: "/compare", label: "Compare", icon: BarChart3 },
] as const;

const FOOTER_NAV = [
  { to: "/about", label: "About" },
  { to: "/terms", label: "Terms" },
  { to: "/privacy", label: "Privacy" },
] as const;

const PAGE_TITLE: Record<string, string> = {
  "/runs": "Runs",
  "/compare": "Compare",
  "/about": "About",
  "/terms": "Terms",
  "/privacy": "Privacy",
};

function NavItems({
  onNavigate,
  className,
}: {
  onNavigate?: () => void;
  className?: string;
}) {
  return (
    <nav className={cn("flex flex-col gap-1", className)}>
      {NAV.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          onClick={onNavigate}
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
  );
}

function FooterLinks({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex flex-wrap gap-x-3 gap-y-1">
      {FOOTER_NAV.map(({ to, label }) => (
        <NavLink
          key={to}
          to={to}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "text-xs transition-colors duration-200",
              isActive
                ? "font-medium text-hf-teal"
                : "text-hf-muted hover:text-hf-text",
            )
          }
        >
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

export function Shell() {
  const { pathname } = useLocation();
  const pageTitle = PAGE_TITLE[pathname];
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    setDrawerOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!drawerOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [drawerOpen]);

  return (
    <div className="relative min-h-screen">
      <LenisRouteSync />
      <BeamsBackground />
      <AmbientOrbs className="hidden md:block" />
      <div className="relative z-10">
        {/* Desktop sidebar */}
        <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col border-r border-hf-border bg-hf-panel/95 backdrop-blur-md md:flex">
          <div className="border-b border-hf-border px-5 py-6">
            <HelixForgeBrand />
          </div>
          <NavItems className="flex-1 p-3" />
          <div className="border-t border-hf-border p-4">
            <FooterLinks />
          </div>
        </aside>

        {/* Mobile drawer */}
        {drawerOpen && (
          <button
            type="button"
            aria-label="Close menu"
            className="fixed inset-0 z-50 bg-black/50 md:hidden"
            onClick={() => setDrawerOpen(false)}
          />
        )}
        <aside
          className={cn(
            "fixed inset-y-0 left-0 z-50 flex w-[min(18rem,88vw)] flex-col border-r border-hf-border bg-hf-panel shadow-xl transition-transform duration-200 md:hidden",
            drawerOpen ? "translate-x-0" : "-translate-x-full",
          )}
          aria-hidden={!drawerOpen}
        >
          <div className="flex items-start justify-between gap-2 border-b border-hf-border px-4 py-4">
            <HelixForgeBrand />
            <button
              type="button"
              aria-label="Close menu"
              onClick={() => setDrawerOpen(false)}
              className="rounded-lg p-2 text-hf-muted hover:bg-hf-elevated hover:text-hf-text"
            >
              <X className="size-5" />
            </button>
          </div>
          <NavItems className="flex-1 p-3" onNavigate={() => setDrawerOpen(false)} />
          <div className="border-t border-hf-border p-4">
            <FooterLinks onNavigate={() => setDrawerOpen(false)} />
          </div>
        </aside>

        <div className="flex min-h-screen flex-col md:ml-64">
          <header className="relative sticky top-0 z-30 shrink-0 border-b border-hf-border bg-hf-panel/80 backdrop-blur-md">
            <HeaderShimmer />
            <div className="flex h-14 items-center justify-between gap-3 px-3 sm:px-6">
              <div className="flex min-w-0 items-center gap-2">
                <button
                  type="button"
                  aria-label="Open menu"
                  aria-expanded={drawerOpen}
                  onClick={() => setDrawerOpen(true)}
                  className="rounded-lg p-2 text-hf-muted hover:bg-hf-elevated hover:text-hf-text md:hidden"
                >
                  <Menu className="size-5" />
                </button>
                <div className="min-w-0 md:hidden">
                  {pageTitle ? (
                    <p className="truncate text-sm font-medium text-hf-text">
                      {pageTitle}
                    </p>
                  ) : (
                    <HelixForgeWordmark className="h-7 w-auto max-w-[140px]" />
                  )}
                </div>
                {pageTitle ? (
                  <p className="hidden text-sm font-medium text-hf-text md:block">
                    {pageTitle}
                  </p>
                ) : (
                  <span className="hidden md:block" />
                )}
              </div>
              <ThemeToggle />
            </div>
          </header>

          <main className="flex-1 p-3 pb-24 sm:p-6 sm:pb-10 md:pb-10">
            <Outlet />
          </main>
        </div>

        {/* Mobile bottom tabs */}
        <nav
          className="fixed inset-x-0 bottom-0 z-40 border-t border-hf-border bg-hf-panel/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-md md:hidden"
          aria-label="Primary"
        >
          <div className="grid grid-cols-3">
            {NAV.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  cn(
                    "flex flex-col items-center gap-0.5 px-2 py-2.5 text-[11px] font-medium transition-colors",
                    isActive ? "text-hf-teal" : "text-hf-muted",
                  )
                }
              >
                <Icon className="size-5" strokeWidth={1.75} />
                {label}
              </NavLink>
            ))}
          </div>
        </nav>
      </div>
    </div>
  );
}
