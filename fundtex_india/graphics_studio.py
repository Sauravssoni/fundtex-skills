"""SVG financial visuals: portfolio pie, exposure bars, correlations and scenarios."""
from __future__ import annotations
import html,math
from .chart_studio import NAVY,PAPER,GRID,TEXT,MUTED,CYAN,GREEN,RED,GOLD

COLOURS=("#6ae4db","#9c8df3","#f7c772","#f58497","#43d4aa","#63a9f6","#d6a1e6","#fb985c")
def _header(title,w=1080,h=610):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            f'<rect width="{w}" height="{h}" fill="{NAVY}"/>',
            f'<rect x="32" y="32" width="{w-64}" height="{h-64}" fill="{PAPER}" rx="16"/>',
            f'<text x="70" y="88" fill="{TEXT}" font-size="28" font-family="Arial" font-weight="bold">{html.escape(title)}</text>',
            f'<text x="70" y="{h-60}" fill="{MUTED}" font-family="Arial" font-size="12">FUNDTEX FINANCIAL INTELLIGENCE  •  HISTORICAL / RESEARCH ONLY</text>']
def _valid(d):
    if not isinstance(d,dict) or not 1<=len(d)<=30:raise ValueError("Expected 1..30 values")
    values={}
    for k,v in d.items():
        if not isinstance(k,str) or len(k)>80:raise ValueError("Invalid metric label")
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
            raise ValueError("Chart values must be finite numbers")
        values[k]=float(v)
    return values

def pie(weights,title="Portfolio sector allocation"):
    d=_valid(weights)
    if any(v<0 for v in d.values()) or sum(d.values())<=0:
        raise ValueError("Pie weights must be nonnegative with nonzero sum")
    if len(d)>12:raise ValueError("Pie is limited to 12 segments; aggregate smaller weights first")
    p=_header(title);tot=sum(d.values());start=-math.pi/2;cx=315;cy=310;r=188
    for i,(name,amt) in enumerate(d.items()):
        fraction=amt/tot;stop=start+fraction*math.tau;end=stop
        # Full-circle SVG arcs are invalid; a single-category circle is explicit.
        if fraction>=.999999:
            p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{COLOURS[i%len(COLOURS)]}"/>')
        elif fraction>0:
            x1=cx+r*math.cos(start);y1=cy+r*math.sin(start);x2=cx+r*math.cos(stop);y2=cy+r*math.sin(stop)
            p.append(f'<path d="M {cx} {cy} L {x1:.1f} {y1:.1f} A {r} {r} 0 {1 if fraction>.5 else 0} 1 {x2:.1f} {y2:.1f} Z" fill="{COLOURS[i%len(COLOURS)]}"/>')
        p.append(f'<rect x="615" y="{173+i*34}" width="15" height="15" fill="{COLOURS[i%len(COLOURS)]}"/>')
        p.append(f'<text x="642" y="{186+i*34}" fill="{TEXT}" font-family="Arial" font-size="16">{html.escape(name[:33])}  —  {100*fraction:.1f}%</text>')
        start=end
    p.extend([f'<circle cx="{cx}" cy="{cy}" r="96" fill="{PAPER}"/>',
              f'<text x="{cx}" y="{cy+4}" fill="{TEXT}" font-size="27" text-anchor="middle" font-family="Arial" font-weight="bold">{len(d)} sectors</text>','</svg>'])
    return "\n".join(p)

def bars(metrics,title="Peer / sector comparison"):
    d=_valid(metrics);p=_header(title)
    maxabs=max(abs(v) for v in d.values()) or 1
    step=min(57,390/len(d));base=180
    for i,(name,v) in enumerate(d.items()):
        y=base+i*step;colour=GREEN if v>=0 else RED
        width=540*abs(v)/maxabs
        p.append(f'<text x="82" y="{y+15:.1f}" fill="{TEXT}" font-family="Arial" font-size="14">{html.escape(name[:25])}</text>')
        p.append(f'<rect x="385" y="{y:.1f}" width="{width:.1f}" height="{step*.49:.1f}" rx="4" fill="{colour}"/>')
        p.append(f'<text x="{395+width:.1f}" y="{y+15:.1f}" fill="{TEXT}" font-family="Arial" font-size="13">{v:,.3f}</text>')
    p.append('</svg>')
    return "\n".join(p)

def heatmap(corr,title="Asset return correlations"):
    if not isinstance(corr,dict) or not 1<=len(corr)<=12:raise ValueError("1..12 assets required")
    names=list(corr)
    cell=min(51,550/len(names));left=255;top=165
    p=_header(title);p.append(f'<text x="70" y="131" font-size="13" font-family="Arial" fill="{MUTED}">Pearson correlation · dated and user-supplied return history</text>')
    for i,a in enumerate(names):
        if not isinstance(corr[a],dict):raise ValueError("Invalid correlation matrix")
        p.append(f'<text x="{left-16}" y="{top+i*cell+cell*.65:.1f}" text-anchor="end" fill="{TEXT}" font-size="11" font-family="Arial">{html.escape(a[:22])}</text>')
        p.append(f'<text x="{left+i*cell+cell*.45:.1f}" y="{top-8}" text-anchor="middle" fill="{TEXT}" font-size="10" font-family="Arial">{i+1}</text>')
        for j,b in enumerate(names):
            x=corr[a].get(b)
            if x is None:col="#445067";desc="N/A"
            elif not isinstance(x,(int,float)) or not math.isfinite(x) or not -1.00001<=x<=1.00001:raise ValueError("Correlations must be -1..1 or null")
            else:
                hue=max(0,min(1,(x+1)/2))
                col=f'rgb({int(240*(1-hue)+15*hue)},{int(99*(1-hue)+210*hue)},{int(137*(1-hue)+170*hue)})'
                desc=f'{x:.2f}'
            p.append(f'<rect x="{left+j*cell:.1f}" y="{top+i*cell:.1f}" width="{cell-2:.1f}" height="{cell-2:.1f}" rx="3" fill="{col}"/>')
            if cell>=40:p.append(f'<text x="{left+j*cell+cell/2:.1f}" y="{top+i*cell+cell*.59:.1f}" font-family="Arial" font-size="12" text-anchor="middle" fill="#0b1120">{desc}</text>')
    p.append('</svg>');return "\n".join(p)

def histogram(values,title="Scenario return distribution",bins=22):
    if not isinstance(values,list) or not 10<=len(values)<=2_000_000:raise ValueError("10..2m values needed")
    if bins<5 or bins>60:raise ValueError("5..60 bins")
    if any(not isinstance(v,(float,int)) or not math.isfinite(v) for v in values):
        raise ValueError("Nonfinite returns")
    lo=min(values);hi=max(values)
    if lo==hi:hi=lo+1e-6
    counts=[0]*bins
    for v in values:
        idx=min(bins-1,int((v-lo)/(hi-lo)*bins));counts[idx]+=1
    p=_header(title);peak=max(counts);left=100;top=160;height=325;barw=850/bins
    for i,v in enumerate(counts):
        h=height*(v/peak if peak else 0);x=left+i*barw;y=top+height-h
        p.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{barw*.86:.2f}" height="{h:.2f}" fill="{CYAN}" opacity=".83"/>')
    p.append(f'<text x="{left}" y="512" fill="{MUTED}" font-family="Arial" font-size="13">{lo*100:.2f}%</text>')
    p.append(f'<text x="950" y="512" fill="{MUTED}" font-family="Arial" font-size="13" text-anchor="end">{max(values)*100:.2f}%</text>')
    p.append('</svg>');return "\n".join(p)

def waterfall(deltas,title="Valuation bridge / illustrative waterfall"):
    d=_valid(deltas)
    if len(d)>12:raise ValueError("Maximum 12 stages")
    cumulative=0;steps=[]
    for name,value in d.items():
        prior=cumulative;cumulative+=value;steps.append((name,prior,cumulative,value))
    ext=[v for _,a,b,_ in steps for v in (a,b)]
    low=min(ext+[0]);high=max(ext+[0]);spread=(high-low) or 1
    p=_header(title);top=155;h=335;left=92;w=870;barw=w/len(steps)
    def y(v):return top+(high-v)/(spread)*h
    for i,(name,a,b,value) in enumerate(steps):
        x=left+i*barw+barw*.15;lo=min(y(a),y(b));hei=abs(y(b)-y(a))
        colour=GREEN if value>=0 else RED
        p.append(f'<rect x="{x:.1f}" y="{lo:.1f}" width="{barw*.62:.1f}" height="{max(2,hei):.1f}" rx="3" fill="{colour}"/>')
        p.append(f'<text x="{x+barw*.31:.1f}" y="515" text-anchor="middle" font-family="Arial" font-size="12" fill="{TEXT}">{html.escape(name[:12])}</text>')
    p.append('</svg>');return "\n".join(p)
