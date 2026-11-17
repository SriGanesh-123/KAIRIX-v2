import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs:ClassValue[]){return twMerge(clsx(inputs));}

const buttonVariants=cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0b3048]/25 focus-visible:ring-offset-2 focus-visible:ring-offset-[#f2f0e9] disabled:pointer-events-none disabled:opacity-45 active:translate-y-px",
  {variants:{
    variant:{
      default:"bg-[#0b3048] text-[#f2f0e9] shadow-neo-sm hover:bg-[#12415d] hover:shadow-neo",
      lime:"bg-[#b9f12f] text-[#0b3048] shadow-[5px_5px_12px_rgba(11,48,72,.12),-5px_-5px_12px_rgba(255,255,255,.7)] hover:bg-[#c8f64d]",
      outline:"border border-[#0b3048]/15 bg-[#f2f0e9] text-[#0b3048] shadow-neo-sm hover:border-[#0b3048]/25 hover:shadow-neo",
      secondary:"bg-[#e8e7df] text-[#0b3048] shadow-neo-sm hover:bg-[#e1e0d7]",
      ghost:"text-[#0b3048] hover:bg-[#0b3048]/5"
    },
    size:{default:"h-10 px-4 py-2",sm:"h-8 rounded-lg px-3 text-xs",lg:"h-12 rounded-2xl px-5",icon:"h-10 w-10"}
  },defaultVariants:{variant:"default",size:"default"}}
);
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>,VariantProps<typeof buttonVariants>{asChild?:boolean}
export const Button=React.forwardRef<HTMLButtonElement,ButtonProps>(({className,variant,size,asChild=false,...props},ref)=>{
  const Comp=asChild?Slot:"button";
  return <Comp ref={ref} className={cn(buttonVariants({variant,size,className}))} {...props}/>;
});
Button.displayName="Button";

const badgeVariants=cva("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-bold tracking-wide",{
  variants:{variant:{
    default:"bg-[#0b3048] text-[#f2f0e9]",lime:"bg-[#b9f12f]/80 text-[#0b3048]",
    outline:"border border-[#0b3048]/15 text-[#0b3048]/70",muted:"bg-[#0b3048]/5 text-[#0b3048]/60",
    pending:"bg-[#e8e3d8] text-[#0b3048]/65"
  }},defaultVariants:{variant:"default"}
});
export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>,VariantProps<typeof badgeVariants>{}
export function Badge({className,variant,...props}:BadgeProps){return <div className={cn(badgeVariants({variant}),className)} {...props}/>;}

export const Card=React.forwardRef<HTMLDivElement,React.HTMLAttributes<HTMLDivElement>>(({className,...props},ref)=><div ref={ref} className={cn("neo-card rounded-2xl",className)} {...props}/>);
Card.displayName="Card";
export function CardHeader({className,...props}:React.HTMLAttributes<HTMLDivElement>){return <div className={cn("flex flex-col gap-1.5 p-5",className)} {...props}/>;}
export function CardTitle({className,...props}:React.HTMLAttributes<HTMLHeadingElement>){return <h3 className={cn("font-display text-base font-bold tracking-tight text-[#0b3048]",className)} {...props}/>;}
export function CardDescription({className,...props}:React.HTMLAttributes<HTMLParagraphElement>){return <p className={cn("text-sm leading-6 text-[#0b3048]/55",className)} {...props}/>;}
export function CardContent({className,...props}:React.HTMLAttributes<HTMLDivElement>){return <div className={cn("px-5 pb-5",className)} {...props}/>;}

export const Input=React.forwardRef<HTMLInputElement,React.ComponentProps<"input">>(({className,type,...props},ref)=>(
  <input ref={ref} type={type} className={cn("neo-inset flex h-11 w-full rounded-xl border border-white/70 bg-[#eeece4] px-3.5 py-2 text-sm text-[#0b3048] placeholder:text-[#0b3048]/35 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0b3048]/20 disabled:cursor-not-allowed disabled:opacity-50",className)} {...props}/>
));
Input.displayName="Input";
export const Textarea=React.forwardRef<HTMLTextAreaElement,React.ComponentProps<"textarea">>(({className,...props},ref)=>(
  <textarea ref={ref} className={cn("neo-inset flex min-h-28 w-full resize-y rounded-xl border border-white/70 bg-[#eeece4] px-3.5 py-3 text-sm leading-6 text-[#0b3048] placeholder:text-[#0b3048]/35 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0b3048]/20 disabled:cursor-not-allowed disabled:opacity-50",className)} {...props}/>
));
Textarea.displayName="Textarea";
