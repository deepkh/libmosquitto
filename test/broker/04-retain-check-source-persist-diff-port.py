#!/usr/bin/env python

# Test for CVE-2018-12546, with the broker being stopped to write the persistence file, plus subscriber on different port.

import inspect, os, sys
# From http://stackoverflow.com/questions/279237/python-import-a-module-from-a-folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import mosq_test
import signal

def write_config(filename, port1, port2, per_listener):
    with open(filename, 'w') as f:
        f.write("per_listener_settings %s\n" % (per_listener))
        f.write("check_retain_source true\n")
        f.write("port %d\n" % (port1))
        f.write("acl_file %s\n" % (filename.replace('.conf', '.acl')))
        f.write("persistence true\n")
        f.write("persistence_file %s\n" % (filename.replace('.conf', '.db')))
        f.write("listener %d\n" % (port2))

def write_acl_1(filename, username):
    with open(filename, 'w') as f:
        if username is not None:
            f.write('user %s\n' % (username))
        f.write('topic readwrite test/topic\n')

def write_acl_2(filename, username):
    with open(filename, 'w') as f:
        if username is not None:
            f.write('user %s\n' % (username))
        f.write('topic read test/topic\n')


def do_test(per_listener, username):
    conf_file = os.path.basename(__file__).replace('.py', '.conf')
    write_config(conf_file, port1, port2, per_listener)

    persistence_file = os.path.basename(__file__).replace('.py', '.db')
    try:
        os.remove(persistence_file)
    except OSError:
        pass

    acl_file = os.path.basename(__file__).replace('.py', '.acl')
    write_acl_1(acl_file, username)


    rc = 1
    keepalive = 60
    connect_packet = mosq_test.gen_connect("retain-check", keepalive=keepalive, username=username)
    connack_packet = mosq_test.gen_connack(rc=0)

    if per_listener == "true":
        u = None
    else:
        # If per listener is false, then the second client will be denied
        # unless we provide a username
        u = username

    connect2_packet = mosq_test.gen_connect("retain-recv", keepalive=keepalive, username=u)
    connack2_packet = mosq_test.gen_connack(rc=0)

    mid = 1
    publish_packet = mosq_test.gen_publish("test/topic", qos=0, payload="retained message", retain=True)
    subscribe_packet = mosq_test.gen_subscribe(mid, "test/topic", 0)
    suback_packet = mosq_test.gen_suback(mid, 0)

    pingreq_packet = mosq_test.gen_pingreq()
    pingresp_packet = mosq_test.gen_pingresp()

    broker = mosq_test.start_broker(filename=os.path.basename(__file__), use_conf=True, port=port1)

    try:
        sock = mosq_test.do_client_connect(connect_packet, connack_packet, port=port1)
        sock.send(publish_packet)
        sock.close()

        sock = mosq_test.do_client_connect(connect2_packet, connack2_packet, port=port2)
        mosq_test.do_send_receive(sock, subscribe_packet, suback_packet, "suback 1")

        if mosq_test.expect_packet(sock, "publish", publish_packet):
            sock.close()

            # Remove "write" ability
            write_acl_2(acl_file, username)
            broker.terminate()
            broker.wait()

            broker = mosq_test.start_broker(filename=os.path.basename(__file__), use_conf=True, port=port1)

            sock = mosq_test.do_client_connect(connect2_packet, connack2_packet, port=port2)
            mosq_test.do_send_receive(sock, subscribe_packet, suback_packet, "suback 2")
            # If we receive the retained message here, it is a failure.
            mosq_test.do_send_receive(sock, pingreq_packet, pingresp_packet, "pingresp")
            rc = 0

        sock.close()
    finally:
        broker.terminate()
        broker.wait()
        os.remove(conf_file)
        os.remove(acl_file)
        os.remove(persistence_file)
        (stdo, stde) = broker.communicate()
        if rc:
            print(stde)
            exit(rc)


(port1, port2) = mosq_test.get_port(2)
do_test("true", username=None)
do_test("true", username="test")
do_test("false", username=None)
do_test("false", username="test")
