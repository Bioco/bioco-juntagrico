# biocò intranet
This is the repo behind the intranet of biocò (Gemüsegenossenschaft Region Baden-Brugg)

## Credits
This is largely based on the work by [juntagrico](https://juntagrico.org/)

## Setup 
### Local test installation
```
python -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt

# restore a backup 
# ... or

python manage.py migrate
python manage.py createsuperuser 
```

### Run local test installation
```
# Define environment variables (see below)
python manage.py runserver
```

### Environment variables to define

#### Required by juntagrico
* JUNTAGRICO_SECRET_KEY
* JUNTAGRICO_EMAIL_HOST
* JUNTAGRICO_EMAIL_USER
* JUNTAGRICO_EMAIL_PASSWORD

#### Optionally used by juntagrico
* JUNTAGRICO_DEBUG (To disable debug mode)
* JUNTAGRICO_EMAIL_WHITELISTED
* JUNTAGRICO_EMAIL_PORT
* JUNTAGRICO_EMAIL_TLS

* DB configuration (alternatively `dj_database_url` is used)
  * JUNTAGRICO_DATABASE_ENGINE
  * JUNTAGRICO_DATABASE_NAME
  * JUNTAGRICO_DATABASE_USER
  * JUNTAGRICO_DATABASE_PASSWORD
  * JUNTAGRICO_DATABASE_HOST
  * JUNTAGRICO_DATABASE_PORT
  
#### Required by the biocò customizations:  
* BIOCO_OMBUDSMAN_CONTACT
  (For example "First Name, email, phone")
* BIOCO_FINANCE_CONTACT
  (For example "First Name, email, phone")
