Price Monitor: A Data Warehouse of Tire Prices
==============================================


Motivation
----------

Tire prices fluctuate.

Chelsea DeNofa recommends that you keep consistent tires on your drift car.
That means consistenly running the same brand, model, size, and age of tire.
By age, I mean how long since manufacture date. I don't believe amount of tread
actually matters, as long as the carcass is still covered in rubber (as opposed to having its slippery cords showing)

In my case, I chose the Lexani LXTR-203 in P205/55R16.
https://simpletire.com/lexani-205-55r16-lxst2031655010-tires
The first time I bought them, they were $49 each.
A month later I wanted two more, and they were $65 each.
I called simpletire and asked how to choose a tire that would stay the same price.
They said there is no such thing as a stable tire price.

I balked at the $65 price tag (Actually, the salesman offered them for $58 since I had bought them before), and I changed to a different brand/model. And later, the Lexani LXTR-203
went down to $48, and has stayed there for three months. So I switched back. But I now
have the oddballs that I bought in the interim.

I wish I had stayed with the Lexanis the whole time, but I didn't have a history
of its pricing. Now I do.


Prerequisites
-------------

    sudo apt install postgresql nginx python3-venv redis-server

Install
-------

    cd path/to/repo
    python3 -m venv env
    env/bin/pip install -r requirements.txt
    # OR
    env/bin/pip install bs4 django jinja2 lxml psycopg2-binary requests redis gunicorn



Create Database User
--------------------

Create a postgresql user that can create databases
(Database creation is required if you want to run the test suite from that environment)

    sudo -u postgres createuser --createdb ubuntu


Create Database
---------------

    sudo -u postgres createdb price_monitor --owner ubuntu


Import Data
-----------

If you have an sql file that is already populated:

    sudo -u postgres psql -d price_monitor  -f /path/to/sql/file

Run Migrations
--------------

Skip this step if you imported data

    cd path/to/repo
    env/bin/python manage.py migrate

Systemd
-------

Service files:

    monitor/price-monitor.service # Runs application server
    monitor/price-monitor-fetch.service # Restarts every hour

Run Tests
---------

    env/bin/python manage.py test

Fetch
-----

### Production

    env/bin/python manage.py fetch_current_prices

### Development

    PAGER=less DJANGO_SETTINGS_MODULE=monitor.settings_development env/bin/python manage.py fetch_current_prices


Run manage.py in Development
----------------------------

    PAGER=less DJANGO_SETTINGS_MODULE=monitor.settings_development env/bin/python manage.py


Run Server in Production
------------------------

Note in production, only certain domains are allowed.
So make sure you have nginx set up.

    env/bin/gunicorn monitor.wsgi


Run Server in Development
-------------------------


    PAGER=less DJANGO_SETTINGS_MODULE=monitor.settings_development env/bin/python manage.py runserver


Low Memory vs Multithreaded
---------------------------

Two solutions are built.
To choose between the two, just open this file:

  simpletire/management/commands/fetch_current_prices.py

and call either

    # The low memory version
    # Single Threaded
    # Makes use of generators instead of building up long lists
    fetch_and_write_pages()

or

    # Multi-Threaded
    # Uses futures
    # Builds up long lists of things to pass to those futures
    fetch_and_write_pages_async()


Performance
-----------

It takes about 500ms to fetch a tire page. That workload is I/O bound.

It takes about 200ms to build the BeautifulSoup document and pull values from it.
This workload is CPU bound. Based on that, it doesn't make sense to apply more than
five threads because five threads will keep the CPU busy.

However, regardless of whether 5 or 10 threads are used, the workload is spread across
all four CPUs, and averages about 30%.

85,000 tires to fetch
Processes about 3/second
Estimated time to completion: 8 hours

Known Bugs
----------

In (heavily restricted) firefox, applying two filters, then pressing the browser back button leaves you with no tires displayed. (Works fine in chromium.)
In duckduckgo on android, click tire link, then click "back", and treadwear column disapppears. (Not tested on other browsers)
Kenda Kaiser is listed twice. Federal SS595 is listed twice.


Feature Requests
----------------

- Cron incantation
- Filter for treadwear (400 or less, 300 or less, 240 or less, 200 or less)
- Click column heading to sort by current ptice (highlight sorted column)
- Contact authors tires@jackdesert.com


Site Down Placeholder
---------------------

Files are in doc/


Backlog
-------

- More padding around search box


Icebox
------

Guide to actual tire height: https://wayalife.com/showthread.php/35075-The-Ultimate-TRUE-TIRE-SIZE-Database
Nominal size: http://en.wikibedia.ru/wiki/Nominal_size
