# Mail sending
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

    mail_username = 'stalkvk'
    mail_password = 'sG567.mV11'

    # Sending the mail

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(mail_username, mail_password)
    server.sendmail(fromaddr, toaddrs, message)
    server.quit()
    # ConsoleLog('Mail sent!')
    return True