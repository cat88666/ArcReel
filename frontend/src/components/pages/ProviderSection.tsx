import { useEffect, useMemo, useCallback } from "react";
import { useLocation, useSearch } from "wouter";
import { Loader2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useProviderCatalog } from "@/hooks/useProviderCatalog";
import type { CatalogRefreshResult } from "@/hooks/useProviderCatalog";
import { useAppStore } from "@/stores/app-store";
import { CustomProviderSection } from "./settings/CustomProviderSection";
import { CustomProviderDetail } from "./settings/CustomProviderDetail";
import { CustomProviderForm } from "./settings/CustomProviderForm";

// ---------------------------------------------------------------------------
// Provider Section
// ---------------------------------------------------------------------------

type Selection =
  | { kind: "custom"; id: number }
  | { kind: "new-custom" }
  | null;

export function ProviderSection() {
  const { t, i18n } = useTranslation(["dashboard", "common"]);
  const { customProviders, loading, error: loadError, reload, refresh } = useProviderCatalog(i18n.language);
  const [location, navigate] = useLocation();
  const search = useSearch();

  const selection: Selection = useMemo(() => {
    const params = new URLSearchParams(search);
    const custom = params.get("custom");
    if (custom === "new") return { kind: "new-custom" };
    if (custom) {
      const id = parseInt(custom, 10);
      if (!isNaN(id)) return { kind: "custom", id };
    }
    return null;
  }, [search]);
  const modelId = new URLSearchParams(search).get("model") ?? undefined;

  // 保存本身已成功，只是目录重取失败：与「保存失败」区分开，否则用户看到表单无错、列表无新项，
  // 分不清是哪一步没成。被后续请求作废（aborted）是正常并发路径，接管方会写下更新的目录。
  const pushToast = useAppStore((s) => s.pushToast);
  const notifyRefreshFailure = useCallback(
    (result: CatalogRefreshResult) => {
      if (result.status === "failed") pushToast(t("provider_saved_refresh_failed"), "warning");
    },
    [pushToast, t],
  );
  const refreshAfterSave = useCallback(() => {
    void refresh().then(notifyRefreshFailure);
  }, [refresh, notifyRefreshFailure]);

  const setSelection = useCallback(
    (sel: Selection) => {
      const p = new URLSearchParams(search);
      p.delete("provider");
      p.delete("custom");
      p.delete("model");
      if (sel?.kind === "custom") p.set("custom", String(sel.id));
      else if (sel?.kind === "new-custom") p.set("custom", "new");
      navigate(`${location}?${p.toString()}`, { replace: true });
    },
    [search, location, navigate],
  );

  // 从「调用端点」小节的「新建供应商并使用此端点」接线过来的预填。
  const prefill = useMemo(() => {
    const params = new URLSearchParams(search);
    return {
      baseUrl: params.get("base_url") ?? undefined,
      endpoint: params.get("endpoint") ?? undefined,
    };
  }, [search]);

  // 拉取完成后 URL 仍未指定选中项时，默认打开首个自定义供应商。
  useEffect(() => {
    if (loading || selection || customProviders.length === 0) return;
    setSelection({ kind: "custom", id: customProviders[0].id });
  }, [loading, selection, customProviders, setSelection]);

  if (loadError) {
    return (
      <div role="alert" className="flex flex-col items-start gap-2.5 px-6 py-8">
        <span className="inline-flex items-center gap-1.5 font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-warm">
          {t("common:load_failed")}
        </span>
        <p className="text-[12.5px] text-text-2">{loadError}</p>
        <button
          type="button"
          onClick={reload}
          className="rounded-[7px] border border-hairline-soft bg-bg-grad-a/55 px-3 py-1.5 text-[12px] text-text-2 transition-colors hover:border-hairline hover:text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
        >
          {t("common:retry")}
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-6 py-8 text-text-3">
        <Loader2 className="h-3.5 w-3.5 motion-safe:animate-spin text-accent-2" aria-hidden />
        <span className="font-mono text-[11px] uppercase tracking-[0.14em]">
          {t("loading_providers")}
        </span>
      </div>
    );
  }

  return (
    <div className="flex min-h-full flex-col lg:flex-row">
      {/* Provider list sidebar */}
      <nav
        aria-label={t("provider_list")}
        className="w-full shrink-0 overflow-y-auto border-b border-hairline-soft px-3 py-4 lg:sticky lg:top-0 lg:max-h-screen lg:w-64 lg:self-start lg:border-b-0 lg:border-r lg:py-5"
        style={{ background: "oklch(0.16 0.010 265 / 0.45)" }}
      >
        <CustomProviderSection
          providers={customProviders}
          selectedId={selection?.kind === "custom" ? selection.id : null}
          onSelect={(id) => setSelection({ kind: "custom", id })}
          onAdd={() => setSelection({ kind: "new-custom" })}
        />
      </nav>

      {/* Detail panel */}
      <div className="min-w-0 flex-1">
        {selection?.kind === "custom" && (
          <CustomProviderDetail
            providerId={selection.id}
            initialModelId={modelId}
            onDeleted={() => {
              void refresh();
              const nextProvider = customProviders.find((provider) => provider.id !== selection.id);
              if (nextProvider) {
                setSelection({ kind: "custom", id: nextProvider.id });
              } else {
                setSelection(null);
              }
            }}
            onSaved={refreshAfterSave}
          />
        )}
        {selection?.kind === "new-custom" && (
          <CustomProviderForm
            initialBaseUrl={prefill.baseUrl}
            initialEndpoint={prefill.endpoint}
            onSaved={(created) => {
              // 选中用新建响应带回的 id，不等目录重取的结局：重取被后续请求接管时，
              // 用户会留在填满的新建表单上，再保存一次就多出一个重复供应商。
              if (created) setSelection({ kind: "custom", id: created.id });
              refreshAfterSave();
            }}
            onCancel={() => {
              if (customProviders.length > 0) {
                setSelection({ kind: "custom", id: customProviders[0].id });
              } else {
                setSelection(null);
              }
            }}
          />
        )}
        {!selection && (
          <div className="p-6 text-[12.5px] text-text-3">{t("select_provider")}</div>
        )}
      </div>
    </div>
  );
}
