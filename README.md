# RivLink Manager
RivLink Manager is an attempt to make network switches administration accessible to anyone.

## Installation

```bash
git clone https://github.com/rivlink/rivlink_manager
cd rivlink_manager
virtualenv --python=python3 env
source env/bin/activate
pip install django
pip install napalm
./manage.py makemigrations
./manage.py migrate
./manage.py createsuperuser
```

## Configuration

Edit ```rivlink_manager/settings.py```

+ Input your own secret key
+ Set debug to false
+ Add all the allowed hosts you need, for example ```127.0.0.0.1``` or ```domain.local```


## Run

```bash
source env/bin/activate
./manage.py runserver 0.0.0.0:8000
```

