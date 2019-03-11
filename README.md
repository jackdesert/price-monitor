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

    sudo apt install postgres nginx python3-venv redis

Install
-------

    cd path/to/repo
    python3 -m venv env
    env/bin/pip install boto3 bs4 django ipdb jinja2 lxml pandas psycopg2-binary requests redis



Create Database User
--------------------

Create a postgresql user that can create databases
(Database creation is required if you want to run the test suite from that environment)

    sudo -u postgres createuser --createdb ubuntu


Create Database
---------------

    sudo -u postgres createdb price_monitor --owner ubuntu


Run Migrations
--------------

    cd path/to/repo
    env/bin/python manage.py migrate


Run Tests
---------

    env/bin/python manage.py test

Fetch
-----

    env/bin/python manage.py fetch_current_prices


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

Backlog
-------

- When one filter is clicked, disable all filters to wait for the page refresh
- On phone, hide some of the data so it all fits on screen
  (Need name, size, mean)
- Once a filter is selected, "Specify at least one filter" needs a different message



- cron incantation
- Decide whether only tires currently in stock should be displayed on stats page
- Decide whether only in-stock readings should be used for calculating mean, max, stddev_samp
  (probably so, as they may ignore prices while it's out of stock)
- Consider whether to use the search functionality on simpletire.com to
  filter by the appropriate tire size. (As opposed to reading the sitemaps)
  The benefit is that you could sort by price and only show the cheap ones.
  But then what if a cheap tire goes expensive for a time...now your stats are impure..

