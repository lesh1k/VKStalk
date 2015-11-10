# Mail sending from v4.0.1. In v.5.0.0+ this was not implemented
# Needs review, cleaning and refactoring


def SendMail(self, mail_type='daily', msg='default_message', filename=''):
    # ConsoleLog('Sending ' + mail_type + ' email...')

    TEXT = ''
    SUBJECT = ''
    if mail_type == 'daily':
        # Add number of logs and error to message
        TEXT += 'Logs written: ' + str(self.logs_counter)
        TEXT += '\nErrors occured: ' + str(self.error_counter)
        TEXT += '\nLast error: ' + str(self.last_error) + '\n\n\n'
        # Writing the message (this message will appear in the email)
        SUBJECT = 'VKStalk report. Name: ' + \
            self.user_data['name'] + '. ID: ' + self.user_id
        if self.filename:
            file_handle = open(self.filename, 'r')
            TEXT = TEXT + file_handle.read()
            file_handle.close()
    elif mail_type == 'error':
        # Writing the message (this message will appear in the email)
        SUBJECT = 'VKStalk ERROR. User ID: ' + self.user_id
        TEXT += msg
    elif mail_type == 'summary':
        # Writing the message (this message will appear in the email)
        SUBJECT = 'VKStalk summary. Name: ' + \
            self.user_data['name'] + '. ID: ' + self.user_id
        if self.filename:
            file_handle = open(filename, 'r')
            TEXT = TEXT + file_handle.read()
            file_handle.close()

    # Constructing the message
    message = 'Subject: %s\n\n%s' % (SUBJECT, TEXT)
    # Specifying the from and to addresses
    fromaddr = 'vkstalk@gmail.com'
    if not self.mail_recipient:
        # ConsoleLog('Mail NOT sent!')
        clear_screen()
        return False
    toaddrs = self.mail_recipient

    # Gmail Login

    mail_username = 'HERE_BE_USERNAME'
    mail_password = 'HERE_BE_PASSWORD'

    # Sending the mail

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(mail_username, mail_password)
    server.sendmail(fromaddr, toaddrs, message)
    server.quit()
    # ConsoleLog('Mail sent!')
    return True


def send_mail_if_time():
    try:
        current_step = 'Sending email.'
        if self.debug_mode:
            WriteDebugLog(current_step, userid=self.user_id)
        if (self.email_notifications
                and (datetime.now().hour in self.mail_notification_hours)
                and (datetime.now().hour != self.last_mail_time)):
            current_step = "Trying to send daily email."
            if self.debug_mode:
                WriteDebugLog(current_step, userid=self.user_id)
            if self.SendMail():
                self.last_mail_time = datetime.now().hour
    except Exception as e:
        current_step = "Could not send DAILY email."
        if self.debug_mode:
            WriteDebugLog(current_step, userid=self.user_id)
        self.HandleError(
            step=current_step,
            exception_msg=e,
            dump_vars=True,
            console_msg='Could not send email.\n' + str(e)
        )
        pass

    # Send summary email if the time has come =)
    try:
        current_step = 'Preparing a summary.'
        if self.debug_mode:
            WriteDebugLog(current_step, userid=self.user_id)
        if (self.email_notifications
                and (datetime.now().hour in self.summary_notification_hours)
                and (time.localtime().tm_wday in self.summary_notification_days)
                and (datetime.now().day != self.last_summary_mail_day)):
            current_step = "Trying to send summary mail."
            if self.debug_mode:
                WriteDebugLog(current_step, userid=self.user_id)
            if self.SendMail(mail_type='summary', filename=Summarize(user_name=self.user_data['name'], max_files=self.max_files_for_summary)):
                self.last_summary_mail_day = datetime.now().day
    except Exception as e:
        current_step = "Could not send SUMMARY email."
        if self.debug_mode:
            WriteDebugLog(current_step, userid=self.user_id)
        self.HandleError(
            step=current_step,
            exception_msg=e,
            dump_vars=True,
            console_msg='Could not send summary email.\n' + str(e)
        )
