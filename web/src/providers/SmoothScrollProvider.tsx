import { useEffect, type ReactNode } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ReactLenis, useLenis } from "lenis/react";
import { useLocation } from "react-router-dom";
import { useMediaQuery } from "@/hooks/useMediaQuery";

gsap.registerPlugin(ScrollTrigger);

/** Lenis + GSAP ticker is for fine-pointer desktops; phones use native scroll. */
const LENIS_MQ =
  "(min-width: 768px) and (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)";

const LENIS_OPTIONS = {
  autoRaf: false,
  anchors: true,
  allowNestedScroll: true,
  respectReducedMotion: true,
  lerp: 0.12,
  smoothWheel: true,
  wheelMultiplier: 1,
  touchMultiplier: 1.2,
  syncTouch: false,
} as const;

function LenisGsapBridge() {
  const lenis = useLenis();

  useEffect(() => {
    if (!lenis) return;

    const onScroll = () => ScrollTrigger.update();
    lenis.on("scroll", onScroll);

    const raf = (time: number) => {
      lenis.raf(time * 1000);
    };

    gsap.ticker.add(raf);
    gsap.ticker.lagSmoothing(0);

    return () => {
      gsap.ticker.remove(raf);
      lenis.off("scroll", onScroll);
    };
  }, [lenis]);

  return null;
}

/** Recalculate scroll bounds after route changes. */
export function LenisRouteSync() {
  const lenis = useLenis();
  const { pathname } = useLocation();

  useEffect(() => {
    if (!lenis) return;
    const id = requestAnimationFrame(() => lenis.resize());
    return () => cancelAnimationFrame(id);
  }, [pathname, lenis]);

  return null;
}

interface SmoothScrollProviderProps {
  children: ReactNode;
}

export function SmoothScrollProvider({ children }: SmoothScrollProviderProps) {
  const enableLenis = useMediaQuery(LENIS_MQ);

  if (!enableLenis) {
    return <>{children}</>;
  }

  return (
    <ReactLenis root autoRaf={false} options={LENIS_OPTIONS}>
      <LenisGsapBridge />
      {children}
    </ReactLenis>
  );
}

export { gsap, ScrollTrigger, useLenis };
