import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ReactLenis, useLenis } from "lenis/react";
import { useEffect, type ReactNode } from "react";
import { useLocation } from "react-router-dom";

gsap.registerPlugin(ScrollTrigger);

const LENIS_OPTIONS = {
  autoRaf: false,
  anchors: true,
  allowNestedScroll: true,
  respectReducedMotion: true,
  lerp: 0.1,
  smoothWheel: true,
  wheelMultiplier: 1,
  touchMultiplier: 1.35,
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
  return (
    <ReactLenis root autoRaf={false} options={LENIS_OPTIONS}>
      <LenisGsapBridge />
      {children}
    </ReactLenis>
  );
}

export { gsap, ScrollTrigger, useLenis };
