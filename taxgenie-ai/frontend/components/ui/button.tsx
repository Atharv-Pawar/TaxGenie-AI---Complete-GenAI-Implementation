import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-xl text-sm font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 disabled:opacity-40 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        default:   "bg-brand-500 text-white hover:bg-brand-600",
        secondary: "bg-surface-card border border-surface-border text-slate-300 hover:text-white hover:border-brand-500/40",
        ghost:     "text-slate-400 hover:text-white hover:bg-surface-card",
        danger:    "bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20",
        outline:   "border border-surface-border text-slate-300 hover:border-brand-500/40 hover:text-white",
      },
      size: {
        sm:      "px-3 py-1.5 text-xs rounded-lg",
        default: "px-5 py-2.5",
        lg:      "px-8 py-4 text-base",
        icon:    "w-9 h-9 rounded-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  )
);
Button.displayName = "Button";

export { Button, buttonVariants };
