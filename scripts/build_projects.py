#!/usr/bin/env python3
"""Insert project source fragments into the single Paper Collage Archive page."""
from pathlib import Path
from html import escape as html_escape, unescape
import json
import re
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "content" / "projects"
HTML_FILE = ROOT / "index.html"
CSS_FILE = ROOT / "assets" / "css" / "style.css"
APP_JS_FILE = ROOT / "assets" / "js" / "app.js"
PROJECT_BLURBS = {
    "spot-radar": "상권 지표를 비교해 조사 후보 선별",
    "starter-kit": "LLM·RAG 개발 기반을 한곳에",
    "inheritance-guide": "상속 절차를 짚어 주는 안내 서비스",
    "github-taskflow": "Git 변경을 보호하는 작업 자동화",
    "webtoon-feedback": "독자 반응을 분석해 작가에게 전달",
    "job-process-automation": "채용 메일을 지원 기록으로 연결",
}
PROJECT_INDEX = [
    ("starter-kit", "AI Starter Kit", "팀 프로젝트 · 2026.10–11", PROJECT_BLURBS["starter-kit"]),
    ("spot-radar", "SPOT RADAR", "팀 프로젝트 · 2026.09–10", PROJECT_BLURBS["spot-radar"]),
    ("github-taskflow", "GitHub Taskflow", "개인 프로젝트 · 2026.09", PROJECT_BLURBS["github-taskflow"]),
    ("job-process-automation", "Job Process Automation", "개인 프로젝트 · 2026.07", PROJECT_BLURBS["job-process-automation"]),
    ("webtoon-feedback", "Webtoon Feedback", "팀 프로젝트 · 2024.03–06", PROJECT_BLURBS["webtoon-feedback"]),
    ("inheritance-guide", "상속길잡이", "팀 프로젝트 · 2026.10–11", PROJECT_BLURBS["inheritance-guide"]),
]
STYLE_START = "/* project-content-v3:start */"
STYLE_END = "/* project-content-v3:end */"
PROJECT_CODE_PATTERN = re.compile(
    r'(<code class="language-([\w+-]+)">)(.*?)(</code>)', re.DOTALL
)
PROJECT_CODE_FORMATTER = HtmlFormatter(nowrap=True, classprefix="tok-")
PROJECT_CSS = r"""
/* project-content-v3:start */
.project-overview,.project-features,.project-contribution,.project-evidence,.project-screens,.project-architecture{margin:24px 0}
.project-overview p,.project-contribution p,.project-evidence p,.project-architecture>p,.project-caption{max-width:930px}
.project-feature-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:12px 0 0;padding:0;list-style:none}
.project-feature-list li{min-width:0;padding:14px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-top:3px solid var(--accent,var(--blue,#315a72))}
.project-feature-list strong{display:block;margin-bottom:6px;font-size:14px;color:var(--ink,#1c2830)}
.project-feature-list p{margin:0;font-size:13px;line-height:1.65;color:var(--muted,#5f6d73)}
.contribution-lanes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.contribution-lanes>section{min-width:0;padding:14px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7)}
.contribution-lanes h4{margin:0 0 7px;font-size:14px;color:var(--accent,var(--blue,#315a72))}
.contribution-lanes p{margin:0}
.evidence-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr));gap:10px;margin:12px 0 14px}
.evidence-card{min-width:0;padding:13px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-bottom:3px solid var(--accent,var(--blue,#315a72))}
.evidence-card strong{display:block;font-size:18px;line-height:1.3;letter-spacing:-.03em;color:var(--accent,var(--blue,#315a72));overflow-wrap:anywhere}
.evidence-card p{margin:7px 0 0;font-size:12px;line-height:1.6}
.project-map .map-flow{flex-wrap:nowrap}
.project-map .map-step{overflow-wrap:anywhere}
.project-map .map-arrow{flex:none}
.project-resources{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:22px 0 8px;padding:14px 0 0;border-top:1px solid var(--line,#d5d0c7)}
.project-resources>span{flex-basis:100%;font:800 10px/1.4 ui-monospace,monospace;letter-spacing:.08em;color:var(--accent,var(--blue,#315a72))}
.project-resources a{display:inline-block;max-width:100%;padding:7px 9px;border:1px solid var(--line,#d5d0c7);background:var(--white,#fffefa);font-size:12px;line-height:1.4;overflow-wrap:anywhere}
.project-resources a:hover{border-color:var(--accent,var(--blue,#315a72));transform:translateY(-1px)}
.related-post-preview{flex:1 1 100%;min-width:0;padding:9px 11px;background:var(--wash,#f2f3ef);border:1px solid var(--line,#d5d0c7)}
.related-post-preview summary{cursor:pointer;font-size:12px;line-height:1.5;font-weight:850;color:var(--accent,var(--blue,#315a72))}
.related-post-preview p{max-width:760px;margin:8px 0;font-size:12px;line-height:1.65;color:var(--muted,#5f6d73)}
.related-post-preview .related-post-full{display:inline-block;padding:6px 8px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);font-size:11px;font-weight:800}
.screen-gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.screen-gallery-two{grid-template-columns:repeat(2,minmax(0,1fr))}
.spot-screen-gallery .spot-screen-shot>a{display:grid;place-items:center;aspect-ratio:5/4;overflow:hidden;background:#ebece7;border:1px solid var(--line,#d5d0c7)}
.spot-screen-gallery .spot-screen-shot img{display:block;width:100%;height:100%;max-height:none;object-fit:contain;background:#ebece7}
.spot-screen-gallery .spot-screen-shot figcaption strong,.spot-screen-gallery .spot-screen-shot figcaption span{display:block}
.spot-screen-gallery .spot-screen-shot figcaption strong{margin-bottom:4px;color:var(--ink,#1c2830);font-size:13px}
.spot-screen-gallery .spot-screen-shot figcaption span{color:var(--muted,#5f6d73);font-size:11px;line-height:1.5}
.project-highlight{margin:28px 0;padding:clamp(16px,2.5vw,24px);background:var(--wash,#f2f3ef);border-left:4px solid var(--accent,var(--blue,#315a72))}
.project-highlight>h3{margin-top:0}
.project-highlight>p{max-width:930px}
.project-highlight-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:14px 0 0}
.project-highlight-grid>section{min-width:0;padding:12px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7)}
.project-highlight-grid strong{display:block;margin-bottom:5px;color:var(--accent,var(--blue,#315a72));font-size:13px}
.project-highlight-grid p{margin:0;font-size:12px;line-height:1.6}
.project-code{margin:18px 0}
.project-code figcaption{font-weight:800}
.project-code pre{font-size:13px!important}
.starter-document-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:14px 0}
.starter-document-card{min-width:0;padding:15px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-top:4px solid var(--accent,var(--blue,#315a72));border-radius:8px}
.starter-document-card h4{margin:2px 0 10px;font-size:15px}
.starter-document-card>small{font:800 10px/1.4 ui-monospace,monospace;letter-spacing:.06em;color:var(--accent,var(--blue,#315a72))}
.starter-document-card ol{display:grid;gap:9px;margin:0;padding:0;list-style:none;counter-reset:docstep}
.starter-document-card li{position:relative;min-width:0;padding:9px 10px 9px 36px;background:var(--wash,#f2f3ef);border:1px solid var(--line,#d5d0c7);counter-increment:docstep}
.starter-document-card li:before{content:counter(docstep,decimal-leading-zero);position:absolute;left:10px;top:10px;color:var(--accent,var(--blue,#315a72));font:800 10px/1.4 ui-monospace,monospace}
.starter-document-card li strong{display:block;margin-bottom:3px;font-size:12px}
.starter-document-card li span{display:block;font-size:11px;line-height:1.5;color:var(--muted,#5f6d73)}
.starter-document-check{display:grid;grid-template-columns:auto minmax(0,1fr);align-items:start;gap:12px;padding:13px;background:color-mix(in srgb,var(--accent,#315a72) 8%,var(--white,#fffefa));border:1px solid var(--line,#d5d0c7)}
.starter-document-check strong{color:var(--accent,var(--blue,#315a72));font-size:13px}
.starter-document-check p{margin:0;font-size:12px;line-height:1.6}
.starter-decision-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:14px 0}
.starter-decision-card{min-width:0;padding:13px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7)}
.starter-decision-card strong{display:block;margin-bottom:5px;color:var(--accent,var(--blue,#315a72));font-size:13px}
.starter-decision-card p{margin:0;font-size:12px;line-height:1.6}
.webtoon-gallery .screen-shot img{display:block;width:100%;height:auto;max-height:300px;object-fit:contain;background:#f1f3f2}
.webtoon-gallery .screen-shot figcaption strong{display:block;margin-bottom:4px;color:var(--accent,var(--blue,#315a72));font-size:13px}
.webtoon-gallery .screen-shot figcaption span{display:block;font-size:11px;line-height:1.5}
.inheritance-flow-list{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin:0;padding:0;list-style:none}
.inheritance-flow-list li{position:relative;display:flex;min-width:0;flex-direction:column;gap:6px;padding:12px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-top:3px solid var(--accent,var(--blue,#315a72))}
.inheritance-flow-list li:not(:last-child):after{content:"→";position:absolute;right:-9px;top:42%;z-index:2;color:var(--accent,var(--blue,#315a72));font-size:14px;font-weight:900}
.inheritance-flow-list small{font:800 9px/1.4 ui-monospace,monospace;color:var(--accent,var(--blue,#315a72))}
.inheritance-flow-list strong{font-size:12px;line-height:1.4}
.inheritance-flow-list span{font-size:10px;line-height:1.5;color:var(--muted,#5f6d73)}
.ed-project-toc{display:grid;gap:3px;max-height:calc(100vh - 190px);overflow:auto;scrollbar-width:thin}
.ed-project-toc button{width:100%;padding:8px 0;border:0;border-top:1px solid #444;background:transparent;color:#e6e1d9;text-align:left;font-size:12px;line-height:1.45;font-weight:750;cursor:pointer}
.ed-project-toc button{padding:8px 10px;border-top:0;border-left:2px solid transparent;color:#536068}
.ed-project-toc button:hover,.ed-project-toc button[aria-current=location]{border-color:var(--accent);background:#f8f7f1;color:var(--ink)}
.ed-global-nav[hidden],.ed-project-toc[hidden]{display:none!important}
.project-case h3[id]{scroll-margin-top:100px}
.project-toc-link{overflow-wrap:anywhere}
.ed-profile-intro{display:grid;grid-template-columns:minmax(180px,.7fr) minmax(0,1.3fr);gap:clamp(20px,4vw,48px);padding:20px 0 30px;border-bottom:1px solid var(--line)}
.ed-profile-pull{align-self:start;padding:14px 18px;background:#e8ecea;border-left:4px solid var(--accent)}
.ed-profile-pull small,.ed-profile-index{font:800 10px/1.4 ui-monospace,monospace;letter-spacing:.1em;color:var(--accent)}
.ed-profile-pull p{margin:10px 0 0;font:700 clamp(18px,2.4vw,25px)/1.5 system-ui,sans-serif;letter-spacing:-.04em}
.ed-profile-prose{max-width:680px;font-size:16px;line-height:1.8}
.ed-profile-prose p:first-child{margin-top:0}
.ed-profile-columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 36px;margin-top:12px}
.ed-profile-columns>section{min-width:0;padding:22px 0;border-bottom:1px solid var(--line)}
.ed-profile-columns h2{margin:8px 0;font:800 22px/1.25 system-ui,sans-serif;letter-spacing:-.05em}
.ed-profile-columns p{margin:8px 0;color:#596166;font-size:13px;line-height:1.7}
.ed-profile-columns a{display:inline-block;margin-top:4px;color:var(--accent);font-size:12px;font-weight:850;text-decoration:underline;text-underline-offset:3px}
.screen-shot{min-width:0;margin:0;padding:8px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7)}
.screen-shot a{display:block}
.screen-shot img{display:block;width:100%;height:220px;object-fit:contain;background:#f1f3f2}
.screen-shot figcaption{padding:8px 2px 2px;font-size:11px;line-height:1.45}
.screen-link-card{display:flex;flex-direction:column;min-height:150px;padding:15px}
.screen-link-card strong{font-size:14px;color:var(--accent,var(--blue,#315a72))}
.screen-link-card p{margin:8px 0 14px;font-size:12px;line-height:1.55}
.screen-link-card a{margin-top:auto;font-weight:800}
.project-caption{margin:10px 0 0;font-size:12px;line-height:1.6;color:var(--muted,#5f6d73)}
.project-caption a{font-weight:800}
.architecture-main{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1.25fr);align-items:stretch;gap:10px}
.architecture-module{min-width:0;padding:13px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-radius:8px}
.architecture-module strong{display:block;margin:5px 0;font:850 17px/1.3 ui-monospace,monospace;color:var(--accent,var(--blue,#315a72));overflow-wrap:anywhere}
.architecture-module p{margin:0;font-size:12px;line-height:1.6}
.architecture-module small{display:block;margin-top:8px;color:var(--muted,#5f6d73);font:700 10px/1.4 ui-monospace,monospace}
.architecture-label{display:block;font:800 9px/1.4 ui-monospace,monospace;letter-spacing:.1em;color:var(--muted,#5f6d73)}
.architecture-arrow,.architecture-connect{align-self:center;text-align:center;color:var(--accent,var(--blue,#315a72));font:800 10px/1.4 ui-monospace,monospace}
.architecture-connect{margin:8px 0}
.architecture-connect:before{content:"↓ ";font-size:15px}
.architecture-adapters{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.architecture-backend{border-width:2px}
.spot-system-lane{margin-top:10px;padding:12px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-radius:8px}
.spot-system-lane h4{margin:0 0 9px;font-size:13px;line-height:1.4;color:var(--accent,var(--blue,#315a72))}
.spot-system-flow{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr) auto minmax(0,1fr);align-items:stretch;gap:8px}
.spot-ingestion-flow{grid-template-columns:minmax(0,1fr) auto minmax(0,1fr) auto minmax(0,1fr)}
.spot-insight-flow{grid-template-columns:minmax(0,1fr) auto minmax(0,1fr)}
.spot-system-node{display:flex;min-width:0;flex-direction:column;justify-content:center;padding:11px;background:var(--wash,#f2f3ef);border:1px solid var(--line,#d5d0c7);border-radius:6px}
.spot-system-node small{font:800 9px/1.4 ui-monospace,monospace;letter-spacing:.05em;color:var(--muted,#5f6d73)}
.spot-system-node strong{display:block;margin:4px 0;font-size:15px;line-height:1.35;color:var(--accent,var(--blue,#315a72));overflow-wrap:anywhere}
.spot-system-node p{margin:0;font-size:11px;line-height:1.55;overflow-wrap:anywhere}
.spot-system-arrow{align-self:center;color:var(--accent,var(--blue,#315a72));font-size:18px;font-weight:900}
.spot-system-note{margin:8px 0 0;color:var(--muted,#5f6d73);font-size:11px;line-height:1.55}
.usecase-layout{display:grid;grid-template-columns:120px minmax(0,1fr);gap:12px;align-items:stretch}
.usecase-actors{display:flex;flex-direction:column;justify-content:center;gap:8px}
.usecase-actor{display:grid;gap:2px;min-width:0;padding:9px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-radius:6px;text-align:center}
.usecase-actor small{font:800 9px/1.4 ui-monospace,monospace;letter-spacing:.06em;color:var(--muted,#5f6d73)}
.usecase-actor strong{font-size:13px;color:var(--accent,var(--blue,#315a72))}
.usecase-actor span{font-size:10px;line-height:1.4;color:var(--muted,#5f6d73)}
.usecase-system{min-width:0;padding:12px;border:2px dashed var(--line,#9eb2bd);border-radius:8px}
.usecase-system h4{margin:0 0 10px;font-size:13px;line-height:1.4}
.usecase-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.usecase-item{display:flex;min-width:0;min-height:82px;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:10px 14px;border:1px solid var(--accent,var(--blue,#315a72));border-radius:999px;background:var(--white,#fffefa);text-align:center}
.usecase-item strong{font-size:12px;line-height:1.4;overflow-wrap:anywhere}
.usecase-item small{font-size:10px;line-height:1.4;color:var(--muted,#5f6d73)}
.usecase-item--included{border-style:dashed;background:var(--wash,#f2f3ef)}
.starter-architecture-entry{display:grid;grid-template-columns:minmax(0,.8fr) auto minmax(0,1.2fr);align-items:stretch;gap:9px}
.starter-architecture-card{min-width:0;padding:13px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-radius:8px}
.starter-architecture-card strong{display:block;margin:5px 0;font-size:16px;line-height:1.35;color:var(--accent,var(--blue,#315a72));overflow-wrap:anywhere}
.starter-architecture-card p{margin:0;font-size:12px;line-height:1.6}
.starter-architecture-label{display:block;color:var(--muted,#5f6d73);font:800 10px/1.4 system-ui,sans-serif}
.starter-architecture-arrow{align-self:center;color:var(--accent,var(--blue,#315a72));font:800 12px/1.4 system-ui,sans-serif;text-align:center}
.starter-arrow-vertical{display:none}
.starter-connection-label{margin:11px 0 8px;text-align:center;font-size:12px;font-weight:800;color:var(--accent,var(--blue,#315a72))}
.starter-connection-label:after{content:"↓";display:block;margin-top:4px;font-size:18px;line-height:1}
.starter-module-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}
.starter-module-card{min-width:0;padding:12px;background:var(--wash,#f2f3ef);border:1px solid var(--line,#d5d0c7);border-radius:7px}
.starter-module-card strong{display:block;margin:4px 0;font-size:15px;color:var(--accent,var(--blue,#315a72));overflow-wrap:anywhere}
.starter-module-card p{margin:0;font-size:11px;line-height:1.55}
.starter-module-card small{display:block;margin-top:7px;font:700 10px/1.4 system-ui,sans-serif;color:var(--muted,#5f6d73)}
.starter-architecture-map{padding:18px}
.starter-request-path{display:grid;grid-template-columns:minmax(0,.9fr) auto minmax(0,1.1fr);align-items:stretch;gap:10px}
.starter-path-node{min-width:0;padding:14px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-radius:7px}
.starter-path-node small,.starter-module-card>small{display:block;color:var(--muted,#5f6d73);font:800 10px/1.4 system-ui,sans-serif}
.starter-path-node strong{display:block;margin:5px 0;font-size:16px;line-height:1.35;color:var(--accent,var(--blue,#315a72))}
.starter-path-node p{margin:0;font-size:12px;line-height:1.55}
.starter-path-node--backend{border:2px solid var(--accent,var(--blue,#315a72))}
.starter-path-arrow{align-self:center;color:var(--accent,var(--blue,#315a72));font-size:20px;font-weight:900}
.starter-port-label{margin:14px 0 8px;padding-top:12px;border-top:1px solid var(--line,#d5d0c7);text-align:center;color:var(--muted,#5f6d73);font-size:12px;font-weight:800}
.starter-module-grid--two{grid-template-columns:repeat(2,minmax(0,1fr))}
.starter-module-grid--two .starter-module-card strong{margin:5px 0;font-size:14px}
.starter-module-grid--two .starter-module-card span{display:block;margin-top:7px;color:var(--muted,#5f6d73);font-size:10px;line-height:1.5}
.starter-storage-summary{display:grid;grid-template-columns:auto minmax(0,1fr);gap:10px;margin-top:10px;padding:10px 12px;background:var(--wash,#f2f3ef);border-left:3px solid var(--accent,var(--blue,#315a72));font-size:11px;line-height:1.55}
.starter-storage-summary strong{color:var(--accent,var(--blue,#315a72))}
.storage-columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.storage-group{min-width:0;padding:12px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-radius:8px}
.storage-group h4{margin:0 0 9px;font-size:13px;line-height:1.4;color:var(--accent,var(--blue,#315a72))}
.storage-entity{display:grid;gap:3px;min-width:0;padding:8px;background:color-mix(in srgb,var(--wash,#edf2f3) 55%,var(--white,#fff));border:1px solid var(--line,#d5d0c7);border-radius:5px}
.storage-entity strong{font:800 11px/1.35 ui-monospace,monospace;overflow-wrap:anywhere}
.storage-entity span,.storage-group>p{font-size:11px;line-height:1.5;overflow-wrap:anywhere}
.storage-relation{padding:5px;text-align:center;color:var(--accent,var(--blue,#315a72));font:800 10px/1.4 system-ui,sans-serif}
.storage-pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}
.storage-local{grid-template-columns:repeat(2,minmax(0,1fr))}
.storage-note{margin:8px 0 0;color:var(--muted,#5f6d73)}
.taskflow-path{display:grid;grid-template-columns:minmax(0,.8fr) auto minmax(0,1fr) auto minmax(0,1.5fr);align-items:stretch;gap:8px}
.taskflow-step,.taskflow-gate{display:flex;min-width:0;flex-direction:column;justify-content:center;padding:12px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-radius:8px}
.taskflow-step small,.taskflow-gate>small{font:800 10px/1.4 system-ui,sans-serif;color:var(--muted,#5f6d73)}
.taskflow-step strong,.taskflow-gate>strong{display:block;margin:5px 0;font-size:14px;line-height:1.4;color:var(--accent,var(--blue,#315a72))}
.taskflow-step p{margin:0;font-size:11px;line-height:1.55}
.taskflow-arrow{align-self:center;color:var(--accent,var(--blue,#315a72));font-size:18px;font-weight:900}
.taskflow-outcomes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:7px}
.taskflow-outcome{min-width:0;padding:9px;background:var(--wash,#f2f3ef);border:1px solid var(--line,#d5d0c7);border-radius:6px}
.taskflow-outcome strong{display:block;margin-bottom:4px;font-size:12px}
.taskflow-outcome span{display:block;font-size:10px;line-height:1.45}
.taskflow-outcome--safe{border-left:4px solid #5b9b76}
.taskflow-outcome--stop{border-left:4px solid #bf5260}
.webtoon-pipeline{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));align-items:stretch;gap:8px}
.webtoon-stage{min-width:0;padding:12px;background:var(--white,#fffefa);border:1px solid var(--line,#d5d0c7);border-top:4px solid var(--accent,var(--blue,#315a72));border-radius:7px}
.webtoon-stage--team{border-top-color:#8b9294}
.webtoon-stage small{display:block;font:800 10px/1.4 system-ui,sans-serif;color:var(--muted,#5f6d73)}
.webtoon-stage strong{display:block;margin:5px 0;font-size:13px;line-height:1.4;overflow-wrap:anywhere}
.webtoon-stage p{margin:0;font-size:11px;line-height:1.5}
.webtoon-stage code{font-size:10px;overflow-wrap:anywhere}
.webtoon-stage--team small:after,.webtoon-stage--mine small:after{display:inline-block;margin-left:6px;padding:2px 5px;border:1px solid currentColor;border-radius:999px;font:800 9px/1.2 system-ui,sans-serif}
.webtoon-stage--team small:after{content:"팀 범위"}
.webtoon-stage--mine small:after{content:"내 구현"}
.webtoon-pipeline-arrow{display:none}
@media(max-width:760px){
 .project-facts{grid-template-columns:minmax(0,1fr)}
 .project-feature-list{grid-template-columns:minmax(0,1fr)}
 .contribution-lanes{grid-template-columns:minmax(0,1fr)}
 .screen-gallery,.screen-gallery-two{grid-template-columns:minmax(0,1fr)}
 .screen-shot img{height:auto;max-height:280px}
 .spot-screen-gallery .spot-screen-shot>a{aspect-ratio:auto;min-height:0}
 .spot-screen-gallery .spot-screen-shot img{height:auto;max-height:360px}
 .project-highlight-grid,.starter-document-grid,.starter-decision-grid{grid-template-columns:minmax(0,1fr)}
 .ed-profile-intro,.ed-profile-columns{grid-template-columns:minmax(0,1fr)}
 .starter-document-check{grid-template-columns:minmax(0,1fr);gap:5px}
 .webtoon-gallery .screen-shot img{max-height:360px}
 .inheritance-flow-list{grid-template-columns:minmax(0,1fr)}
 .inheritance-flow-list li:not(:last-child):after{content:"↓";right:12px;top:auto;bottom:-11px}
 .ed-project-toc{display:flex;max-width:100%;max-height:none;overflow-x:auto;overflow-y:hidden;gap:6px;scroll-snap-type:x proximity}
 .ed-project-toc button{flex:0 0 auto;width:auto;max-width:72vw;padding:7px 9px;border:1px solid #59616b;border-radius:4px;white-space:nowrap;scroll-snap-align:start}
 .ed-project-toc button{border-color:var(--line);background:var(--white)}
 .project-map .map-flow{flex-direction:column;align-items:stretch}
 .project-map .map-arrow{transform:rotate(90deg);align-self:center;line-height:1}
 .architecture-main{grid-template-columns:minmax(0,1fr)}
 .architecture-arrow{font-size:0}
 .architecture-arrow:after{content:"↓";font:800 16px/1 ui-monospace,monospace}
 .architecture-adapters,.storage-columns,.storage-pair,.storage-local,.starter-module-grid{grid-template-columns:minmax(0,1fr)}
 .starter-architecture-entry,.taskflow-path{grid-template-columns:minmax(0,1fr)}
 .starter-request-path{grid-template-columns:minmax(0,1fr)}
 .starter-path-arrow{justify-self:center;transform:rotate(90deg);line-height:1}
 .starter-module-grid--two{grid-template-columns:minmax(0,1fr)}
 .starter-storage-summary{grid-template-columns:minmax(0,1fr);gap:3px}
 .starter-architecture-arrow{justify-self:center;line-height:1}
 .starter-arrow-horizontal{display:none}
 .starter-arrow-vertical{display:inline}
 .taskflow-arrow{justify-self:center;transform:rotate(90deg);line-height:1}
 .taskflow-outcomes{grid-template-columns:minmax(0,1fr)}
 .webtoon-pipeline{grid-template-columns:minmax(0,1fr)}
 .webtoon-pipeline-arrow{display:block;justify-self:center;transform:rotate(90deg);color:var(--accent,var(--blue,#315a72));font-size:16px;font-weight:900;line-height:1}
 .spot-system-flow,.spot-ingestion-flow,.spot-insight-flow{grid-template-columns:minmax(0,1fr)}
 .spot-system-arrow{justify-self:center;transform:rotate(90deg);line-height:1}
 .usecase-layout{grid-template-columns:minmax(0,1fr)}
 .usecase-actors{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}
 .usecase-list{grid-template-columns:minmax(0,1fr)}
 .usecase-item{min-height:62px;border-radius:36px}
}

/* Home: let the specimen, not a greeting, introduce the archive. */
.ed-home-hero--specimen{grid-template-columns:minmax(190px,.38fr) minmax(0,1fr);gap:clamp(18px,3vw,36px);align-items:stretch;background:var(--paper-sand,#e9e0d4);padding:clamp(16px,2.6vw,30px)}
.ed-home-copy--specimen{display:flex;flex-direction:column;justify-content:center;min-width:0;padding:clamp(8px,1.6vw,20px) 0}
.ed-specimen-kicker{display:block;color:var(--accent-strong,#8e2942);font:800 10px/1.5 ui-monospace,monospace;letter-spacing:.14em}
.ed-specimen-title{margin:15px 0 12px;font:900 clamp(32px,5vw,62px)/.88 var(--sans,system-ui,sans-serif);letter-spacing:-.075em;overflow-wrap:anywhere}
.ed-specimen-title span{display:block;color:var(--accent-strong,#8e2942)}
.ed-specimen-note{max-width:25ch;margin:8px 0 0;color:var(--ink-soft,#514a50);font:14px/1.8 var(--serif,Georgia,serif)}
.ed-home-hero--specimen .ed-still-life{min-height:clamp(320px,45vw,500px);background:#28212f}
.ed-home-hero--specimen .ed-still-life svg{object-fit:cover}
.ed-home-hero--specimen .ed-still-caption{left:14px;right:14px;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}
.ed-rail-profile:before{content:"CONTACT / OPEN LETTER"}
.ed-rail-profile strong{margin-bottom:6px}
.ed-rail-profile a{display:inline-block;color:var(--ink,#292536);font:700 12px/1.6 ui-monospace,monospace;text-decoration:underline;text-decoration-color:var(--accent,#a42d49);text-underline-offset:3px;overflow-wrap:anywhere}
.ed-rail-profile a:hover{color:var(--accent-strong,#8e2942)}
.ed-home-link:nth-child(3) strong{letter-spacing:-.06em}

/* Project cards stay quiet until the pointer or keyboard selects them. */
.project-specimen,
.project-specimen:nth-child(3n + 2),
.project-specimen:nth-child(3n){background:var(--paper-white,#fffdf8);transition:transform .18s ease,box-shadow .18s ease,background .18s ease}
.project-specimen:hover,
.project-specimen:focus-visible,
.project-specimen:nth-child(3n + 2):hover,
.project-specimen:nth-child(3n):hover{background:linear-gradient(145deg,var(--paper-white,#fffdf8),var(--paper-lavender,#e8dfeb));transform:translateY(-3px);box-shadow:8px 10px 0 var(--shadow-soft,#46365725)}
.project-specimen:focus-visible{outline:2px solid var(--accent-strong);outline-offset:3px}

/* Project facts become a generous specimen label sheet. */
.project-reader .project-facts{gap:10px 12px;margin:28px 0 42px;padding:20px;background:var(--paper-sand,#eee6db);border:1px solid var(--line-strong,#c9bdcf);box-shadow:5px 6px 0 var(--shadow-soft,#46365718)}
.project-reader .project-facts>div{min-width:0;padding:14px 16px;background:var(--paper-white,#fffdf8);border:1px solid var(--line,#d8ced9);border-left:3px solid var(--accent-strong,#a42d49);border-radius:0}
.project-reader .project-facts dt{font-size:10px;letter-spacing:.13em}
.project-reader .project-facts dd{margin-top:6px;font-size:14px;line-height:1.7}

/* Blog: a compact title index above an ordinary card archive. */
.diary-index{display:block;padding:0;border:0}
.diary-title-index{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 28px;margin:0 0 32px;padding:0;border-top:1px solid var(--line-strong);list-style:none}
.diary-title-index li{min-width:0;border-bottom:1px solid var(--line)}
.diary-title-index a{display:grid;grid-template-columns:42px minmax(0,1fr);align-items:baseline;gap:10px;padding:11px 4px;color:var(--ink);text-decoration:none}
.diary-title-index a:hover .diary-title-index__title{color:var(--accent-strong);text-decoration:underline;text-underline-offset:4px}
.diary-title-index__number{color:var(--accent-strong);font:800 10px/1.5 var(--mono);letter-spacing:.1em}
.diary-title-index__title{min-width:0;font:700 14px/1.5 var(--sans);overflow-wrap:anywhere}
.diary-card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px 18px;padding:0}
.diary-entry{min-height:205px}
.diary-entry:first-child{grid-column:auto;min-height:205px;padding:17px 18px 15px;border-left:1px solid var(--line)}
.diary-entry__format{display:none!important}
.diary-entry__title{font-size:clamp(17px,2vw,22px)}
.diary-entry__read{margin-top:auto}

/* About keeps personal fragments separate from project and CV details. */
.ed-profile-pull small{letter-spacing:.14em}
.ed-profile-prose p{max-width:68ch}
.ed-profile-columns .ed-profile-learning{grid-column:1/-1}
.ed-profile-learning .ed-learning-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 20px;margin-top:14px;border-top:1px dashed var(--line)}
.ed-profile-learning .ed-learning-list p{margin:0;padding:12px 0 0}
.ed-profile-learning .ed-learning-list strong{color:var(--ink);font:800 14px/1.7 var(--sans)}
.ed-taste-tags{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 0;padding:0;list-style:none}
.ed-taste-tags li{max-width:100%;padding:7px 10px;background:var(--paper-sand,#eee6db);border:1px dashed var(--line-strong,#c9bdcf);font:700 12px/1.5 var(--serif);color:var(--ink-soft)}
@media(max-width:850px){
 .ed-home-hero--specimen{grid-template-columns:minmax(0,1fr)}
 .ed-home-copy--specimen{padding:8px 0 0}
 .ed-specimen-title{font-size:clamp(34px,9vw,56px)}
 .ed-home-hero--specimen .ed-still-life{min-height:clamp(270px,65vw,420px)}
}
@media(max-width:700px){
 .diary-title-index{grid-template-columns:minmax(0,1fr)}
 .diary-card-grid{grid-template-columns:minmax(0,1fr)}
 .project-reader .project-facts{grid-template-columns:minmax(0,1fr);padding:14px}
 .ed-profile-learning .ed-learning-list{grid-template-columns:minmax(0,1fr)}
}
/* project-content-v3:end */
"""

MOBILE_CASCADE_PATCH = r"""
.project-map figcaption{font:800 13px/1.5 system-ui,-apple-system,"Malgun Gothic","Noto Sans KR",sans-serif!important;letter-spacing:0!important}
.overview-map .map-flow{display:flex;min-width:0}
.overview-map .map-step{display:block;min-width:0}
@media(max-width:700px){
 .project-map .map-flow{flex-wrap:wrap}
 .project-map .map-step{flex:1 1 125px;min-width:0}
 .project-map .map-arrow{align-self:center}
 .markdown-table-wrap{min-width:0;max-width:100%;overflow-x:auto;overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch}
}
"""

FINAL_APPROVED_CSS = r"""
/* final-portfolio-polish:start */
@font-face{font-family:"Archive Sans";src:url("../noto-sans-cjk-kr.woff") format("woff");font-style:normal;font-weight:400;font-display:swap}
/* One consistent typeface across the site, including editorial labels. */
@font-face{font-family:"NEXON Lv1 Gothic";src:url("https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_20-04@2.1/NEXON%20Lv1%20Gothic%20OTF.woff") format("woff");font-style:normal;font-weight:400;font-display:swap}
@font-face{font-family:"NEXON Lv1 Gothic";src:url("https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_20-04@2.1/NEXON%20Lv1%20Gothic%20OTF%20Bold.woff") format("woff");font-style:normal;font-weight:700;font-display:swap}
:root{--archive-font:"NEXON Lv1 Gothic","Archive Sans","Malgun Gothic",sans-serif;--sans:var(--archive-font);--serif:var(--archive-font);--body:var(--sans);--title:var(--sans);--display:var(--sans);--mono:var(--sans)}
body{font-family:var(--sans);line-height:1.75}
body :not(pre):not(pre *):not(code):not(code *){font-family:var(--sans)!important}
pre,pre *,code,code *{font-family:ui-monospace,"SFMono-Regular",Consolas,monospace!important}

/* A single motion specimen occupies the main column's first viewport. */
@media(min-width:851px){
 .view[data-view="home"] .ed-home{height:100dvh;min-height:0;display:grid;grid-template-rows:auto minmax(0,1fr) auto;gap:18px;padding:26px 0 28px}
 .ed-home-hero--specimen{display:flex;min-height:0;overflow:hidden}
 .ed-home-hero--specimen .ed-collage-stage{flex:1 1 auto;width:100%;height:100%;min-height:0;aspect-ratio:auto}
}
.ed-home-hero--specimen{grid-template-columns:none;padding:12px;background:#28212f;box-shadow:7px 9px 0 var(--plum),0 0 0 3px var(--sun);transform:none}
.ed-home-hero--specimen::before,.ed-home-hero--specimen::after{display:none!important}
.ed-home-hero--specimen .ed-collage-stage{margin:0;transform:none;box-shadow:none;outline:0;outline-offset:0}
.ed-home-links{grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.ed-home-link{min-height:108px;padding:14px 17px;justify-content:space-between}
.ed-home-link strong{display:block;margin:14px 0 0;font-size:clamp(16px,1.9vw,21px);line-height:1.3;white-space:nowrap;letter-spacing:-.04em}

/* Each shelf card is plain until its own accent is revealed on hover. */
.project-specimen{--card-accent:var(--accent);--card-wash:#f8e4e4}
.project-specimen:nth-child(3n + 2){--card-accent:var(--sun);--card-wash:#fcf0cf}
.project-specimen:nth-child(3n){--card-accent:var(--plum);--card-wash:#ece0f1}
.project-specimen,.project-specimen:nth-child(3n + 2),.project-specimen:nth-child(3n){background:var(--paper-white)!important;border-top-color:var(--card-accent)!important}
.project-specimen:is(:hover,:focus-visible),.project-specimen:nth-child(3n + 2):is(:hover,:focus-visible),.project-specimen:nth-child(3n):is(:hover,:focus-visible){background:linear-gradient(155deg,var(--paper-white) 36%,var(--card-wash))!important;border-top-color:var(--card-accent)!important}
.project-index-note{max-width:80ch;font-size:15px;line-height:1.9}

/* Project metadata reads as four rows of a field ledger. */
.project-reader .project-facts{display:block;margin:27px 0 42px;padding:4px 24px;background:var(--paper-sand);border:1px solid var(--line-strong);border-top:4px solid var(--accent-strong);box-shadow:5px 6px 0 var(--shadow-soft)}
.project-reader .project-facts>div{display:grid;grid-template-columns:112px minmax(0,1fr);align-items:baseline;gap:16px;min-width:0;padding:17px 0;background:transparent;border:0;border-bottom:1px solid var(--line-strong)}
.project-reader .project-facts>div:last-child{border-bottom:0}
.project-reader .project-facts dt{color:var(--accent-strong);font-size:12px;font-weight:850;line-height:1.5;letter-spacing:.05em}
.project-reader .project-facts dd{margin:0;font-size:15px;line-height:1.75;overflow-wrap:anywhere}

/* A full-width numbered title list and, below it, equal two-column cards. */
.ed-blog-head::after{content:"NOTES"}
.diary-index{display:block;padding:0;border:0}
.diary-title-index{display:block;margin:0 0 29px;padding:0;border-top:1px solid var(--line-strong);list-style:none}
.diary-title-index li{border-bottom:1px solid var(--line)}
.diary-title-index a{display:grid;grid-template-columns:minmax(0,1fr) 44px;gap:20px;align-items:baseline;padding:14px 5px}
.diary-title-index__title{font-size:15px;font-weight:700;line-height:1.65;min-width:0}
.diary-title-index__number{justify-self:end;font-size:12px;line-height:1.65;color:var(--accent-strong)}
.diary-card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px 18px}
.diary-entry,.diary-entry:first-child{grid-column:auto;min-height:210px;padding:19px 20px 17px;border:1px solid var(--line);border-top:3px solid var(--accent)}
.diary-entry::before{display:none}
.diary-entry__title{font-size:clamp(18px,2vw,22px)}

/* Career and credentials first; personality in the bottom margin. */
.profile-archive-sheet{max-width:1050px}
.profile-archive-sheet>.ed-about-header{display:block;width:100%;max-width:none;margin:0 0 28px;padding:0 0 21px;background:transparent;clip-path:none;transform:none;border-bottom:2px solid var(--ink)}
.profile-archive-sheet>.ed-about-header h1{margin:5px 0 4px;font-size:clamp(30px,4vw,45px);line-height:1.1;letter-spacing:-.065em}
.ed-about-header p{margin:5px 0 0;color:var(--ink-soft);font-size:14px}
.ed-about-facts{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(260px,1fr);gap:17px;align-items:start}
.ed-about-facts>section{min-width:0;padding:19px 21px;background:var(--paper-white);border:1px solid var(--line);border-top:4px solid var(--plum)}
.ed-about-experience{grid-row:span 2}
.ed-about-facts h2{margin:8px 0 14px;font-size:22px;line-height:1.25;letter-spacing:-.04em}
.ed-about-help{margin:-4px 0 13px;font-size:12px;line-height:1.7;color:var(--ink-soft)}
.ed-about-records,.ed-credential-list,.ed-learning-records{margin:0;padding:0;list-style:none}
.ed-about-records li{display:grid;grid-template-columns:minmax(105px,.8fr) minmax(125px,1fr);gap:3px 10px;padding:12px 0;border-top:1px solid var(--line)}
.ed-about-records strong{font-size:13px;line-height:1.5}
.ed-about-records li>span{font-size:12px;line-height:1.6;color:var(--ink-soft)}
.ed-about-records time{grid-column:1/-1;font-size:11px;color:var(--accent-strong)}
.ed-credential-list{display:flex;flex-wrap:wrap;gap:8px}
.ed-credential-list li{padding:7px 10px;background:var(--paper-sand);border:1px solid var(--line-strong);font-size:12px;line-height:1.5;font-weight:700}
.ed-learning-records li{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:4px 12px;padding:10px 0;border-top:1px solid var(--line)}
.ed-learning-records strong{font-size:13px;font-weight:750}
.ed-learning-records span{font-size:11px;white-space:nowrap;color:var(--accent-strong)}
.ed-about-personal{margin-top:28px;padding-top:25px;border-top:2px dashed var(--line-strong)}
.ed-about-personal>header small{font-size:10px;font-weight:850;letter-spacing:.12em;color:var(--accent-strong)}
.ed-about-personal>header h2{margin:5px 0 17px;font-size:25px;line-height:1.3;letter-spacing:-.045em}
.profile-archive-sheet .ed-about-personal .ed-profile-columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:0}
.profile-archive-sheet .ed-about-personal .ed-profile-columns>section{padding:19px 21px}
.profile-archive-sheet .ed-about-personal h3{margin:9px 0 11px;font-size:20px;line-height:1.35;letter-spacing:-.045em}
.profile-archive-sheet .ed-about-personal p{margin:0;font-size:14px;line-height:1.85;color:var(--ink-soft)}

@media(max-width:850px){
 .view[data-view="home"] .ed-home{height:auto;display:flex;flex-direction:column;gap:18px;padding:34px 0 72px}
 .ed-home-hero--specimen{display:flex;min-height:0}
 .ed-home-hero--specimen .ed-collage-stage{width:100%;height:auto;min-height:0;aspect-ratio:720/500}
 .ed-about-facts{grid-template-columns:minmax(0,1fr)}
 .ed-about-experience{grid-row:auto}
}
@media(max-width:700px){
 .project-reader .project-facts{padding:5px 16px}
 .project-reader .project-facts>div{grid-template-columns:minmax(0,1fr);gap:4px;padding:13px 0}
 .project-reader .project-facts dd{font-size:14px}
 .diary-card-grid,.profile-archive-sheet .ed-about-personal .ed-profile-columns{grid-template-columns:minmax(0,1fr)}
 .ed-home-links{grid-template-columns:repeat(2,minmax(0,1fr))}
 .ed-home-link:last-child{grid-column:1/-1}
}
@media(max-width:520px){
 .ed-home-links{grid-template-columns:minmax(0,1fr)}
 .ed-home-link:last-child{grid-column:auto}
 .ed-home-link{min-height:100px}
 .ed-home-hero--specimen{padding:7px}
 .ed-home-hero--specimen .ed-collage-stage{aspect-ratio:1/1}
 .diary-title-index a{gap:10px;padding:12px 1px}
 .diary-title-index__title{font-size:13px;line-height:1.6}
 .ed-about-records li{grid-template-columns:minmax(0,1fr)}
 .ed-about-records time{grid-column:auto}
 .ed-about-facts>section{padding:17px 15px}
}
/* final-portfolio-polish:end */
"""

TYPOGRAPHY_CSS = r"""
/* approved-font-roles:start — do not introduce extra fonts inside prose */
/* Editorial headings: page names, project names, and article cards. */
body :is(.ed-section-label h1,.ed-reader-head h1,.ed-blog-head h1,.diary-reader-head h1,.specimen-title,.diary-entry__title,.ed-home-link strong,.ed-about-facts h2,.ed-about-personal>header h2,.profile-archive-sheet>.ed-about-header h1){font-family:var(--title)!important;font-weight:700;letter-spacing:-.045em}
/* Body text, UI labels, and headings all use Nexon Lv.1 Gothic. */
body :is(.project-index-note,.specimen-description,.project-reader .project-lede,.ed-blog-head p,.diary-entry__excerpt,.ed-about-header p,.ed-about-help,.ed-profile-pull p,.ed-profile-prose p,.ed-profile-columns p,.profile-archive-sheet .ed-about-facts p,.profile-archive-sheet .ed-about-personal p){font-family:var(--body)!important}
body :is(.project-index-note,.specimen-description,.project-reader .project-lede,.ed-blog-head p,.diary-entry__excerpt,.ed-about-header p,.ed-about-help,.ed-profile-pull p,.ed-profile-prose p,.ed-profile-columns p,.profile-archive-sheet .ed-about-facts p,.profile-archive-sheet .ed-about-personal p) :is(a,strong,span,em,b,small){font-family:var(--body)!important}
body :is(.project-reader .case-copy,.diary-reader .markdown-body) :is(p,li,blockquote,figcaption,td,dd){font-family:var(--body)!important}
body :is(.project-reader .case-copy,.diary-reader .markdown-body) :is(p,li,blockquote,figcaption,td,dd) :is(a,strong,span,em,b,small){font-family:var(--body)!important}
/* The project/article body, its subsection headings, UI controls, and metadata remain in one sans family. */
body :is(.project-reader .case-copy h3,.diary-reader .markdown-body h1,.diary-reader .markdown-body h2,.diary-reader .markdown-body h3,.ed-about-personal h3,.profile-archive-sheet .ed-about-facts p,.project-reader .project-facts dt,.project-reader .project-facts dd){font-family:var(--sans)!important}
/* A few editorial labels retain their spacing, but use the same Nexon family. */
body :is(.specimen-footer>span:last-child,.diary-entry__folio,.diary-title-index__number,.ed-about-personal>header small){font-family:var(--display)!important;font-weight:400;letter-spacing:.02em}
body .ed-blog-head::after{font-family:var(--display)!important;font-weight:400;letter-spacing:.04em}
/* Keep generous line-height on large Korean headings. */
body .ed-section-label h1,body .profile-archive-sheet>.ed-about-header h1{line-height:1.17}
body .specimen-title{line-height:1.27}
/* approved-font-roles:end */

/* font-pair-home:start */
/* A/B type study: body remains NEXON; only editorial/display headings switch. */
@font-face{font-family:"Jalnan Gothic";src:url("https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_231029@1.1/JalnanGothic.woff") format("woff");font-style:normal;font-weight:400;font-display:swap}
@font-face{font-family:"Bithumb Gothic Basic";src:url("https://cdn.jsdelivr.net/gh/Project-Noonnu/2610082345@basic/basic/Bithumb%20Gothic%20Basic.woff2") format("woff2");font-style:normal;font-weight:700;font-display:swap}
body[data-font-pair="A"]{--title:"Jalnan Gothic",var(--sans)}
body[data-font-pair="B"]{--title:"Bithumb Gothic Basic",var(--sans)}
body :is(.ed-type-sample__title,.ed-section-label h1,.ed-reader-head h1,.ed-blog-head h1,.diary-reader-head h1,.specimen-title,.diary-entry__title,.ed-about-facts h2,.ed-about-personal>header h2,.ed-about-personal h3,.profile-archive-sheet>.ed-about-header h1){font-family:var(--title)!important}
.ed-rail{gap:24px}
.ed-type-lab{position:relative;z-index:3;margin-top:0;color:#302b3a}
.ed-type-lab__top{display:flex;align-items:center;justify-content:space-between;gap:6px;margin-bottom:8px}
.ed-type-lab__label{font:800 9px/1.3 ui-monospace,monospace;letter-spacing:.14em;color:#9b304b}
.ed-type-lab__current{font:700 8px/1.3 ui-monospace,monospace;letter-spacing:.04em;color:#746a7b;text-align:right}
.ed-type-switch{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}
.ed-type-switch button{display:flex;align-items:center;gap:7px;min-width:0;padding:8px 8px;border:1px solid #cfc4d5;background:#fffaf1;color:#383145;box-shadow:2px 3px 0 #46365716;cursor:pointer;text-align:left;transition:background .16s,border-color .16s,transform .16s}
.ed-type-switch button strong{display:grid;place-items:center;flex:0 0 23px;width:23px;height:23px;background:#e8dfec;color:#463657;font:800 11px/1 ui-monospace,monospace}
.ed-type-switch button span{font:700 9px/1.25 var(--sans);white-space:nowrap;letter-spacing:-.03em}
.ed-type-switch button[aria-pressed="true"]{background:#3b3044;border-color:#3b3044;color:#fffaf1;transform:translateY(-1px);box-shadow:3px 4px 0 #46365730}
.ed-type-switch button[aria-pressed="true"] strong{background:#efca59;color:#302b3a}
.ed-type-sample{min-height:104px;margin-top:9px;padding:10px 11px 9px;background:#fffaf1;border:1px solid #d2c8d5;box-shadow:3px 4px 0 #46365718;clip-path:polygon(0 1%,98% 0,100% 94%,95% 100%,2% 98%)}
.ed-type-sample>small{display:block;margin-bottom:6px;color:#9b304b;font:700 8px/1.3 ui-monospace,monospace;letter-spacing:.06em}
.ed-type-sample__title{display:block;margin:0;color:#302b3a;font-size:17px;font-weight:700;line-height:1.35;letter-spacing:-.045em;overflow-wrap:anywhere}
.ed-type-sample__body{margin:5px 0 0;color:#61596a;font:11px/1.55 var(--sans)!important;letter-spacing:-.02em}

/* D-direction Home: the artwork, not a framed card, fills the entire main viewport. */
.view[data-view="home"]{height:100dvh;min-height:0;overflow:hidden}
.view[data-view="home"] .ed-home{width:100%;max-width:none;height:100dvh;min-height:0;margin:0;padding:0;display:block}
.view[data-view="home"] .ed-content:before{display:none!important}
.ed-home-hero--specimen{position:relative;display:block;width:100%;height:100%;min-height:0;margin:0;padding:0;overflow:hidden;background:#28212f;border:0;clip-path:none;box-shadow:none;transform:none}
.ed-home-hero--specimen::before,.ed-home-hero--specimen::after{display:none!important}
.ed-home-hero--specimen .ed-collage-stage{display:block;width:100%;height:100%;min-height:0;margin:0;aspect-ratio:auto;overflow:hidden;background:#28212f;border:0;outline:0;outline-offset:0;box-shadow:none;transform:none}
.ed-home-hero--specimen .ed-collage-stage::before,.ed-home-hero--specimen .ed-collage-stage::after{display:none!important}
.ed-home-hero--specimen .ed-collage-stage svg{display:block;width:100%;height:100%;max-width:none;object-fit:cover}
@media(max-width:850px){
 .ed-rail{gap:11px}
 .ed-type-lab{margin-top:0}
 .ed-type-lab__top{margin-bottom:6px}
 .ed-type-sample{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);align-items:center;gap:4px 12px;min-height:0;padding:8px 10px}
 .ed-type-sample>small{grid-column:1/-1;margin:0}
 .ed-type-sample__title{font-size:16px}
 .ed-type-sample__body{margin:0;font-size:10px!important}
 .view[data-view="home"]{height:calc(100svh - var(--rail-height,150px));min-height:0}
 .view[data-view="home"] .ed-home{height:100%;min-height:0}
 .ed-home-hero--specimen,.ed-home-hero--specimen .ed-collage-stage{height:100%;min-height:0}
 .ed-home-hero--specimen .ed-collage-stage{aspect-ratio:auto}
}
@media(max-width:520px){
 .ed-type-switch button{padding:7px 8px}
 .ed-type-sample__title{font-size:15px}
 .ed-type-sample__body{font-size:10px!important}
}
@media(prefers-reduced-motion:reduce){.ed-type-switch button{transition:none!important}}
/* font-pair-home:end */
"""


def replace_template(source: str, slug: str, fragment: str) -> str:
    pattern = re.compile(
        r'<template id="tpl-' + re.escape(slug) + r'">.*?</template>', re.DOTALL
    )
    fragment = highlight_project_code(fragment)
    wrapped = f'<template id="tpl-{slug}">{fragment.strip()}</template>'
    updated, count = pattern.subn(lambda _: wrapped, source, count=1)
    if count == 0:
        anchor = '<script id="blog-posts-data"'
        if anchor not in source:
            raise RuntimeError("프로젝트 템플릿을 삽입할 블로그 데이터 위치를 찾지 못했습니다.")
        updated = source.replace(anchor, wrapped + "\n" + anchor, 1)
    elif count != 1:
        raise RuntimeError(f"프로젝트 템플릿이 중복되어 있습니다: {slug}")
    return updated


def highlight_project_code(fragment: str) -> str:
    """Apply the same Pygments token colors used by Markdown code blocks."""
    def replace(match):
        language = match.group(2).lower()
        try:
            lexer = get_lexer_by_name(language, stripnl=False, ensurenl=False)
        except ClassNotFound:
            return match.group(0)
        code = unescape(match.group(3))
        highlighted = pygments_highlight(code, lexer, PROJECT_CODE_FORMATTER)
        return match.group(1) + highlighted + match.group(4)

    return PROJECT_CODE_PATTERN.sub(replace, fragment)


def replace_project_index(source: str) -> str:
    entries = "".join(
        f'<a class="project-specimen" href="#project/{html_escape(slug, quote=True)}" aria-label="{html_escape(title, quote=True)} 기록 열기">'
        f'<span class="specimen-topline"><span>OBJECT / {index:02d}</span><span aria-hidden="true">↗</span></span>'
        f'<span class="specimen-kind">{html_escape(kind)}</span>'
        f'<strong class="specimen-title">{html_escape(title)}</strong>'
        f'<span class="specimen-description">{html_escape(blurb)}</span>'
        f'<span class="specimen-footer"><span>OPEN RECORD</span><span>NO. {index:02d}</span></span></a>'
        for index, (slug, title, kind, blurb) in enumerate(PROJECT_INDEX, 1)
    )
    block = (
        '<section class="view" data-view="projects" hidden><div class="ed-content project-index-page">'
        '<header class="ed-section-label"><small>INDEX / 06 · OBJECTS</small><h1>프로젝트 서가</h1></header>'
        '<p class="ed-index-note project-index-note">문제의 모양이 달랐던 만큼, 해답을 찾아가는 경로도 같지 않았습니다. 각자의 출발점에서 선택하고 고쳐온 것들을 하나의 기록으로 묶었습니다.</p>'
        f'<nav class="project-shelf" data-project-index aria-label="프로젝트 표본 목록">{entries}</nav>'
        '</div></section>'
    )
    pattern = re.compile(r'<section class="view" data-view="projects" hidden>.*?</section>', re.DOTALL)
    updated, count = pattern.subn(lambda _: block, source, count=1)
    if count != 1:
        raise RuntimeError("프로젝트 목록을 하나 찾지 못했습니다.")
    return updated


def ensure_project_toc_markup(source: str) -> str:
    # Rebuild the shell to eliminate stale or malformed sidebar markup.
    pattern = re.compile(r'<body[^>]*>.*?<div class="ed-shell">.*?<main class="ed-main"[^>]*>', re.DOTALL)
    replacement = '''<body data-direction="editorial" data-font-pair="A">
<a class="skip-link" href="#main-content">본문으로 건너뛰기</a>
<div class="ed-shell">
<aside class="ed-rail">
<a class="ed-brand" href="#home">김수빈<small>PERSONAL ARCHIVE / FIELD NOTES</small></a>
<nav class="ed-nav" id="ed-global-nav" aria-label="주요 메뉴">
<a data-route-link href="#home">HOME</a>
<a data-route-link href="#projects">PROJECTS</a>
<a data-route-link href="#blog">BLOG</a>
<a data-route-link href="#about">ABOUT</a>
</nav>
<section class="ed-type-lab" aria-label="서체 조합 A/B 비교">
  <div class="ed-type-lab__top">
    <span class="ed-type-lab__label">TYPE STUDY</span>
    <span class="ed-type-lab__current" data-type-pair-label>A · JALNAN GOTHIC</span>
  </div>
  <div class="ed-type-switch" role="group" aria-label="비교할 제목 서체 선택">
    <button type="button" data-font-pair-choice="A" aria-pressed="true"><strong>A</strong><span>잘난체 고딕</span></button>
    <button type="button" data-font-pair-choice="B" aria-pressed="false"><strong>B</strong><span>빗썸 Basic</span></button>
  </div>
  <div class="ed-type-sample" aria-live="polite">
    <small>같은 문장 · 같은 크기</small>
    <strong class="ed-type-sample__title">분류되지 않은 조각들</strong>
    <p class="ed-type-sample__body">오래 마음에 남은 것들을 모으고, 시간이 지난 뒤 다시 펼쳐 봅니다.</p>
  </div>
</section>
<nav id="ed-project-toc" class="ed-project-toc project-toc-nav" data-project-toc aria-label="현재 프로젝트 목차" hidden></nav>
<div class="ed-rail-profile"><strong>CONTACT</strong><a href="mailto:wesbeen.k@gmail.com">wesbeen.k@gmail.com ↗</a></div>
</aside>
<main class="ed-main" id="main-content" tabindex="-1">'''
    updated, count = pattern.subn(lambda _: replacement, source, count=1)
    if count != 1:
        raise RuntimeError("아카이브의 body/sidebar/main 구조를 찾지 못했습니다.")
    return updated


def update_project_router(source: str) -> str:
    slugs = [item[0] for item in PROJECT_INDEX]
    source, count = re.subn(
        r"const projectSlugs=\[[^\]]*\];",
        "const projectSlugs=" + json.dumps(slugs, ensure_ascii=False) + ";",
        source,
        count=1,
    )
    if count != 1:
        raise RuntimeError("프로젝트 라우터 목록을 하나 찾지 못했습니다.")
    route_hook = "if(route.startsWith('project/'))buildProjectTOC(activeProject);else clearProjectTOC();"
    # Replace the complete route-hook slot, including its surrounding whitespace,
    # so repeated builds do not accumulate blank lines.
    route_anchor = "document.body.dataset.route=route.startsWith('project/')?'detail':route.startsWith('post/')?'post-detail':route;"
    route_slot = re.compile(
        re.escape(route_anchor)
        + r"(?:\s*" + re.escape(route_hook) + r")?\s*(?=let restoreY=)"
    )
    replacement = route_anchor + "\n  " + route_hook + "\n  "
    source, count = route_slot.subn(lambda _: replacement, source, count=1)
    if count != 1:
        raise RuntimeError("프로젝트 목차 호출 위치를 찾지 못했습니다.")
    toc_helpers = r'''let projectTocObserver=null;
 function buildProjectTOC(root){
  const toc=document.querySelector('[data-project-toc]'),globalNav=document.getElementById('ed-global-nav');
  if(!toc)return;
  if(projectTocObserver){projectTocObserver.disconnect();projectTocObserver=null}
  toc.replaceChildren();
  const headings=[...root.querySelectorAll('.case-copy h3')];
  headings.forEach((heading,index)=>{
   const label=heading.textContent.trim().replace(/\s+/g,' ');
   if(!heading.id){const base=label.toLowerCase().replace(/[^\p{L}\p{N}]+/gu,'-').replace(/^-|-$/g,'')||'section';heading.id='project-section-'+base+'-'+(index+1)}
   heading.tabIndex=-1;
   const button=document.createElement('button');button.type='button';button.className='project-toc-link';button.dataset.tocTarget=heading.id;button.textContent=label;toc.append(button);
  });
  toc.hidden=headings.length===0;
  if(globalNav)globalNav.hidden=headings.length>0;
  if(!headings.length||!('IntersectionObserver' in window))return;
  projectTocObserver=new IntersectionObserver(entries=>{
   const active=entries.filter(entry=>entry.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top)[0];
   if(!active)return;
   let activeButton=null;
   toc.querySelectorAll('button').forEach(button=>{
    if(button.dataset.tocTarget===active.target.id){
     if(!button.hasAttribute('aria-current'))activeButton=button;
     button.setAttribute('aria-current','location');
    }else button.removeAttribute('aria-current');
   });
   if(activeButton){const containerRect=toc.getBoundingClientRect(),itemRect=activeButton.getBoundingClientRect();if(itemRect.left<containerRect.left)toc.scrollLeft-=containerRect.left-itemRect.left;else if(itemRect.right>containerRect.right)toc.scrollLeft+=itemRect.right-containerRect.right;if(itemRect.top<containerRect.top)toc.scrollTop-=containerRect.top-itemRect.top;else if(itemRect.bottom>containerRect.bottom)toc.scrollTop+=itemRect.bottom-containerRect.bottom;}
  },{rootMargin:'-18% 0px -72% 0px',threshold:0});
  headings.forEach(heading=>projectTocObserver.observe(heading));
 }
 function clearProjectTOC(){
  if(projectTocObserver){projectTocObserver.disconnect();projectTocObserver=null}
  const toc=document.querySelector('[data-project-toc]'),globalNav=document.getElementById('ed-global-nav');
  if(toc){toc.replaceChildren();toc.hidden=true}
  if(globalNav)globalNav.hidden=false;
 }
 document.addEventListener('click',event=>{
  const button=event.target.closest('[data-toc-target]');if(!button)return;
  const target=document.getElementById(button.dataset.tocTarget);if(!target)return;
  target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  target.focus({preventScroll:true});
 });
'''
    anchor = " function current(){return(location.hash||'#home').slice(1)}"
    if anchor not in source:
        raise RuntimeError("프로젝트 목차 코드를 넣을 라우터 위치를 찾지 못했습니다.")
    # Remove every generated copy, including duplicates left by earlier builds,
    # then insert the canonical helper block once.
    source = re.sub(
        r"let projectTocObserver=null;.*?(?= function current\(\)\{return\(location.hash\|\|'#home'\)\.slice\(1\)\})",
        "",
        source,
        flags=re.DOTALL,
    )
    source = source.replace(anchor, toc_helpers + anchor, 1)
    return source


def replace_styles(source: str) -> str:
    project_block = re.compile(
        r"\s*" + re.escape(STYLE_START) + r".*?" + re.escape(STYLE_END) + r"\s*",
        re.DOTALL,
    )
    source = project_block.sub("\n", source)
    # Earlier builds placed About/Home overrides outside STYLE_END. The
    # canonical block is removed first; only orphaned legacy tails remain.
    source = re.sub(
        r"\n/\* Home: let the specimen, not a greeting, introduce the archive\. \*/"
        r".*?(?=\n(?:/\* project-content-v3:start \*/|/\* phase-layer:project-components \*/))",
        "",
        source,
        flags=re.DOTALL,
    )
    anchor = "/* phase-layer:project-components */"
    if source.count(anchor) != 1:
        raise RuntimeError("프로젝트 컴포넌트 CSS 삽입 위치를 찾지 못했습니다.")
    return source.replace(anchor, PROJECT_CSS.strip() + "\n\n" + anchor, 1)


def update_starter_kit_labels(source: str) -> str:
    source = source.replace(
        "<strong>상속길잡이 AI 스타터킷</strong>",
        "<strong>AI Starter Kit</strong>",
    )
    return source.replace(">상속길잡이 AI 스타터킷</a>", ">AI Starter Kit</a>")


def update_job_process_labels(source: str) -> str:
    return source.replace(
        "<small>개인 프로젝트, 개발 중단</small>",
        "<small>개인 프로젝트</small>",
    )


def replace_mobile_cascade_patch(source: str) -> str:
    marker = re.compile(
        r"\s*/\* mobile-cascade-patch:start \*/.*?/\* mobile-cascade-patch:end \*/\s*",
        re.DOTALL,
    )
    source = marker.sub("\n", source)
    source, count = re.subn(
        r"\.project-map \.map-flow,\s*\.project-map \.map-step\{display:none\}",
        "",
        source,
    )
    if count > 1:
        raise RuntimeError(f"화살표만 남기는 구형 도식 규칙이 중복되어 있습니다: {count}")
    patch = (
        "\n/* mobile-cascade-patch:start */\n"
        + MOBILE_CASCADE_PATCH.strip()
        + "\n/* mobile-cascade-patch:end */\n"
    )
    return source.rstrip() + patch


def replace_final_styles(source: str) -> str:
    marker = re.compile(
        r"\s*/\* final-portfolio-polish:start \*/.*?/\* final-portfolio-polish:end \*/\s*",
        re.DOTALL,
    )
    source = marker.sub("\n", source)
    typography_marker = re.compile(
        r"\s*/\* approved-font-roles:start.*?/\* approved-font-roles:end \*/\s*",
        re.DOTALL,
    )
    source = typography_marker.sub("\n", source)
    font_pair_marker = re.compile(
        r"\s*/\* font-pair-home:start \*/.*?/\* font-pair-home:end \*/\s*",
        re.DOTALL,
    )
    source = font_pair_marker.sub("\n", source)
    return source.rstrip() + "\n" + FINAL_APPROVED_CSS.strip() + "\n" + TYPOGRAPHY_CSS.strip() + "\n"


def main() -> None:
    fragments = {
        source.stem: source.read_text(encoding="utf-8")
        for source in sorted(PROJECTS_DIR.glob("*.html"))
    }
    if set(fragments) != set(PROJECT_BLURBS):
        raise RuntimeError("프로젝트 원고 파일 구성이 예상과 다릅니다.")

    if not HTML_FILE.exists():
        raise FileNotFoundError(HTML_FILE)
    source = HTML_FILE.read_text(encoding="utf-8")
    if not CSS_FILE.exists():
        raise FileNotFoundError(CSS_FILE)
    if not APP_JS_FILE.exists():
        raise FileNotFoundError(APP_JS_FILE)
    styles = CSS_FILE.read_text(encoding="utf-8")
    app_js = APP_JS_FILE.read_text(encoding="utf-8")
    for slug, fragment in fragments.items():
        source = replace_template(source, slug, fragment)
    # The specimen shelf is regenerated from PROJECT_INDEX in one pass;
    # do not patch blurbs into the previous index markup (which is no longer
    # the legacy .ed-entry structure).
    source = replace_project_index(source)
    source = ensure_project_toc_markup(source)
    app_js = update_project_router(app_js)
    source = update_starter_kit_labels(source)
    source = update_job_process_labels(source)
    styles = replace_styles(styles)
    styles = replace_mobile_cascade_patch(styles)
    styles = replace_final_styles(styles)
    HTML_FILE.write_text(source, encoding="utf-8")
    CSS_FILE.write_text(styles, encoding="utf-8")
    APP_JS_FILE.write_text(app_js, encoding="utf-8")
    print(f"프로젝트 {len(PROJECT_INDEX)}개 소개를 {HTML_FILE.name}에 반영했습니다.")


if __name__ == "__main__":
    main()
