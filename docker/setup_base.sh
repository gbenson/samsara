set -exuo pipefail

echo 'assumeyes=1' >> /etc/yum.conf

yum install deltarpm
yum update

yum install libxml2-python libxslt-python python-virtualenv mailcap

yum clean all
rm -rf /usr/share/doc/*
