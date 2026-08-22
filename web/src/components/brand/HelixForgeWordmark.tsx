import { cn } from "@/lib/utils";

interface HelixForgeWordmarkProps {
  className?: string;
  title?: string;
}

/** Stitch mono wordmarks — high-contrast light (dark text) / inverted dark (white text). */
const WORDMARK = {
  light: "/brand/helixforge-wordmark-mono-light-transparent.png",
  dark: "/brand/helixforge-wordmark-mono-dark-transparent.png",
} as const;

export function HelixForgeWordmark({
  className,
  title = "HelixForge",
}: HelixForgeWordmarkProps) {
  return (
    <>
      <img
        src={WORDMARK.light}
        alt={title}
        className={cn(
          "h-auto w-full object-contain object-left dark:hidden",
          className,
        )}
      />
      <img
        src={WORDMARK.dark}
        alt={title}
        className={cn(
          "hidden h-auto w-full object-contain object-left dark:block",
          className,
        )}
      />
    </>
  );
}
