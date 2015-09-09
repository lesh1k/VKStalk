from vkstalk import VKStalk
import sys
import re

if __name__ == "__main__":
    keys = []
    values = []
    if (len(sys.argv) % 2 == 1) and (len(sys.argv) > 1):
        # because sys.argv[0] is the filename (i.e. main.py)
        for i in range(1, len(sys.argv)):
            if i % 2 == 0:
                values.append(sys.argv[i])
            else:
                keys.append(sys.argv[i])
        passed_args = dict(zip(keys, values))

    # enable debug mode only if explicitly specified
    enable_debug = bool(int(passed_args.get('debug', 0)))

    # get userID from system args or input from kbd if first is empty
    # e.g."45156687" or "alexei.dvorac"
    user_id = passed_args.get('id', raw_input('User ID:'))

    # see if there is need in email notifications
    email_notifications = bool(int(passed_args.get(
        'notifications', raw_input('Enable email notifications? (0/1):'))))

    # ask for email
    # e.g. mail@example.com
    if email_notifications:
        email = passed_args.get('email', raw_input('Email:'))
        email_valid = False
        while not email_valid:
            email_valid = False if not re.match(
                r"[^@]+@[^@]+\.[^@]+", email) else True
            if not email_valid:
                print 'Invalid mail. Try again...'
                # e.g. mail@example.com
                email = raw_input('Email:')
    else:
        email = ''

    vk_object = VKStalk(user_id, debug_mode=enable_debug,
                        email_notifications=email_notifications, email=email)
    vk_object.Work()
