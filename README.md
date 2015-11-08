####VKStalk - vk.com scraper
######v5.0.0 BETA

Python console application. Scraps a VK user's public information.
When running it displays:
- User online/offline (if offline, it shows last seen time)
- User is using mobile client
- User status (OR current music track if available)
- User data updates (any updates to user data, e.g. profile photo, nr. of wallposts)

#####Setup
1. Clone or download this repo
2. Start a virtualenv within root directory
3. Activate virtualenv
4. Install requirements `pip install -r requirements/base.txt`
5. In src/config. Make a copy of sample_secrets.py and rename it to secrets.py
7. Fill your database information. (By default it uses postgres, but you can try any other database, see [this](http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html))
6. Start the app `python main.py USER_VK_ID`

#####Notes
- You can go ahead and play with settings in src/config/settings.py.
- To see accepted CLI arguments run `python main.py -h`
- To get a summary on user run `python main.py USER_VK_ID --summary`. By default it will write the summary to a file in PROJECT_ROOT/summaries and also print to console. You can change this behaviour using CLI arguments.
