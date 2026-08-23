import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";

export type ThemeSelectOption<T extends string | number> = {
  value: T;
  label: string;
};

type ThemeSelectProps<T extends string | number> = {
  value: T;
  onChange: (value: T) => void;
  options: ThemeSelectOption<T>[];
  className?: string;
  "aria-label"?: string;
};

export function ThemeSelect<T extends string | number>({
  value,
  onChange,
  options,
  className,
  "aria-label": ariaLabel,
}: ThemeSelectProps<T>) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const selected = options.find((option) => option.value === value);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      if (rootRef.current?.contains(event.target as Node)) return;
      setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  return (
    <div ref={rootRef} className={cn("relative", className)}>
      <button
        type="button"
        aria-label={ariaLabel}
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          "flex min-w-[9.5rem] items-center justify-between gap-2 rounded-lg border border-hf-border bg-hf-panel/80 px-3 py-2 text-sm font-mono text-hf-text shadow-sm backdrop-blur-sm transition-colors",
          "hover:border-hf-teal/40 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-hf-teal",
          open && "border-hf-teal/50 ring-1 ring-hf-teal/30",
        )}
      >
        <span>{selected?.label ?? "Select…"}</span>
        <ChevronDown
          className={cn(
            "size-4 shrink-0 text-hf-muted transition-transform duration-200",
            open && "rotate-180 text-hf-teal",
          )}
          aria-hidden
        />
      </button>

      {open && (
        <ul
          role="listbox"
          aria-label={ariaLabel}
          className="absolute right-0 z-50 mt-1.5 max-h-60 min-w-full overflow-auto rounded-xl border border-hf-border bg-hf-panel py-1 shadow-lg"
          data-lenis-prevent
        >
          {options.map((option) => {
            const isSelected = option.value === value;
            return (
              <li key={String(option.value)} role="presentation">
                <button
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => {
                    onChange(option.value);
                    setOpen(false);
                  }}
                  className={cn(
                    "w-full px-3 py-2 text-left text-sm font-mono transition-colors",
                    isSelected
                      ? "bg-hf-teal/15 text-hf-teal"
                      : "text-hf-text hover:bg-hf-elevated hover:text-hf-teal",
                  )}
                >
                  {option.label}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
