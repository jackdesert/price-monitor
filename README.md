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



Install
-------

    env/bin/pip install psycopg2-binary requests bs4 ipdb lxml jinja2


Fetch
-----

    env/bin/python manage.py fetch_current_prices


Timings
-------

Took 19 minutes for full pass on one tire size. (1194 tires, 481 in stock)

Backlog
-------

- Query from Athena
  - adapt query to use a window function instead of DISTINCT ON
    because PrestoDB (Athena's backend) does not support DISTINCT ON

- cron incantation
- Decide whether only tires currently in stock should be displayed on stats page
- Decide whether only in-stock readings should be used for calculating mean, max, stddev_samp
  (probably so, as they may ignore prices while it's out of stock)
- Consider whether to use the search functionality on simpletire.com to
  filter by the appropriate tire size. (As opposed to reading the sitemaps)
  The benefit is that you could sort by price and only show the cheap ones.
  But then what if a cheap tire goes expensive for a time...now your stats are impure..

