import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { API } from "@/api";
import { FinalOutputsDialog } from "./FinalOutputsDialog";
import { useAppStore } from "@/stores/app-store";

describe("FinalOutputsDialog", () => {
  beforeEach(() => {
    useAppStore.setState(useAppStore.getInitialState(), true);
    vi.restoreAllMocks();
  });

  it("lists final outputs and loads the selected video preview", async () => {
    vi.spyOn(API, "listFinalOutputs").mockResolvedValue({
      outputs: [{ name: "第1集_final.mp4", size: 26_700_372 }],
    });
    vi.spyOn(API, "requestFinalOutputToken").mockResolvedValue({
      download_token: "preview-token",
      expires_in: 300,
    });

    render(<FinalOutputsDialog projectName="demo" onClose={vi.fn()} />);

    expect(await screen.findAllByText("25.5 MB")).toHaveLength(2);
    const video = await screen.findByLabelText("第1集_final.mp4 成片预览");
    expect(video).toHaveAttribute(
      "src",
      "/api/v1/projects/demo/final-outputs/%E7%AC%AC1%E9%9B%86_final.mp4?download_token=preview-token",
    );
  });

  it("requests a fresh token when downloading", async () => {
    vi.spyOn(API, "listFinalOutputs").mockResolvedValue({
      outputs: [{ name: "episode.mp4", size: 5 }],
    });
    const requestToken = vi
      .spyOn(API, "requestFinalOutputToken")
      .mockResolvedValueOnce({ download_token: "preview-token", expires_in: 300 })
      .mockResolvedValueOnce({ download_token: "download-token", expires_in: 300 });
    let downloadedUrl = "";
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      downloadedUrl = this.href;
    });

    render(<FinalOutputsDialog projectName="demo" onClose={vi.fn()} />);
    await screen.findByLabelText("episode.mp4 成片预览");
    fireEvent.click(screen.getByRole("button", { name: "下载成片" }));

    await waitFor(() => expect(requestToken).toHaveBeenCalledTimes(2));
    expect(downloadedUrl).toContain("download_token=download-token");
    expect(downloadedUrl).toContain("download=true");
  });

  it("shows an empty state when no final output exists", async () => {
    vi.spyOn(API, "listFinalOutputs").mockResolvedValue({ outputs: [] });
    const requestToken = vi.spyOn(API, "requestFinalOutputToken");

    render(<FinalOutputsDialog projectName="demo" onClose={vi.fn()} />);

    expect(await screen.findByText("还没有已合成的成片")).toBeInTheDocument();
    expect(requestToken).not.toHaveBeenCalled();
  });
});
