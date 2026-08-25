import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { SITE } from "@/content/site";

type StaticPageLayoutProps = {
  title: string;
  subtitle?: string;
  showLastUpdated?: boolean;
  children: ReactNode;
};

export function StaticPageLayout({
  title,
  subtitle,
  showLastUpdated = false,
  children,
}: StaticPageLayoutProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {subtitle ? (
          <p className="mt-1 text-sm text-hf-muted">{subtitle}</p>
        ) : null}
        {showLastUpdated ? (
          <p className="mt-2 text-xs text-hf-muted">
            Last updated: {SITE.lastUpdated}
          </p>
        ) : null}
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

type StaticSectionProps = {
  title: string;
  children: ReactNode;
};

export function StaticSection({ title, children }: StaticSectionProps) {
  return (
    <section className="hf-panel space-y-3">
      <h2 className="text-base font-semibold text-hf-text">{title}</h2>
      <div className="space-y-3 text-sm leading-relaxed text-hf-muted">
        {children}
      </div>
    </section>
  );
}

export function StaticInlineLink({
  to,
  children,
}: {
  to: string;
  children: ReactNode;
}) {
  return (
    <Link
      to={to}
      className="text-hf-teal underline-offset-2 hover:underline"
    >
      {children}
    </Link>
  );
}
