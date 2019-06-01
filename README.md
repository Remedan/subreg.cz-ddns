# subreg.cz DDNS

A simple script that checks the host's current public IP via https://ipify.org and uses subreg.cz's SOAP API to create/update a DNS record pointing to said IP. Depends on [zeep](https://python-zeep.readthedocs.io/).

Before running the script you need to rename `settings.dist.ini` to `settings.ini` and edit it appropriately. For 'sub.example.org' the domain field should be 'example.org' and subdomain is 'sub'.
