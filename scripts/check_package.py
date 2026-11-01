#!/usr/bin/env python3
"""Offline public-package checks. Never score art or invoke a generation service."""
from pathlib import Path
import hashlib,json,re
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser

def check(root):
    count=0
    def require(ok,message):
        nonlocal count
        if not ok:raise ValueError(message)
        count+=1
    profile=json.loads((root/'style_profile.json').read_text())
    skill=(root/'SKILL.md').read_text()
    require(skill.startswith('---\nname: lafiteskill\n'),'Skill name/frontmatter')
    require(profile['version'] in skill,'Skill/Profile version mismatch')
    require(profile['profile_id']=='lafiteskill','Runtime identifier mismatch')
    require(len(profile['core_traits'])==7,'Seven retained principles required')
    require('evidence_catalog' not in profile,'Private historical catalog in runtime')
    for required in ('README.md','LICENSE','CHANGELOG.md','examples/README.md','assets/ASSET-LICENSE.md'):
        require((root/required).is_file(),'Missing '+required)
    approved=root/'assets/approved/manifest.json'
    manifest=json.loads(approved.read_text())
    asset=approved.parent/manifest['path']
    require(hashlib.sha256(asset.read_bytes()).hexdigest()==manifest['sha256'],'Approved image hash')
    require(manifest['user_accepted'] is True and manifest['external_requests'] is None,'Reference provenance changed')
    require((approved.parent/manifest['asset_license']).is_file(),'Asset license link')
    require((root/profile['approved_visual_reference']).is_file(),'Profile approved reference')
    for trait in profile['core_traits']:
        require((root/trait['evidence']).is_file(),'Broken trait evidence')
    examples=root/'examples/real-cases'
    index=json.loads((examples/'index.json').read_text())
    require(index['packaging_generation_calls']==0 and len(index['cases'])==2,'Two historical showcase cases; no packaging generation')
    for entry in index['cases']:
        case_path=(examples/entry['case']).resolve()
        require(case_path.is_relative_to(examples) and case_path.is_file(),'Case path')
        case=json.loads(case_path.read_text())
        folder=case_path.parent
        require(case['user_accepted'] is True and case['approval_quote']=='两张都认可','Explicit user approval')
        require(case['generated_profile_version']=='1.29.0' and case['packaged_version']==profile['version'],'Historical versus packaged versions')
        require(case['actual_calls']==1 and case['generated_during_this_packaging'] is False,'Historical one-call case')
        require(hashlib.sha256((folder/case['image']).read_bytes()).hexdigest()==case['image_sha256']==entry['image_sha256'],'Showcase image hash')
        prompt=(folder/case['prompt']).read_text()
        require(hashlib.sha256(prompt.encode()).hexdigest()==case['prompt_sha256'],'Actual prompt hash')
        redacted=json.loads((folder/'request-redacted.json').read_text())
        require(redacted['record_type']=='redacted_copy_not_original_request_bytes' and redacted['redactions'],'Request redaction disclosure')
        require(redacted['request']['prompt']==prompt and redacted['original_request_sha256']==case['original_request_sha256'],'Public request/prompt provenance')
        require(case['identity_photo_distributed'] is False and not (folder/'input').exists(),'Private photo excluded')
        require([x['role'] for x in case['references']]==['identity','quality'],'Reference roles')
        review=json.loads((folder/'visual-review.json').read_text())
        require(review['user_accepted'] is True and review['remaining_issues'],'Approval with remaining limitations')
        require(case['timeline']['frozen_at_utc']<case['timeline']['started_at_utc']<case['timeline']['completed_at_utc'],'Actual frozen/request timeline')
    allowed={'.md','.json','.py','.yml','.yaml','.txt','.html'}
    for path in sorted(root.rglob('*')):
        if any(part in {'.git','__pycache__','input','output'} for part in path.relative_to(root).parts):continue
        if not path.is_file():continue
        require(not path.is_symlink(),'Public package must be standalone: '+str(path))
        require(path.name!='.DS_Store' and not path.name.startswith('.env'),'Private/cache artifact')
        if path.suffix=='.png':
            require(not re.search(rb'/(?:Users|home)/[^/\s]+/',path.read_bytes()),'Private path in image metadata')
        if path.suffix not in allowed and path.name not in {'LICENSE','.gitignore'}:continue
        body=path.read_text()
        require(not re.search(r'/(?:Users|home)/[^/\s]+/|Photos Library\.photoslibrary|127\.0\.0\.1:[0-9]+',body),'Private path in '+str(path.relative_to(root)))
        require(not re.search(r'sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}',body),'Credential-like value')
        if path.suffix=='.md':
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',body):
                url=urlsplit(target)
                if url.scheme or url.netloc or not url.path:continue
                dest=(path.parent/unquote(url.path)).resolve()
                require(dest.is_relative_to(root) and dest.is_file(),'Broken local link: '+str(path.relative_to(root))+' -> '+target)
    class LocalLinks(HTMLParser):
        def __init__(self):super().__init__();self.targets=[]
        def handle_starttag(self,tag,attrs):
            for key,value in attrs:
                if key in {'href','src'} and value:self.targets.append(value)
    for page in root.rglob('*.html'):
        if any(part in {'.git','output','input'} for part in page.relative_to(root).parts):continue
        parser=LocalLinks();parser.feed(page.read_text())
        for target in parser.targets:
            url=urlsplit(target)
            if url.scheme or url.netloc or not url.path:continue
            resolved=(page.parent/unquote(url.path)).resolve()
            require(resolved.is_relative_to(root) and resolved.is_file(),'Broken replay asset/link')
    return {'status':'pass','checks':count,'profile_version':profile['version'],'generation_calls':0,'scope':'packaging, links, reference provenance and privacy; not artistic quality'}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    try:print(json.dumps(check(root),ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError) as exc:
        print(json.dumps({'status':'fail','reason':str(exc)},ensure_ascii=False));raise SystemExit(1)
