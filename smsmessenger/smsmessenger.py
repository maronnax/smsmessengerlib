import imaplib
import email
import time
import smtplib
from queue import Queue
import random
from threading import Lock
from threading import Thread
# from smsmessenger.secret import


USERNAME = None
PASSWORD = None
FROMADDR = None
TOADDRS = None
SMTP_SERVER = None
RECIEVE_PORT = None
SEND_PORT = None
MESSAGE_INTERVAL = None

def setupModule(username, password, fromaddrs, toaddrs, smtp_server, recieve_port, send_port, message_interval):
    USERNAME = username
    PASSWORD = password
    FROMADDR = fromaddrs
    TOADDRS = toaddrs
    SMTP_SERVER = smtp_server
    RECIEVE_PORT = recieve_port
    SEND_PORT = send_port
    MESSAGE_INTERVAL = message_interval
    return



import pdb


callbacks = {}

class InfiniteQueue(Queue):
    def __init__(self, default_value, *kwds, **args):
        self.default_value = default_value
        super(InfiniteQueue, self).__init__(*kwds, **args)

    def get(self, *kwds, **args):
        is_empty = super(InfiniteQueue, self).empty()
        if is_empty:
            return self.default_value

        value = super(InfiniteQueue, self).get(*kwds, **args)
        return value

check_rate_queue = InfiniteQueue(MESSAGE_INTERVAL)

class Globals:
    def __init__(self):
        self._lock = Lock()
        self._quit = False

    def setQuit(self, value):
        self._lock.acquire()
        self._quit = value
        self._lock.release()
        return

    def getQuit(self):
        self._lock.acquire()
        value = self._quit
        self._lock.release()
        return value

    quit = property(getQuit, setQuit)

def makeRandomCode(length = 3):
    alphabet = "0123456789"
    code = "".join([random.choice(alphabet) for ndx in range(length)])
    return code

def extract_body(payload):
    if isinstance(payload,str):
        return payload
    else:
        return '\n'.join([extract_body(part.get_payload()) for part in payload])

def checkMessagesFunction(thread_globals):
     while not thread_globals.quit:
         checkNewMessages()
         interval = check_rate_queue.get()
         print("Sleeping for {} seconds.".format(interval))
         time.sleep(interval)

def checkMessagesOnce(wait_time):
    time.sleep(wait_time)
    checkNewMessages()
    return

module_globals = Globals()

def checkNewMessages():
    conn = imaplib.IMAP4_SSL(SMTP_SERVER, RECIEVE_PORT)
    conn.login(USERNAME, PASSWORD)
    conn.select()
    typ, data = conn.search(None, 'UNSEEN')
    try:
        for num in data[0].split():
            typ, msg_data = conn.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(str(response_part[1], 'utf-8'))
                    subject=msg['subject']
                    print(subject)
                    payload=msg.get_payload()
                    body=extract_body(payload)

                    possible_code = body.split()[0]
                    if possible_code in callbacks:
                        func, args = callbacks[possible_code]
                        func(*args)
                        callbacks.pop(possible_code)

                    print(body)
            typ, response = conn.store(num, '+FLAGS', r'(\Seen)')
    finally:
        try:
            conn.close()
        except:
            pass
        conn.logout()

def sendTextMessage(message, callback = None, args = ()):
    new_intervals = list(reversed([20 for ndx in range(5)] + [40 for ndx in range(5)] + [60 for ndx in range(5)]))
    if callback is not None:
        text_code = makeRandomCode(3)
        message = "{}\nCode: ({})".format(message, text_code)
        callbacks[text_code] = (callback, args)

    # The actual mail send
    server = smtplib.SMTP('{}:{}'.format(SMTP_SERVER, SEND_PORT))
    server.starttls()
    server.login(USERNAME, PASSWORD)
    server.sendmail(FROMADDR, TOADDRS, message)
    server.quit()

    if callback is not None:
        check_once_thread = Thread(target=checkMessagesOnce, args = (60, ))
        check_once_thread.start()
        check_rate_queue.queue.clear()
        for interval in new_intervals:
            check_rate_queue.put(interval)

    return

def makeCallback(msg_ndx):
    def callback():
        sendTextMessage("got your response to {}".format(msg_ndx))
        return
    return callback

def main():
    thread = Thread(target = checkMessagesFunction, args = (module_globals, ))
    thread.start()
    msg_ndx = 1

    while not module_globals.quit:
        message = "This is message {}".format(msg_ndx)
        sendTextMessage(message, makeCallback(msg_ndx))
        msg_ndx += 1
        time.sleep(30)

    return


if __name__ == '__main__':
    main()
