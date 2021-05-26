FROM python:3.7-slim

RUN mkdir /vlan_control
RUN mkdir /vlan_control/vlan_files

COPY ./vlan_control.py /vlan_control/
COPY ./requirements.txt /vlan_control/
COPY ./rtp_devices.py /vlan_control/
COPY ./sjc_devices.py /vlan_control/

RUN pip install -r /vlan_control/requirements.txt

WORKDIR /vlan_control

ENTRYPOINT ["./vlan_control.py"]
