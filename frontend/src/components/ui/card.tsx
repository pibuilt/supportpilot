import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "glass-panel rounded-3xl border border-[color:var(--line)] bg-[color:var(--panel)] p-5 shadow-panel",
        className,
      )}
      {...props}
    />
  );
}
