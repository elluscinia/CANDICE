#-*- coding: utf-8 -*-
import plistlib
import vk
import time
import requests
from Tkinter import *
from tkFileDialog import *

class Face:
    def __init__(self):
        self.but = Button(root)
        self.butUp = Button(root)
        self.txt = Entry(root)
        self.txtT = Entry(root)
        self.lbl = Label(root)

        self.but['text'] = 'Выбрать файл iTunes'
        self.but['font'] = 'Arial 12'
        self.but.bind('<Button-1>',self.open)

        self.butUp['text'] = 'Загрузить плейлист'
        self.butUp['font'] = 'Arial 12'
        self.butUp.bind('<Button-1>',self.upload)

        self.txt['width'] = '100'
        self.txt['bd'] = '1'
        
        self.txtT['width'] = '100'
        self.txtT['bd'] = '1'

        
        self.lbl['text'] = 'Token'
        self.lbl['font'] = 'Arial 12'
        
        self.lbl.pack()
        self.txtT.pack()

        self.but.pack()
        self.txt.pack()

        self.butUp.pack()        
        
    def open(self,event):
        self.txt.delete('0', END)
        op = askopenfilename()
        self.txt.insert('0', op)
    def upload(self,event):
        token = self.txtT.get()
        path = self.txt.get()
        if (token != '') & (path != ''):
            playlists = iTunesPlaylist(path)
            VKPlaylist(playlists, token)
        else:
            print 'Заполнены не все поля'

def iTunesPlaylist(XMLpath):
    """
    Функция для парсинга плейлистов из iTunes 
    :param XMLpath: путь к файлу XML с библиотекой музыки из iTunes
    :param return: возвращает словарь с плейлистами
    """
    library = plistlib.readPlist(XMLpath)

    IDs = []
    tracks = []
    PlayLists = {}

    for playlists in library['Playlists']:
        # вынимаем ID треков из плейлиста и добавляем в список
        for Tracks in playlists.get('Playlist Items'):
            IDs.append(Tracks.get('Track ID'))

        # ищем по ID имя исполнителя и название композиции, добавляем в список треков
        for ID in IDs:
            artist = library.Tracks.get(str(ID)).get('Artist')
            name = library.Tracks.get(str(ID)).get('Name')
            tracks.append(artist + ' - ' + name)

        # меняем начало списка, чтобы искать и добавлять музыку VK снизу вверх
        tracks.reverse()

        # добавляем получившийся плейлист в словарь
        PlayLists.update({playlists.Name: tracks})

    return PlayLists

def VKPlaylist(playlists, token):
    """
    Функция находит композиции VK и добавляет в одноименный плейлист
    :param playlists: словарь плейлистов
    :param token: токен для подключения к API вконтакте
    """
    vkapi = vk.API(access_token=token)
    audio_ids = []

    for playlist in playlists:
        notFind = []
        print playlist.encode('utf-8')

        i = 0
        while (i < len(playlists.get(playlist))):
            try:
                time.sleep(3)
                audio = vkapi.audio.search(q=(playlists.get(playlist))[i].encode('utf-8'), auto_complete=1, sort=2, count=1).get('items')[0]
            except requests.exceptions.Timeout:
                # 'Timeout occurred'
                pass
            except vk.api.VkAPIMethodError as e:
                print e
                print 'Captcha'
                time.sleep(60)
            except IndexError:
                # не найдена
                notFind.append(playlists.get(playlist)[i])
                i += 1
            else:
                # найдено
                i += 1
                flag = 'not add'
                while flag == 'not add':
                    try:
                        time.sleep(3)
                        audio_ids.append(str(vkapi.audio.add(audio_id=audio.get('id'), owner_id=audio.get('owner_id'))))
                    except requests.exceptions.Timeout:
                        # "Timeout occurred"
                        pass
                    except vk.api.VkAPIMethodError as e:
                        print e
                        print 'Captcha[2]'
                        time.sleep(60)
                    else:
                        # добавлено успешно
                        flag = 'add'
                        print audio.get('artist').encode('utf-8'), ' - ', audio.get('title').encode('utf-8')

        # создаём альбом и добавляем туда найденную музыку
        album_id = vkapi.audio.addAlbum(title=playlist).get('album_id')
        vkapi.audio.moveToAlbum(album_id=album_id, audio_ids=','.join(audio_ids))

        print 'Ненайденные композиции:'
        for music in notFind:
            print music.encode('utf-8')

if __name__ == '__main__':
    root = Tk()
    root.wm_title('CANDICE')
    obj = Face()
    root.mainloop()

else:
    print 'CANDICE - модуль для переноса плейлиста из iTunes в VK'