#!/usr/bin/env python3
"""Assemble a role-separated request locally; never call a generation service."""
from pathlib import Path
import argparse,json,hashlib
FIELDS=('role','facial_character','charm_contrast','character_silhouette','action_design','paw_prop_roles','posture','gaze','clothing_response','animal_traits','visible_character_hook')
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def assemble(plan,composition,profile,base_dir=None):
    base_dir=Path(base_dir or Path.cwd()).resolve()
    if plan.get('profile_version')!=profile['version']:raise ValueError('Profile version mismatch')
    for f in FIELDS:
        if not isinstance(plan.get(f),str) or not plan[f].strip():raise ValueError('Missing character field: '+f)
    if not plan.get('identity_anchors'):raise ValueError('Missing individual identity anchors')
    if plan.get('gaze_mode')!=composition.get('viewer_relationship'):raise ValueError('Gaze mismatch')
    if not plan.get('clothing_override') and len(plan.get('clothing_options',[]))<2:raise ValueError('Compare clothing choices or record user override')
    if not plan.get('clothing_choice_reason'):raise ValueError('Missing visible clothing reason')
    if plan.get('design_review',{}).get('status')!='reviewed_as_design':raise ValueError('Design review required')
    refs=plan.get('reference_inputs',[]);seen=set();roles=[]
    for ref in refs:
        p=Path(ref['path']).expanduser()
        p=(p if p.is_absolute() else base_dir/p).resolve()
        if ref['role'] not in {'identity','structure','quality'} or str(p) in seen:raise ValueError('Invalid role or duplicate reference')
        if not p.is_file() or sha(p)!=ref['sha256']:raise ValueError('Reference missing or hash mismatch')
        seen.add(str(p));roles.append(dict(path=str(p),role=ref['role'],sha256=ref['sha256']))
    if not any(x['role']=='identity' for x in roles) and not plan.get('identity_waiver'):raise ValueError('Identity photo required')
    if any(x['role']=='structure' for x in roles) and plan['design_review'].get('structure_status')!='pass':raise ValueError('Structure reference must be reviewed')
    chunks=['Image '+str(i+1)+' role: '+x['role']+'.' for i,x in enumerate(roles)]
    chunks+=[' '.join(plan[f] for f in FIELDS if f!='role'),'Individual identity: '+', '.join(plan['identity_anchors'])+'.', 'Clothing decision: '+plan['clothing_choice_reason']]
    for f in ('whole_picture_goal','reconstruction_plan','visibility_plan','background_plan'):
        if not composition.get(f):raise ValueError('Missing painting relationship: '+f)
        chunks.append(composition[f])
    chunks += [profile['generation_instructions']['style_prompt'],profile['generation_instructions']['constraints_clause']]
    prompt='\n\n'.join(chunks)+'\n';request={'prompt':prompt,'transparent_background':False}
    if roles:request['referenced_image_paths']=[x['path'] for x in roles]
    trace={'profile_version':profile['version'],'references':roles,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'plan_sha256':hashlib.sha256(canonical(plan)).hexdigest(),'composition_sha256':hashlib.sha256(canonical(composition)).hexdigest(),'tool_input_images':[x['path'] for x in roles],'request':request,'generated':False}
    return prompt,trace
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','composition','profile','prompt','trace'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--request',type=Path)
    parser.add_argument('--reference-root',type=Path)
    args=parser.parse_args()
    read=lambda path:json.loads(path.read_text(encoding='utf-8'))
    try:
        prompt,trace=assemble(read(args.plan),read(args.composition),read(args.profile),args.reference_root or args.plan.resolve().parent)
    except (ValueError,KeyError,TypeError,OSError) as exc:
        parser.error(str(exc))
    outputs=[(args.prompt,prompt),(args.trace,json.dumps(trace,ensure_ascii=False,indent=2)+'\n')]
    if args.request:outputs.append((args.request,json.dumps(trace['request'],ensure_ascii=False,indent=2)+'\n'))
    for path,body in outputs:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(body,encoding='utf-8')
    print('Assembled prompt/request locally; generation calls=0')
if __name__=='__main__':
    main()
