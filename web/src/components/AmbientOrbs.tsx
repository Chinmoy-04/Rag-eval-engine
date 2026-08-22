import { cn } from "@/lib/utils";

interface AmbientOrbsProps {
  className?: string;
}

/** Slow drifting teal glow orbs — complements BeamsBackground. */
export function AmbientOrbs({ className }: AmbientOrbsProps) {
  return (
    <div
      aria-hidden
      className={cn(
        "pointer-events-none fixed inset-0 z-0 overflow-hidden",
        className,
      )}
    >
      <div
        className={cn(
          "hf-orb hf-orb-a absolute -left-[10%] top-[8%] h-[min(520px,70vw)] w-[min(520px,70vw)] rounded-full",
          "bg-hf-teal/14 blur-[110px] dark:bg-hf-teal/20",
        )}
      />
      <div
        className={cn(
          "hf-orb hf-orb-b absolute right-[-8%] top-[42%] h-[min(420px,55vw)] w-[min(420px,55vw)] rounded-full",
          "bg-hf-teal-bright/10 blur-[100px] dark:bg-hf-teal-bright/16",
        )}
      />
      <div
        className={cn(
          "hf-orb hf-orb-c absolute bottom-[-12%] left-[30%] h-[min(380px,50vw)] w-[min(380px,50vw)] rounded-full",
          "bg-hf-teal/10 blur-[95px] dark:bg-hf-teal/14",
        )}
      />
    </div>
  );
}
