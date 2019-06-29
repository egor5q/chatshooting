# -*- coding: utf-8 -*-
import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)


client=MongoClient(os.environ['database'])
db=client.chatshooting
users=db.users


rest=[]
     # GUNPOWDER 6 selitra / 2 coal / 1 sera
allres={'iron':20, 'gold':5, 'diamond':1, 'gunpowder':30, 'selitra':20, 'coal':17, 'sera':15, 'leather':15,
       'exp':25, 'glass':15}                     # Цифра значит количество бросков куба 
                                                 # на получение единицы ресурса
 

ib='Железная пуля. При успешном попадании в цель, та уходит в мут на 1 минуту.'
gb='Золотая пуля. При успешном попадании в цель, та уходит в мут на 3 минуты.'
dib='Алмазная пуля. При успешном попадании в цель, та уходит в мут на 5 минут. Нельзя отразить железным щитом.'
gp='Порох. Нужен для изготовления пуль.'
iss='Железный щит. При наличии, тратится и отражает железную или золотую пулю в стрелявшего.'
ds='Алмазный щит. При наличии, имеет шанс отразить ЛЮБУЮ пулю в стрелявшего. Этот щит нельзя сломать.'
exp='Банка с опытом. При крафте, повышает шансы на нахождение любых ресурсов на 10% от базового. Максимальный бонус: +100%.'


recipes={
    'iron_bullet':{'iron':6,
                  'gunpowder':10,
                   'info':ib
                  },
    'gold_bullet':{'gold':6,
                   'gunpowder':10,
                   'info':gb
                  },
    'diamond_bullet':{'diamond':6,
                      'gunpowder':10,
                      'info':dib
                     },
    'gunpowder':{'selitra':6,
                 'coal':2,
                 'sera':1,
                 'info':gp
                },
    'iron_shield':{'iron':12,
                   'leather':10,
                   'info':iss
             },
    'diamond_shield':{'diamond':40,
                      'leather':40,
                      'iron':50,
                      'gold':15,
                      'info':ds
                     },
    'exp_bottle':{'exp':50,
                  'glass':20,
                  'info':exp
                 }


}







@bot.message_handler(commands=['attack'])
def attack(m):
    pass


@bot.message_handler(commands=['farm'])
def farm(m):
    user=users.find_one({'id':m.from_user.id})
    if user!=None:
        if user['id'] not in rest:
            findres(user)
        else:
            bot.send_message(m.chat.id, 'Отдохните минуту перед следующей добычей ресурсов!')


            
@bot.message_handler(commands=['craft'])
def craft(m):
    user=users.find_one({'id':m.from_user.id})
    if user!=None:
        kb=types.InlineKeyboardMarkup()
        for ids in recipes:
            kb.add(types.InlineKeyboardButton(text=resname(ids), callback_data=str(user['id'])+' info '+ids))
        bot.send_message(m.chat.id, 'Выберите предмет для просмотра информации.', reply_markup=kb)
            


@bot.message_handler()
def allmessages(m):
    if users.find_one({'id':m.from_user.id})==None:
        users.insert_one(createuser(m.from_user))
        bot.send_message(m.chat.id, 'Здарова, новичок! Жми /farm, чтобы фармить ресурсы и крафтить патроны!')
    user=users.find_one({'id':m.from_user.id})
    if user['name']!=m.from_user.first_name or user['username']!=m.from_user.username:
        users.update_one({'id':user['id']},{'$set':{'name':m.from_user.first_name, 'username':m.from_user.username}})
        user=users.find_one({'id':m.from_user.id})
    
        
        
        
@bot.callback_query_handler(func=lambda call:True)
def inline(call):
    user=users.find_one({'id':call.from_user.id})
    if user!=None:
        if int(call.data.split(' ')[0])==user['id']:
            if 'info' in call.data:
                

        



def findres(user):
    taken={}
    for ids in allres:
        amount=0
        for i in range(allres[ids]):
            if random.randint(1,100)<=user['chance']:
                amount+=1
        if amount>0:
            taken.update({ids:amount})
    text='Вот, что вам удалось добыть:\n\n'
    if len(taken)>0:
        for ids in taken:
            text+=resname(ids)+': '+str(taken[ids])+'\n'
            if ids in user['items']:
                x='$inc'
            else:
                x='$set'
            users.update_one({'id':user['id']},{x:'items.'+ids:taken[ids]}})
    else:
        text='Вы ничего не добыли!'
    bot.send_message(m.chat.id, text)
    rest.append(user['id'])
    t=threading.Timer(60, endrest, args=[user['id']])
    t.start()
         
        
def endrest(id):
    if id in rest:
        rest.remove(id)
        
 
def resname(res):
    if res=='iron':
        return 'Железо'
    if res=='gold':
        return 'Золото'
    if res=='diamond':
        return 'Алмазы'
    if res=='gunpowder':
        return 'Порох'
    if res=='selitra':
        return 'Селитра'
    if res=='coal':
        return 'Уголь'
    if res=='sera':
        return 'Сера'
    if res=='leather':
        return 'Кожа'
    if res=='iron_bullet':
        return 'Железная пуля'
    if res=='gold_bullet':
        return 'Золотая пуля'
    if res=='diamond_bullet':
        return 'Алмазная пуля'
    if res=='gunpowder':
        return 'Порох'
    if res=='iron_shield':
        return 'Железный щит'
    if res=='diamond_shield':
        return 'Алмазный щит'
    if res=='exp_bottle':
        return 'Бутыль опыта'


def createuser(user):
    return {
        'id':user.id,
        'name':user.first_name,
        'username':user.username,
        'items':{},
        'chance':10   # %
        
        
    }
        


def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)   

print('7777')
bot.polling(none_stop=True,timeout=600)

