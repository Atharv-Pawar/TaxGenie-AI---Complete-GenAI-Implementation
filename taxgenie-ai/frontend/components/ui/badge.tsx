import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-medium",
  {
    variants: {
      variant: {
        default:  "bg-brand-500/10 border-brand-500/20 text-brand-400",
        success:  "bg-green-500/10 border-green-500/20 text-green-400",
        warning:  "bg-yellow-500/10 border-yellow-500/20 text-yellow-400",
        danger:   "bg-red-500/10 border-red-500/20 text-red-400",
        info:     "bg-blue-500/10 border-blue-500/20 text-blue-400",
        neutral:  "bg-surface-elevated border-surface-border text-slate-400",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
