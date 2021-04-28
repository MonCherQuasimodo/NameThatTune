'''
   Prod. by Stepan Platinsky / MonCherQuasimodo
   11.04.2021
'''

#pip install pytube
#pip install moviepy

from pytube import YouTube
from moviepy.editor import *
from moviepy.editor import VideoFileClip
from enum import Enum

import os
import shutil
import string
import time
import traceback
 
   
build_folder = 'build'
tmp_folder = 'tmp_folder'

class ContentType(Enum):
  NONE = 0
  AUDIO = 1
  VIDEO = 2
  BOTH = 3
  
  
TypeToItemName = {
  ContentType.AUDIO : "Track",
  ContentType.VIDEO : "MuteVideo"
  ContentType.BOTH : "Video"
}

TypeToItemExtension = {
  ContentType.AUDIO : ".mp3",
  ContentType.VIDEO : ".webm"
  ContentType.BOTH : ".avi"
}

TypeToItemCodec = {
  ContentType.AUDIO : "mp3",
  ContentType.VIDEO : "libvpx"
  ContentType.BOTH : "mpeg4" 
}

def progress_func(stream, chunk, bytes_remaining):
  prev = -1
  cur_progress = int((1-bytes_remaining/stream.filesize) * 100)
  if (cur_progress > prev) :
    print('Download progress: {}%'.format(cur_progress), end='\r')
    prev = cur_progress

def download(url, type):
  yt = YouTube(url, on_progress_callback=progress_func).streams
  paths = []
  
  if type &  ContentType.AUDIO:
    paths[TypeToItemNamep[ContentType.AUDIO]] = yt.filter(only_audio=True).order_by('abr').desc().first().download(output_path=tmp_folder)
  
  if type & ContentType.VIDEO:
    paths[TypeToItemNamep[ContentType.VIDEO]] = yt.filter(file_extension='webm').order_by('resolution').desc().first().download(output_path=tmp_folder) 
  
  return paths

def time_converter(time):
    return tuple(map(int, time.split(':')))

def crop(type, path, new_name, begin, end, path_to_save):
  begin = time_converter(begin)
  end = time_converter(end)
  
  if type == ContentType.AUDIO:
    audio_clip = AudioFileClip(path)
    audio_clip.subclip(begin, end).write_audiofile(filename=os.path.join(path_to_save, new_name + '.mp3'), codec='mp3')
    audio_clip.close()
  elif type == ContentType.VIDEO:
    video_clip = VideoFileClip(path)
    video_clip.subclip(begin, end).write_videofile(bitrate="25000k", filename=os.path.join(path_to_save, new_name + '.webm'), codec='libvpx')
    video_clip.close()
  else:
    pass

def handle_item(**params):
  path = download(params['url'], params['type'])
  crop(params['type'], path, params['new_name'], params['begin'], params['end'], params['path_to_save'])
  os.remove(path)

def parse_format_line(line):
  # url new_name begin end
  labels = ['url', 'begin', 'end']
  params = dict(zip(labels, line.split()))
  return params

def delete_puctuation_and_separator(str):
  return str.translate(str.maketrans(string.punctuation, '_' * len(string.punctuation)))

def content_of_file(path):
  if not os.path.isfile(path):
    open(path, 'a').close()
  with open(path, 'r', encoding='UTF8') as file:
    content = file.readlines()
  return content

def resize_list(list, size):
  return list[:size] + [0]*(size - len(list))
  

def handler_dir(path_to_save, path_to_format_list, type):
  os.mkdir(tmp_folder)
  
  name_cash_file = os.path.join(os.path.abspath('./' + build_folder), delete_puctuation_and_separator(path_to_format_list) + '.txt')
  
  content_format_input = content_of_file(path_to_format_list) 
  previous_content_cash = resize_list(content_of_file(name_cash_file), len(content_format_input))
  
  with open(name_cash_file, 'w', encoding='UTF8') as cash_file:
    for ind, zip_val in enumerate(zip(previous_content_cash, content_format_input), 1):
      
      cash = zip_val[0]
      input = zip_val[1]
      output_name = '{}_{}'.format(TypeToItemName[type], ind)
      
      if (input == cash):
        print ('{} is not changed'.format(output_name))
      elif not input.startswith('https'):
        print ('{} is not provides https ref'.format(output_name))
      else: 
        handle_item(type=type, path_to_save=path_to_save, new_name=output_name, **parse_format_line(input))
        print ('Done {}'.format(output_name))
      cash_file.write(input)
      
  os.rmdir(tmp_folder)

def delete_all_files_with_particular_extension(ext):
  for root, dirnames, filenames in os.walk(os.path.abspath(os.getcwd())):
    for filename in filenames:
      if filename.endswith(ext):
       os.remove(os.path.join(os.path.abspath(root), filename))

def main():
  if not os.path.isdir('./' + build_folder):
    os.mkdir(build_folder)
  
  for root, dirnames, filenames in os.walk(os.path.abspath(os.getcwd())):
    for filename in filenames:      
      if filename.endswith('List.txt'):  
        type = ContentType.AUDIO
      #if filename.endswith('ListVideos.txt'):
      #  type = ContentType.VIDEO
      else:
        type = ContentType.NONE
      if type != ContentType.NONE:
        path_to_save_content = root
        path_to_format_list = os.path.join(root, filename)
        handler_dir(path_to_save_content, path_to_format_list, type)

try:
    start_time = time.time()
    #delete_all_files_with_particular_extension(('.mp3', '.webm'))
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
except Exception as err:
    if os.path.isdir(tmp_folder):
      shutil.rmtree(tmp_folder) 
    print(err, file=sys.stderr)
    traceback.print_exc()