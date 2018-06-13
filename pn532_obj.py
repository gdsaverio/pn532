#------------------------
# Transformed in object by gdsaverio (Italy)
# Date 13/06/2018
#
# Note that the I2C connection is externaly created so you can use it for other peripherals
#-----------------------

import time

class PN532:
  I2C=None
  Addr=36
  CardNum=0
  CardResult=''
  
  def __init__(self,wI2C,wAddr=36):
    self.I2C=wI2C
    self.Addr=wAddr

  def wait_ack(self):
    while True:
      ack = str(self.I2C.readfrom(self.Addr, 12)).replace('\\x',' ').replace("b'",'').strip()
      if ack[0:11] == '01 00 00 ff':
        if ack[0:20] == '01 00 00 ff 00 ff 00':
          return True
        else:
          print('ACK %s not success' %ack)
          return False
        time.sleep(0.2)	
          
  def read(self,len=30):
    rbytes = self.I2C.readfrom(self.Addr,len)
    result = str(rbytes).replace('\\x',' ').replace("b'",'').strip()
    if result[0:11] == '01 00 00 ff':
      return rbytes
    else:
      return False

  def write(self,cmd):
    self.I2C.writeto(self.Addr, cmd)
    time.sleep(0.1)
    if self.wait_ack():
      return True
    else:
      return False

  def get_version(self):
    cmd_version = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x02\xFE\xD4\x02\x2A')
    if self.write(cmd_version):
      return self.read()
    else:
      return False
    
  def config(self):
    cmd_config = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x05\xFB\xD4\x14\x01\x02\x01\x14')
    if self.write(cmd_config):
      return True
    else:
      return False

  def wait_card(self):
    self.CardNum=0
    self.CardResult=''
    if not self.config():
      return False
    cmd_waitcard = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x04\xFC\xD4\x4A\x01\x00\xE1')
    if self.write(cmd_waitcard):
      while True:
        result = self.read(len=100)
        if result:
          result = (' '.join([str('%02X' % c) for c in result]))
          l = int(result[36:38],0)
          nl = 38+l+l/2
          card_num = int(result[39:int(nl)].replace(' ','').strip(),16)
          self.CardNum=card_num
          self.CardResult=result
          return True
        time.sleep(0.2)
    else:
      return False
