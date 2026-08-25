import { Link } from "react-router-dom";
import { HelixForgeWordmark } from "@/components/brand/HelixForgeWordmark";
import { cn } from "@/lib/utils";

interface HelixForgeBrandProps {
  className?: string;
}

/** Sidebar lockup — links to About; theme-matched Stitch wordmark + RAG Eval label. */
export function HelixForgeBrand({ className }: HelixForgeBrandProps) {
  return (
    <Link
      to="/about"
      className={cn(
        "block space-y-2 rounded-lg transition-opacity hover:opacity-80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-hf-teal/40",
        className,
      )}
      aria-label="About HelixForge RAG Eval"
    >
      <HelixForgeWordmark className="h-10 w-auto max-w-[188px]" />
      <p className="font-mono text-xs font-bold uppercase tracking-[0.22em] text-hf-teal dark:text-hf-teal-bright dark:drop-shadow-[0_0_10px_rgba(45,212,191,0.45)]">
        RAG Eval
      </p>
    </Link>
  );
}
