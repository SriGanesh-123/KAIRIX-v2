import { useState, type ReactNode } from "react";
import {
  Activity, ArrowDown, ArrowRight, ArrowUpRight, Bell, BookOpen, Boxes,
  BrainCircuit, CheckCircle2, ChevronDown, CircleDashed, Code2, Command,
  Database, FileCode2, FileSearch, FileText, GitBranch, Info, Layers3,
  LockKeyhole, Network, Search, Settings2, UploadCloud, Waypoints, Workflow
} from "lucide-react";
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle, Input, Textarea } from "@/components/ui";

type PageKey="overview"|"investigation"|"sources"|"pipeline"|"graph";
const navItems:{key:PageKey;label:string;hint:string;icon:typeof Activity}[]=[
  {key:"overview",label:"Overview",hint:"Workspace health",icon:Activity},
  {key:"investigation",label:"Investigation",hint:"Ask your codebase",icon:BrainCircuit},
  {key:"sources",label:"Source explorer",hint:"Browse legacy assets",icon:Code2},
  {key:"pipeline",label:"Pipeline",hint:"Knowledge extraction",icon:Workflow},
  {key:"graph",label:"Knowledge graph",hint:"Trace relationships",icon:Network}
];
const pageTitles:Record<PageKey,string>={overview:"Workspace overview",investigation:"Investigation",sources:"Source explorer",pipeline:"Knowledge pipeline",graph:"Knowledge graph"};

function Sidebar({active,onNavigate}:{active:PageKey;onNavigate:(key:PageKey)=>void}){
  return <aside className="sidebar-shell fixed inset-y-0 left-0 z-30 flex w-[248px] flex-col px-4 py-5 text-[#f2f0e9] max-md:w-[68px] max-md:px-2">
    <div className="sidebar-brand flex items-center gap-3 px-2">
      <div className="brand-mark flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[#b9f12f] text-[#0b3048]"><Boxes size={23} strokeWidth={2.2}/></div>
      <div className="sidebar-brand-copy"><p className="font-display text-[18px] font-extrabold tracking-[.16em]">KAIRIX</p><p className="mt-0.5 text-[9px] font-semibold uppercase tracking-[.22em] text-[#f2f0e9]/40">Legacy intelligence</p></div>
    </div>
    <div className="sidebar-caption mt-10 px-3 text-[10px] font-bold uppercase tracking-[.2em] text-[#f2f0e9]/35">Workspace</div>
    <nav aria-label="Primary navigation" className="sidebar-nav mt-3 flex flex-col gap-1.5 max-md:mt-8">
      {navItems.map(item=>{const Icon=item.icon;const selected=active===item.key;return <button key={item.key} type="button" onClick={()=>onNavigate(item.key)} aria-current={selected?"page":undefined} title={item.label} className={"group flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left transition-all duration-200 "+(selected?"bg-[#b9f12f] text-[#0b3048] shadow-[0_8px_22px_rgba(0,0,0,.16)]":"text-[#f2f0e9]/65 hover:bg-white/[.06] hover:text-[#f2f0e9]")}>
        <Icon size={17} strokeWidth={selected?2.4:1.8}/>
        <span className="sidebar-label min-w-0 flex-1"><span className="block text-[13px] font-semibold">{item.label}</span><span className={"sidebar-hint mt-0.5 block text-[10px] "+(selected?"text-[#0b3048]/60":"text-[#f2f0e9]/30")}>{item.hint}</span></span>
        {selected&&<span className="h-1.5 w-1.5 rounded-full bg-[#0b3048] max-md:hidden"/>}
      </button>})}
    </nav>
    <div className="sidebar-secondary mt-9">
      <div className="px-3 text-[10px] font-bold uppercase tracking-[.2em] text-[#f2f0e9]/35">Platform</div>
      <div className="mt-3 flex items-center gap-3 rounded-xl px-3 py-3 text-[#f2f0e9]/45"><Database size={16}/><span className="text-xs font-medium">Data connections</span><span className="ml-auto h-1.5 w-1.5 rounded-full bg-[#b9f12f]/70"/></div>
      <div className="flex items-center gap-3 rounded-xl px-3 py-3 text-[#f2f0e9]/45"><GitBranch size={16}/><span className="text-xs font-medium">Lineage workspace</span></div>
    </div>
    <div className="sidebar-status mt-auto rounded-2xl border border-white/10 bg-white/[.04] p-3.5">
      <div className="flex items-center gap-2 text-[#b9f12f]"><Settings2 size={15}/><span className="text-[10px] font-bold uppercase tracking-[.16em]">Workspace status</span></div>
      <p className="mt-2 text-xs font-semibold text-[#f2f0e9]/80">Frontend foundation</p>
      <p className="mt-1 text-[10px] leading-4 text-[#f2f0e9]/40">Backend connection is not configured.</p>
    </div>
    <div className="sidebar-version mt-4 flex items-center justify-between px-2 text-[9px] font-medium tracking-wide text-[#f2f0e9]/25"><span>KAIRIX WEB</span><span>0.1.0</span></div>
  </aside>;
}

function AppShell({active,onNavigate,children}:{active:PageKey;onNavigate:(key:PageKey)=>void;children:ReactNode}){
  return <div className="min-h-screen bg-[#f2f0e9] text-[#0b3048]">
    <Sidebar active={active} onNavigate={onNavigate}/>
    <div className="main-shell min-h-screen pl-[248px] max-md:pl-[68px]">
      <header className="topbar sticky top-0 z-20 flex h-[76px] items-center justify-between border-b border-[#0b3048]/[.07] bg-[#f2f0e9]/90 px-8 backdrop-blur-xl max-lg:px-6 max-md:h-[68px]">
        <div className="flex min-w-0 items-center gap-2 text-sm"><span className="font-display font-extrabold tracking-[.14em] text-[#0b3048]/35 max-sm:hidden">KAIRIX</span><span className="text-[#0b3048]/20 max-sm:hidden">/</span><span className="truncate font-semibold">{pageTitles[active]}</span></div>
        <div className="flex items-center gap-3">
          <div className="relative hidden w-[250px] xl:block"><Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#0b3048]/35"/><Input aria-label="Search workspace" placeholder="Search workspace..." className="h-10 pl-9 pr-10 text-xs shadow-none" disabled/><span className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded-md border border-[#0b3048]/10 px-1.5 py-0.5 font-mono text-[9px] text-[#0b3048]/35">⌘ K</span></div>
          <button type="button" disabled aria-label="Notifications unavailable" className="neo-raised flex h-10 w-10 items-center justify-center rounded-xl text-[#0b3048]/40"><Bell size={17}/></button>
          <div className="flex items-center gap-2 rounded-xl border border-[#0b3048]/[.07] bg-white/35 px-2 py-1.5"><div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#0b3048] text-[#b9f12f]"><Command size={14}/></div><div className="hidden sm:block"><p className="text-[11px] font-bold leading-4">Analyst workspace</p><p className="text-[9px] leading-3 text-[#0b3048]/40">Local preview</p></div><ChevronDown size={13} className="text-[#0b3048]/35"/></div>
        </div>
      </header>
      <main className="main-content mx-auto w-full max-w-[1600px] px-8 py-8 max-lg:px-6 max-md:px-4 max-md:py-6">{children}
        <footer className="mt-12 flex flex-wrap items-center justify-between gap-2 border-t border-[#0b3048]/[.07] pt-5 text-[10px] text-[#0b3048]/35"><span>KAIRIX · Legacy Intelligence Workbench</span><span>Midnight teal / soft pearl / neon lime</span></footer>
      </main>
    </div>
  </div>;
}

function Eyebrow({children}:{children:ReactNode}){return <div className="mb-2 flex items-center gap-2"><span className="eyebrow-dot"/><span className="eyebrow">{children}</span></div>}

function Overview({navigate}:{navigate:(key:PageKey)=>void}){
  const services=[{name:"Source catalog",detail:"COBOL · SQL · SSIS assets",icon:Code2},{name:"Knowledge graph",detail:"Neo4j relationship layer",icon:Network},{name:"Vector index",detail:"Qdrant semantic retrieval",icon:Database}];
  const stages=[{num:"01",title:"Discover",detail:"Locate legacy source files",icon:BookOpen},{num:"02",title:"Understand",detail:"Parse and extract knowledge",icon:BrainCircuit},{num:"03",title:"Connect",detail:"Build graph and vector links",icon:GitBranch},{num:"04",title:"Investigate",detail:"Trace logic with evidence",icon:Workflow}];
  const links=[{title:"Source explorer",desc:"Browse programs, SQL scripts and ETL packages.",icon:Code2,key:"sources" as PageKey,cta:"Explore assets"},{title:"Knowledge pipeline",desc:"Review the processing and indexing workflow.",icon:Workflow,key:"pipeline" as PageKey,cta:"View pipeline"},{title:"Knowledge graph",desc:"Explore relationships and downstream lineage.",icon:Network,key:"graph" as PageKey,cta:"Open graph"}];
  return <div className="space-y-7">
    <section className="flex flex-wrap items-end justify-between gap-4"><div><Eyebrow>LEGACY REVERSE ENGINEERING WORKSPACE</Eyebrow><h1 className="font-display text-[clamp(2rem,3vw,2.8rem)] font-extrabold tracking-[-.055em]">Workspace overview</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-[#0b3048]/55">A single place to understand your legacy landscape, follow data lineage and investigate business logic.</p></div><Button variant="lime" size="lg" onClick={()=>navigate("investigation")}>Start an investigation <ArrowUpRight size={16}/></Button></section>
    <section className="hero-panel relative overflow-hidden rounded-[28px] p-7 text-[#f2f0e9] md:p-9"><div className="hero-orb hero-orb-one"/><div className="hero-orb hero-orb-two"/>
      <div className="relative z-10 grid gap-8 md:grid-cols-[1.3fr_.7fr] md:items-center"><div className="max-w-2xl"><Badge variant="lime" className="mb-5 border border-[#b9f12f]/20 bg-[#b9f12f]/10 text-[#c8f64d]">INTELLIGENCE WORKBENCH</Badge><h2 className="font-display text-3xl font-extrabold leading-[1.12] tracking-[-.045em] md:text-[2.55rem]">Make the invisible logic in legacy systems <span className="text-[#b9f12f]">visible.</span></h2><p className="mt-4 max-w-xl text-sm leading-6 text-[#f2f0e9]/60">Move from raw source files to structured knowledge, connected lineage and evidence-backed answers.</p><Button variant="lime" className="mt-6" onClick={()=>navigate("sources")}>Explore source landscape <ArrowRight size={15}/></Button></div>
      <div className="relative mx-auto flex w-full max-w-[270px] items-center justify-center py-5"><div className="hero-ring hero-ring-outer"/><div className="hero-ring hero-ring-middle"/><div className="hero-core flex h-28 w-28 items-center justify-center rounded-[30px] bg-[#b9f12f] text-[#0b3048]"><Boxes size={45} strokeWidth={1.5}/></div><span className="hero-node hero-node-a"><Code2 size={16}/></span><span className="hero-node hero-node-b"><Network size={16}/></span><span className="hero-node hero-node-c"><BrainCircuit size={16}/></span></div></div>
      <div className="relative z-10 mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-4"><div className="flex items-center gap-2 text-xs text-[#f2f0e9]/60"><CircleDashed size={14} className="text-[#b9f12f]"/> Frontend preview · backend not connected</div><span className="font-mono text-[10px] tracking-wider text-[#f2f0e9]/30">KAIRIX / WORKSPACE</span></div>
    </section>
    <section className="grid gap-4 xl:grid-cols-[1.15fr_.85fr]">
      <Card><CardHeader className="flex-row items-start justify-between"><div><CardTitle>Platform connections</CardTitle><CardDescription className="mt-1">Live data will appear when the frontend API is connected.</CardDescription></div><Badge variant="pending">NOT CONNECTED</Badge></CardHeader><CardContent className="space-y-3">{services.map(s=>{const Icon=s.icon;return <div key={s.name} className="flex items-center gap-3 rounded-xl border border-[#0b3048]/[.06] bg-[#f2f0e9]/55 px-3.5 py-3"><div className="neo-inset flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-[#0b3048]/60"><Icon size={18}/></div><div className="min-w-0 flex-1"><p className="text-sm font-bold">{s.name}</p><p className="mt-0.5 text-[11px] text-[#0b3048]/45">{s.detail}</p></div><Badge variant="outline"><span className="h-1.5 w-1.5 rounded-full bg-[#c19a55]"/> Pending</Badge></div>})}</CardContent></Card>
      <Card><CardHeader><CardTitle>How KAIRIX works</CardTitle><CardDescription className="mt-1">The four layers behind the intelligence workflow.</CardDescription></CardHeader><CardContent className="grid grid-cols-2 gap-3">{stages.map(s=>{const Icon=s.icon;return <div key={s.num} className="neo-inset min-h-[112px] rounded-xl p-3.5"><div className="flex items-center justify-between"><span className="font-mono text-[10px] font-semibold text-[#0b3048]/35">{s.num}</span><Icon size={16} className="text-[#0b3048]/55"/></div><p className="mt-3 text-sm font-bold">{s.title}</p><p className="mt-1 text-[10px] leading-4 text-[#0b3048]/45">{s.detail}</p></div>})}</CardContent></Card>
    </section>
    <section><div className="mb-4 flex items-end justify-between gap-3"><div><h2 className="font-display text-lg font-extrabold tracking-tight">Explore your workspace</h2><p className="mt-1 text-xs text-[#0b3048]/50">Jump into a core area of the platform.</p></div><span className="hidden items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-[#0b3048]/35 sm:flex"><CheckCircle2 size={12}/> UI foundation ready</span></div>
      <div className="grid gap-4 md:grid-cols-3">{links.map(l=>{const Icon=l.icon;return <button key={l.key} type="button" onClick={()=>navigate(l.key)} className="neo-card group rounded-2xl p-5 text-left transition-all duration-200 hover:-translate-y-1 hover:shadow-neo"><div className="flex items-center justify-between"><div className="neo-inset flex h-11 w-11 items-center justify-center rounded-xl"><Icon size={20}/></div><ArrowUpRight size={17} className="text-[#0b3048]/30 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5"/></div><h3 className="mt-5 font-display text-base font-bold">{l.title}</h3><p className="mt-1.5 min-h-10 text-xs leading-5 text-[#0b3048]/50">{l.desc}</p><span className="mt-4 inline-flex items-center gap-1.5 text-xs font-bold">{l.cta} <ArrowRight size={13}/></span></button>})}</div>
    </section>
  </div>;
}

function Investigation(){
  const examples=["How is earned premium calculated?","Trace the data flow into KPI reporting.","Which programs update policy status?"];
  const modes=[{icon:GitBranch,title:"Lineage mode",desc:"Follow upstream and downstream dependencies."},{icon:Search,title:"Semantic mode",desc:"Find related logic across source artifacts."},{icon:FileSearch,title:"Evidence mode",desc:"Review source references and line anchors."}];
  return <div className="mx-auto max-w-5xl space-y-7"><section><Eyebrow>EVIDENCE-BACKED REASONING</Eyebrow><div className="flex flex-wrap items-end justify-between gap-3"><div><h1 className="font-display text-3xl font-extrabold tracking-[-.05em]">Investigate your codebase</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-[#0b3048]/55">Ask natural-language questions and trace the answer back to source evidence.</p></div><Badge variant="pending"><LockKeyhole size={11}/> Awaiting API connection</Badge></div></section>
    <Card className="overflow-hidden"><div className="border-b border-[#0b3048]/[.07] bg-[#0b3048] p-6 text-[#f2f0e9] md:p-8"><div className="flex items-center gap-3"><div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#b9f12f] text-[#0b3048]"><BrainCircuit size={20}/></div><div><p className="font-display text-lg font-bold">Investigation agent</p><p className="text-xs text-[#f2f0e9]/50">Natural language · lineage · semantic search</p></div></div><Textarea className="mt-6 min-h-[150px] border-white/10 bg-white/[.07] text-[#f2f0e9] placeholder:text-[#f2f0e9]/30 shadow-none focus-visible:ring-[#b9f12f]/30" placeholder="Ask how a business rule works, where a field originates, or how data moves through the system..."/><div className="mt-4 flex flex-wrap items-center justify-between gap-3"><span className="flex items-center gap-2 text-[11px] text-[#f2f0e9]/45"><Info size={13}/> Query execution will be enabled after API integration.</span><Button variant="lime" disabled>Run investigation <ArrowUpRight size={15}/></Button></div></div><CardContent className="pt-5"><p className="mb-3 text-[10px] font-bold uppercase tracking-[.16em] text-[#0b3048]/40">Example questions</p><div className="flex flex-wrap gap-2">{examples.map(q=><span key={q} className="rounded-full border border-[#0b3048]/10 bg-white/35 px-3 py-2 text-[11px] text-[#0b3048]/60">{q}</span>)}</div></CardContent></Card>
    <div className="grid gap-4 md:grid-cols-3">{modes.map(m=>{const Icon=m.icon;return <Card key={m.title} className="p-5"><div className="neo-inset flex h-10 w-10 items-center justify-center rounded-xl"><Icon size={18}/></div><h3 className="mt-4 text-sm font-bold">{m.title}</h3><p className="mt-1 text-xs leading-5 text-[#0b3048]/50">{m.desc}</p></Card>})}</div>
  </div>;
}

function Sources(){
  const formats=[{label:"COBOL",detail:"Programs and copybooks",icon:FileCode2},{label:"SQL",detail:"Queries and stored procedures",icon:FileText},{label:"SSIS",detail:"ETL packages and data flows",icon:BookOpen}];
  return <div className="space-y-7"><section className="flex flex-wrap items-end justify-between gap-4"><div><Eyebrow>SOURCE LANDSCAPE</Eyebrow><h1 className="font-display text-3xl font-extrabold tracking-[-.05em]">Source explorer</h1><p className="mt-2 text-sm text-[#0b3048]/55">Browse legacy assets and inspect the files that shape your business systems.</p></div><Badge variant="pending">Catalog not connected</Badge></section>
    <div className="grid gap-4 md:grid-cols-3">{formats.map(f=>{const Icon=f.icon;return <Card key={f.label} className="p-5"><div className="flex items-center justify-between"><div className="neo-inset flex h-10 w-10 items-center justify-center rounded-xl"><Icon size={18}/></div><Badge variant="outline">{f.label}</Badge></div><h3 className="mt-4 text-sm font-bold">{f.label} assets</h3><p className="mt-1 text-xs text-[#0b3048]/50">{f.detail}</p></Card>})}</div>
    <Card><CardContent className="pt-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-display text-base font-bold">Repository files</h2><p className="mt-1 text-xs text-[#0b3048]/45">Search and filter the indexed source catalog.</p></div><div className="relative w-full max-w-xs"><Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#0b3048]/35"/><Input className="pl-9" placeholder="Search files..." disabled/></div></div>
      <div className="mt-5 flex min-h-[300px] flex-col items-center justify-center rounded-2xl border border-dashed border-[#0b3048]/15 bg-[#f2f0e9]/50 px-5 text-center"><div className="neo-inset flex h-14 w-14 items-center justify-center rounded-2xl text-[#0b3048]/55"><FileSearch size={24}/></div><h3 className="mt-4 font-display text-base font-bold">No source catalog connected</h3><p className="mt-2 max-w-md text-xs leading-5 text-[#0b3048]/50">Once the frontend is connected to the Python source service, indexed COBOL, SQL and SSIS files will appear here.</p><div className="mt-4 inline-flex items-center gap-2 rounded-full bg-[#0b3048]/[.05] px-3 py-2 text-[10px] font-semibold text-[#0b3048]/50"><UploadCloud size={13}/> File ingestion is not available in this preview</div></div>
    </CardContent></Card>
  </div>;
}

function Pipeline(){
  const rows=[
    {layer:"LAYER 01",title:"Source landscape",desc:"Locate and classify COBOL, SQL and SSIS files.",icon:FileSearch,output:"Classified source assets"},
    {layer:"LAYER 02",title:"Knowledge engineering",desc:"Parse code, build line-anchored evidence and reconcile extracted knowledge.",icon:Workflow,output:"Canonical knowledge packages"},
    {layer:"LAYER 03",title:"Knowledge & relationships",desc:"Load entities and lineage into Neo4j, then embed code and summaries in Qdrant.",icon:GitBranch,output:"Graph nodes · vector collections"},
    {layer:"LAYER 04",title:"Investigation",desc:"Route questions through graph traversal and semantic retrieval.",icon:Layers3,output:"Evidence-backed answers"}
  ];
  const systems=[{name:"Parser layer",sub:"Tree-sitter · sqlglot · XML",icon:FileSearch},{name:"Graph storage",sub:"Neo4j · Cypher traversal",icon:Database},{name:"Vector retrieval",sub:"Qdrant · semantic search",icon:CheckCircle2}];
  return <div className="space-y-7"><section className="flex flex-wrap items-end justify-between gap-4"><div><Eyebrow>PROCESS ORCHESTRATION</Eyebrow><h1 className="font-display text-3xl font-extrabold tracking-[-.05em]">Knowledge pipeline</h1><p className="mt-2 text-sm text-[#0b3048]/55">Understand each stage from raw legacy code to searchable enterprise knowledge.</p></div><Badge variant="pending"><CircleDashed size={12}/> Execution unavailable</Badge></section>
    <Card><CardHeader><CardTitle>End-to-end processing flow</CardTitle><CardDescription>Architecture view · runtime progress will appear after service integration.</CardDescription></CardHeader><CardContent><div className="space-y-2">{rows.map((r,i)=>{const Icon=r.icon;return <div key={r.layer}><div className="flex flex-col gap-3 rounded-2xl border border-[#0b3048]/[.07] bg-white/35 p-4 sm:flex-row sm:items-center"><div className="flex items-center gap-3 sm:w-[190px] sm:shrink-0"><div className="neo-inset flex h-11 w-11 items-center justify-center rounded-xl"><Icon size={19}/></div><div><p className="font-mono text-[9px] font-semibold tracking-wider text-[#0b3048]/35">{r.layer}</p><p className="mt-1 text-sm font-bold">{r.title}</p></div></div><p className="flex-1 text-xs leading-5 text-[#0b3048]/55">{r.desc}</p><div className="sm:w-[200px] sm:shrink-0"><p className="text-[9px] font-bold uppercase tracking-wider text-[#0b3048]/35">Output</p><p className="mt-1 text-[11px] font-semibold text-[#0b3048]/70">{r.output}</p></div><Badge variant="pending" className="self-start sm:self-center">Not connected</Badge></div>{i<rows.length-1&&<div className="flex h-7 items-center pl-7 text-[#0b3048]/25"><ArrowDown size={15}/></div>}</div>})}</div></CardContent></Card>
    <div className="grid gap-4 md:grid-cols-3">{systems.map(s=>{const Icon=s.icon;return <Card key={s.name} className="p-5"><Icon size={19} className="text-[#0b3048]/55"/><p className="mt-4 text-sm font-bold">{s.name}</p><p className="mt-1 text-xs text-[#0b3048]/45">{s.sub}</p></Card>})}</div>
  </div>;
}

function Graph(){
  return <div className="space-y-7"><section className="flex flex-wrap items-end justify-between gap-4"><div><Eyebrow>RELATIONSHIP INTELLIGENCE</Eyebrow><h1 className="font-display text-3xl font-extrabold tracking-[-.05em]">Knowledge graph</h1><p className="mt-2 text-sm text-[#0b3048]/55">Explore entities, business rules and the lineage connecting them.</p></div><Badge variant="pending">Graph not connected</Badge></section>
    <Card className="overflow-hidden"><CardHeader className="flex-row flex-wrap items-center justify-between gap-3"><div><CardTitle>Graph canvas</CardTitle><CardDescription className="mt-1">Interactive graph exploration will be available after Neo4j integration.</CardDescription></div><div className="relative w-full max-w-[260px]"><Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#0b3048]/35"/><Input placeholder="Find an entity..." className="pl-9" disabled/></div></CardHeader><CardContent><div className="graph-grid relative flex min-h-[390px] flex-col items-center justify-center overflow-hidden rounded-2xl border border-dashed border-[#0b3048]/15 bg-[#f2f0e9]/65 px-5 text-center"><div className="neo-inset relative z-10 flex h-16 w-16 items-center justify-center rounded-[22px] text-[#0b3048]/60"><Network size={27}/></div><h3 className="relative z-10 mt-5 font-display text-lg font-bold">Your graph starts here</h3><p className="relative z-10 mt-2 max-w-md text-xs leading-5 text-[#0b3048]/50">Run knowledge extraction and load the canonical packages into Neo4j. Connected entities and lineage paths will be rendered in this canvas.</p><div className="relative z-10 mt-5 inline-flex items-center gap-2 rounded-full bg-white/65 px-3 py-2 text-[10px] font-semibold text-[#0b3048]/50"><Info size={13}/> No graph data is being displayed</div></div></CardContent></Card>
    <div className="grid gap-4 md:grid-cols-2"><Card className="p-5"><div className="flex items-center gap-3"><div className="neo-inset flex h-10 w-10 items-center justify-center rounded-xl"><Waypoints size={18}/></div><div><p className="text-sm font-bold">Relationship discovery</p><p className="mt-1 text-xs text-[#0b3048]/45">Cross-file semantic matching</p></div></div></Card><Card className="p-5"><div className="flex items-center gap-3"><div className="neo-inset flex h-10 w-10 items-center justify-center rounded-xl"><GitBranch size={18}/></div><div><p className="text-sm font-bold">Data lineage</p><p className="mt-1 text-xs text-[#0b3048]/45">Upstream and downstream tracing</p></div></div></Card></div>
  </div>;
}

export default function App(){
  const [active,setActive]=useState<PageKey>("overview");
  let page:ReactNode;
  switch(active){case"investigation":page=<Investigation/>;break;case"sources":page=<Sources/>;break;case"pipeline":page=<Pipeline/>;break;case"graph":page=<Graph/>;break;default:page=<Overview navigate={setActive}/>;}
  return <AppShell active={active} onNavigate={setActive}>{page}</AppShell>;
}
