import machineimport neopixelfrom network import WLANfrom ubinascii import hexlifyENV = 'dev'  LINELEN = 16LINEPIN = 12FLAGS = ['On', 'Off']cfg = {    'client_id': hexlify(machine.unique_id()),    'mac': hexlify(WLAN().config('mac')),    'last_message': 0,    'message_interval': 5,    'counter': 0,    'wlan_ssid': 'ArmyDep',      'wlan_password': 'z0BcfpHu',
    'port': 1883,
    'user': 'mqtt',
    'password': 'skabent0mqtt'}scale = neopixel.NeoPixel(machine.Pin(LINEPIN), LINELEN)
topics = {
    'sub': b'scl/all/cup',
    'sub_id': b'scl/' + cfg['mac'] + b'/cup',
    'sub_ping': b'scl/all/ping',
    'pub': b'ask/scl/all/cup',
    'pub_id': b'ask/scl/' + cfg['mac'] + b'/cup',
    'pub_id_pong': b'ask/scl/' + cfg['mac'] + b'/pong'
}
FULLB = 32HALFB = 32TIMEON = 250TIMEOFF = 250