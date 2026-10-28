"""Small stdlib-only checks for agents and CI; no source generation."""
from pathlib import Path
import argparse, re, sys

ROOT=Path(__file__).resolve().parents[1]

def without_comments(text):
    return re.sub(r'(?<!\\)%[^\n]*','',text)

def inspect_sources():
    errors=[];heads={};leaves={};alltext=[];used=set()
    for f in sorted((ROOT/'sections').rglob('*.tex')):
        t=without_comments(f.read_text());alltext.append(t)
        for kind,rows in [('Qhead',heads),('Subhead',leaves)]:
            for match in re.finditer(r'\\'+kind+r'\{([\d.]+)\}\{([^{}]+)\}',t):
                qid,title=match.groups()
                if qid in rows:errors.append('Duplicate ID '+qid)
                rows[qid]=(title,f)
                body=t[match.end():]
                if kind=='Subhead' and len(body.split())<35:
                    errors.append('No substantive body: '+qid)
        for macro in ['input','QuestionFile','Subfile','IncludeSection']:
            pattern=(r'\\'+macro+r'\{([^}]+)\}' if macro=='input'
                     else r'\\'+macro+r'\{[^}]+\}\{([^}]+)\}')
            for path in re.findall(pattern,t):
                target=ROOT/(path+'.tex')
                if not target.exists():errors.append('Missing input '+path)
                elif macro in ['QuestionFile','Subfile']:used.add(target.resolve())
        for path in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',t):
            if not (ROOT/path).is_file():errors.append('Missing figure '+path)
    text='\n'.join(alltext)
    for qid in leaves:
        if qid.rsplit('.',1)[0] not in heads:errors.append('Unknown parent '+qid)
    for rows,depth in [(heads,2),(leaves,3)]:
        if any(len(q.split('.'))!=depth for q in rows):errors.append('Wrong ID depth')
        parents={q.rsplit('.',1)[0] for q in rows}
        for parent in parents:
            numbers=sorted(int(q.rsplit('.',1)[1]) for q in rows if q.rsplit('.',1)[0]==parent)
            if numbers!=list(range(1,len(numbers)+1)):errors.append('Non-contiguous '+parent)
    for qid,(title,f) in {**heads,**leaves}.items():
        if f.resolve() not in used:errors.append('Unreachable question file '+qid)
    if {q.split('.')[0] for q in heads}!={str(n) for n in range(1,7)}:
        errors.append('Programme must contain all six chapters')
    targets=set(heads)|set(leaves)
    for qid in re.findall(r'\\Qref\{([^}]+)\}',text):
        if qid not in targets:errors.append('Unknown question reference '+qid)
    labels=re.findall(r'\\label\{([^}]+)\}',text)
    if len(labels)!=len(set(labels)):errors.append('Duplicate equation/object labels')
    for label in re.findall(r'\\(?:eqref|ref|hyperref)\{([^}]+)\}',text):
        if label not in labels:errors.append('Unknown label '+label)
    bib=(ROOT/'bib/references.bib').read_text()
    keys=set(re.findall(r'@\w+\{([^,]+),',bib))
    for keylist in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}',text):
        for key in keylist.split(','):
            if key not in keys:errors.append('Unknown citation '+key)
    for qid,(_,f) in heads.items():
        t=without_comments(f.read_text())
        for macro in ['sources','recap','board','oral','bait']:
            if '\\'+macro+'{' not in t:errors.append(qid+' missing '+macro)
        if not re.search(r'\\Qhead\{[^}]+\}\{[^}]+\}\{[^}]+\}',t):
            errors.append(qid+' missing official formulation')
    pre=(ROOT/'config/preamble.tex').read_text()
    if r'\setcounter{tocdepth}{0}' not in pre:errors.append('TOC must contain chapters only')
    matrix=(ROOT/'docs/SOURCES.md').read_text()
    mapped=set(re.findall(r'^\| (\d+\.\d+)\s',matrix,re.M))
    if mapped!=set(heads):errors.append('Source map and current groups disagree')
    print(f'Source check: {len(heads)} groups, {len(leaves)} subquestions, {len(labels)} stable object labels')
    return errors,heads,leaves

def inspect_build(heads,leaves,all_sections):
    errors=[];jobs=['main']
    if all_sections:jobs+=['oscillations','waves','statistics','generation','antennas','detection']
    for job in jobs:
        pdf=ROOT/'build'/f'{job}.pdf';log=ROOT/'build'/f'{job}.log'
        if not pdf.is_file() or b'%%EOF' not in pdf.read_bytes()[-1024:]:errors.append('Missing/incomplete PDF '+job)
        if not log.is_file():errors.append('Missing log '+job);continue
        t=log.read_text(errors='replace')
        for pattern in ['Overfull',r'Undefined control sequence',r'undefined references',
                        'undefined citations','Missing character','No hyphenation patterns',
                        r'LaTeX Warning: (?:Reference|Citation).*undefined',r'multiply defined']:
            if re.search(pattern,t,re.I):errors.append(job+': '+pattern)
        if 'Output written on' not in t:errors.append('No successful output '+job)
    qlist=(ROOT/'build/main.qlist').read_text()
    expected={**heads,**leaves}
    listed=re.findall(r'\\List(?:Group|Leaf)\s*\{([^}]+)\}\{([^}]+)\}',qlist)
    if len(listed)!=len(expected):errors.append('Compiled question-list count mismatch')
    for qid,title in listed:
        if qid not in expected or title!=expected[qid][0]:errors.append('Compiled list mismatch '+qid)
    toc=(ROOT/'build/main.toc').read_text()
    # LaTeX records every level in .toc; tocdepth controls which ones are printed.
    # Presence of section records is therefore not a layout defect.
    chapters=re.findall(r'\\contentsline\s*\{chapter\}\{\\numberline\s*\{(\d+)\}',toc)
    if chapters!=[str(n) for n in range(1,7)]:errors.append('TOC chapter coverage mismatch')
    print('Build logs checked: '+', '.join(jobs))
    return errors

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compiled',action='store_true');p.add_argument('--all-sections',action='store_true')
    args=p.parse_args();errors,heads,leaves=inspect_sources()
    if args.compiled:errors+=inspect_build(heads,leaves,args.all_sections)
    if errors:print('\n'.join(errors),file=sys.stderr);raise SystemExit(1)
    print('Checks passed. This is not human acceptance or a proof of every formula.')

if __name__=='__main__':main()
