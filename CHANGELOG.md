# Changelog

All notable changes to this project will be documented in this file.
    ## [2.7.1] - 2026-04-10

### Bug Fixes

- Quad-match violation + terminology rename role→title    
- Add AMP communication restriction to all sub-agents    
- Correct communication rules in main-agent    
- Correct governance terminology, version sync, and communication rules    
- Resolve all CPV MINOR issues (7 → 0)    
- Publish.py runs CPV validation remotely + pre-push enforces --strict    
- Ruff F541 — remove extraneous f-prefix in publish.py    
- Remove CPV_PUBLISH_PIPELINE bypass from pre-push hook — CPV --strict always runs    
- Publish.py + pre-push use cpv-remote-validate via uvx    
- Align pyproject.toml version to 2.7.0 (matches plugin.json)    

### Features

- Add compatible-titles and compatible-clients to agent profile    
- Add communication permissions from title-based graph    
- Add smart publish pipeline + pre-push hook enforcement    
- Add R12 minimum team composition rule to MANAGER persona    
- Add API quick reference and auth docs to MANAGER persona    
- R16 — MANAGER must NEVER use governance password    
- MANAGER can create teams via AID auth + team lifecycle management    
- Comprehensive MANAGER powers update — AID auth, team CRUD, wake/hibernate    

### Miscellaneous

- Update uv.lock    
- Bump version to 2.6.8    
- Update uv.lock    

### Ci

- Update validate.yml to use cpv-remote-validate --strict    
- Strict publish.py + pre-push hook + release.yml propagation    


