# SceneMixer 整站候选广域检索：主检索记录

核查时间：2026-11-06。此轮先发现仓库，再核其是否可作为 [SceneMixer](https://scenemixer.cn/) 整站复刻底座；不能把搜索命中数当成满足条件的项目数。GitHub Repository Search API 默认相关度、每组取前 30 条；统计会随索引变化。第 11–14 组触发 GitHub 搜索 API 速率限制，未计入样本；后续使用网页搜索和项目第一方文档补查。

| 原样检索式 | GitHub 命中总数 | 实取条数 |
| --- | ---: | ---: |
| `AI short drama` | 583 | 30 |
| `novel to video` | 253 | 30 |
| `AI filmmaking` | 498 | 30 |
| `AI video studio` | 5147 | 30 |
| `AI film production` | 447 | 30 |
| `AI storyboard generator` | 241 | 30 |
| `AI drama generator` | 80 | 30 |
| `3D previs AI video` | 11 | 11 |
| `AI video SaaS` | 1111 | 30 |
| `短剧 AI 视频` | 249 | 30 |

这 10 组共返回 **260 个去重仓库样本**（各组只取前排，组间重复；并非检索库全部）。样本含模型、模板、教程、作品集、单点工具和不相关项目。宽松初筛后发现此前报告漏掉的[连镜](https://github.com/zaylora/video-canvas)、[NovaNova Studio](https://github.com/Swayingleaves/novanova-studio)、[TapCanvas](https://github.com/anymouschina/TapCanvas)、[Huohuo Drama](https://github.com/appolloqin/huohuo-drama)、[Toonflow](https://github.com/HBAI-Ltd/Toonflow-app)等强相关项目。由此旧报告把影策直接排为唯一开源第一名的范围依据不足，必须重审。

第一方证据初看：连镜 [README](https://github.com/zaylora/video-canvas)有 Go 短剧工作室、3D 导演台、账户/积分/支付，但[短剧资产区源码](https://github.com/zaylora/video-canvas/blob/master/web/src/pages/drama/workspace/assets-area.tsx)显示短剧一期不含导演台；普通画布输出可转参考媒体，尚不能算自动同片场视频约束。Toonflow [README](https://github.com/HBAI-Ltd/Toonflow-app)有 3D 创作与多租户账务包，但[发布 UI](https://github.com/HBAI-Ltd/Toonflow-app/blob/master/apps/web/src/components/settings/panels/multiTenant/developmentNotice.vue)仍将多租户标为开发中，支付调用官方云接口，不能算自建支付闭环。TapCanvas [README](https://github.com/anymouschina/TapCanvas)明确社区版无短信验证码和在线支付。其余深入核验见同目录的国际、中文/Go 广域笔记。

此记录只证明本轮搜索范围与前排样本；不能推导全网只有这些项目，也不能把未实测源码等同已上线产品。
