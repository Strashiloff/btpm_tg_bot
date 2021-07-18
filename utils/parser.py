def parsePlayers (string):
  arr = string.split(' ')
  players = ''
  try:
    online = int(arr[5])
  except Exception as e:
    return 0, 'никого нет('
  if online > 0:
    for i in range(13, len(arr)):
      players += arr[i]
      
  return online, players