import { useState, useEffect } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { api } from "@/lib/api";
import { motion } from "framer-motion";
import { Map } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function AmbiguityMap() {
  const [markdown, setMarkdown] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.ambiguity()
      .then(data => setMarkdown(data.markdown))
      .catch(() => setMarkdown("# Ambiguity Map\n\nUnable to load ambiguity map."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-body" style={{ color: "var(--text-3)" }}>Loading…</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-8">
          <Map size={28} style={{ color: "var(--accent-1)" }} />
          <div>
            <h1 className="text-h1" style={{ color: "var(--text-1)" }}>Audit Dashboard</h1>
            <p className="text-caption">Integrity metrics, validation rules, and logic maps across 18 central schemes.</p>
          </div>
        </div>
      </motion.div>

      <GlassCard tone="raised" className="prose max-w-none">
        <div style={{ color: "var(--text-1)", lineHeight: 1.7 }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {markdown}
          </ReactMarkdown>
        </div>
      </GlassCard>
    </div>
  );
}
