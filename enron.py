#!/usr/bin/env python

import os
import email
from collections import defaultdict
import time


EMAIL_PATH = 'enron_with_categories'


class Email:
  def __init__(self, s):
    msg = email.message_from_string(s)

    self.id = msg['message-id']
    self.sender = msg['from'].strip()
    self.subject = msg['subject']
    self.date = msg['date']
    self.timestamp = time.mktime(email.utils.parsedate(msg['date']))

    self.to = []
    if msg['to']:
      self.to = [r.strip() for r in msg['to'].split(',')]

    self.cc = []
    if msg['cc']:
      self.to = [r.strip() for r in msg['cc'].split(',')]

    self.bcc = []
    if msg['bcc']:
      self.to = [r.strip() for r in msg['bcc'].split(',')]

    self.recipients = self.to + self.cc + self.bcc


  def direct(self):
    return len(self.recipients) == 1

  def broadcast(self):
    return len(self.recipients) > 1


def enron_emails():
  for path, dirs, files in os.walk(EMAIL_PATH):
    if not dirs:
      for f in files:
        if f.endswith('.txt'):
          yield Email(open(os.path.join(path, f)).read())


emails = list(enron_emails())

recipient_count = defaultdict(int)
sender_count = defaultdict(int)

# Build a map from recipients to emails for response lookup.
recipient_map = defaultdict(list)

for m in emails:
  if m.direct():
    recipient_count[m.recipients[0]] += 1

  if m.broadcast():
    sender_count[m.sender] += 1

  for r in m.recipients:
    recipient_map[r].append(m)

top_recipients = recipient_count.items()
top_recipients.sort(key=lambda x: -x[1])
print '\nTop recipients:'
print top_recipients[:3]

top_senders = sender_count.items()
top_senders.sort(key=lambda x: -x[1])
print '\nTop senders:'
print top_senders[:3]

responses = []
for m in emails:
  for n in recipient_map[m.sender]:
    if (n.timestamp < m.timestamp and
        n.sender in m.recipients and
        n.subject and m.subject and  # Assume nonempty subjects.
        n.subject in m.subject):
      responses.append((m.timestamp - n.timestamp, n, m))

responses.sort()
print '\nFastest responses:'
for response_time, original, response in responses[:5]:
  print
  print '----- Original -----'
  print original.id
  print original.date
  print 'From:', original.sender
  print 'To:', ', '.join(original.recipients)
  print 'Subject:', original.subject
  print '----- Response -----'
  print response.id
  print response.date
  print 'From:', response.sender
  print 'To:', ', '.join(response.recipients)
  print 'Subject:', response.subject
  print
  print 'Response time: %s seconds' % response_time
