import discord
import asyncio
import re

client = discord.Client()
mongo = None
config = None

@client.event
async def on_ready():
   print('Logged in as')
   print(client.user.name)
   for server in client.servers:
      for s_member in server.members:
         print(s_member.name, s_member.id)

   print('------')

@client.event
async def on_message(message):
   if len(message.embeds) > 0:
      pass
   else:
      await handle_karma(message.content, message.channel)

def get_member_id(member):
   cursor = mongo.karma.find_one({"member": member})
   if cursor == None:
      found = False
      for server in client.servers:
         if server.name == config['discord-server']:
            for s_member in server.members:
               if s_member.name == member:
                  mongo.karma.insert({"member": member, "member_id": s_member.id, "count":0})
                  return s_member.id

      if not found:
         mongo.karma.insert({"member": member, "count":0})

   else:
      if "member_id" not in cursor:
         return None

      return cursor['member_id']

async def handle_karma(message, channel):
   operators = ["+", "-"]

   for op in operators:
      string = "(\S*[{0}]\{0})".format(op)
      regex = re.compile(string)

      match = regex.findall(message)
      if len(match) > 0:
         for m in match:
            error = False
            if op == "+" and "-" in m:
               error = True
            if op == "-" and "+" in m:
               error = True
            if "" == m:
               error = True

            if not error:
               count = m.count(op)
               mod = count % 2
               if count == 1:
                  error = True
               else:
                  if mod == 0:
                     count = count / 2
                  else:
                     count = ((count + 1) / 2) - 1

            if not error:
               member = m[:m.find(op)].lower()
               if "@" in member:
                  regex = re.compile("<@(.*)>")
                  match = regex.search(member)
                  if match == None and "@" == member[0]:
                     member_id = member.remove(0)
                  else:
                     member_id = match.groups()[0]

               else:
                  member_id = get_member_id(member)

               if member != "":
                  reply_format = '<@%s> now has %s karma'
                  reply_member = member_id
                  if member_id == None:
                     reply_format = '%s now has %s karma'
                     reply_member = member

                     current_count = write_karma(count, op, member=member)
                  else:
                     current_count = write_karma(count, op, member_id=member_id)

                  reply = reply_format % (reply_member, int(current_count))
                  await client.send_message(channel,  reply)

def write_karma(count, operator, member=None, member_id=None):
   if operator == "-":
      count = 0 - count

   current_count = count

   if member == None and member_id != None:
      key = "member_id"
      value = member_id.lower()
   else:
      key = "member"
      value = member.lower()

   cursor = mongo.karma.find_one({key: value})
   if cursor == None:
      if operator == "+":
         mongo.karma.insert({key: value, "count": current_count})
      else:
         mongo.karma.insert({key: value, "count": current_count})
   else:
      current_count = cursor['count'] + count

      mongo.karma.update({key: value}, {"$set": {"count": current_count}})

   return current_count

class Bot(object):
   def __init__(self, db, settings):
      global mongo
      global config

      mongo = db
      config = settings

   def run(self):
      client.run(config['token'])
