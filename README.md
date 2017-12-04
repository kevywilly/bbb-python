# bbb-python


```bash
sudo su root
cd ~

# add ssh key
ssh-keygen -t rsa -b 4096
cat .ssh/id_rsa.pub

# install python io
git clone git://github.com/adafruit/adafruit-beaglebone-io-python.git
cd adafruit-beaglebone-io-python
sudo python setup.py install

# install pwm driver
git clone https://github.com/adafruit/Adafruit_Python_PCA9685.git
cd Adafruit_Python_PCA9685
sudo python setup.py install

# install beaglebone fix for gpio i2c which uses I2C1 by default
# However bbb makes I2C2 available by default on pins p19 and p20 on header 9

git clone git@github.com:kevywilly/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
sudo python setup.py install

# install pip
pip install numpy scypy

# download bbb-python 
cd /var/lib/cloud9/
git clone git@github.com:kevywilly/bbb-python.git

# give cloud9 access to folder
chown -R root:cloud9ide bbb-python
chmod 775 -R bbb-python


```
