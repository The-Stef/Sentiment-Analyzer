import re

date_pattern = re.compile(r'\b\d{1,2}/\d{1,2}/\d{2}\b')
time_pattern = re.compile(r'\d{2}:\d{2}')
name_pattern = re.compile(r'(?<=- )(.*?)(?=:)')
msg_pattern = re.compile(r'(?<=: )(.*)$')

# Admin messages - useless for sentiment analysis
FILTERS = [
      "<Media omitted>",
      "changed the settings so only admins can edit the group settings",
      "changed this group's icon",
      "changed the group description",
      "pinned a message",
      "added",
      "now an admin",
      "removed",
      "no longer an admin",
      "joined using this group's invite link",
      "left",
      "changed this group's settings to allow only admins to send messages to this group",
      "started a call",
      "changed this group's settings to allow all members to send messages to this group",
      "changed the settings so all members can edit the group settings",
      "changed this group's settings to allow only admins to add others to this group",
      "turned on admin approval to join this group",
      "created group",
      "Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them. Learn more.",
      "changed their phone number to a new number. Tap to message or add the new number.",
      "was added",
      "changed to",
      "This message was deleted",
      "This group has over 256 members so now only admins can edit the group settings.",
      "New members need admin approval to join this group.",
      "As a member, you can join groups in the community and get admin updatesYour profile is visible to admins",
      "As a member, you can join groups in the community and get admin updates",
      "Your profile is visible to admins",
      "joined from the community",
      "updated the message timer. New messages will disappear from this chat 7 days after they're sent, except when kept.",
      "You received a view once message. For added privacy, you can only open it on your phone.",
]

FILTERS_REGEX = re.compile('|'.join(map(re.escape, FILTERS)))