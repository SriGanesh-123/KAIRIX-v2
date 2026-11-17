import type { Config } from "tailwindcss";

export default {
  darkMode:["class"],
  content:["./index.html","./src/**/*.{ts,tsx}"],
  theme:{
    extend:{
      colors:{
        border:"hsl(var(--border))",input:"hsl(var(--input))",ring:"hsl(var(--ring))",
        background:"hsl(var(--background))",foreground:"hsl(var(--foreground))",
        primary:{DEFAULT:"hsl(var(--primary))",foreground:"hsl(var(--primary-foreground))"},
        secondary:{DEFAULT:"hsl(var(--secondary))",foreground:"hsl(var(--secondary-foreground))"},
        muted:{DEFAULT:"hsl(var(--muted))",foreground:"hsl(var(--muted-foreground))"},
        accent:{DEFAULT:"hsl(var(--accent))",foreground:"hsl(var(--accent-foreground))"},
        kairix:{teal:"#0b3048",pearl:"#f2f0e9",lime:"#b9f12f"}
      },
      borderRadius:{xl:"var(--radius)",lg:"calc(var(--radius) - 2px)",md:"calc(var(--radius) - 4px)"},
      fontFamily:{sans:["DM Sans","sans-serif"],display:["Manrope","sans-serif"],mono:["IBM Plex Mono","monospace"]},
      boxShadow:{
        neo:"9px 9px 22px rgba(11,48,72,.09), -9px -9px 22px rgba(255,255,255,.88)",
        "neo-sm":"5px 5px 12px rgba(11,48,72,.08), -5px -5px 12px rgba(255,255,255,.9)",
        "neo-inset":"inset 4px 4px 10px rgba(11,48,72,.08), inset -4px -4px 10px rgba(255,255,255,.9)"
      }
    }
  },
  plugins:[]
} satisfies Config;