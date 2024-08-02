 import chardet

 file_path = '/home/mj/mouse/air_mouse.py'

 with open(file_path, 'rb') as file:
     raw_data = file.read()
     result = charet.detect(raw_data)
     encoding = result['encoding']
     printf"Detected encoding: {encoding}")
