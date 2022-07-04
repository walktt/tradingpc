history = {}
def doit(val):
    key = 'qqq'
    if (key in history) and (history[key] != val):
        print('new value' + val, ' old value' + history[key])
        history[key] = val
    else:
        history[key] = val
        print('same value or not in history')

