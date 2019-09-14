from flask import abort, make_response
import dns.resolver
import os

# Data to serve with our API
domains = {
    1: {
        'domain': 'fi.uba.ar',
        'ip':'157.92.49.38',
        'custom':'​False',
    },
}

def obtain_ip(domain_name):
  try:
    result = dns.resolver.query(domain_name)
    dns_records = [ip.address for ip in result]
    ip_address = dns_records[0]
    custom = False
    response = '{{\n  "domain": "{}",\n  "ip": "{}",\n  "custom": {}\n}}'.format(domain_name, ip_address, str(custom).lower())
    #return make_response(ip_address, 200)
    return make_response(response, 200)
  except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
    return "no existe el dominio hijo de puta"

	#response = ''
	#for answer in result.response.answer:
#		response += str(answer) + os.linesep
	#return response#[1].split(" ")[4]


