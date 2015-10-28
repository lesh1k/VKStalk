#VKStalk - vk.com stalker
v4.0.1

=====================================================================================

Dependencies:

* Python 2.7.3-2.7.5
* BeautifulSoup4


Python console application.
This app allows collecting info about a VK.com user. 
It does not use a VK.com user acc, thus only public info is collected.
It displays the following info: user online/offline, current status.
It writes logs to the CUR_DIR/Data/Logs. In logs most of the available info can
be found (e.g. number of wallposts, photos, profile_pic link, etc.)

Email notifications.
Summaries are sent every Sunday at 9:00.
Daily reviews (logs written), daily at 9:00 and 21:00.

======================================================================================

- To run it under Windows, just double click the main.py
- To run it under Linux you should launch it from a terminal.
and there are several options available:
either python main.py,
or python main.py id USER_ID notifications EMAIL_NOTIFICATIONS debug DEBUG 

======================================================================================

OPTIONS

id - user id you would like to stalk
notifications: 0-no, any other value - yes [to receive updates by email]
debug: 0-no, any other value - yes [will write debug logs to CUR_DIR/Data/Debug]
email: email on which updates will be sent.