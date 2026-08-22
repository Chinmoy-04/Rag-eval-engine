import { cn } from "@/lib/utils";

interface HelixForgeIconProps {
  className?: string;
  title?: string;
}

/** Hex helix icon mark (Stitch screen 816d0daf). */
export function HelixForgeIcon({
  className,
  title = "HelixForge",
}: HelixForgeIconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 48 48"
      fill="none"
      role="img"
      aria-label={title}
      className={cn("size-8 shrink-0 text-hf-teal", className)}
    >
      <title>{title}</title>
      <path
        d="M24 4 40.25 13v22L24 44 7.75 35V13L24 4Z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M32 12 24 26 16 12"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M16 36 24 22 32 36"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
