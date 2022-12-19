import json
import logging
from json import dumps, loads

from kafka import KafkaProducer, KafkaConsumer

logging.basicConfig(level=logging.INFO)


class Producer:
    def send_message(self, topic, data, ip, port):


        producer = KafkaProducer(bootstrap_servers=ip+":"+port,
                                     compression_type='gzip',
                                     max_request_size=3173440261,
                                     value_serializer=lambda x:
                                     dumps(x, ensure_ascii=False).encode('utf-8'))
        producer.send(topic, value=data)
        producer.flush()
