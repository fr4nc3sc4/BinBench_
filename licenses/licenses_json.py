import json

# CREATE LICENSES JSON FILE FROM OUTPUT OF WEBSCRAPING_PKGS.PY

pkgs = {}
licenses = {}

with open('pkgs.json') as openfile:
    pkgs = json.load(openfile)
    for pkg in pkgs:
        pkg_license = pkgs.get(pkg)
        
        if ', ' in pkg_license:  
            split_licenses = pkg_license.split(', ')
            
            for license in split_licenses:
                
                if license in licenses:
                    licenses[license].append(pkg)
                else:
                    licenses[license] = [pkg]
        else:
            if pkg_license in licenses:
                    licenses[pkg_license].append(pkg)
            else:
                    licenses[pkg_license] = [pkg]
with open('licenses.json', 'w+') as outfile:
    json.dump(licenses, outfile, indent=2, sort_keys=True)

