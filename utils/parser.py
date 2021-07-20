def parsePlayers (string):
  arr = string.split(' ')
  players = 'никого нет('
  online = 0
  try:
    online = int(arr[2])
  except Exception as e:
    return 0, 'никого нет('
  if online > 0:
    players=''
    for i in range(10, len(arr)):
      players += arr[i]
      if i < len(arr) - 1:
        players += ', '
      
  return online, players