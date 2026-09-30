import { render, screen, waitFor, within, act, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { Router } from "wouter";
import { memoryLocation } from "wouter/memory-location";
import i18n from "@/i18n";
import { API } from "@/api";
import { useAppStore } from "@/stores/app-store";
import { useConfigStatusStore } from "@/stores/config-status-store";
import { useEndpointCatalogStore } from "@/stores/endpoint-catalog-store";
import { ProviderSection } from "./ProviderSection";
import type { ProviderInfo, CustomProviderInfo, EndpointDescriptor } from "@/types";

function renderAt(path = "/app/settings?custom=1") {
  const location = memoryLocation({ path, record: true });
  return {
    ...render(
      <Router hook={location.hook} searchHook={location.searchHook}>
        <ProviderSection />
      </Router>,
    ),
    location,
  };
}

// 后端按 Accept-Language 成文供应商与模型名，这里用替身按当前语言返回对应译名。
function providersFor(lang: string): { providers: ProviderInfo[] } {
  return {
    providers: [
      {
        id: "gemini-aistudio",
        display_name: lang === "en" ? "Gemini AI Studio (EN)" : "Gemini AI Studio（中文）",
        description: "",
        status: "ready",
        media_types: ["video"],
        capabilities: [],
        configured_keys: [],
        missing_keys: [],
        models: {},
      },
    ],
  };
}

// 自定义供应商名是用户数据、真实场景不随语言变化；这里让替身按语言分叉，
// 只为让「custom 列表随语言一起重取」可被 DOM 断言观察到。
function customFor(lang: string): { providers: CustomProviderInfo[] } {
  return {
    providers: [
      {
        id: 1,
        display_name: lang === "en" ? "My Endpoint (EN)" : "我的端点（中文）",
        discovery_format: "openai",
        base_url: "https://example.invalid",
        api_key_masked: "sk-***",
        models: [],
        created_at: "2026-01-01T00:00:00Z",
        image_max_workers: null,
        video_max_workers: null,
        audio_max_workers: null,
      },
    ],
  };
}

const CHAT_ENDPOINT: EndpointDescriptor = {
  key: "openai-chat",
  media_type: "text",
  family: "openai",
  kind: "python",
  source: "builtin",
  display_name_key: "endpoint_openai_chat",
  display_name: null,
  request_method: "POST",
  request_path_template: "/v1/chat/completions",
  image_capabilities: null,
  end_image_capable: false,
  size_fixed: false,
  duration_fixed: false,
  duration_frame_rate_missing: false,
  duration_tier_empty: false,
  native_resolution: null,
};

function customProvider(id: number, displayName: string): CustomProviderInfo {
  return {
    id,
    display_name: displayName,
    discovery_format: "openai",
    base_url: "https://example.invalid",
    api_key_masked: "sk-***",
    models: [],
    created_at: "2026-01-01T00:00:00Z",
    image_max_workers: null,
    video_max_workers: null,
    audio_max_workers: null,
  };
}

/** 在「新建自定义供应商」表单里填满必填项并保存。 */
function saveNewCustomProvider() {
  fireEvent.change(screen.getByLabelText(/名称/), { target: { value: "我的中转站" } });
  fireEvent.change(screen.getByLabelText(/Base URL/), { target: { value: "https://api.example.invalid" } });
  fireEvent.change(screen.getByLabelText(/API Key/), { target: { value: "sk-live" } });
  fireEvent.click(screen.getByRole("button", { name: "手动添加模型" }));
  fireEvent.change(screen.getByRole("textbox", { name: "模型 ID" }), { target: { value: "gpt-4o" } });
  fireEvent.click(screen.getByRole("button", { name: "保存" }));
}

describe("ProviderSection", () => {
  beforeEach(() => {
    useAppStore.setState(useAppStore.getInitialState(), true);
    useConfigStatusStore.setState(useConfigStatusStore.getInitialState(), true);
    vi.spyOn(useConfigStatusStore.getState(), "refresh").mockResolvedValue();
    vi.spyOn(API, "getProviders").mockImplementation(() =>
      Promise.resolve(providersFor(i18n.language)),
    );
    vi.spyOn(API, "listCustomProviders").mockImplementation(() =>
      Promise.resolve(customFor(i18n.language)),
    );
    vi.spyOn(API, "getCustomProvider").mockResolvedValue(customProvider(1, "我的端点（中文）"));
    vi.spyOn(API, "getProviderConfig").mockRejectedValue(new Error("detail not under test"));
    vi.spyOn(API, "listCredentials").mockResolvedValue({ credentials: [] });
    vi.spyOn(API, "patchProviderConfig").mockResolvedValue();
  });

  afterEach(async () => {
    await act(async () => {
      await i18n.changeLanguage("zh");
    });
    vi.restoreAllMocks();
  });

  it("refetches the provider catalog when the interface language changes", async () => {
    renderAt();

    const nav = () => screen.getByRole("navigation");
    await screen.findByRole("navigation");
    expect(within(nav()).getByText("我的端点（中文）")).toBeInTheDocument();
    expect(within(nav()).queryByText("Gemini AI Studio（中文）")).not.toBeInTheDocument();

    await act(async () => {
      await i18n.changeLanguage("en");
    });

    // 切换语言后目录须按新语言重取，否则停留在切换前的译名
    await waitFor(() =>
      expect(within(nav()).getByText("My Endpoint (EN)")).toBeInTheDocument(),
    );
    expect(within(nav()).queryByText("我的端点（中文）")).not.toBeInTheDocument();
  });

  it("keeps the catalog rendered while the language-triggered refetch is in flight", async () => {
    let releaseRefetch: (() => void) | null = null;
    vi.spyOn(API, "getProviders").mockImplementation(() => {
      const lang = i18n.language;
      if (lang !== "en") return Promise.resolve(providersFor(lang));
      return new Promise((resolve) => {
        releaseRefetch = () => resolve(providersFor(lang));
      });
    });

    renderAt();
    await screen.findByRole("navigation");

    await act(async () => {
      await i18n.changeLanguage("en");
    });

    // 语言切换是静默刷新：不回到 loading 面板，详情面板不被卸载
    expect(screen.queryByText(/加载供应商列表|Loading providers/)).not.toBeInTheDocument();
    expect(
      within(screen.getByRole("navigation")).getByText("我的端点（中文）"),
    ).toBeInTheDocument();

    await act(async () => {
      releaseRefetch?.();
      await Promise.resolve();
    });
    await waitFor(() =>
      expect(
        within(screen.getByRole("navigation")).getByText("My Endpoint (EN)"),
      ).toBeInTheDocument(),
    );
  });

  it("keeps the previous catalog when a language-triggered refetch fails", async () => {
    vi.spyOn(API, "getProviders").mockImplementation(() => {
      const lang = i18n.language;
      if (lang !== "en") return Promise.resolve(providersFor(lang));
      return Promise.reject(new Error("network down"));
    });

    renderAt();
    await screen.findByRole("navigation");

    await act(async () => {
      await i18n.changeLanguage("en");
    });

    // 静默刷新失败不得把整个小节换成错误面板：那会卸载详情面板、丢掉未保存的表单输入
    await waitFor(() =>
      expect(
        within(screen.getByRole("navigation")).getByText("我的端点（中文）"),
      ).toBeInTheDocument(),
    );
    expect(screen.queryByText("network down")).not.toBeInTheDocument();
  });

  it("surfaces the error when the language switches before any catalog has loaded", async () => {
    vi.spyOn(API, "getProviders").mockImplementation(() => {
      // 首次（中文）拉取永不落定：语言切换发生在它返回之前
      if (i18n.language !== "en") return new Promise<never>(() => {});
      return Promise.reject(new Error("network down"));
    });

    renderAt();

    // 首次拉取尚未返回就切语言：没有可留的目录，失败必须走错误面板而非留下空列表
    await act(async () => {
      await i18n.changeLanguage("en");
    });

    await screen.findByText("network down");
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("shows only custom providers and selects the first one when the URL names no selection", async () => {
    const { location } = renderAt("/app/settings");
    const nav = await screen.findByRole("navigation");

    expect(within(nav).queryByText("Gemini AI Studio（中文）")).not.toBeInTheDocument();
    await waitFor(() =>
      expect(within(nav).getByText("我的端点（中文）").closest('[aria-current="page"]')).not.toBeNull(),
    );
    // replace 写回：历史里只剩替换后的一条，不追加
    expect(location.history).toEqual(["/app/settings?custom=1"]);
  });
  it("selects the newly created custom provider after the form saves", async () => {
    useEndpointCatalogStore.setState(useEndpointCatalogStore.getInitialState(), true);
    vi.spyOn(API, "listEndpointCatalog").mockResolvedValue({ endpoints: [CHAT_ENDPOINT] });
    vi.spyOn(API, "getCustomProvider").mockResolvedValue(customProvider(2, "我的中转站"));
    vi.spyOn(API, "createCustomProvider").mockResolvedValue(customProvider(2, "我的中转站"));
    vi.mocked(API.listCustomProviders)
      .mockReset()
      .mockResolvedValueOnce({ providers: [customProvider(1, "旧端点")] })
      .mockResolvedValue({ providers: [customProvider(1, "旧端点"), customProvider(2, "我的中转站")] });

    const { location } = renderAt("/app/settings?custom=new");
    await screen.findByRole("button", { name: "保存" });

    saveNewCustomProvider();

    // 保存后须切到刚建好的那一项，否则用户停在填满的表单上，再保存一次就多出一个重复供应商
    await waitFor(() => expect(location.history.at(-1)).toBe("/app/settings?custom=2"));
    await waitFor(() => expect(API.getCustomProvider).toHaveBeenCalledWith(2));
  });

  it("still selects the created provider when the catalog refresh fails", async () => {
    useEndpointCatalogStore.setState(useEndpointCatalogStore.getInitialState(), true);
    vi.spyOn(API, "listEndpointCatalog").mockResolvedValue({ endpoints: [CHAT_ENDPOINT] });
    vi.spyOn(API, "getCustomProvider").mockResolvedValue(customProvider(2, "我的中转站"));
    vi.spyOn(API, "createCustomProvider").mockResolvedValue(customProvider(2, "我的中转站"));
    vi.mocked(API.listCustomProviders)
      .mockReset()
      .mockResolvedValueOnce({ providers: [customProvider(1, "旧端点")] })
      .mockRejectedValue(new Error("network down"));

    const { location } = renderAt("/app/settings?custom=new");
    await screen.findByRole("button", { name: "保存" });

    saveNewCustomProvider();

    // 选中来自新建响应，与目录重取的结局无关；刷新失败另行告警。
    await waitFor(() => expect(location.history.at(-1)).toBe("/app/settings?custom=2"));
    await waitFor(() =>
      expect(useAppStore.getState().toast).toMatchObject({
        text: "已保存，但供应商列表刷新失败，请重新加载页面",
        tone: "warning",
      }),
    );
  });
});
