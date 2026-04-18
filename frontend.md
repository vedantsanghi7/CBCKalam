# KALAM — Frontend Build Guide
### The design language, component library, and build instructions for the web UI
> Pair file: `KALAM_IMPLEMENTATION_PLAN.md` covers everything else. This file owns the frontend only.

---

## 0. Read This First

### 0.1 Design Reference
The visual language is taken from three reference screens (soft gradient + frosted glass + dark pills + 3D mascot). This file translates that aesthetic into KALAM's welfare-assistant context. The look should feel **premium and trustworthy**, not toy-like — we're telling people whether they qualify for government money, so beauty must coexist with gravity.

### 0.2 Tonal Shift From References
The references are playful productivity SaaS dashboards. KALAM is a welfare tool. Keep:
- The glassmorphism, gradient, rounded corners, dark pills, mascot.
Change:
- Copy is respectful, not cute. No "Hey there! 👋 Need a boost?" — instead "Namaste 🙏 Main aapki madad kar sakta hoon."
- Status indicators are serious and unambiguous (see Section 8).
- Accessibility budget is high — minimum 16px body text, AA contrast on all text, keyboard navigable end-to-end.

### 0.3 Relationship to the Backend
Every UI state maps to an engine output defined in the main plan's Phase 6 schema. Do not invent new statuses in the UI; surface what the backend returns. Backend routes to call are listed in Section 13 and are the same ones named in `KALAM_IMPLEMENTATION_PLAN.md` § 14.

### 0.4 State & Logging Discipline
This file inherits the same rules as the main plan:
- Update `PROJECT_STATE.md` after meaningful UI work.
- Frontend LLM calls (if any — e.g. streaming assistant replies) also get logged to `prompt_log/`.
- Do NOT call Sarvam directly from the browser. All LLM calls go through the backend API. The browser never sees the API key.

---

## 1. Tech Stack

| Layer | Choice | Why |
|------|--------|-----|
| Framework | **React 18 + Vite** | Fast dev loop, standard for modern SPAs |
| Language | **TypeScript** | Eligibility data is strongly typed in the backend — mirror it |
| Styling | **Tailwind CSS** + CSS custom properties for design tokens | Matches `frontend-design` skill conventions; utility speed |
| Components | **shadcn/ui** (Radix under the hood) | Accessible primitives we can restyle to match the glass aesthetic |
| Animation | **Framer Motion** | Smooth entry animations, shared layout transitions |
| Icons | **Lucide React** + **Simple Icons** for brand logos | Lucide is line-based and matches the clean aesthetic; Simple Icons for Google/Slack-style service logos |
| 3D mascot | **Spline** (embed) OR a static PNG/GLB of a free 3D illustration | See § 7 |
| Routing | **React Router v6** | Standard |
| Data fetching | **TanStack Query (react-query)** | Caches `/schemes`, handles chat turn retries |
| Forms | **React Hook Form** + **Zod** | Slot editing / manual profile entry |
| Voice input | **Web Speech API** (initially) → backend Sarvam STT fallback | See § 10 |
| i18n | **react-i18next** | English / Hindi / Hinglish copy decks |
| Markdown | **react-markdown** + **remark-gfm** | Render scheme notes, ambiguity notes |

Install baseline:
```bash
npm create vite@latest kalam-web -- --template react-ts
cd kalam-web
npm install tailwindcss @tailwindcss/typography framer-motion lucide-react \
  react-router-dom @tanstack/react-query react-hook-form zod \
  react-markdown remark-gfm i18next react-i18next clsx tailwind-merge
npx shadcn@latest init
```

Add shadcn primitives as needed: `button`, `card`, `dialog`, `input`, `textarea`, `select`, `tabs`, `tooltip`, `popover`, `progress`, `badge`, `scroll-area`, `separator`, `skeleton`.

---

## 2. The Design Language — What We Copied and Why

Extracted from the three reference images:

### 2.1 Five pillars
1. **Soft gradient background.** A pale watercolor bloom of blue → pink → cream. Creates warmth without committing to a bold brand color.
2. **Frosted glass panels.** `backdrop-blur` + semi-transparent white + hairline border. Gives depth without hard edges.
3. **Heavy corner radii.** 20–32px on cards, 9999px (fully round) on buttons and input pills.
4. **Dark pill primary buttons.** Near-black pills with white text. Visual gravity exactly where the user needs to act.
5. **Floating 3D mascot.** A small character with a speech bubble — makes an AI tool feel approachable. For KALAM, it's a guide figure, not a toy.

### 2.2 What we intentionally drop
- The integrated-apps right sidebar (Slack/Calendar/Drive). KALAM is single-purpose — no workspace bloat.
- The multi-card landing ("Deep Research / Make an Image / Create Music"). We have one job.
- The "Upgrade to Pro" CTA. There is no pro tier.

---

## 3. Design Tokens

Put these in `src/styles/tokens.css` and expose as CSS variables. Tailwind reads them via `tailwind.config.ts`.

```css
/* src/styles/tokens.css */
:root {
  /* Background gradient stops */
  --bg-1: #EEF1FA;   /* cool blue-white, top-left */
  --bg-2: #F5E8F1;   /* dusty pink, center */
  --bg-3: #FFF4E1;   /* cream, bottom-right */
  --bg-4: #E8EFFA;   /* secondary blue bloom */

  /* Surface (glass) */
  --surface-1: rgba(255, 255, 255, 0.55);   /* cards */
  --surface-2: rgba(255, 255, 255, 0.70);   /* raised cards */
  --surface-3: rgba(255, 255, 255, 0.85);   /* dialogs */
  --surface-ink: rgba(20, 22, 34, 0.92);    /* dark pill / primary */

  /* Borders */
  --border-hairline: rgba(255, 255, 255, 0.6);
  --border-ink: rgba(20, 22, 34, 0.08);

  /* Text */
  --text-1: #141622;          /* primary */
  --text-2: #4A4E63;          /* secondary */
  --text-3: #7A7E92;          /* tertiary / captions */
  --text-inverse: #FFFFFF;

  /* Status colors — calibrated for AA contrast on glass */
  --status-qualifies: #0E7A4D;          /* deep green */
  --status-qualifies-bg: #DDF4E8;
  --status-almost: #9A5B00;              /* amber */
  --status-almost-bg: #FCEBCB;
  --status-no: #8A1F1F;                  /* muted red */
  --status-no-bg: #F6DADA;
  --status-uncertain: #4A4690;           /* deep violet — "we don't know yet" */
  --status-uncertain-bg: #E5E2F5;

  /* Accent (used sparingly — brand gradient text, focus rings) */
  --accent-1: #6E6CFF;       /* indigo */
  --accent-2: #E67AA8;       /* rose */

  /* Radii */
  --radius-xs: 8px;
  --radius-sm: 12px;
  --radius-md: 20px;
  --radius-lg: 28px;
  --radius-xl: 36px;
  --radius-pill: 9999px;

  /* Shadows — soft, never harsh */
  --shadow-sm: 0 1px 2px rgba(20, 22, 34, 0.04), 0 1px 3px rgba(20, 22, 34, 0.04);
  --shadow-md: 0 4px 20px rgba(20, 22, 34, 0.06), 0 2px 6px rgba(20, 22, 34, 0.04);
  --shadow-lg: 0 20px 60px rgba(20, 22, 34, 0.08), 0 8px 20px rgba(20, 22, 34, 0.05);
  --shadow-glow: 0 0 0 4px rgba(110, 108, 255, 0.15);   /* focus */

  /* Blur */
  --blur-sm: 12px;
  --blur-md: 24px;
  --blur-lg: 40px;

  /* Type scale */
  --font-sans: "Inter", "Plus Jakarta Sans", system-ui, -apple-system, sans-serif;
  --font-display: "Plus Jakarta Sans", "Inter", sans-serif;
  --font-devanagari: "Noto Sans Devanagari", "Inter", sans-serif;

  /* Spacing rhythm (4px base) */
  --s-1: 4px;  --s-2: 8px;  --s-3: 12px; --s-4: 16px;
  --s-5: 20px; --s-6: 24px; --s-8: 32px; --s-10: 40px;
  --s-12: 48px; --s-16: 64px; --s-20: 80px;
}

/* Optional dark mode (ship light first) */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-1: #14151F; --bg-2: #1B1830; --bg-3: #201F28; --bg-4: #131924;
    --surface-1: rgba(30, 32, 48, 0.55);
    --surface-2: rgba(30, 32, 48, 0.70);
    --surface-3: rgba(30, 32, 48, 0.85);
    --border-hairline: rgba(255, 255, 255, 0.08);
    --text-1: #F2F3F8; --text-2: #B6BACB; --text-3: #878BA0;
  }
}
```

### 3.1 Type scale
Fluid via `clamp()`, so it adapts without a dozen breakpoints.

```css
.text-display    { font-size: clamp(2.25rem, 2vw + 1.5rem, 3.5rem); font-weight: 700; letter-spacing: -0.02em; line-height: 1.05; }
.text-h1         { font-size: clamp(1.75rem, 1vw + 1.25rem, 2.25rem); font-weight: 700; line-height: 1.15; }
.text-h2         { font-size: clamp(1.35rem, 0.5vw + 1.15rem, 1.625rem); font-weight: 600; line-height: 1.25; }
.text-h3         { font-size: 1.125rem; font-weight: 600; line-height: 1.3; }
.text-body       { font-size: 1rem;    font-weight: 400; line-height: 1.55; }  /* 16px minimum — accessibility floor */
.text-sm         { font-size: 0.9375rem; line-height: 1.5; }                    /* 15px — only for captions */
.text-caption    { font-size: 0.875rem; color: var(--text-3); line-height: 1.4; }
```

**Accessibility floor:** body text never goes below 16px. Chat bubbles and scheme descriptions use `.text-body` or larger.

---

## 4. The Gradient Background (Recipe)

This is the signature of the look. Two overlapping radial gradients on a cream base, plus a subtle grain overlay. The mesh is animated very slowly (40s) so it feels alive without being distracting.

```css
/* src/styles/background.css */
.kalam-bg {
  min-height: 100dvh;
  background-color: var(--bg-3);
  background-image:
    radial-gradient(60% 50% at 10% 15%, var(--bg-1) 0%, transparent 60%),
    radial-gradient(55% 45% at 85% 30%, var(--bg-2) 0%, transparent 65%),
    radial-gradient(70% 60% at 50% 95%, var(--bg-4) 0%, transparent 70%);
  background-attachment: fixed;
  position: relative;
  isolation: isolate;
}

/* Subtle animated sheen */
.kalam-bg::before {
  content: "";
  position: fixed; inset: -10%;
  background-image:
    radial-gradient(40% 35% at 20% 50%, rgba(110, 108, 255, 0.10), transparent 70%),
    radial-gradient(45% 40% at 80% 60%, rgba(230, 122, 168, 0.10), transparent 70%);
  filter: blur(40px);
  animation: drift 40s ease-in-out infinite alternate;
  z-index: -1;
  pointer-events: none;
}

@keyframes drift {
  0%   { transform: translate3d(-2%, -1%, 0) rotate(0deg); }
  100% { transform: translate3d(2%, 1%, 0) rotate(8deg); }
}

/* Grain — makes gradients feel like watercolor, not CSS */
.kalam-bg::after {
  content: "";
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/></filter><rect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/></svg>");
  opacity: 0.035;
  mix-blend-mode: overlay;
  pointer-events: none;
  z-index: -1;
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  .kalam-bg::before { animation: none; }
}
```

Apply once on `<body>` or the root `<App>` wrapper. Every screen inherits it.

---

## 5. The Glass Recipe

The single most important component. Use this class combination everywhere you'd show a card.

```css
/* src/styles/glass.css */
.glass {
  background: var(--surface-1);
  backdrop-filter: blur(var(--blur-md)) saturate(180%);
  -webkit-backdrop-filter: blur(var(--blur-md)) saturate(180%);
  border: 1px solid var(--border-hairline);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.glass--raised {
  background: var(--surface-2);
  box-shadow: var(--shadow-lg);
}

.glass--dialog {
  background: var(--surface-3);
  backdrop-filter: blur(var(--blur-lg)) saturate(200%);
}

/* The signature inner-highlight that sells the "liquid glass" feel —
   a 1px white line along the top edge, faked with an inset shadow */
.glass-highlight {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    inset 0 -1px 0 rgba(20, 22, 34, 0.04),
    var(--shadow-md);
}

/* Fallback for browsers without backdrop-filter support */
@supports not (backdrop-filter: blur(1px)) {
  .glass { background: rgba(255, 255, 255, 0.85); }
}
```

Tailwind arbitrary utilities (put in `tailwind.config.ts`) so we can write `glass` / `glass-raised` / `glass-highlight` as single utilities:

```ts
// tailwind.config.ts
import type { Config } from "tailwindcss";
import plugin from "tailwindcss/plugin";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)"],
        display: ["var(--font-display)"],
        deva: ["var(--font-devanagari)"],
      },
      colors: {
        ink: "var(--surface-ink)",
        "text-1": "var(--text-1)",
        "text-2": "var(--text-2)",
        "text-3": "var(--text-3)",
      },
      borderRadius: {
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
        pill: "var(--radius-pill)",
      },
    },
  },
  plugins: [
    plugin(({ addUtilities }) => {
      addUtilities({
        ".glass": {
          background: "var(--surface-1)",
          backdropFilter: "blur(var(--blur-md)) saturate(180%)",
          WebkitBackdropFilter: "blur(var(--blur-md)) saturate(180%)",
          border: "1px solid var(--border-hairline)",
          borderRadius: "var(--radius-lg)",
          boxShadow: "var(--shadow-md)",
        },
        ".glass-raised": { background: "var(--surface-2)", boxShadow: "var(--shadow-lg)" },
        ".glass-dialog": { background: "var(--surface-3)", backdropFilter: "blur(var(--blur-lg)) saturate(200%)" },
        ".glass-highlight": {
          boxShadow:
            "inset 0 1px 0 rgba(255,255,255,0.9), inset 0 -1px 0 rgba(20,22,34,0.04), var(--shadow-md)",
        },
      });
    }),
  ],
} satisfies Config;
```

Now in JSX: `<div className="glass glass-highlight p-6">...</div>`.

### 5.1 Critical rule about backdrop-filter
`backdrop-blur` only works if the element behind is actually blurred — so the `.kalam-bg` must be present in the stacking context. If you nest a glass card inside a solid white div, the blur has nothing to blur and the surface looks flat. Test on every screen.

---

## 6. Component Library

Build these components first, then assemble screens from them. All live in `src/components/`.

### 6.1 `<GlassCard>` — the workhorse
```tsx
// src/components/ui/GlassCard.tsx
import { cn } from "@/lib/cn";
import { HTMLAttributes, forwardRef } from "react";

type Props = HTMLAttributes<HTMLDivElement> & {
  tone?: "default" | "raised" | "dialog";
};

export const GlassCard = forwardRef<HTMLDivElement, Props>(
  ({ className, tone = "default", ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        tone === "raised" ? "glass glass-raised glass-highlight" :
        tone === "dialog" ? "glass-dialog glass-highlight" :
        "glass glass-highlight",
        "p-6",
        className
      )}
      {...props}
    />
  )
);
GlassCard.displayName = "GlassCard";
```

### 6.2 `<PillButton>` — the dark primary button
Matches the black pill in all three references.
```tsx
// src/components/ui/PillButton.tsx
import { cn } from "@/lib/cn";
import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "ghost" | "outline";
type Size = "sm" | "md" | "lg";

const base = "inline-flex items-center justify-center gap-2 font-medium rounded-pill transition-all active:scale-[0.98] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-indigo-200/60 disabled:opacity-50";
const variants: Record<Variant, string> = {
  primary: "bg-ink text-white hover:bg-[#1E2030]",
  ghost:   "bg-white/40 text-text-1 hover:bg-white/70 backdrop-blur-md",
  outline: "border border-black/10 bg-white/50 text-text-1 hover:bg-white/80 backdrop-blur-md",
};
const sizes: Record<Size, string> = {
  sm: "h-9 px-4 text-sm",
  md: "h-11 px-5 text-[15px]",
  lg: "h-13 px-6 text-base",
};

export function PillButton({
  variant = "primary", size = "md", className, ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size }) {
  return <button className={cn(base, variants[variant], sizes[size], className)} {...rest} />;
}
```

### 6.3 `<IconRail>` — the left vertical nav
A column of circular icon buttons like the left edge of reference images 1 and 2.
```tsx
// src/components/layout/IconRail.tsx
import { MessageCircle, Search, Compass, BookOpen, History, Settings } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/cn";

const items = [
  { to: "/chat",     icon: MessageCircle, label: "Chat" },
  { to: "/schemes",  icon: Compass,       label: "Browse schemes" },
  { to: "/search",   icon: Search,        label: "Search" },
  { to: "/docs",     icon: BookOpen,      label: "Learn" },
  { to: "/history",  icon: History,       label: "History" },
];

export function IconRail() {
  return (
    <nav aria-label="Primary" className="fixed left-4 top-4 bottom-4 flex flex-col items-center gap-3 z-20">
      <div className="glass glass-highlight flex flex-col items-center gap-2 px-2 py-4 rounded-pill">
        {items.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to} to={to}
            aria-label={label}
            className={({ isActive }) => cn(
              "w-11 h-11 rounded-full grid place-items-center transition-all",
              "hover:bg-black/5",
              isActive ? "bg-ink text-white" : "text-text-2"
            )}
          >
            <Icon size={20} strokeWidth={1.75} />
          </NavLink>
        ))}
      </div>
      <NavLink
        to="/settings"
        aria-label="Settings"
        className="glass glass-highlight w-11 h-11 mt-auto rounded-full grid place-items-center text-text-2 hover:text-text-1"
      >
        <Settings size={20} strokeWidth={1.75} />
      </NavLink>
    </nav>
  );
}
```

### 6.4 `<ChatBubble>` — for user + assistant turns
Two variants: dark ink pill (user, right-aligned) and light glass card (assistant, left-aligned).
```tsx
// src/components/chat/ChatBubble.tsx
import { cn } from "@/lib/cn";
import { motion } from "framer-motion";

type Props = {
  from: "user" | "assistant";
  children: React.ReactNode;
  timestamp?: string;
  avatar?: React.ReactNode;
};

export function ChatBubble({ from, children, timestamp, avatar }: Props) {
  const isUser = from === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
      className={cn("flex gap-3 w-full", isUser ? "justify-end" : "justify-start")}
    >
      {!isUser && <div className="shrink-0 w-8 h-8 rounded-full bg-ink grid place-items-center text-white text-sm font-semibold">K</div>}
      <div className={cn("flex flex-col max-w-[78%]", isUser && "items-end")}>
        <div className={cn(
          "px-5 py-3 text-body",
          isUser
            ? "bg-ink text-white rounded-3xl rounded-br-lg"
            : "glass glass-highlight rounded-3xl rounded-bl-lg"
        )}>
          {children}
        </div>
        {timestamp && <span className="text-caption mt-1 px-2">{timestamp}</span>}
      </div>
      {isUser && avatar}
    </motion.div>
  );
}
```

### 6.5 `<ChatComposer>` — the input at the bottom
Mirrors the rounded pill input with `+` icon, mic, and dark send button from images 1 and 2.
```tsx
// src/components/chat/ChatComposer.tsx
import { Plus, Mic, Send } from "lucide-react";
import { useState } from "react";
import { PillButton } from "@/components/ui/PillButton";

export function ChatComposer({ onSend, onVoice }: { onSend: (v: string) => void; onVoice: () => void }) {
  const [val, setVal] = useState("");
  const submit = () => { if (val.trim()) { onSend(val); setVal(""); } };

  return (
    <div className="glass glass-raised glass-highlight rounded-pill flex items-center gap-2 p-2">
      <button aria-label="Attach" className="w-10 h-10 rounded-full grid place-items-center hover:bg-black/5 text-text-2">
        <Plus size={20} />
      </button>
      <input
        value={val}
        onChange={(e) => setVal(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
        placeholder="Apna sawal likhein ya mic dabayein…"
        aria-label="Your message"
        className="flex-1 bg-transparent border-0 outline-none text-body placeholder:text-text-3 px-2"
      />
      <button onClick={onVoice} aria-label="Voice input"
        className="w-10 h-10 rounded-full grid place-items-center hover:bg-black/5 text-text-2">
        <Mic size={20} />
      </button>
      <PillButton onClick={submit} size="md" aria-label="Send" className="w-11 h-11 p-0">
        <Send size={18} />
      </PillButton>
    </div>
  );
}
```

### 6.6 `<StatusBadge>` — the single most important component in KALAM
Users see this on every scheme. It must be unambiguous, large, and accessible.
```tsx
// src/components/scheme/StatusBadge.tsx
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from "lucide-react";

export type Status = "QUALIFIES" | "ALMOST_QUALIFIES" | "DOES_NOT_QUALIFY" | "UNCERTAIN";

const map: Record<Status, { label: string; icon: React.ElementType; fg: string; bg: string }> = {
  QUALIFIES:         { label: "Eligible",           icon: CheckCircle2, fg: "var(--status-qualifies)", bg: "var(--status-qualifies-bg)" },
  ALMOST_QUALIFIES:  { label: "Almost eligible",    icon: AlertTriangle, fg: "var(--status-almost)",   bg: "var(--status-almost-bg)" },
  DOES_NOT_QUALIFY:  { label: "Not eligible",       icon: XCircle,       fg: "var(--status-no)",       bg: "var(--status-no-bg)" },
  UNCERTAIN:         { label: "Needs clarification", icon: HelpCircle,   fg: "var(--status-uncertain)",bg: "var(--status-uncertain-bg)" },
};

export function StatusBadge({ status }: { status: Status }) {
  const { label, icon: Icon, fg, bg } = map[status];
  return (
    <span
      role="status"
      style={{ backgroundColor: bg, color: fg }}
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-sm font-semibold"
    >
      <Icon size={14} strokeWidth={2.25} />
      {label}
    </span>
  );
}
```

Never use color alone — icon + label + color together, so colorblind users are served.

### 6.7 `<SchemeCard>` — the result card
The thing the user came here to see. Must show status, confidence, and a drill-down affordance.
```tsx
// src/components/scheme/SchemeCard.tsx
import { GlassCard } from "@/components/ui/GlassCard";
import { StatusBadge, Status } from "./StatusBadge";
import { ConfidenceMeter } from "./ConfidenceMeter";
import { ArrowUpRight } from "lucide-react";

type Props = {
  schemeId: string;
  name: string;
  status: Status;
  confidence: number;           // 0..1
  ministry: string;
  benefitLine: string;          // "₹6,000/year via DBT"
  applicationOrder?: number;
  onOpen: () => void;
};

export function SchemeCard(p: Props) {
  return (
    <GlassCard tone="raised" className="flex flex-col gap-4 p-6 hover:-translate-y-0.5 transition-transform">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-caption uppercase tracking-wide">{p.ministry}</div>
          <h3 className="text-h2 mt-1">{p.name}</h3>
        </div>
        <StatusBadge status={p.status} />
      </div>

      <p className="text-body text-text-2">{p.benefitLine}</p>

      <ConfidenceMeter value={p.confidence} status={p.status} />

      <div className="flex items-center justify-between mt-2">
        {p.applicationOrder ? (
          <span className="text-caption">Suggested order: <b>#{p.applicationOrder}</b></span>
        ) : <span />}
        <button onClick={p.onOpen} className="inline-flex items-center gap-1 text-sm font-semibold text-text-1 hover:underline">
          View details <ArrowUpRight size={14} />
        </button>
      </div>
    </GlassCard>
  );
}
```

### 6.8 `<ConfidenceMeter>` — the explainable number
Never show a lone number. Show the breakdown.
```tsx
// src/components/scheme/ConfidenceMeter.tsx
type Props = {
  value: number;   // 0..1
  status: "QUALIFIES" | "ALMOST_QUALIFIES" | "DOES_NOT_QUALIFY" | "UNCERTAIN";
  breakdown?: { base: number; completeness: number; cleanliness: number; freshness: number };
};

export function ConfidenceMeter({ value, status, breakdown }: Props) {
  const pct = Math.round(value * 100);
  const track =
    status === "QUALIFIES" ? "var(--status-qualifies)" :
    status === "ALMOST_QUALIFIES" ? "var(--status-almost)" :
    status === "DOES_NOT_QUALIFY" ? "var(--status-no)" :
                                   "var(--status-uncertain)";
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-caption">Confidence</span>
        <span className="text-sm font-semibold">{pct}%</span>
      </div>
      <div className="h-2 w-full bg-black/5 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-[width] duration-700 ease-out"
          style={{ width: `${pct}%`, backgroundColor: track }}
          role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}
        />
      </div>
      {breakdown && (
        <dl className="mt-2 grid grid-cols-4 gap-2 text-caption">
          <Metric k="Base"        v={breakdown.base} />
          <Metric k="Data"        v={breakdown.completeness} />
          <Metric k="Clarity"     v={breakdown.cleanliness} />
          <Metric k="Freshness"   v={breakdown.freshness} />
        </dl>
      )}
    </div>
  );
}
function Metric({ k, v }: { k: string; v: number }) {
  return (
    <div>
      <dt className="text-text-3">{k}</dt>
      <dd className="font-medium text-text-1">{Math.round(v * 100)}%</dd>
    </div>
  );
}
```

### 6.9 `<MascotBubble>` — the floating guide
Like the robot-with-speech-bubble from the references, but tuned for trust.
```tsx
// src/components/mascot/MascotBubble.tsx
import { motion } from "framer-motion";

export function MascotBubble({ message, imgSrc = "/mascot.png" }: { message: string; imgSrc?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.4 }}
      className="fixed bottom-8 right-8 z-30 flex items-end gap-3 pointer-events-none"
    >
      <div className="glass glass-highlight px-4 py-2 rounded-2xl max-w-xs text-sm pointer-events-auto">
        {message}
      </div>
      <motion.img
        src={imgSrc}
        alt=""
        width={96} height={96}
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        className="drop-shadow-xl select-none"
      />
    </motion.div>
  );
}
```

Hide on screens < 1024px — don't crowd small devices.

### 6.10 Other essentials
- `<SlotChipRow>` — shows known user slots as editable chips above the chat, so the user can see and correct what the system has about them.
- `<QuickReplyOptions>` — renders the `options` array from the backend's follow-up question as horizontal pills. User taps one → sends as next turn.
- `<DocumentChecklist>` — numbered list of docs with download-template buttons and "I have this" toggle.
- `<ApplicationSteps>` — numbered ordered list with arrow connectors for the application sequence.
- `<SourceCitation>` — tiny chip with the source URL and fetch date, always shown with rule evaluations. Click → opens the source in a new tab.
- `<AmbiguityNote>` — amber/violet callout component, shown prominently when any rule has flags.
- `<VoiceRecorder>` — mic button that records and posts to `/stt`.

---

## 7. The 3D Mascot

The references use a stylized white robot. For KALAM we want something that fits a welfare context — friendly, Indian-respectful, not corporate.

### 7.1 Options, ranked

1. **Build it in Spline** (recommended). Create a simple rounded character (think: a friendly owl, a diya, or an abstract assistant blob). Spline exports to a `<spline-viewer>` web component with one line of code. Free tier is enough. Time: 2–3 hours for a non-artist using their templates.

2. **Use a free 3D illustration pack.** Render a single PNG or use a GLB with `<model-viewer>`. Good sources:
   - **3dicons.co** (CC0) — has friendly character packs
   - **iconscout.com 3D** — free illustrations, check license
   - **Spline Community** — clone and fork
   - **Microsoft Fluent Emoji** — the 3D emoji set is CC-BY, includes friendly faces (🙂, 👍, 📋, 🏛️)

3. **Generate a static image** via an AI image tool, then use it as a PNG. Lowest effort, looks fine, but no animation. Prompt: *"friendly minimalist 3D mascot, soft lighting, off-white color palette, low-poly, isometric, approachable, Indian-cultural-neutral, no face details, clean background, isolated on transparent"*. Export at 2x retina (512×512 minimum).

4. **Skip the mascot entirely.** The aesthetic still works — the references proved the glass + gradient is the signature, not the robot. If you're behind schedule, drop the mascot and add a subtle abstract illustration (a diya, a lotus, a simple gradient orb) in its place.

### 7.2 Implementation — Spline embed
```html
<!-- index.html or inside a component -->
<script type="module" src="https://unpkg.com/@splinetool/viewer/build/spline-viewer.js"></script>
<spline-viewer url="https://prod.spline.design/YOUR_SCENE/scene.splinecode" style="width:120px;height:120px"></spline-viewer>
```

### 7.3 When NOT to show the mascot
- On the results page when any scheme status is `DOES_NOT_QUALIFY` or `UNCERTAIN`. A smiling character next to "Not eligible" is tone-deaf. Hide it.
- On error states.
- During the first question of a chat session — let the user focus.

---

## 8. Screens — Layouts

### 8.1 `/` — Landing / Welcome
Loosely inspired by reference image 2, but built for a first-time welfare user.

```
┌─ IconRail ─┬──────────────────────── main ─────────────────────────┐
│            │                                                        │
│    • chat  │   Namaste 🙏                                            │
│    • …     │   Kaunsi sarkari yojana aapke liye hai? Chaliye         │
│            │   pata lagate hain.                                    │
│            │                                                        │
│            │   [ Start check — 2 min ]  [ Browse all 18 schemes ]   │
│            │                                                        │
│            │   ┌──glass card─┐ ┌──glass card─┐ ┌──glass card─┐     │
│            │   │ 🌾 Farmer   │ │ 🏥 Health    │ │ 🏠 Housing  │     │
│            │   │ schemes     │ │ schemes      │ │ schemes     │     │
│            │   │ 4 available │ │ 1 available  │ │ 2 available │     │
│            │   └─────────────┘ └──────────────┘ └─────────────┘     │
│            │                                                        │
│            │   ┌────────────────── Composer ────────────────────┐    │
│            │   │ + | Type or tap mic in Hindi / English / Hinglish  🎙 ➤ │ │
│            │   └──────────────────────────────────────────────────┘    │
│            │                                                        │
│            │                                 [MascotBubble bottom-right] │
└────────────┴────────────────────────────────────────────────────────┘
```

**Copy matters:**
- The hero headline and sub-headline are bilingual in the same block (not a separate toggle) — normalizes Hinglish.
- The "Start check" button is the **only** primary CTA. Everything else is secondary.
- Category cards are filter shortcuts, not replacements for the chat.

### 8.2 `/chat` — The conversational interface
The main workhorse, loosely inspired by reference image 1. Full-height layout:

```
┌─ IconRail ─┬──────────── main (chat column) ──────────┬─ context rail ┐
│            │   ⟵ back   Eligibility check   [ End ]   │ Your info     │
│            │                                           │ (SlotChipRow) │
│            │   [assistant bubble]                      │  age: 34      │
│            │   [user bubble]                           │  state: RJ    │
│            │   [assistant bubble]                      │  land: owned  │
│            │    [QuickReplyOptions: Yes | No | Skip]   │   [+ edit]    │
│            │                                           │               │
│            │   …                                       │ Progress:     │
│            │                                           │ ██████░░░░ 60%│
│            │                                           │ 6 of 10 slots │
│            │                                           │               │
│            │   ┌────────── Composer ────────────┐      │               │
│            │   │  + | message…           🎙 ➤  │      │               │
│            │   └────────────────────────────────┘      │               │
└────────────┴───────────────────────────────────────────┴───────────────┘
```

Details:
- Max chat width **680px** for readability. Context rail is 320px. Hide context rail under 1024px and put it in a sheet accessible via a floating button.
- **Auto-scroll** to the newest bubble; **preserve scroll** if the user is reading back.
- When the backend returns `ready_to_match: true`, an inline `<SchemeResultsTeaser>` appears in the chat stream: "I have enough info — view results (4 eligible, 2 almost)". Clicking transitions to `/results`.

### 8.3 `/results` — Scheme matches (the payoff)
Grid of `<SchemeCard>`. Group by status: Eligible first, then Almost, then Uncertain, then Not Eligible (collapsed under a "Show ineligible" toggle — show what's POSSIBLE first).

```
┌─────────────────────────────────────────────────────────────┐
│   Aap 4 yojanaon ke liye eligible hain.                     │
│   2 ke liye almost. 1 clarification chahiye.                │
│                                                             │
│   [tab:  Eligible (4)  |  Almost (2)  |  Unclear (1)  |  No (3) ] │
│                                                             │
│   ┌ SchemeCard ──┐  ┌ SchemeCard ──┐  ┌ SchemeCard ──┐      │
│   │ PM-KISAN     │  │ PMJAY        │  │ PMJDY        │      │
│   │ ✅ Eligible  │  │ ✅ Eligible  │  │ ✅ Eligible  │      │
│   │ ██████ 91%   │  │ ██████ 88%   │  │ ██████ 95%   │      │
│   │ #2 Apply     │  │ #3 Apply     │  │ #1 Apply first│      │
│   └──────────────┘  └──────────────┘  └──────────────┘      │
│   …                                                         │
│                                                             │
│   [ Apply in order — see next steps → ]                     │
└─────────────────────────────────────────────────────────────┘
```

### 8.4 `/scheme/:id` — Scheme detail (drill-down)
Opened from a `SchemeCard`. Must show:
- Header: scheme name, ministry, status badge, confidence meter **with breakdown**.
- Rules evaluated: a table/list with each rule, user's value, rule result (✓/✗/?), source citation chip.
- `<AmbiguityNote>` if any rule has flags.
- `<DocumentChecklist>` with the docs needed.
- Benefit details and the official application URL as a `<PillButton>` opening in a new tab.
- "Go to application" is NEVER auto-submitted — KALAM helps discover, user applies.

### 8.5 `/schemes` — Catalogue browse
Grid of all 18 schemes with minimal info + a filter bar (category, ministry, status). For curious users who don't want a chat.

### 8.6 `/ambiguity-map` — The evaluator-facing page
Exposes the ambiguity map JSON as a readable page. Tables for Overlaps, Contradictions, Undefined Terms. This is one of the six deliverables — it lives at a URL the evaluator can hit.

### 8.7 `/history` — Past sessions
Cards grouped by day (like the Today / Yesterday split in reference image 1 and 3). Each card shows: started-at time, # schemes matched, quick re-open.

### 8.8 `/prompt-log` (dev-only, route-guarded)
Renders the contents of `prompt_log/` as a browsable table. Useful during judging — evaluators can drill into any LLM call.

---

## 9. Motion & Micro-interactions

Keep it calm. No bouncing. Every motion must serve readability, not decoration.

| Surface | Animation | Spec |
|---------|-----------|------|
| Chat bubble enter | fade + 8px rise | 250ms, `cubic-bezier(0.16, 1, 0.3, 1)` |
| Scheme card grid | stagger in | 60ms stagger, same easing, 300ms total each |
| Status badge | none on render; shake (3deg, 120ms × 2) if status UNCERTAIN to draw attention | only once, disable if `prefers-reduced-motion` |
| Confidence bar fill | width transition 700ms `ease-out` | fills on mount |
| Composer | focus → border lifts to `var(--accent-1)`, scale 1.005 | 150ms |
| Page transition | shared layout on `<SchemeCard>` → `/scheme/:id` header | Framer Motion `layoutId` |
| Mascot | 3s vertical bob, amplitude 6px | infinite, pauses on hover |
| Background gradient | 40s slow drift | covered in § 4 |

**Reduced motion:** the app respects `prefers-reduced-motion: reduce` for every one of these. No exceptions.

---

## 10. Voice Input (Hinglish)

1. Tap mic → use Web Speech API where available (`webkitSpeechRecognition`, language `hi-IN` with English allowed).
2. If not available (Safari desktop), record with `MediaRecorder`, POST audio blob to `/stt` (backend proxies to Sarvam Saaras v3 with `mode: "transcribe"` and `language: "hi-IN"`).
3. Show a live waveform while recording (reference image 1 has one — use `wavesurfer.js` or a simple `<canvas>` based on `AudioContext.getByteFrequencyData`).
4. On stop, drop the transcribed text into the composer so the user can edit before sending.

Accessibility: voice is an enhancement, never the only way to input.

---

## 11. Accessibility Floor (Non-Negotiable)

1. **Contrast:** every text/background pair passes **WCAG AA** (4.5:1 body, 3:1 large). Test every glass surface with an auto-checker — the semi-transparent backgrounds are the risk zone.
2. **Keyboard:** every interactive element is reachable via `Tab` and operable via `Enter`/`Space`. Visible focus rings (`focus-visible:ring-4 ring-indigo-200/60`).
3. **Screen reader:** status badges include the text label (not just color/icon); composer has `aria-label`; chat bubbles use `role="log"` with `aria-live="polite"` on the assistant's stream.
4. **Text scaling:** layouts survive 200% browser zoom. No fixed-height text containers.
5. **Language attribute:** `<html lang="en-IN">` by default; bilingual content wrapped in `<span lang="hi">Hindi text</span>` so screen readers switch voices.
6. **Forms:** every input has a visible label (not just placeholder).
7. **Motion:** `prefers-reduced-motion` respected everywhere (§ 9).
8. **Color-blind:** status uses icon + label + color — never color alone.
9. **Touch targets:** 44×44px minimum. The rail icons, composer buttons, and status badges all meet this.

---

## 12. Features That Must Be Directly Available
From any screen, the user can reach, in at most **two taps**:

1. **Start a new eligibility check** — persistent IconRail → Chat.
2. **Switch language / register** — top-right persistent toggle (EN / हिंदी / Hinglish). Stored in `localStorage`.
3. **Voice input** — mic always visible in the composer.
4. **See my current info** — the SlotChipRow is always visible in the context rail (desktop) or behind a floating button (mobile).
5. **Edit any slot** — chip → tap → inline editor. Backend `/session/{id}/patch` endpoint updates the slot and re-matches.
6. **Export results as PDF** — one button on the results page. Uses `window.print()` with a print-tuned stylesheet initially; later swap in a server-rendered PDF if needed.
7. **Share results via WhatsApp / copy link** — one button. Creates a signed, read-only URL of the results page.
8. **Get help** — persistent IconRail `?` icon, opens a dialog with three tips and a "contact" link.
9. **See sources** — every rule on the scheme detail page has a clickable source citation chip.
10. **See my prompt log (dev only)** — bottom-left footer link, visible only when `localStorage.kalam_dev === "1"`.

---

## 13. API Integration

All fetches through a thin client in `src/lib/api.ts`. Base URL from `VITE_API_BASE`.

```ts
// src/lib/api.ts
const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
  });
  if (!r.ok) throw new ApiError(r.status, await r.text());
  return r.json();
}
export class ApiError extends Error { constructor(public status: number, m: string){ super(m); } }

// Endpoints (mirror backend plan § 14)
export const api = {
  startSession: ()          => req<{ session_id: string }>("/session", { method: "POST" }),
  turn: (sid: string, utterance: string) =>
    req<TurnResponse>(`/session/${sid}/turn`, { method: "POST", body: JSON.stringify({ utterance }) }),
  patch: (sid: string, slot: string, value: unknown) =>
    req(`/session/${sid}/patch`, { method: "POST", body: JSON.stringify({ slot, value }) }),
  match: (sid: string)      => req<EngineOutput>(`/session/${sid}/match`, { method: "POST" }),
  listSchemes: ()           => req<SchemeSummary[]>("/schemes"),
  getScheme: (id: string)   => req<Scheme>(`/schemes/${id}`),
  ambiguity: ()             => req<AmbiguityMap>("/ambiguity-map"),
};
```

### 13.1 Types must mirror the backend exactly
Generate TypeScript types from the backend Pydantic models. Options:
- `datamodel-codegen` on the backend side → emits TS.
- Or hand-write in `src/types.ts` and keep in sync (easier for this size).

Types to cover: `TurnResponse`, `EngineOutput`, `SchemeResult`, `RuleEvaluation`, `AmbiguityNote`, `Scheme`.

### 13.2 Optimistic UI
- When the user sends a message, render their bubble immediately (optimistic) and show a "KALAM is thinking" typing indicator (three pulsing dots in a glass card) until the assistant reply arrives.
- If the backend errors, show a retry button inside the assistant bubble slot — never a toast (toasts lose the thread).

### 13.3 Never call Sarvam from the browser
The API key stays on the server. If a developer suggests calling Sarvam directly from the SPA "for speed," refuse — it leaks the key. All LLM calls are backend-mediated.

---

## 14. File Structure

```
kalam-web/
├── index.html
├── public/
│   ├── mascot.png              # or mascot.glb
│   └── favicon.svg
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── router.tsx
│   ├── styles/
│   │   ├── tokens.css
│   │   ├── background.css
│   │   ├── glass.css
│   │   └── globals.css
│   ├── lib/
│   │   ├── api.ts
│   │   ├── cn.ts
│   │   └── i18n.ts
│   ├── types.ts                 # mirrors backend pydantic
│   ├── components/
│   │   ├── ui/                  # GlassCard, PillButton, StatusBadge, etc.
│   │   ├── layout/              # IconRail, Shell, PageHeader
│   │   ├── chat/                # ChatBubble, ChatComposer, SlotChipRow, QuickReplyOptions
│   │   ├── scheme/              # SchemeCard, ConfidenceMeter, DocumentChecklist, ApplicationSteps, SourceCitation, AmbiguityNote
│   │   └── mascot/              # MascotBubble
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── Chat.tsx
│   │   ├── Results.tsx
│   │   ├── SchemeDetail.tsx
│   │   ├── SchemesCatalogue.tsx
│   │   ├── AmbiguityMap.tsx
│   │   ├── History.tsx
│   │   ├── Settings.tsx
│   │   └── PromptLog.tsx        # dev-only
│   ├── i18n/
│   │   ├── en.json
│   │   ├── hi.json
│   │   └── hinglish.json
│   └── hooks/
│       ├── useSession.ts
│       ├── useVoice.ts
│       └── useReducedMotion.ts
├── tailwind.config.ts
├── vite.config.ts
├── tsconfig.json
├── .env.example                 # VITE_API_BASE=http://localhost:8000
└── package.json
```

---

## 15. Build Order

Each step should end with a commit + a `PROJECT_STATE.md` update.

1. Scaffold Vite + TS + Tailwind + shadcn. Get the `.kalam-bg` working. Render "Hello KALAM" on a glass card. Verify the glass actually blurs.
2. Build the design system: GlassCard, PillButton, StatusBadge, ConfidenceMeter. Put them on a `/_kitchen-sink` route and screenshot against the reference images.
3. Build the IconRail and shared `<Shell>` layout.
4. Build the `/` landing page.
5. Build the Chat page: ChatBubble, ChatComposer, QuickReplyOptions, SlotChipRow, context rail. Wire to `api.startSession` + `api.turn` with a **mocked backend** first (`msw`). Don't wait for the real backend.
6. Build Results page + SchemeCard grid. Mock data.
7. Build SchemeDetail page. Mock data.
8. Swap mock for real backend once it's available. Keep `msw` mocks in place as fallback for offline dev.
9. Add voice input.
10. Add i18n toggles, History page, Ambiguity map page, Prompt log viewer.
11. Mascot + micro-interactions.
12. Accessibility audit: axe-core + manual keyboard traversal + screen-reader walkthrough (VoiceOver on macOS, NVDA on Windows).
13. Performance pass: images to WebP, lazy-load routes, compress the gradient grain SVG (already tiny).
14. Final QA: walk the 10 adversarial profiles through the UI. For each, screenshot the results. File under `docs/demo_screenshots/`.

---

## 16. Pre-Submission Visual QA Checklist

Before calling the frontend done, compare side-by-side with the reference images and confirm:

1. Background has the multi-bloom gradient with subtle movement (not a flat or linear gradient).
2. All cards use the glass recipe (visible blur when overlapping the gradient).
3. Primary action everywhere is a dark ink pill, not a colored button.
4. Corner radii are generous (≥20px on cards).
5. Status badges are unambiguous and accessible (icon + label + color).
6. Chat bubbles: user = dark pill right, assistant = glass card left.
7. Composer is a rounded pill with attach, mic, and a dark send button.
8. At least one mascot-with-speech-bubble floats on the landing and chat screens.
9. IconRail on the left matches the vertical stack aesthetic.
10. Typography is Inter/Plus Jakarta, not system default.
11. On results pages, ineligible schemes are collapsed by default — the eye lands on "what you can get," not "what you can't."
12. Keyboard-only navigation completes a full eligibility check without touching a mouse.
13. 200% browser zoom doesn't break any layout.
14. Screen reader announces status changes (`aria-live`).
15. All copy exists in EN, HI, and Hinglish variants.

---

## 17. Two Traps to Avoid

1. **The backdrop-blur trap.** A glass card looks flat if there's no textured background behind it. If you nest a `glass` div inside a white parent, the blur blurs pure white and you see nothing. Always keep the `.kalam-bg` in the stacking context below.
2. **The "cute when serious" trap.** The mascot and rounded corners are lovely when telling someone they qualify for ₹6,000/year. They are jarring when telling a widow "we're not sure — please consult a CSC." Build conditional logic that **mutes decoration** (hide mascot, dampen animations, switch mascot speech to a sober line) whenever the dominant result status is `DOES_NOT_QUALIFY` or `UNCERTAIN`. Beauty must never drown out accuracy.

---

— End of frontend guide —
