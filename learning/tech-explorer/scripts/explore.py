#!/usr/bin/env python3
import argparse
import json
import os
import re
import ssl
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
REPORTS_DIR = ROOT / "output" / "reports"


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def has_text(value: str) -> bool:
    return bool(value and value.strip())


def clean_text(value: str) -> str:
    return value.strip() if value else ""


def count_chinese_chars(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text or ""))


def should_keep_chinese_excerpt(text: str) -> bool:
    normalized = clean_text(text)
    if not normalized:
        return False
    chinese_count = count_chinese_chars(normalized)
    return chinese_count >= 80


def join_sections(sections: list) -> str:
    return "\n\n---\n\n".join([section for section in sections if section])


def prompt_text(prompt: str, required: bool = False) -> str:
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("输入不能为空，请重试。")


def prompt_menu(title: str, options: list, allow_multiple: bool = False) -> list:
    normalized = [item for item in options if item]
    if not normalized:
        return []

    while True:
        print(f"=== {title} ===")
        for idx, item in enumerate(normalized, start=1):
            print(f"{idx}. {item}")

        guide = "请输入编号"
        if allow_multiple:
            guide += "（可用英文逗号分隔多选）"
        guide += "，直接回车默认选择第 1 项："
        raw = input(f"{guide}\n> ").strip()
        if not raw:
            return [normalized[0]]

        tokens = [item.strip() for item in raw.split(",") if item.strip()]
        try:
            indexes = [int(item) for item in tokens]
        except ValueError:
            print("输入格式不正确，请输入编号。")
            continue

        if not allow_multiple and len(indexes) > 1:
            print("当前仅支持单选，请重新输入。")
            continue

        if any(index < 1 or index > len(normalized) for index in indexes):
            print("编号超出范围，请重新输入。")
            continue

        return [normalized[index - 1] for index in indexes]


def jina_read(url: str, prefix: str, limit: int = 12000) -> str:
    target = prefix.rstrip("/") + "/" + url
    req = urllib.request.Request(target, headers={"User-Agent": "tech-explorer/1.1"})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=90, context=context) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    return body[:limit]


def infer_source_type(url: str) -> str:
    lower_url = (url or "").lower()
    if "github.com" in lower_url:
        return "官方仓库"
    if "arxiv.org" in lower_url or "doi.org" in lower_url or "acm.org" in lower_url or "ieee.org" in lower_url:
        return "论文/预印本"
    if "spec" in lower_url or "rfc" in lower_url or "standard" in lower_url:
        return "标准/规范"
    if "blog" in lower_url or "engineering" in lower_url:
        return "官方博客/工程文章"
    return "官方文档"


def infer_source_authority(source_type: str) -> str:
    if source_type in {"官方文档", "官方仓库", "标准/规范"}:
        return "A"
    if source_type in {"论文/预印本", "官方博客/工程文章"}:
        return "B"
    return "C"


def infer_source_role(source_type: str) -> str:
    mapping = {
        "官方文档": "定义、能力边界与使用方式",
        "官方仓库": "实现结构、接口与示例",
        "标准/规范": "对象模型、协议约束与兼容边界",
        "论文/预印本": "研究背景、方法论与实验结论",
        "官方博客/工程文章": "案例、设计动机与工程实践",
    }
    return mapping.get(source_type, "补充说明")


def infer_source_name(url: str, source_type: str) -> str:
    normalized = clean_text(url)
    if not normalized:
        return source_type
    host = normalized.replace("https://", "").replace("http://", "").split("/")[0]
    return f"{source_type} ({host})"


def dedupe_sources(candidates: list) -> list:
    seen = set()
    results = []
    for candidate in candidates:
        url = clean_text(candidate.get("url", ""))
        if not url or url in seen:
            continue
        seen.add(url)
        results.append(candidate)
    return results


def build_source_candidates(doc_url: str, github_url: str, tech_entry: dict, extra_urls: list) -> list:
    candidates = []
    if has_text(doc_url):
        candidates.append(
            {
                "name": "官方文档",
                "url": doc_url,
                "type": "官方文档",
                "authority": "A",
                "role": "定义、能力边界与基础用法",
            }
        )
    if has_text(github_url):
        candidates.append(
            {
                "name": "官方仓库",
                "url": github_url,
                "type": "官方仓库",
                "authority": "A",
                "role": "实现结构、接口定义与示例入口",
            }
        )

    for item in (tech_entry or {}).get("sources", []):
        source_type = item.get("type") or infer_source_type(item.get("url", ""))
        candidates.append(
            {
                "name": item.get("name") or infer_source_name(item.get("url", ""), source_type),
                "url": item.get("url", ""),
                "type": source_type,
                "authority": item.get("authority") or infer_source_authority(source_type),
                "role": item.get("role") or infer_source_role(source_type),
            }
        )

    for url in extra_urls:
        source_type = infer_source_type(url)
        candidates.append(
            {
                "name": infer_source_name(url, source_type),
                "url": url,
                "type": source_type,
                "authority": infer_source_authority(source_type),
                "role": infer_source_role(source_type),
            }
        )
    return dedupe_sources(candidates)


def normalize_source_excerpt(text: str, limit: int = 220) -> str:
    normalized = clean_text(re.sub(r"\s+", " ", text or ""))
    if len(normalized) > limit:
        return normalized[: limit - 1] + "…"
    return normalized


def fetch_sources(source_candidates: list, prefix: str) -> list:
    records = []
    for candidate in source_candidates:
        body = ""
        error = ""
        try:
            body = jina_read(candidate["url"], prefix, limit=5000)
        except Exception as exc:
            error = str(exc)
        records.append(
            {
                **candidate,
                "body": body,
                "status": "成功" if has_text(body) else "失败",
                "excerpt": normalize_source_excerpt(body),
                "error": error,
            }
        )
    return records


def extract_tags(text: str, catalog) -> list:
    tags = []
    for item in catalog:
        tag = item["tag"]
        if tag and tag in text:
            tags.append(tag)
    return sorted(set(tags))


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def match_kb(new_tags: set, technologies: list, threshold: float):
    rows = []
    for tech in technologies:
        score = jaccard(new_tags, set(tech.get("tags", [])))
        shared = sorted(new_tags & set(tech.get("tags", [])))
        if score >= threshold:
            rows.append((score, tech, shared))
    rows.sort(key=lambda x: x[0], reverse=True)
    return rows


def slug(s: str) -> str:
    return re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "_", s).strip("_")[:80] or "tech"


def resolve_name(args_name: str, confirm_cfg: dict, technologies: list, interactive: bool) -> str:
    if args_name:
        return args_name.strip()
    if not interactive:
        raise ValueError("未提供技术名称。请传入 name，或取消 --yes 后使用交互模式。")

    preset_names = confirm_cfg.get("preset_technologies") or [tech["name"] for tech in technologies[:6]]
    choice = prompt_menu("请选择要探索的技术", preset_names)[0]
    if choice == "手动输入":
        return prompt_text("请输入技术名称：", required=True)
    return choice


def build_round2_options(confirm_cfg: dict, matches: list) -> list:
    options = []
    for item in confirm_cfg["round2"].get("preset_options", []):
        if item == "对比 Top1":
            if matches:
                options.append(f"对比 {matches[0][1]['name']}")
            continue
        if item == "对比 Top2":
            if len(matches) >= 2:
                options.append(f"对比 {matches[1][1]['name']}")
            continue
        options.append(item)
    return options


def resolve_compare_names(args_compare: str, matches: list, confirm_cfg: dict, interactive: bool) -> list:
    compare_names = [item.strip() for item in args_compare.split(",") if item.strip()]
    if compare_names or not interactive:
        return compare_names

    options = build_round2_options(confirm_cfg, matches)
    if not options:
        return []

    choice = prompt_menu(confirm_cfg["round2"]["title"], options)[0]
    if choice == "全部对比":
        return [tech["name"] for _, tech, _ in matches]
    if choice == "继续探索":
        return []
    if choice == "手动输入":
        manual = prompt_text("请输入要对比的技术名，多个用英文逗号分隔：")
        return [item.strip() for item in manual.split(",") if item.strip()]
    if choice.startswith("对比 "):
        return [choice.replace("对比 ", "", 1).strip()]
    return []


def run_round1(name: str, intro: str, confirm_cfg: dict, interactive: bool) -> str:
    if not interactive:
        return intro

    print("===", confirm_cfg["round1"]["title"], "===")
    print("技术名称:", name)
    print("摘要预览:\n", intro[:500])
    print(confirm_cfg["round1"]["prompt"])
    options = confirm_cfg["round1"].get("preset_options") or confirm_cfg["round1"]["valid_replies"]
    choice = prompt_menu(confirm_cfg["round1"]["title"], options)[0]
    if choice == "不是":
        raise ValueError("已中止。请修正信息后重试。")
    if choice in {"补充", "手动输入"}:
        extra = prompt_text("请输入补充说明：")
        if extra:
            return f"{intro}\n\n用户补充：{extra}"
    return intro


def print_match_preview(matches: list):
    if not matches:
        print("- 暂无达到阈值的匹配结果")
        return
    for score, tech, shared in matches:
        print(f"- {tech['name']}: {int(round(score * 100))}%  shared={','.join(shared) or '—'}")


def build_tech_lookup(technologies: list) -> dict:
    return {tech["name"].strip().lower(): tech for tech in technologies if tech.get("name")}


def get_tech_entry(name: str, tech_lookup: dict):
    return tech_lookup.get(name.strip().lower()) if name else None


def build_default_architecture(name: str, tags: list, summary: str) -> dict:
    tag_set = set(tags)
    lower_name = name.lower()

    if "harness engineering" in lower_name or {"验证", "测试框架"} & tag_set:
        return {
            "view": "验证治理驱动逻辑分层",
            "layers": [
                {"name": "场景定义层", "responsibility": "定义任务、样例、评测目标与验收口径"},
                {"name": "编排执行层", "responsibility": "驱动 Agent、工具、流程与回放执行"},
                {"name": "观测评测层", "responsibility": "采集日志、轨迹、指标并生成评分"},
                {"name": "治理闭环层", "responsibility": "沉淀规范、基线、反馈与持续优化"},
            ],
            "physical_view": "Case / Dataset -> Harness Runtime -> Agent / Toolchain -> Metrics / Eval / Governance",
            "control_point": "评测口径与执行编排",
            "integration_surface": "Agent 运行时、工具链、数据集、观测系统",
            "boundary": "关注可复现、可度量、可治理，不替代底层协议或模型本体",
            "difference_marker": "验证治理主导",
        }

    if {"协议", "标准化", "API"} & tag_set:
        return {
            "view": "协议驱动逻辑分层",
            "layers": [
                {"name": "协议定义层", "responsibility": "定义对象模型、接口与兼容边界"},
                {"name": "客户端适配层", "responsibility": "在宿主侧发起请求、管理连接与会话"},
                {"name": "服务暴露层", "responsibility": "把工具、资源、数据源封装成统一能力"},
                {"name": "安全治理层", "responsibility": "负责权限、审计、隔离与生命周期"},
            ],
            "physical_view": "Host / Client -> Protocol Channel -> Server -> Tool / Data System",
            "control_point": "协议兼容性与接口抽象",
            "integration_surface": "工具、资源、外部系统接口",
            "boundary": "强调标准化接入，不直接承担复杂任务规划",
            "difference_marker": "协议标准化主导",
        }

    if {"大模型", "生成式 AI", "推理"} & tag_set:
        return {
            "view": "模型能力驱动逻辑分层",
            "layers": [
                {"name": "输入控制层", "responsibility": "处理提示词、上下文、检索增强与约束"},
                {"name": "推理生成层", "responsibility": "完成理解、推理、生成与采样"},
                {"name": "后处理层", "responsibility": "做格式约束、校验与安全过滤"},
                {"name": "服务封装层", "responsibility": "向上游系统暴露 API 或应用能力"},
            ],
            "physical_view": "App / API Gateway -> Prompt / Retrieval -> Model Serving -> Guardrail / Post-process",
            "control_point": "模型推理链路与上下文控制",
            "integration_surface": "检索系统、模型服务、后处理能力",
            "boundary": "偏模型能力供给，不天然包含任务自治和多步编排",
            "difference_marker": "模型能力主导",
        }

    if {"AI IDE", "编程助手", "编辑器"} & tag_set:
        return {
            "view": "工作台集成驱动逻辑分层",
            "layers": [
                {"name": "开发交互层", "responsibility": "承载编辑器、面板、命令与用户操作入口"},
                {"name": "智能助手层", "responsibility": "处理补全、问答、修改建议与任务触发"},
                {"name": "工具执行层", "responsibility": "连接终端、代码搜索、诊断与外部能力"},
                {"name": "工作区同步层", "responsibility": "管理文件、上下文、状态与协作信息"},
            ],
            "physical_view": "IDE UI -> Assistant Runtime -> Local / Remote Tools -> Workspace / Repo",
            "control_point": "开发者工作流与 IDE 内嵌体验",
            "integration_surface": "编辑器能力、终端、代码库、外部工具",
            "boundary": "偏开发工作台，不是底层协议标准本身",
            "difference_marker": "工作台集成主导",
        }

    if {"多智能体", "多 Agent 协作", "协作"} & tag_set:
        return {
            "view": "协同调度驱动逻辑分层",
            "layers": [
                {"name": "任务拆解层", "responsibility": "定义角色、目标与任务切分"},
                {"name": "协同调度层", "responsibility": "路由消息、分发子任务与控制依赖"},
                {"name": "角色执行层", "responsibility": "由多个 Agent 执行专属职责"},
                {"name": "共享状态层", "responsibility": "同步上下文、结果聚合与冲突处理"},
            ],
            "physical_view": "Coordinator -> Worker Agents -> Shared Memory / Bus -> Result Aggregation",
            "control_point": "角色划分与调度策略",
            "integration_surface": "多个 Agent、共享状态、消息通道",
            "boundary": "强调协作机制，单 Agent 内部能力不是核心重点",
            "difference_marker": "协同调度主导",
        }

    if {"智能体", "规划", "执行", "多步任务"} & tag_set:
        return {
            "view": "任务自治驱动逻辑分层",
            "layers": [
                {"name": "目标理解层", "responsibility": "解释意图、约束与可用上下文"},
                {"name": "规划决策层", "responsibility": "拆解任务、选择策略、决定下一步"},
                {"name": "执行工具层", "responsibility": "调用工具、读写环境并执行动作"},
                {"name": "记忆反馈层", "responsibility": "沉淀状态、观察结果并迭代修正"},
            ],
            "physical_view": "User Goal -> Planner -> Tool Executor -> Memory / Observation",
            "control_point": "规划-执行反馈闭环",
            "integration_surface": "工具、环境、记忆、外部观察源",
            "boundary": "强调自治执行，不等同于协议标准化或 IDE 宿主",
            "difference_marker": "任务编排主导",
        }

    return {
        "view": "通用集成逻辑分层",
        "layers": [
            {"name": "接入层", "responsibility": "提供统一入口与外部交互接口"},
            {"name": "核心处理层", "responsibility": "承载核心能力、路由与业务决策"},
            {"name": "集成扩展层", "responsibility": "连接外部工具、服务与数据源"},
            {"name": "治理保障层", "responsibility": "处理安全、监控、审计与运维要求"},
        ],
        "physical_view": "Client -> Core Runtime -> Integration Adapters -> External Systems",
        "control_point": "核心运行时与外部集成边界",
        "integration_surface": "外部服务与适配器",
        "boundary": "缺少更明确标签时按通用集成架构理解",
        "difference_marker": "集成封装主导",
    }


def resolve_architecture(name: str, tags: list, summary: str, tech_entry=None) -> dict:
    architecture = (tech_entry or {}).get("architecture", {})
    if architecture:
        return {
            "name": name,
            "view": architecture.get("view", "逻辑分层"),
            "layers": architecture.get("layers", []),
            "physical_view": architecture.get("physical_view", ""),
            "control_point": architecture.get("control_point", ""),
            "integration_surface": architecture.get("integration_surface", ""),
            "boundary": architecture.get("boundary", ""),
            "difference_marker": architecture.get("difference_marker", "架构重心待补充"),
            "planes": architecture.get("planes", {}),
            "summary": summary,
        }

    default_arch = build_default_architecture(name, tags, summary)
    default_arch["name"] = name
    default_arch["summary"] = summary
    return default_arch


def infer_architecture_planes(architecture: dict) -> dict:
    configured = architecture.get("planes", {}) or {}
    if configured:
        return {
            "control": configured.get("control", ""),
            "data": configured.get("data", ""),
            "execution": configured.get("execution", ""),
            "governance": configured.get("governance", ""),
        }

    layers = architecture.get("layers", [])
    layer_names = [layer.get("name", "") for layer in layers]
    responsibilities = [layer.get("responsibility", "") for layer in layers]
    combined = "；".join([text for text in layer_names + responsibilities if has_text(text)])

    control = architecture.get("control_point", "")
    governance = architecture.get("integration_surface", "")
    execution = ""
    data = ""

    for layer in layers:
        name = layer.get("name", "")
        responsibility = layer.get("responsibility", "")
        if not execution and re.search(r"执行|运行时|服务暴露|工具|模型服务|执行器|协同", name + responsibility):
            execution = f"{name}：{responsibility}"
        if not data and re.search(r"数据|资源|上下文|记忆|数据集|检索|共享", name + responsibility):
            data = f"{name}：{responsibility}"
        if not governance and re.search(r"治理|安全|评测|审计|反馈|闭环", name + responsibility):
            governance = f"{name}：{responsibility}"

    if not control and layers:
        control = f"{layers[0].get('name', '')}：{layers[0].get('responsibility', '')}"
    if not execution and len(layers) >= 2:
        execution = f"{layers[min(1, len(layers) - 1)].get('name', '')}：{layers[min(1, len(layers) - 1)].get('responsibility', '')}"
    if not data:
        if has_text(architecture.get("physical_view", "")):
            data = architecture.get("physical_view", "")
        else:
            data = combined
    if not governance and layers:
        governance = f"{layers[-1].get('name', '')}：{layers[-1].get('responsibility', '')}"

    return {
        "control": control,
        "data": data,
        "execution": execution,
        "governance": governance,
    }


def render_layer_rows(architecture: dict) -> str:
    layers = architecture.get("layers", [])
    if not layers:
        return "| 1 | 待补充 | 待补充 |\n"

    rows = []
    for idx, layer in enumerate(layers, start=1):
        rows.append(f"| {idx} | {layer.get('name', '待补充')} | {layer.get('responsibility', '待补充')} |")
    return "\n".join(rows) + "\n"


def summarize_layers(architecture: dict) -> str:
    layers = architecture.get("layers", [])
    names = [layer.get("name", "") for layer in layers if layer.get("name")]
    return " -> ".join(names) if names else "待补充"


def resolve_compare_entries(compare_names: list, technologies: list, matches: list, target_name: str) -> list:
    tech_lookup = build_tech_lookup(technologies)
    results = []
    names = compare_names or [tech["name"] for _, tech, _ in matches if tech["name"] != target_name][:3]

    for name in names:
        tech = get_tech_entry(name, tech_lookup)
        if tech:
            results.append(tech)
            continue
        results.append(
            {
                "name": name,
                "summary": f"{name}：待补充摘要。",
                "tags": [],
                "doc_url": "",
                "github_url": "",
            }
        )
    return results


def build_intro_text(name: str, summary: str, tags: list, raw: str) -> str:
    if has_text(summary):
        return clean_text(summary)
    if tags:
        return f"{name} 目前主要可归纳为「{'、'.join(tags)}」相关技术，当前报告重点从能力边界、逻辑分层与对比关系进行整理。"
    if has_text(raw):
        return f"已抓取到 {name} 的官方资料并完成初步分析，当前报告重点整理其能力定位、架构视角与对比差异。"
    return f"当前仅识别到技术名称 {name}，报告先给出可落地的通用架构视角。"


def summarize_source_mix(source_records: list) -> str:
    successful = [item for item in source_records if item.get("status") == "成功"]
    if not successful:
        return ""
    type_names = sorted(set([item.get("type", "") for item in successful if item.get("type")]))
    authority_names = sorted(set([item.get("authority", "") for item in successful if item.get("authority")]))
    return "本报告综合使用 {count} 个可信来源，覆盖 {types}，可信级别涉及 {authorities}。".format(
        count=len(successful),
        types="、".join(type_names),
        authorities="、".join(authority_names),
    )


def build_difference_text(base_arch: dict, compare_arch: dict) -> str:
    base_marker = base_arch.get("difference_marker", "")
    compare_marker = compare_arch.get("difference_marker", "")
    if not compare_marker:
        return "待补充"
    if base_marker == compare_marker:
        return f"同属「{compare_marker}」，但控制点不同：本技术更关注 {base_arch.get('control_point', '待补充')}。"
    return f"本技术偏「{base_marker}」，对比技术偏「{compare_marker}」。"


def render_compare_arch_rows(base_arch: dict, compare_entries: list) -> str:
    if not compare_entries:
        return ""

    rows = []
    for tech in compare_entries:
        architecture = resolve_architecture(tech["name"], tech.get("tags", []), tech.get("summary", ""), tech)
        rows.append(
            "| {name} | {layers} | {control_point} | {difference} |".format(
                name=tech["name"],
                layers=summarize_layers(architecture),
                control_point=architecture.get("control_point", "待补充"),
                difference=build_difference_text(base_arch, architecture),
            )
        )
    return "\n".join(rows) + "\n"


def render_bullet_lines(items: list) -> str:
    return "\n".join([f"- {item}" for item in items if has_text(item)])


def render_mermaid_architecture(architecture: dict) -> str:
    layers = architecture.get("layers", [])
    if not layers:
        return ""

    lines = ["```mermaid", "flowchart TD"]
    prev_node = ""
    for idx, layer in enumerate(layers, start=1):
        node = f"L{idx}"
        label = f"{layer.get('name', '未命名层')}<br/>{layer.get('responsibility', '')}"
        lines.append(f'    {node}["{label}"]')
        if prev_node:
            lines.append(f"    {prev_node} --> {node}")
        prev_node = node
    lines.append("```")
    return "\n".join(lines)


def get_unified_compare_layers() -> list:
    return [
        {"key": "entry", "name": "宿主接入层", "desc": "用户入口、宿主环境、IDE / Host 集成"},
        {"key": "control", "name": "控制编排层", "desc": "目标解释、策略决策、流程编排"},
        {"key": "integration", "name": "协议集成层", "desc": "协议抽象、工具接入、外部服务连接"},
        {"key": "execution", "name": "执行运行层", "desc": "任务执行、运行时、工具调用"},
        {"key": "data", "name": "数据上下文层", "desc": "上下文、资源、数据集、记忆或工作区"},
        {"key": "governance", "name": "治理评测层", "desc": "安全、评测、审计、反馈闭环"},
    ]


def get_architecture_scene_hint(architecture: dict) -> str:
    name = architecture.get("name", "")
    marker = architecture.get("difference_marker", "")
    summary = architecture.get("summary", "")
    tags = " ".join(architecture.get("tags", [])) if architecture.get("tags") else ""
    text = f"{name} {marker} {summary} {tags}"

    patterns = [
        (r"MCP|协议", "标准化工具接入"),
        (r"Cursor|IDE|工作台", "开发工作台增强"),
        (r"Harness|评测|治理", "评测治理基座"),
        (r"Agent 框架|框架", "框架级能力组织"),
        (r"多智能体|协同", "多角色协同执行"),
        (r"大模型|模型", "模型推理服务"),
        (r"Agent|自治|多步任务", "自治多步任务"),
    ]
    for pattern, hint in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return hint
    return "能力边界待定"


def infer_unified_layer_profile(architecture: dict) -> dict:
    planes = infer_architecture_planes(architecture)
    marker = architecture.get("difference_marker", "")
    tags = set(architecture.get("tags", []) or [])
    scene = get_architecture_scene_hint(architecture)
    depth_map = {layer["key"]: "弱" for layer in get_unified_compare_layers()}

    if re.search(r"工作台集成", marker):
        depth_map.update({"entry": "强", "control": "中", "integration": "中", "execution": "中", "data": "中", "governance": "弱"})
    elif re.search(r"协议标准化", marker):
        depth_map.update({"entry": "中", "control": "中", "integration": "强", "execution": "中", "data": "中", "governance": "中"})
    elif re.search(r"任务编排", marker):
        depth_map.update({"entry": "弱", "control": "强", "integration": "中", "execution": "强", "data": "中", "governance": "中"})
    elif re.search(r"验证治理", marker):
        depth_map.update({"entry": "弱", "control": "强", "integration": "中", "execution": "中", "data": "中", "governance": "强"})
    elif re.search(r"模型能力", marker):
        depth_map.update({"entry": "弱", "control": "中", "integration": "中", "execution": "强", "data": "强", "governance": "中"})
    elif re.search(r"协同调度", marker):
        depth_map.update({"entry": "弱", "control": "强", "integration": "中", "execution": "强", "data": "中", "governance": "中"})
    elif re.search(r"框架编排", marker):
        depth_map.update({"entry": "弱", "control": "强", "integration": "强", "execution": "中", "data": "中", "governance": "中"})

    if {"AI IDE", "编辑器"} & tags:
        depth_map["entry"] = "强"
    if {"协议", "工具调用", "API"} & tags:
        depth_map["integration"] = "强"
    if {"执行", "多步任务", "自动化"} & tags:
        depth_map["execution"] = "强" if depth_map["execution"] != "弱" else "中"
    if {"验证", "测试框架", "标准化"} & tags:
        depth_map["governance"] = "强" if depth_map["governance"] != "弱" else "中"
    if {"数据", "资源", "记忆"} & tags:
        depth_map["data"] = "强" if depth_map["data"] != "弱" else "中"

    detail_map = {
        "entry": scene,
        "control": planes.get("control", architecture.get("control_point", "")),
        "integration": architecture.get("integration_surface", "") or planes.get("data", ""),
        "execution": planes.get("execution", ""),
        "data": planes.get("data", architecture.get("physical_view", "")),
        "governance": planes.get("governance", architecture.get("integration_surface", "")),
    }
    return {"depth": depth_map, "detail": detail_map}


def render_unified_layer_table(architectures: list) -> str:
    if len(architectures) <= 1:
        return ""
    layers = get_unified_compare_layers()
    header = "| 统一分层 | " + " | ".join([arch.get("name", "") for arch in architectures]) + " |"
    divider = "|" + "------|" * (len(architectures) + 1)
    rows = [header, divider]
    profiles = {arch.get("name", ""): infer_unified_layer_profile(arch) for arch in architectures}
    for layer in layers:
        cells = [layer["name"]]
        for arch in architectures:
            profile = profiles[arch.get("name", "")]
            depth = profile["depth"].get(layer["key"], "弱")
            detail = profile["detail"].get(layer["key"], "")
            cells.append(f"{depth} / {detail}" if has_text(detail) else depth)
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def pad_text(text: str, width: int) -> str:
    normalized = clean_text(text).replace("\n", " ")
    if len(normalized) > width:
        return normalized[: width - 1] + "…"
    return normalized.ljust(width)


def get_depth_symbol(depth: str) -> str:
    mapping = {
        "强": "[##]",
        "中": "[==]",
        "弱": "[  ]",
    }
    return mapping.get(depth, "[  ]")


def summarize_profile_span(architecture: dict) -> dict:
    profile = infer_unified_layer_profile(architecture)
    layers = get_unified_compare_layers()
    active_layers = [layer for layer in layers if profile["depth"].get(layer["key"], "弱") in {"强", "中"}]
    dominant_layers = [layer["name"] for layer in layers if profile["depth"].get(layer["key"], "弱") == "强"]

    if active_layers:
        span = f"{active_layers[0]['name']} -> {active_layers[-1]['name']}"
    else:
        span = "未形成显著跨度"

    if not dominant_layers:
        dominant_layers = [layer["name"] for layer in active_layers[:1]] if active_layers else []

    return {
        "span": span,
        "dominant_layers": dominant_layers,
        "scene": get_architecture_scene_hint(architecture),
        "marker": architecture.get("difference_marker", ""),
    }


def render_text_compare_diagram(architectures: list) -> str:
    if len(architectures) <= 1:
        return ""

    profiles = {arch.get("name", ""): infer_unified_layer_profile(arch) for arch in architectures}
    tech_width = 16
    layer_width = 14
    cell_width = 8

    header = pad_text("统一分层", layer_width) + " | " + " | ".join(
        [pad_text(arch.get("name", ""), tech_width) for arch in architectures]
    )
    divider = "-" * len(header)
    rows = [header, divider]

    for layer in get_unified_compare_layers():
        line = [pad_text(layer["name"], layer_width)]
        for arch in architectures:
            profile = profiles[arch.get("name", "")]
            depth = profile["depth"].get(layer["key"], "弱")
            cell = get_depth_symbol(depth)
            line.append(pad_text(cell, cell_width))
        rows.append(" | ".join(line))

    tech_notes = []
    for architecture in architectures:
        summary = summarize_profile_span(architecture)
        dominant = "、".join(summary["dominant_layers"]) if summary["dominant_layers"] else "无明显主导层"
        tech_notes.append(
            "- `{name}`：跨度 `{span}`；主导层 `{dominant}`；典型场景 `{scene}`；差异标记 `{marker}`。".format(
                name=architecture.get("name", ""),
                span=summary["span"],
                dominant=dominant,
                scene=summary["scene"],
                marker=summary["marker"],
            )
        )

    legend = [
        "",
        "图示说明：",
        "1. 行表示统一分层，列表示对比技术。",
        "2. `[##] / [==] / [  ]` 分别表示强覆盖、中覆盖、弱覆盖。",
        "3. 该图只呈现层次跨度与重心分布，具体说明见下方技术说明与 4.3、4.5。",
        "",
        "技术说明：",
    ]
    return "```text\n" + "\n".join(rows + legend) + "\n```\n\n" + "\n".join(tech_notes)


def build_graph_cells_for_architectures(architectures: list) -> str:
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    next_id = 2
    column_width = 240
    layer_height = 56
    start_x = 40
    start_y = 40
    column_gap = 60

    for index, architecture in enumerate(architectures):
        base_x = start_x + index * (column_width + column_gap)
        header_id = str(next_id)
        next_id += 1
        cells.append(
            '<mxCell id="{id}" value="{value}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">'
            '<mxGeometry x="{x}" y="{y}" width="{w}" height="42" as="geometry"/>'
            '</mxCell>'.format(
                id=header_id,
                value=escape(architecture.get("name", "未命名技术")),
                x=base_x,
                y=start_y,
                w=column_width,
            )
        )

        prev_id = header_id
        for layer_index, layer in enumerate(architecture.get("layers", []), start=1):
            node_id = str(next_id)
            next_id += 1
            y = start_y + 60 + (layer_index - 1) * (layer_height + 18)
            value = escape(f"{layer.get('name', '未命名层')}\n{layer.get('responsibility', '')}")
            cells.append(
                '<mxCell id="{id}" value="{value}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">'
                '<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
                '</mxCell>'.format(
                    id=node_id,
                    value=value,
                    x=base_x,
                    y=y,
                    w=column_width,
                    h=layer_height,
                )
            )
            edge_id = str(next_id)
            next_id += 1
            cells.append(
                '<mxCell id="{id}" style="endArrow=block;html=1;rounded=0;strokeColor=#666666;" edge="1" parent="1" source="{source}" target="{target}">'
                '<mxGeometry relative="1" as="geometry"/>'
                '</mxCell>'.format(
                    id=edge_id,
                    source=prev_id,
                    target=node_id,
                )
            )
            prev_id = node_id

        note_lines = []
        if has_text(architecture.get("control_point", "")):
            note_lines.append(f"控制点：{architecture['control_point']}")
        if has_text(architecture.get("difference_marker", "")):
            note_lines.append(f"差异标记：{architecture['difference_marker']}")
        if note_lines:
            note_id = str(next_id)
            next_id += 1
            y = start_y + 60 + len(architecture.get("layers", [])) * (layer_height + 18)
            cells.append(
                '<mxCell id="{id}" value="{value}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">'
                '<mxGeometry x="{x}" y="{y}" width="{w}" height="68" as="geometry"/>'
                '</mxCell>'.format(
                    id=note_id,
                    value=escape("\n".join(note_lines)),
                    x=base_x,
                    y=y,
                    w=column_width,
                )
            )
    return "".join(cells)


def build_unified_compare_cells(architectures: list) -> str:
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    layers = get_unified_compare_layers()
    profiles = {arch.get("name", ""): infer_unified_layer_profile(arch) for arch in architectures}
    layer_col_width = 220
    tech_col_width = 180
    header_height = 48
    row_height = 72
    start_x = 40
    start_y = 40
    next_id = 2

    cells.append(
        '<mxCell id="{id}" value="统一分层" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">'
        '<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        '</mxCell>'.format(
            id=next_id,
            x=start_x,
            y=start_y,
            w=layer_col_width,
            h=header_height,
        )
    )
    next_id += 1

    current_x = start_x + layer_col_width
    for architecture in architectures:
        cells.append(
            '<mxCell id="{id}" value="{value}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">'
            '<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
            '</mxCell>'.format(
                id=next_id,
                value=escape(architecture.get("name", "")),
                x=current_x,
                y=start_y,
                w=tech_col_width,
                h=header_height,
            )
        )
        next_id += 1
        current_x += tech_col_width

    for row_index, layer in enumerate(layers, start=1):
        y = start_y + header_height + (row_index - 1) * row_height
        cells.append(
            '<mxCell id="{id}" value="{value}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontStyle=1;" vertex="1" parent="1">'
            '<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
            '</mxCell>'.format(
                id=next_id,
                value=escape(f'{layer["name"]}\n{layer["desc"]}'),
                x=start_x,
                y=y,
                w=layer_col_width,
                h=row_height,
            )
        )
        next_id += 1

        current_x = start_x + layer_col_width
        for architecture in architectures:
            profile = profiles[architecture.get("name", "")]
            depth = profile["depth"].get(layer["key"], "弱")
            fill = {"强": "#d5e8d4", "中": "#fff2cc", "弱": "#f8cecc"}.get(depth, "#f5f5f5")
            stroke = {"强": "#82b366", "中": "#d6b656", "弱": "#b85450"}.get(depth, "#b7b7b7")
            value = escape(depth)
            cells.append(
                '<mxCell id="{id}" value="{value}" style="rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};" vertex="1" parent="1">'
                '<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
                '</mxCell>'.format(
                    id=next_id,
                    value=value,
                    fill=fill,
                    stroke=stroke,
                    x=current_x,
                    y=y,
                    w=tech_col_width,
                    h=row_height,
                )
            )
            next_id += 1
            current_x += tech_col_width

    legend_y = start_y + header_height + len(layers) * row_height + 24
    legend_items = [
        ("强覆盖", "#d5e8d4", "#82b366"),
        ("中覆盖", "#fff2cc", "#d6b656"),
        ("弱覆盖", "#f8cecc", "#b85450"),
    ]
    legend_x = start_x
    for label, fill, stroke in legend_items:
        cells.append(
            '<mxCell id="{id}" value="{value}" style="rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};" vertex="1" parent="1">'
            '<mxGeometry x="{x}" y="{y}" width="120" height="32" as="geometry"/>'
            '</mxCell>'.format(
                id=next_id,
                value=escape(label),
                fill=fill,
                stroke=stroke,
                x=legend_x,
                y=legend_y,
            )
        )
        next_id += 1
        legend_x += 140

    note_y = legend_y + 56
    current_x = start_x + layer_col_width
    for architecture in architectures:
        summary = summarize_profile_span(architecture)
        dominant = "、".join(summary["dominant_layers"]) if summary["dominant_layers"] else "无明显主导层"
        note = "跨度：{span}\n主导层：{dominant}\n场景：{scene}\n差异：{marker}".format(
            span=summary["span"],
            dominant=dominant,
            scene=summary["scene"],
            marker=summary["marker"],
        )
        cells.append(
            '<mxCell id="{id}" value="{value}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">'
            '<mxGeometry x="{x}" y="{y}" width="{w}" height="92" as="geometry"/>'
            '</mxCell>'.format(
                id=next_id,
                value=escape(f"{architecture.get('name', '')}\n{note}"),
                x=current_x,
                y=note_y,
                w=tech_col_width,
            )
        )
        next_id += 1
        current_x += tech_col_width

    cells.append(
        '<mxCell id="{id}" value="{value}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontStyle=1;" vertex="1" parent="1">'
        '<mxGeometry x="{x}" y="{y}" width="{w}" height="92" as="geometry"/>'
        '</mxCell>'.format(
            id=next_id,
            value=escape("图示解释\n纵向为统一分层，横向为对比技术。\n色块仅表达覆盖深度，避免与 4.3 的细节矩阵重复。"),
            x=start_x + layer_col_width + len(architectures) * tech_col_width - 220,
            y=note_y + 112,
            w=220,
        )
    )
    return "".join(cells)


def build_plane_matrix_cells(architectures: list) -> str:
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
    headers = ["技术", "控制面", "数据面", "执行面", "治理面"]
    column_widths = [180, 260, 260, 260, 260]
    start_x = 40
    start_y = 40
    row_height = 84
    header_height = 42
    next_id = 2

    current_x = start_x
    for idx, header in enumerate(headers):
        cell_id = str(next_id)
        next_id += 1
        cells.append(
            '<mxCell id="{id}" value="{value}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;" vertex="1" parent="1">'
            '<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
            '</mxCell>'.format(
                id=cell_id,
                value=escape(header),
                x=current_x,
                y=start_y,
                w=column_widths[idx],
                h=header_height,
            )
        )
        current_x += column_widths[idx]

    for row_index, architecture in enumerate(architectures, start=1):
        y = start_y + header_height + (row_index - 1) * row_height
        planes = infer_architecture_planes(architecture)
        row_values = [
            architecture.get("name", ""),
            planes.get("control", ""),
            planes.get("data", ""),
            planes.get("execution", ""),
            planes.get("governance", ""),
        ]
        current_x = start_x
        for col_index, value in enumerate(row_values):
            cell_id = str(next_id)
            next_id += 1
            fill = "#fff2cc" if col_index == 0 else "#f5f5f5"
            stroke = "#d6b656" if col_index == 0 else "#b7b7b7"
            cells.append(
                '<mxCell id="{id}" value="{value}" style="rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};" vertex="1" parent="1">'
                '<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
                '</mxCell>'.format(
                    id=cell_id,
                    value=escape(value),
                    fill=fill,
                    stroke=stroke,
                    x=current_x,
                    y=y,
                    w=column_widths[col_index],
                    h=row_height,
                )
            )
            current_x += column_widths[col_index]
    return "".join(cells)


def wrap_drawio_diagram(name: str, cells: str) -> str:
    return (
        '<diagram id="{diagram_id}" name="{name}">'
        '<mxGraphModel dx="1386" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2200" pageHeight="1400" math="0" shadow="0">'
        '<root>{cells}</root>'
        '</mxGraphModel>'
        '</diagram>'
    ).format(
        diagram_id=escape(f"diagram-{slug(name)}"),
        name=escape(name),
        cells=cells,
    )


def build_drawio_xml(title: str, target_arch: dict, compare_arches: list) -> str:
    diagrams = [
        wrap_drawio_diagram(f"{target_arch.get('name', '目标技术')}-架构", build_graph_cells_for_architectures([target_arch]))
    ]
    all_arches = [target_arch] + compare_arches
    if len(all_arches) > 1:
        diagrams.append(
            wrap_drawio_diagram("架构并列对比", build_unified_compare_cells(all_arches))
        )
        diagrams.append(
            wrap_drawio_diagram("四平面对比矩阵", build_plane_matrix_cells(all_arches))
        )

    return (
        '<mxfile host="app.diagrams.net" modified="{modified}" agent="tech-explorer" version="26.0.0">{diagrams}</mxfile>'
    ).format(
        modified=datetime.now().isoformat(),
        diagrams="".join(diagrams),
    )


def maybe_write_drawio(report_path: Path, target_arch: dict, compare_arches: list) -> Path:
    valid_target = target_arch if target_arch.get("layers") else None
    if not valid_target:
        return None

    drawio_path = report_path.with_suffix(".drawio")
    drawio_path.write_text(
        build_drawio_xml(f"{report_path.stem}-architecture", valid_target, [item for item in compare_arches if item.get("layers")]),
        encoding="utf-8",
    )
    return drawio_path


def build_intro_section(intro: str, doc_url: str, gh_url: str, source_records: list) -> str:
    items = []
    if has_text(intro):
        items.append("## 摘要\n\n" + clean_text(intro))
    source_mix = summarize_source_mix(source_records)
    if has_text(source_mix):
        items.append("## 1. 研究范围与证据基础\n\n" + source_mix)
    definition_lines = []
    if has_text(doc_url):
        definition_lines.append(f"**官方文档**: [{doc_url}]({doc_url})")
    if has_text(gh_url):
        definition_lines.append(f"**GitHub**: [{gh_url}]({gh_url})")
    if definition_lines:
        items.append("## 2. 研究对象与基础资料\n\n" + "\n\n".join(definition_lines))
    if not items:
        return ""
    return "\n\n".join(items)


def build_tag_section(new_tags: list, catalog: list) -> str:
    if not new_tags:
        return ""
    hint_map = {item["tag"]: item.get("hint", "") for item in catalog}
    rows = "\n".join([f"| {tag} | {hint_map.get(tag, '')} |" for tag in new_tags])
    return (
        "## 4. 语义标签归纳\n\n"
        "| Tag | 说明 |\n"
        "|-----|------|\n"
        f"{rows}"
    )


def build_sources_section(source_records: list) -> str:
    successful = [item for item in source_records if item.get("status") == "成功"]
    if not successful:
        return ""

    rows = []
    for item in successful:
        rows.append(
            "| {name} | {type} | {authority} | {role} |".format(
                name=item.get("name", ""),
                type=item.get("type", ""),
                authority=item.get("authority", ""),
                role=item.get("role", ""),
            )
        )

    discussion = []
    if any(item.get("type") == "官方文档" for item in successful):
        discussion.append("官方文档用于抽取定义、术语边界与基础能力。")
    if any(item.get("type") == "官方仓库" for item in successful):
        discussion.append("官方仓库用于补充实现结构、接口组织与示例入口。")
    if any(item.get("type") == "标准/规范" for item in successful):
        discussion.append("标准/规范用于校正协议约束、对象模型与兼容边界。")
    if any(item.get("type") in {"论文/预印本", "官方博客/工程文章"} for item in successful):
        discussion.append("论文或工程文章用于补充设计动机、实验现象与落地案例。")

    return (
        "## 3. 可信来源汇总\n\n"
        "| 来源 | 类型 | 可信级别 | 主要贡献 |\n"
        "|------|------|----------|----------|\n"
        + "\n".join(rows)
        + ("\n\n### 3.1 交叉验证说明\n\n" + render_bullet_lines(discussion) if discussion else "")
    )


def build_architecture_section(architecture: dict, drawio_path: Path) -> str:
    section_parts = ["## 5. 技术架构分析"]
    if drawio_path:
        section_parts.append(
            "**Draw.io 源文件**: `{path}`\n\n"
            "页签说明：`{name}-架构` 为目标技术页，`架构并列对比` 为横向对照页，`四平面对比矩阵` 为控制 / 数据 / 执行 / 治理四平面矩阵。".format(
                path=drawio_path,
                name=architecture.get("name", "目标技术"),
            )
        )

    overview_items = [
        f"架构类型：{architecture.get('view', '')}" if has_text(architecture.get("view", "")) else "",
        f"逻辑分层：{summarize_layers(architecture)}" if has_text(summarize_layers(architecture)) else "",
        f"物理落位：{architecture.get('physical_view', '')}" if has_text(architecture.get("physical_view", "")) else "",
        f"核心控制点：{architecture.get('control_point', '')}" if has_text(architecture.get("control_point", "")) else "",
        f"集成边界：{architecture.get('integration_surface', '')}" if has_text(architecture.get("integration_surface", "")) else "",
        f"架构说明：{architecture.get('boundary', '')}" if has_text(architecture.get("boundary", "")) else "",
    ]
    overview = render_bullet_lines(overview_items)
    if overview:
        section_parts.append("### 5.1 架构视角\n\n" + overview)

    mermaid = render_mermaid_architecture(architecture)
    if mermaid:
        section_parts.append("### 5.2 架构图\n\n" + mermaid)

    layer_rows = render_layer_rows(architecture).strip()
    if layer_rows:
        section_parts.append(
            "### 5.3 逻辑分层明细\n\n"
            "| 层级 | 分层名称 | 主要职责 |\n"
            "|------|----------|----------|\n"
            f"{layer_rows}"
        )
    return "\n\n".join(section_parts)


def build_match_section(matches: list) -> str:
    if not matches:
        return ""
    rows = []
    for score, tech, shared in matches:
        pct = int(round(score * 100))
        rows.append(f"| {tech['name']} | {', '.join(shared) or '—'} | {pct}% |")
    return (
        "### 6.1 对比对象与匹配依据\n\n"
        "| 技术 | 匹配 Tags | 匹配度 |\n"
        "|------|----------|--------|\n"
        + "\n".join(rows)
    )


def build_compare_section(name: str, base_arch: dict, compare_entries: list, matches: list) -> str:
    compare_arches = [resolve_architecture(item["name"], item.get("tags", []), item.get("summary", ""), item) for item in compare_entries]
    all_arches = [base_arch] + compare_arches
    parts = ["## 6. 对比分析"]

    match_section = build_match_section(matches)
    if match_section:
        parts.append(match_section)

    text_compare = render_text_compare_diagram(all_arches)
    if text_compare:
        parts.append(
            "### 6.2 架构并列图示\n\n"
            "该图示采用与 `drawio` 页签 `架构并列对比` 一致的统一分层矩阵结构：纵向固定公共分层，横向并列各技术，通过覆盖深度与必要说明展示场景和实现差异。\n\n"
            + text_compare
        )

    unified_table = render_unified_layer_table(all_arches)
    if unified_table:
        parts.append(
            "### 6.3 统一分层覆盖矩阵\n\n"
            "说明：`强 / 中 / 弱` 分别表示该技术在对应统一层中的覆盖强度、控制深度或能力主导程度。\n\n"
            + unified_table
        )

    compare_rows = render_compare_arch_rows(base_arch, compare_entries).strip()
    if compare_rows:
        parts.append(
            "### 6.4 分层与控制点对比\n\n"
            "| 技术 | 实现逻辑 / 物理分层 | 主要涉及层 | 主要差异标记 |\n"
            "|------|---------------------|------------|--------------|\n"
            f"| {name} | {summarize_layers(base_arch)} | {base_arch.get('control_point', '')} | 基准：{base_arch.get('difference_marker', '')} |\n"
            f"{compare_rows}"
        )

    plane_rows = []
    for architecture in [base_arch] + compare_arches:
        planes = infer_architecture_planes(architecture)
        plane_rows.append(
            "| {name} | {control} | {data} | {execution} | {governance} |".format(
                name=architecture.get("name", ""),
                control=planes.get("control", ""),
                data=planes.get("data", ""),
                execution=planes.get("execution", ""),
                governance=planes.get("governance", ""),
            )
        )
    if plane_rows and len(plane_rows) > 1:
        parts.append(
            "### 6.5 四平面对比矩阵\n\n"
            "| 技术 | 控制面 | 数据面 | 执行面 | 治理面 |\n"
            "|------|--------|--------|--------|--------|\n"
            + "\n".join(plane_rows)
        )

    discussion_points = []
    for architecture in compare_arches:
        discussion_points.append(
            "相较于 {name}，`{base}` 更强调「{base_marker}」，而 `{name}` 更偏向「{compare_marker}」，二者的核心分歧集中在 `{base_control}` 与 `{compare_control}` 两类控制点。".format(
                name=architecture.get("name", ""),
                base=base_arch.get("name", ""),
                base_marker=base_arch.get("difference_marker", ""),
                compare_marker=architecture.get("difference_marker", ""),
                base_control=base_arch.get("control_point", ""),
                compare_control=architecture.get("control_point", ""),
            )
        )
    if discussion_points:
        parts.append("### 6.6 差异讨论\n\n" + render_bullet_lines(discussion_points))

    return "\n\n".join([item for item in parts if item]) if len(parts) > 1 else ""


def build_learning_section(doc_url: str, gh_url: str) -> str:
    resources = []
    if has_text(doc_url):
        resources.append(f"- [官方文档]({doc_url})")
    if has_text(gh_url):
        resources.append(f"- [GitHub 仓库]({gh_url})")
    if not resources:
        return ""
    return "## 7. 参考资料\n\n" + "\n".join(resources)


def build_excerpt_section(excerpt: str) -> str:
    if not should_keep_chinese_excerpt(excerpt):
        return ""
    normalized = clean_text(excerpt)
    if len(normalized) > 3500:
        normalized = normalized[:3500] + "\n\n…"
    return "## 附录：深度抓取摘录\n\n" + normalized


def build_report(
    name: str,
    intro: str,
    doc_url: str,
    gh_url: str,
    new_tags: list,
    compare_names: list,
    matches: list,
    deep_excerpt: str,
    catalog: list,
    technologies: list,
    tech_entry: dict,
    drawio_path: Path,
    source_records: list,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    compare_line = ", ".join(compare_names) if compare_names else ""
    target_arch = resolve_architecture(name, new_tags, intro, tech_entry)
    compare_entries = resolve_compare_entries(compare_names, technologies, matches, name)
    sections = [
        build_intro_section(intro, doc_url, gh_url, source_records),
        build_sources_section(source_records),
        build_tag_section(new_tags, catalog),
        build_architecture_section(target_arch, drawio_path),
        build_compare_section(name, target_arch, compare_entries, matches),
        build_learning_section(doc_url, gh_url),
        build_excerpt_section(deep_excerpt),
    ]

    header_lines = [f"# 技术探索研究：{name}", "", f"**成文时间**: {now}"]
    if has_text(compare_line):
        header_lines.append(f"**对比技术**: {compare_line}")
    return "\n".join(header_lines) + "\n\n---\n\n" + join_sections(sections) + "\n"


def maybe_feishu(webhook: str, text: str):
    if not webhook:
        return
    payload = json.dumps({"msg_type": "text", "content": {"text": text[:4000]}}).encode("utf-8")
    req = urllib.request.Request(
        webhook,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15).read()
    except urllib.error.URLError:
        pass


def main():
    parser = argparse.ArgumentParser(description="tech-explorer")
    parser.add_argument("name", nargs="?", default="", help="技术名称")
    parser.add_argument("--compare", default="", help="逗号分隔对比技术名，如 MCP,Agent")
    parser.add_argument("--doc-url", default="", help="官方文档 URL，用于 Jina 抓取")
    parser.add_argument("--github-url", default="", help="GitHub 仓库 URL")
    parser.add_argument("--extra-url", action="append", default=[], help="附加可信来源 URL，可重复传入")
    parser.add_argument("--yes", action="store_true", help="跳过交互确认")
    args = parser.parse_args()

    kb = load_json(CONFIG_DIR / "knowledge_base.json")
    confirm_cfg = load_json(CONFIG_DIR / "confirm.json")
    threshold = float(confirm_cfg.get("match_threshold", 0.6))
    prefix = confirm_cfg.get("jina_reader_prefix", "https://r.jina.ai/")

    catalog = kb["tag_catalog"]
    technologies = kb["technologies"]
    tech_lookup = build_tech_lookup(technologies)
    interactive = not args.yes
    name = resolve_name(args.name, confirm_cfg, technologies, interactive)
    tech_entry = get_tech_entry(name, tech_lookup)
    doc_url = args.doc_url or (tech_entry or {}).get("doc_url", "")
    github_url = args.github_url or (tech_entry or {}).get("github_url", "")
    source_candidates = build_source_candidates(doc_url, github_url, tech_entry, args.extra_url)
    source_records = fetch_sources(source_candidates, prefix)
    successful_sources = [item for item in source_records if item.get("status") == "成功"]
    raw = "\n\n".join([item.get("body", "") for item in successful_sources if has_text(item.get("body", ""))])

    new_tags = extract_tags(raw or name, catalog)
    if tech_entry:
        new_tags = sorted(set(new_tags) | set(tech_entry.get("tags", [])))
    tag_set = set(new_tags)
    matches = match_kb(tag_set, technologies, threshold)
    matches = [item for item in matches if item[1]["name"].strip().lower() != name.strip().lower()]

    summary = (tech_entry or {}).get("summary", "")
    intro = build_intro_text(name, summary, sorted(tag_set), raw)
    intro = run_round1(name, intro, confirm_cfg, interactive)

    compare_names = [x.strip() for x in args.compare.split(",") if x.strip()]
    if interactive and not compare_names:
        print("===", confirm_cfg["round2"]["title"], "===")
        print_match_preview(matches)
        print(confirm_cfg["round2"]["prompt"])
    compare_names = resolve_compare_names(args.compare, matches, confirm_cfg, interactive)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = REPORTS_DIR / f"tech_explorer_{slug(name)}_{stamp}.md"
    target_architecture = resolve_architecture(name, sorted(tag_set), intro, tech_entry)
    compare_architectures = [
        resolve_architecture(item["name"], item.get("tags", []), item.get("summary", ""), item)
        for item in resolve_compare_entries(compare_names, technologies, matches, name)
    ]
    drawio_path = maybe_write_drawio(out_path, target_architecture, compare_architectures)
    report = build_report(
        name=name,
        intro=intro,
        doc_url=doc_url,
        gh_url=github_url,
        new_tags=sorted(tag_set),
        compare_names=compare_names,
        matches=matches,
        deep_excerpt=raw,
        catalog=catalog,
        technologies=technologies,
        tech_entry=tech_entry,
        drawio_path=drawio_path,
        source_records=source_records,
    )
    out_path.write_text(report, encoding="utf-8")
    print(str(out_path))

    webhook = os.environ.get("FEISHU_WEBHOOK", "")
    maybe_feishu(webhook, f"tech-explorer 报告已生成: {out_path}\n技术: {name}")


if __name__ == "__main__":
    main()
