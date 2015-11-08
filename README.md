####VKStalk - vk.com scraper
######v5.0.0 BETA

Python console application. Scraps a VK user's public information.
When running it displays in console:
- User online/offline (if offline, it shows last seen time)
- User is using mobile client
- User status (OR current music track if available)
- User data updates (any updates to user data, e.g. profile photo, nr. of wallposts)

#####Sample console output
```
=======| VKStalk ver. 5.0.0 BETA |=======

Launched on 08-November-2015 at 22:15
User ID: 45156687
User Name: Alexey Dvorak
Logs written: 0

==============| LATEST LOG |==============

>>> Checked on 2015-11-08 at 22:15:30 <<<

Date: 08-11-2015. Time: 19:09:20
Alexey Dvorak -- last seen yesterday at 03:49 [Mobile]
Status: it was all about cookies

==========================================
```

#####Setup
1. Clone or download this repo
2. Start a virtualenv within root directory
3. Activate virtualenv
4. Install requirements `pip install -r requirements/base.txt`
5. In `src/config`. Make a copy of `sample_secrets.py` and rename it to `secrets.py`
7. In `src/config/secrets.py`
  - Fill your database information. (By default it uses postgres, but you can try any other database, see [this](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html))
  - Set your timezone `CLIENT_TZ`
8. Start the app `python main.py USER_VK_ID`

#####Notes
- You can go ahead and play with settings in `src/config/settings.py`.
  - Of more interest could be: `DATA_FETCH_INTERVAL`, `MAX_CONNECTION_ATTEMPTS`, `CONNECTION_TIMEOUT`, `CONSOLE_LOG_TEMPLATE`
- To see accepted CLI arguments run `python main.py -h`
- To get the summary on a user run `python main.py USER_VK_ID --summary`. By default it will write the summary to a file in `PROJECT_ROOT/summaries` and also print to console. You can change this behaviour using CLI arguments.

#####Currently it parses the following information
- User data
  - name
  - birthday
  - photo
  - hometown
  - site
  - instagram
  - facebook
  - twitter
  - skype
  - phone
  - university
  - studied_at
  - wallposts
  - photos
  - videos
  - followers
  - communities
  - noteworthy_pages
  - current_city
  - info_1
  - info_2
  - info_3
- Activity
  - is_online
  - is_mobile
  - status
  - last_visit_lt_an_hour_ago
  - last_visit
