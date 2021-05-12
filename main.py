import  time, math, ujson, networkimport umqttsimple import config 
import webrepl

ping_msg = b''station = network.WLAN(network.STA_IF)
timeData = {'On':config.TIMEON, 'Off':config.TIMEOFF, 'flagon':0,            'Flag':'On', 'color':{'On':[0,0,0], 'Off':[0,0,0]},            'numLEDs':0, 'Prev':0, 'Current':0}newCom = {'borders':[50,100,150], 'level':0, 'state':'blue'}def parse_command(command):    for t in command:        newCom[t] = command[t]    print(newCom)    if newCom['level'] < newCom['borders'][0]:        timeData['numLEDs'] = int(newCom['level']/newCom['borders'][0]*16)        timeData['color']['On'] = (0,config.FULLB,0)    elif newCom['level'] in range(newCom['borders'][0], newCom['borders'][1]):        rel_level = newCom['level']-newCom['borders'][0]        rel_range = newCom['borders'][1]-newCom['borders'][0]        timeData['numLEDs'] = int(rel_level/rel_range*16)+1        timeData['color']['On'] = (config.HALFB,config.HALFB,0)    else:        rel_level = newCom['level']-newCom['borders'][1]        rel_range = newCom['borders'][2]-newCom['borders'][1]        timeData['numLEDs'] = int(rel_level/rel_range*16)+1        if timeData['numLEDs'] >= 16:            timeData['numLEDs'] = 16        timeData['color']['On'] = (config.FULLB,0,0)    if newCom['state'] == 'blue':        timeData['color']['Off'] = (0,0,config.FULLB)    elif newCom['state'] == 'lightblue':        timeData['color']['Off'] = (0,config.HALFB,config.HALFB)    else:        timeData['color']['Off'] = timeData['color']['On']  def mqtt_callback(topic, msg):
    global client
    global ping_msg
    if topic in (config.topics['sub'], config.topics['sub_id']):        try:
            cmd = ujson.loads(msg)
            datahold = cmd.get('datahold')
            parse_command(datahold)
            return         except:            time.sleep(.2)            return
    elif (topic == config.topics['sub_ping']):
        ping_msg = msg

def send_pong(msg, client):
    client.publish(config.topics['pub_id_pong'], msg)
    return
def connect_and_subscribe():    bList = str(station.ifconfig()[0]).split('.')    bList[-1] = '254'    brokerIP = '.'.join(bList)    print("MQTT broker address: " + brokerIP)
    port = config.cfg.get('port')
    user = config.cfg.get('user')
    password = config.cfg.get('password')    client = umqttsimple.MQTTClient(config.cfg.get('client_id'), brokerIP, port, user, password)    client.set_callback(mqtt_callback)    try:        client.connect()    except:        timeData['mqtt_conn'] = False        return client    sub_topics = [config.topics[t] for t in config.topics if 'sub' in t]    for t in sub_topics:        client.subscribe(t)    print('connected to {}, subscribed to {}'.format(brokerIP, sub_topics))    for i in range (config.LINELEN):        config.scale[i] = (0,0,0)    config.scale.write()    try:
        cmd_out = '{"timestamp":1}'
        client.publish(config.topics['pub'], cmd_out)
        timeData['mqtt_conn'] = True    except:        timeData['mqtt_conn'] = False        restart_and_reconnect()    return clientdef restart_and_reconnect():    print('Failed to connect to MQTT broker. Reconnecting...')    if station.isconnected() == False:        print('WiFi connection lost!')        wifi_init()    for x in range(5):        config.scale[0]=(0,255,0)
        config.scale.write()
        time.sleep_ms(250)
        config.scale[0]=(0,0,0)
        config.scale.write()
        time.sleep_ms(250)
def wifi_init():    station.active(True)    station.connect(config.cfg['wlan_ssid'], config.cfg['wlan_password'])    while station.isconnected() == False:        for x in range (5):            config.scale[0]=(255,0,0)            config.scale.write()            time.sleep_ms(250)            config.scale[0]=(0,0,0)            config.scale.write()            time.sleep_ms(250)    print('Connection successful')    print(station.ifconfig())
    webrepl.start()def mqtt_init():    timeData['mqtt_conn'] = False    while timeData['mqtt_conn'] == False:        restart_and_reconnect()        client = connect_and_subscribe()    return clientdef wifi_init():    station.active(True)    station.connect(config.cfg['wlan_ssid'], config.cfg['wlan_password'])    while station.isconnected() == False:        for x in range (5):            config.scale[0]=(255,0,0)            config.scale.write()            time.sleep_ms(250)            config.scale[0]=(0,0,0)            config.scale.write()            time.sleep_ms(250)    print('Connection successful')    print(station.ifconfig())def main():
    global ping_msg    wifi_init()    client = mqtt_init()        while True:        timeData['Current'] = time.ticks_ms()        try:            client.check_msg()            if (timeData['Current'] - timeData['Prev']) >= timeData[timeData['Flag']]:                timeData['Prev'] = timeData['Current']                timeData['flagon'] = (timeData['flagon'] + 1) % 2                timeData['Flag'] = config.FLAGS[timeData['flagon']]                for i in range(timeData['numLEDs']):                    config.scale[i] = timeData['color'][timeData['Flag']]                for i in range(timeData['numLEDs'], config.LINELEN):                    config.scale[i] = (0,0,0)                config.scale.write()
            if ping_msg != b'':
                send_pong(ping_msg, client)
                ping_msg = b''        except OSError as e:            client = mqtt_init()    main()