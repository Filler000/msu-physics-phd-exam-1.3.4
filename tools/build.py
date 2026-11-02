"""Optional agent helper. Normal editor build: latexmk -xelatex main.tex."""
from pathlib import Path
import argparse, os, re, shutil, subprocess

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'
NAMES=['oscillations','waves','statistics','generation','antennas','detection']

def question_sources():
    """Use the actual programme headings as the single source of ticket IDs."""
    result={}
    for source in sorted((ROOT/'sections').rglob('main.tex')):
        text=re.sub(r'(?<!\\)%[^\n]*','',source.read_text(encoding="utf-8"))
        for qid in re.findall(r'\\Qhead\{([1-6]\.\d+)\}',text):
            if qid in result:
                raise ValueError('Duplicate question ID '+qid)
            result[qid]=source
    return dict(sorted(result.items(),key=lambda row:tuple(map(int,row[0].split('.')))))

def compile_one(source,job):
    cmd=['latexmk','-xelatex','-interaction=nonstopmode','-halt-on-error',
         '-file-line-error',f'-jobname={job}',str(source)]
    result=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                          text=True,encoding='utf-8',errors='replace')
    (BUILD/f'{job}-build.txt').write_text(result.stdout,encoding='utf-8')
    if result.returncode:
        print(result.stdout[-7000:]);raise SystemExit(result.returncode)
    print(BUILD/f'{job}.pdf',flush=True)

def external_labels():
    aux=(BUILD/'main.aux').read_text(encoding='utf-8')
    labels=re.findall(r'\\newlabel\{(eq:[^}]+)\}\{\{([^}]+)\}',aux)
    offsets=re.findall(r'\\newlabel\{eqoffset:([^}]+)\}\{\{(\d+)\}',aux)
    lines=['\\externalEq{'+key+'}{'+number+'}' for key,number in labels]
    lines+=['\\externalEqCounter{'+key+'}{'+number+'}' for key,number in offsets]
    (BUILD/'externalrefs.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def subset(kind,value,job):
    driver=BUILD/f'_{job}.tex'
    driver.write_text('\\def\\SubsetBuild{1}\n\\def\\UseExternalRefs{1}\n'
                      +'\\def\\Only'+kind+'{'+value+'}\n'
                      +('\\input{config/question_preview}\n' if kind=='Question' else '')
                      +'\\input{main.tex}\n',encoding='utf-8')
    compile_one(driver.relative_to(ROOT),job)

def build_question(qid,sources):
    job='question_'+qid.replace('.','_')
    subset('Question',qid,job)
    parent=qid if qid.count('.')==1 else qid.rsplit('.',1)[0]
    destination=sources[parent].parent/(job+'.pdf')
    shutil.copy2(BUILD/(job+'.pdf'),destination)
    print(destination,flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--all',action='store_true')
    group.add_argument('--questions',action='store_true',help='Build and export all programme tickets')
    group.add_argument('--section',type=int,choices=range(1,7))
    group.add_argument('--question',help='Group 1.4 or subquestion 1.4.2')
    args=parser.parse_args();BUILD.mkdir(exist_ok=True)
    os.environ['PYTHONUTF8']='1'
    sources=question_sources()
    if args.question:
        if not re.fullmatch(r'[1-6]\.\d+(?:\.\d+)?',args.question):parser.error('Invalid ID')
        macro='Subhead' if args.question.count('.')==2 else 'Qhead'
        needle='\\'+macro+'{'+args.question+'}'
        if not any(needle in f.read_text(encoding="utf-8") for f in (ROOT/'sections').rglob('*.tex')):
            parser.error('Unknown current question')
    # latexmk reuses an up-to-date full build; otherwise refresh the shared
    # numbering before a selective build so references cannot use stale data.
    compile_one(Path('main.tex'),'main')
    external_labels()
    if args.all or args.section:
        for n in range(1,7) if args.all else [args.section]:
            subset('Section',str(n),NAMES[n-1])
    elif args.question:
        build_question(args.question,sources)
    elif args.questions:
        for qid in sources:
            build_question(qid,sources)

if __name__=='__main__':main()
