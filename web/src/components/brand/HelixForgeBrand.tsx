import { HelixForgeWordmark } from "@/components/brand/HelixForgeWordmark";
import { cn } from "@/lib/utils";

interface HelixForgeBrandProps {
  className?: string;
}

/** Sidebar lockup — theme-matched Stitch wordmark + RAG Eval label. */
export function HelixForgeBrand({ className }: HelixForgeBrandProps) {
  return (
    <div className={cn("space-y-2", className)}>
      <HelixForgeWordmark className="h-10 w-auto max-w-[188px]" />
      <p className="font-mono text-xs font-bold uppercase tracking-[0.22em] text-hf-teal dark:text-hf-teal-bright dark:drop-shadow-[0_0_10px_rgba(45,212,191,0.45)]">
        RAG Eval
      </p>
    </div>
  );
}
