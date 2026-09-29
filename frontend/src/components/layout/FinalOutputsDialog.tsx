import { useEffect, useId, useState } from "react";
import { Download, Film, Loader2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { API } from "@/api";
import { GlassModal } from "@/components/ui/GlassModal";
import { ModalCloseButton } from "@/components/ui/ModalCloseButton";
import { PrimaryButton } from "@/components/ui/PrimaryButton";
import { useAppStore } from "@/stores/app-store";
import { errMsg } from "@/utils/async";

interface FinalOutput {
  name: string;
  size: number;
}

interface FinalOutputsDialogProps {
  projectName: string;
  onClose: () => void;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function triggerBrowserDownload(url: string) {
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.style.display = "none";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
}

export function FinalOutputsDialog({ projectName, onClose }: FinalOutputsDialogProps) {
  const { t } = useTranslation("dashboard");
  const titleId = useId();
  const descriptionId = useId();
  const [outputs, setOutputs] = useState<FinalOutput[]>([]);
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void API.listFinalOutputs(projectName)
      .then(({ outputs: nextOutputs }) => {
        if (cancelled) return;
        setOutputs(nextOutputs);
        setSelectedName(nextOutputs[0]?.name ?? null);
      })
      .catch((error) => {
        if (!cancelled) setLoadError(errMsg(error));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectName]);

  useEffect(() => {
    if (!selectedName) return;
    let cancelled = false;
    void API.requestFinalOutputToken(projectName, selectedName)
      .then(({ download_token }) => {
        if (cancelled) return;
        setPreviewUrl(API.getFinalOutputUrl(projectName, selectedName, download_token));
        setPreviewError(null);
      })
      .catch((error) => {
        if (!cancelled) setPreviewError(errMsg(error));
      });
    return () => {
      cancelled = true;
    };
  }, [projectName, selectedName]);

  const handleSelect = (name: string) => {
    setSelectedName(name);
    setPreviewUrl(null);
    setPreviewError(null);
  };

  const handleDownload = async () => {
    if (!selectedName || downloading) return;
    setDownloading(true);
    try {
      const { download_token } = await API.requestFinalOutputToken(projectName, selectedName);
      triggerBrowserDownload(
        API.getFinalOutputUrl(projectName, selectedName, download_token, true),
      );
    } catch (error) {
      useAppStore
        .getState()
        .pushNotification(
          t("final_output_download_failed", { message: errMsg(error) }),
          "error",
        );
    } finally {
      setDownloading(false);
    }
  };

  const selected = outputs.find((output) => output.name === selectedName) ?? null;

  return (
    <GlassModal
      open
      onClose={onClose}
      labelledBy={titleId}
      describedBy={descriptionId}
      widthClassName="w-full max-w-4xl"
      panelClassName="max-h-[88vh]"
    >
      <div
        className="flex items-start justify-between gap-4 px-6 py-5"
        style={{ borderBottom: "1px solid var(--color-hairline-soft)" }}
      >
        <div className="flex items-start gap-3">
          <span
            aria-hidden
            className="grid h-9 w-9 shrink-0 place-items-center rounded-xl"
            style={{
              background: "var(--color-accent-dim)",
              border: "1px solid var(--color-accent-soft)",
              color: "var(--color-accent-2)",
            }}
          >
            <Film className="h-4 w-4" />
          </span>
          <div>
            <h2
              id={titleId}
              className="display-serif text-[17px] font-semibold tracking-tight"
              style={{ color: "var(--color-text)" }}
            >
              {t("final_outputs")}
            </h2>
            <p
              id={descriptionId}
              className="mt-1 text-[12.5px] leading-[1.55]"
              style={{ color: "var(--color-text-3)" }}
            >
              {t("final_outputs_description")}
            </p>
          </div>
        </div>
        <ModalCloseButton onClick={onClose} />
      </div>

      <div className="grid min-h-[24rem] grid-cols-[15rem_minmax(0,1fr)] overflow-hidden">
        <div
          className="max-h-[70vh] overflow-y-auto p-3"
          style={{ borderRight: "1px solid var(--color-hairline-soft)" }}
        >
          {outputs.map((output) => (
            <button
              key={output.name}
              type="button"
              onClick={() => handleSelect(output.name)}
              aria-pressed={output.name === selectedName}
              className="focus-ring mb-2 w-full rounded-lg px-3 py-2.5 text-left"
              style={{
                background:
                  output.name === selectedName
                    ? "var(--color-accent-dim)"
                    : "oklch(0.16 0.010 265 / 0.45)",
                border:
                  output.name === selectedName
                    ? "1px solid var(--color-accent-soft)"
                    : "1px solid var(--color-hairline-soft)",
              }}
            >
              <span
                className="block truncate text-[12.5px] font-medium"
                style={{ color: "var(--color-text)" }}
              >
                {output.name}
              </span>
              <span className="num mt-1 block text-[10.5px]" style={{ color: "var(--color-text-4)" }}>
                {formatFileSize(output.size)}
              </span>
            </button>
          ))}
        </div>

        <div className="flex min-w-0 flex-col p-5">
          {loading ? (
            <div className="flex flex-1 items-center justify-center gap-2 text-[13px]" style={{ color: "var(--color-text-3)" }}>
              <Loader2 className="h-4 w-4 animate-spin" />
              {t("final_outputs_loading")}
            </div>
          ) : loadError ? (
            <div className="flex flex-1 items-center justify-center text-[13px]" style={{ color: "var(--color-danger)" }}>
              {t("final_output_load_failed", { message: loadError })}
            </div>
          ) : !selected ? (
            <div className="flex flex-1 items-center justify-center text-[13px]" style={{ color: "var(--color-text-3)" }}>
              {t("final_outputs_empty")}
            </div>
          ) : (
            <>
              <div className="min-h-0 flex-1 overflow-hidden rounded-xl bg-black">
                {previewUrl ? (
                  // eslint-disable-next-line jsx-a11y/media-has-caption -- compose-video 成片没有独立字幕轨可供播放器挂载
                  <video
                    key={previewUrl}
                    src={previewUrl}
                    controls
                    preload="metadata"
                    className="h-full max-h-[58vh] w-full object-contain"
                    aria-label={t("final_output_preview", { name: selected.name })}
                  />
                ) : (
                  <div className="flex h-full min-h-[18rem] items-center justify-center gap-2 text-[13px]" style={{ color: "var(--color-text-3)" }}>
                    {previewError ? (
                      t("final_output_preview_failed", { message: previewError })
                    ) : (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {t("presentation_loading")}
                      </>
                    )}
                  </div>
                )}
              </div>
              <div className="mt-4 flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <p className="truncate text-[13px] font-medium" style={{ color: "var(--color-text)" }}>
                    {selected.name}
                  </p>
                  <p className="num mt-0.5 text-[10.5px]" style={{ color: "var(--color-text-4)" }}>
                    {formatFileSize(selected.size)}
                  </p>
                </div>
                <PrimaryButton
                  size="sm"
                  onClick={() => void handleDownload()}
                  disabled={downloading}
                  leadingIcon={
                    downloading ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Download className="h-3.5 w-3.5" />
                    )
                  }
                >
                  {t("final_output_download")}
                </PrimaryButton>
              </div>
            </>
          )}
        </div>
      </div>
    </GlassModal>
  );
}
