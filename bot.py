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




@bot.message_handler(commands=['farm'])
def farm(m):
    user=users.find_one({'id':m.from_user.id})
    if user!=None:
        if user['id'] not in rest:
            findres(user, m)
        else:
            bot.send_message(m.chat.id, 'Отдохните минуту перед следующей добычей ресурсов!')


            
@bot.message_handler(commands=['craft'])
def craft(m):
    user=users.find_one({'id':m.from_user.id})
    if user!=None:
        mainmenu(user, m)
            

def mainmenu(user, m, edit=False):  
    kb=types.InlineKeyboardMarkup()
    text='Выберите предмет для просмотра информации.'
    for ids in recipes:
        kb.add(types.InlineKeyboardButton(text=resname(ids), callback_data=str(user['id'])+' info '+ids))
    if edit==False:
        try:
            bot.send_message(m.chat.id, text, reply_markup=kb)
        except:
            bot.send_message(m.message.chat.id, text, reply_markup=kb)
    else:
        medit(text, m.message.chat.id, m.message.message_id)
            

@bot.message_handler()
def allmessages(m):
    if users.find_one({'id':m.from_user.id})==None:
        users.insert_one(createuser(m.from_user))
        bot.send_message(m.chat.id, 'Здарова, новичок! Жми /farm, чтобы фармить ресурсы и крафтить патроны!')
    user=users.find_one({'id':m.from_user.id})
    if user['name']!=m.from_user.first_name or user['username']!=m.from_user.username:
        users.update_one({'id':user['id']},{'$set':{'name':m.from_user.first_name, 'username':m.from_user.username}})
        user=users.find_one({'id':m.from_user.id})
      
    bullet=None
    if m.text[:12].lower()=='железная пуля':
        bullet='iron_bullet'
    elif m.text[:11].lower()=='золотая пуля':
        bullet='gold_bullet'
    elif m.text[:12].lower()=='алмазная пуля':
        bullet='diamond_bullet'
    if bullet!=None:
        shoot(m, bullet)
        
       
    
def shoot(m, bullet):
    d_chance=10
    user=users.find_one({'id':m.from_user.id})
    if user!=None:
        if bullet=='iron_bullet':
            timer=60
        if bullet=='gold_bullet':
            timer=180
        if bullet=='diamond_bullet':
            timer=300
            
        shoot=False
        if bullet in user['items']:
            if user['items'][bullet]>0:
                shoot=True
        if shoot==True:
            data=time.time()
            data=data+timer
            if m.reply_to_message!=None:
                try:
                    user2=users.find_one({'id':m.reply_to_message.from_user.id})
                    if user2!=None:
                        i_shield=False
                        d_shield=False
                        if 'iron_shield' in user2['items']:
                            if user2['items']['iron_shield']>0:
                                i_shield=True
                        if 'diamond_shield' in user2['items']:
                            if user2['items']['diamond_shield']>0:
                                d_shield=True
                        if user['username']==None:
                            name1=user['name']
                        else:
                            name1='@'+user['username']
                        if user2['username']==None:
                            name2=user2['name']
                        else:
                            name2='@'+user2['username']
                        restricting=user2['id']
                        if d_shield==True and random.randint(1,100)<=d_chance:
                            text=name1+' попытался застрелить '+name2+', используя ('+resname(bullet).lower()+'), но алмазный щит цели отразил выстрел. '+name1+' убил себя. Респавн через ('+str(int(timer/60))+') минут.'
                            restricting=user['id']
                        elif i_shield==True and bullet!='diamond_bullet':
                            text=name1+' попытался застрелить '+name2+', используя ('+resname(bullet).lower()+'), но у цели был железный щит. '+name1+' убил себя. Респавн через ('+str(int(timer/60))+') минут.'
                            restricting=user['id']
                        else:
                            text=name1+' стреляет в '+name2+', используя ('+resname(bullet).lower()+'). Цель мертва. Респавн цели через ('+str(int(timer/60))+') минут.'
                        bot.restrict_chat_member(m.chat.id, restricting, data, can_send_messages=False,
                                                can_send_media_messages=False, can_send_other_messages=False)
                        bot.send_message(m.chat.id, text)
                        
                    else:
                        bot.send_message(m.chat.id, 'Этот юзер еще не писал ничего в чат!')
                    
                    
                except:
                    bot.send_message(m.chat.id, 'Либо вы стреляете в админа, либо у бота нет права на мут!')
                    bot.send_message(441399484, traceback.format_exc())
                    
            else:
                bot.send_message(m.chat.id, 'Нужно реплайнуть это на кого-то!')
        else:
            bot.send_message(m.chat.id, 'У вас нет такой пули!')
    
    
    
        
@bot.callback_query_handler(func=lambda call:True)
def inline(call):
    user=users.find_one({'id':call.from_user.id})
    if user!=None:
        if int(call.data.split(' ')[0])==user['id']:
            if 'info' in call.data:
                item=call.data.split(' ')[2]
                text=recipes[item]['info']
                text+='\n'
                text+='Требуемые ресурсы:\n\n'
                for ids in recipes[item]:
                    if ids!='info':
                        text+=resname(ids)+': '+str(recipes[item][ids])+'\n'
                kb=types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton(text='Скрафтить', callback_data=str(user['id'])+' craft '+item))
                kb.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
                
                
            elif 'craft' in call.data:
                item=call.data.split(' ')[2]
                craftable=True
                for ids in recipes[item]:
                    if ids!='info':
                        if ids in user['items']:
                            if user['items'][ids]>=recipes[item][ids]:
                                pass
                            else:
                                craftable=False
                        else:
                            craftable=False
                            
                if craftable==True:
                    for ids in recipes[item]:
                        if ids!='info':
                            users.update_one({'id':user['id']},{'$inc':{'items.'+ids:-recipes[item][ids]}})
                if item in user['items']:
                    x='$inc'
                else:
                    x='$set'
                users.update_one({'id':user['id']},{x:{item:1}})
                text='Вы успешно скрафтили предмет "'+resname(item)+'"!'
                medit(text, call.message.chat.id, call.message.message_id)
                
   
            if call.data=='back':
                mainmenu(user, call, edit=True)
                
            
        else:
            bot.answer_callback_query(call.id, 'Это не ваше меню!')

        



def findres(user, m):
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
            users.update_one({'id':user['id']},{x:{'items.'+ids:taken[ids]}})
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
    if res=='glass':
        return 'Стекло'
    if res=='exp':
        return 'Опыт'
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
    return 'Без названия ('+res+')'


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

