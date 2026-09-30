import { Plus } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { CustomProviderInfo } from "@/types";

// ---------------------------------------------------------------------------
// Status dot (replicates preset provider pattern)
// ---------------------------------------------------------------------------

function CustomStatusDot({ provider }: { provider: CustomProviderInfo }) {
  const { t } = useTranslation("dashboard");
  const ready = provider.base_url && provider.api_key_masked;
  const color = ready ? "bg-good" : "bg-text-4";
  const label = ready ? t("status_connected") : t("status_unconfigured");
  return <span className={`h-2 w-2 shrink-0 rounded-full ${color}`} role="img" aria-label={label} />;
}

// ---------------------------------------------------------------------------
// Sidebar section for custom providers
// ---------------------------------------------------------------------------

interface CustomProviderSectionProps {
  providers: CustomProviderInfo[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  onAdd: () => void;
}

export function CustomProviderSection({ providers, selectedId, onSelect, onAdd }: CustomProviderSectionProps) {
  const { t } = useTranslation("dashboard");
  return (
    <div>
      <div className="mb-3 flex items-center justify-between gap-3 px-2">
        <div className="text-[12.5px] font-semibold text-text-2">{t("custom_providers")}</div>
        <button
          type="button"
          onClick={onAdd}
          className="inline-flex h-7 items-center gap-1.5 rounded-[7px] border border-accent/30 bg-accent-dim px-2.5 text-[11.5px] font-medium text-accent-2 transition-colors hover:border-accent/50 hover:bg-accent-dim/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
        >
          <Plus className="h-3.5 w-3.5" aria-hidden="true" />
          <span>{t("add_custom_provider")}</span>
        </button>
      </div>
      <div className="space-y-1">
        {providers.map((p) => {
          const isActive = selectedId === p.id;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => onSelect(p.id)}
              aria-current={isActive ? "page" : undefined}
              aria-pressed={isActive}
              className={`group flex w-full items-center gap-2.5 rounded-[8px] border px-3 py-2.5 text-left text-[12.5px] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                isActive
                  ? "border-accent/35 bg-accent-dim text-text shadow-[inset_0_1px_0_oklch(1_0_0_/_0.04)]"
                  : "border-transparent text-text-3 hover:border-hairline-soft hover:bg-bg-grad-a/55 hover:text-text"
              }`}
            >
              {/* 自定义 provider 恒用字母徽章，不按 display_name 猜品牌：中转站协议无关，
                  打某品牌图标会名不副实，且自由文本名匹配对中文名割裂。将来若要品牌化，
                  走用户显式选图标，而非名字猜测。 */}
              <span className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-[5px] border border-hairline-soft bg-bg-grad-b/70 font-mono text-[10px] font-bold uppercase text-text-2">
                {Array.from(p.display_name)[0] ?? "?"}
              </span>
              <span className="min-w-0 flex-1 truncate">{p.display_name}</span>
              <CustomStatusDot provider={p} />
            </button>
          );
        })}
      </div>
    </div>
  );
}
