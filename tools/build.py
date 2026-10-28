"""Optional agent helper. Normal editor build: latexmk -xelatex main.tex."""
from pathlib import Path
import argparse, os, re, subprocess

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'
NAMES=['oscillations','waves','statistics','generation','antennas','detection']

def compile_one(source,job):
    cmd=['latexmk','-xelatex','-interaction=nonstopmode','-halt-on-error',
         '-file-line-error',f'-jobname={job}',str(source)]
    result=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                          text=True,encoding='utf-8',errors='replace')
    (BUILD/f'{job}-build.txt').write_text(result.stdout)
    if result.returncode:
        print(result.stdout[-7000:]);raise SystemExit(result.returncode)
    print(BUILD/f'{job}.pdf',flush=True)

def external_labels():
    aux=(BUILD/'main.aux').read_text()
    labels=re.findall(r'\\newlabel\{(eq:[^}]+)\}\{\{([^}]+)\}',aux)
    offsets=re.findall(r'\\newlabel\{eqoffset:([^}]+)\}\{\{(\d+)\}',aux)
    lines=['\\externalEq{'+key+'}{'+number+'}' for key,number in labels]
    lines+=['\\externalEqCounter{'+key+'}{'+number+'}' for key,number in offsets]
    (BUILD/'externalrefs.tex').write_text('\n'.join(lines)+'\n')

def subset(kind,value,job):
    driver=BUILD/f'_{job}.tex'
    driver.write_text('\\def\\SubsetBuild{1}\n\\def\\UseExternalRefs{1}\n'
                      +'\\def\\Only'+kind+'{'+value+'}\n\\input{main.tex}\n')
    compile_one(driver.relative_to(ROOT),job)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--all',action='store_true')
    group.add_argument('--section',type=int,choices=range(1,7))
    group.add_argument('--question',help='Group 1.4 or subquestion 1.4.2')
    args=parser.parse_args();BUILD.mkdir(exist_ok=True)
    os.environ['PYTHONUTF8']='1'
    if args.question:
        if not re.fullmatch(r'[1-6]\.\d+(?:\.\d+)?',args.question):parser.error('Invalid ID')
        macro='Subhead' if args.question.count('.')==2 else 'Qhead'
        needle='\\'+macro+'{'+args.question+'}'
        if not any(needle in f.read_text() for f in (ROOT/'sections').rglob('*.tex')):
            parser.error('Unknown current question')
    if not args.section and not args.question or not (BUILD/'main.aux').exists():
        compile_one(Path('main.tex'),'main')
    external_labels()
    if args.all or args.section:
        for n in range(1,7) if args.all else [args.section]:
            subset('Section',str(n),NAMES[n-1])
    elif args.question:
        subset('Question',args.question,'question_'+args.question.replace('.','_'))

if __name__=='__main__':main()
