/** Slow shimmer along the sticky header's bottom edge. */
export function HeaderShimmer() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-x-0 bottom-0 h-px overflow-hidden"
    >
      <div className="hf-header-shimmer absolute inset-y-0 w-2/5 bg-gradient-to-r from-transparent via-hf-teal/70 to-transparent dark:via-hf-teal-bright/55" />
    </div>
  );
}
