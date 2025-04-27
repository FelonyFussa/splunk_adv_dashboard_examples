# splunk_adv_dashboard_examples
A collection of Splunk dashboards, exploring beyond the standard usecases.

## Installation
---

1. pip3 install cryptography
2. install application normally
3. add CRYPTOGRAPHY_ALLOW_OPENSSL_102=1 to splunk_launch.conf
4. restart splunk

# Dashboards
## Configuration Dashboard
This dashboard provides a form to submit a URL, Username and password. The provided password will be "encyrpted" in the backend. a decyption utility is included in the bin diectory of the app.

includes:
- restmap.conf
- web.conf
- credential_handler.js
  - handles sending form input to splunk restmap
- credentials.py
  - creates configuration file in app/local to store input information and identification of generated password key
    - to generate a new key, simply delete the created key in app/etc/auth
  - warning, currently contains debug log in app/var/log that contains clear text form submission
- decrypt_pass.py
  - poc to collect key informaiton and decrypt provided password.

## decrypt password

1. cd to etc/apps/adv_dashboards
2. python3 bin/decrypt_pass
