import { Fragment } from "react";

export function AnimatePresence({ children }: { children: React.ReactNode }) {
  return <Fragment>{children}</Fragment>;
}

export function motion({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
  initial?: unknown;
  animate?: unknown;
  exit?: unknown;
}) {
  return <div className={className}>{children}</div>;
}

motion.div = motion;
