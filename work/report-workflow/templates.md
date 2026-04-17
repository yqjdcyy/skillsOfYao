# Report Templates

Reference: `config/system.json` -> `paths.reportTemplatePath`

If `paths.reportTemplatePath` is missing, ask the user to provide the template path first.

## Daily Report

工时规则：未指定时当天总工时 8h，各需求平均；plan.md 大项后 `3h`、`1d` 等格式为指定工时，需带入。

场景标签：涉及 skywalking、SwAgent、国际化 → 国际场景；其它 → 国内。

链接：plan.md 中完成项含 URL 时，日报完成细项须保留为 Markdown 链接（如 `[描述](url)` 或 `描述（[链接](url)）`）， lucp 上线单用 `[Launch-xxx](https://lucp.lkcoffee.com/launch/Launch-xxx)`。

多层次：完成细项按 plan.md 层级输出，缩进体现父子。顶层环节为一级（4 空格），子项再缩进一层（8 空格），更深层继续缩进（12 空格…）。

```md
## 日报｜「日期，如2026-02-18」
### 「需求名称」
- 标签
    - 「环境：国内 / 国际场景（skywalking、SwAgent、国际化相关）」
    - 「模块，如排障、架构、AI探索、优化、答疑、其它」
- 进度
    - 「进度说明，如 0%-> 30%； 其中可按阶段 设计-开发-联调-测试-上线 规划大致进度 20%-50%-60%-80%-100%」
- 工时
    - 「默认：8h/N（N=当日需求数）；指定：如 3h、1d」
- 完成细项
    - 「环节，如方案设计、功能开发、回归测试、功能上线」
        - 「环节下的子项1」
        - 「环节下的子项2」
            - 「子项2下的更深层细项（按 plan.md 层级递归）」
```

Multiple demands per day: repeat the `### 需求名称` block for each.

## Weekly Report

按工作项聚合日报需求；进度列为百分比或「x% → y%」；备注列为要点（可多行用 <br>，子项用 &nbsp;&nbsp;• ）。内容须完整可展示，不得使用「见日报」等引用。工作项名称可按对外汇报习惯合并（如 排障订阅能力增强→故障订阅能力建设、处置能力建设→故障处置能力建设）。

```md
## 周报｜「周期，如 2026-02-27～2026-03-05」

{reportWorkflow.authorName} 「YYYY.MM.DD-YYYY.MM.DD」 工作周报

| 工作项 | 进度 | 备注 |
| :--- | :--- | :--- |
| 「工作项名称1」 | 「x% → y%」或「当前%」 | - 「阶段/状态，如 待联调、功能开发中」<br>- 完成细项：<br>  &nbsp;&nbsp;• 「细项1」<br>  &nbsp;&nbsp;• 「细项2」 |
| 「工作项名称2」 | 「x% → y%」 | - 「要点」<br>- 「要点」 |
| 答疑 | - | - 「本周答疑概况或具体事项」 |
| 其它 | - | - 「双周会、探索项等」 |
```

## Monthly Report

月报内容须完整可展示，不得使用引用形式。OKR 表同一 O 下多行 KR 时，O 列首行填完、后续行留空；上线表同一服务多版本时，服务名称首行填、后续行留空。

```md
## 月报｜「月份，如 2026-02」

### 「组员」-「YYYY.MM」 工作复盘 ({reportWorkflow.reviewGroup})

#### 一、OKR

| **Current.O（子目标）** | KR（关键工作项） | 进度 | **备注** |
|-------------------------|------------------|------|----------|
| O：「O 描述」 | 「KR 描述，可多行用 <br>」 | 「进度，如 33%→66%」 | 「补充说明，多条用 <br> 分隔；未涉及则略过」 |
| | 「同一 O 下第二项 KR 时，O 列留空」 | | |

#### 二、其他有意义的或重要工作项
- 「工作事项」

#### 三、本月上线、发版本（二方包、launch等）

| 服务名称 | 版本 | 功能描述 | 线上变更 |
|----------|------|----------|----------|
| 「服务名称」 | 「版本号」 | 「功能概述」 | [Launch-xxx](https://lucp.lkcoffee.com/launch/Launch-xxx) |
| | 「同服务多版本时，服务名列留空」 | | |

#### 四、本月事故、事件情况
- 无

#### 五、本月主要完成的文档情况
- 「文档列表」

#### 六、总结、经验、成长、收获等
- 「总结内容」
```

## Shoot-Weekly (Troubleshooting Iteration)

```md
### 「迭代方向，如触发能力、分析能力、生命周期管理、其它」
- 「包含整体进度说明、关键细节项」
    - 「按需求的大小，按需补充拆分细节项」
    - 「按需补充相关设计文档、跟进文档及更多说明细节」
```

Extract from daily reports within the time range, group by iteration direction, summarize progress and details.
