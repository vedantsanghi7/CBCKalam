/** @type {import('tailwindcss').Config} */
import plugin from "tailwindcss/plugin";

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
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
        "status-qualifies": "var(--status-qualifies)",
        "status-almost": "var(--status-almost)",
        "status-no": "var(--status-no)",
        "status-uncertain": "var(--status-uncertain)",
      },
      borderRadius: {
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
        pill: "var(--radius-pill)",
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
        glow: "var(--shadow-glow)",
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
        ".glass-raised": {
          background: "var(--surface-2)",
          boxShadow: "var(--shadow-lg)",
        },
        ".glass-dialog": {
          background: "var(--surface-3)",
          backdropFilter: "blur(var(--blur-lg)) saturate(200%)",
        },
        ".glass-highlight": {
          boxShadow:
            "inset 0 1px 0 rgba(255,255,255,0.9), inset 0 -1px 0 rgba(20,22,34,0.04), var(--shadow-md)",
        },
      });
    }),
  ],
};
